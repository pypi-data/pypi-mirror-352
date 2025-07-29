import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
import copy

from .models import TaskNotification, Task, TaskStatus, TaskFailedError, TaskDefinition
from .executor import ToolExecutor
from .message import MessageAdapter
from .scheduler import TaskScheduler


class AgentFlowPilot:
    """
    负责加载任务定义、调度任务执行以及处理任务执行过程中的各种状态。
    """

    def __init__(
        self,
        tool_executor: ToolExecutor,
        external_service: MessageAdapter,
        logger: logging.Logger,
        context: Dict[str, Any] = {},
    ):
        self.tasks: Dict[str, Task] = {}
        self.context: Dict[str, Any] = context
        self.tool_executor: ToolExecutor = tool_executor
        self.external_service: MessageAdapter = external_service
        self.logger: logging.Logger = logger
        self.scheduler = TaskScheduler(self.context, logger)
        self.snapshot: Optional[Task] = None
        self.transaction = ""

    def load_tool_chain(self, transaction: str, definitions: List[Dict[str, Any]]) -> None:
        """
        加载任务定义

        参数:
            definitions (List[Dict[str, Any]]): 任务定义列表

        异常:
            ValueError: 当定义列表为空或格式不正确时抛出
        """
        self.transaction = transaction
        if not definitions:
            raise ValueError("任务定义列表不能为空")
        definitions[-1]["is_end_task"] = True
        try:
            self.tasks = {definition["name"]: Task(TaskDefinition(**definition)) for definition in definitions}
            self.scheduler.tasks = self.tasks
        except KeyError as e:
            raise ValueError(f"任务定义格式不正确:  {self.transaction} 缺少必要的键 {e}")
        except Exception as e:
            raise ValueError(f"加载任务定义失败:  {self.transaction}  {str(e)}")

    def finally_status(self) -> TaskStatus:
        """
        获取任务流的最终状态
        返回:
            TaskStatus: 任务流的最终状态
        """
        all_completed = all(task.status == TaskStatus.COMPLETED for task in self.tasks.values())
        return TaskStatus.COMPLETED if all_completed else TaskStatus.FAILED

    def get_execution_report(self) -> Dict[str, Any]:
        """
        获取执行报告

        返回:
            Dict[str, Any]: 包含任务执行状态、上下文和任务信息的报告
        """
        all_completed = all(task.status == TaskStatus.COMPLETED for task in self.tasks.values())

        snapshot_data = self.snapshot.definition.to_dict() if self.snapshot else {}

        task_info = {}
        for name, task in self.tasks.items():
            result = task.result
            task_info[name] = {
                "status": task.status.name,
                "parameters": task.resolved_parameters,
                "result": (result.output if result and hasattr(result, "output") else None),
                "error": result.error if result and hasattr(result, "error") else None,
                "is_end_task": task.is_end_task,
            }

        return {
            "status": "COMPLETED" if all_completed else "FAILED",
            "context": self.context,
            "snapshot": snapshot_data,
            "tasks": task_info,
        }

    async def arun(self) -> None:
        if not self.scheduler or not self.tasks:
            raise ValueError("请先加载任务定义")

        scheduler_task = asyncio.create_task(self.scheduler.scheduler_loop())
        run_task = asyncio.create_task(self._arun())
        await asyncio.gather(scheduler_task, run_task)

    async def _notify(self, status: TaskStatus, task: Optional[Task]):
        """
        通知外部服务任务状态变化
        """
        if not task:
            return

        self.logger.info(f"通知外部服务任务状态变化: {self.transaction} {status}, task: {task.status.name}")
        notification = TaskNotification(
            transaction=self.transaction, status=status, task=copy.deepcopy(task), context=self.context
        )
        taskx = asyncio.create_task(self.external_service.notify(notification))
        asyncio.gather(taskx)

    async def _arun(self) -> None:
        """
        运行任务流

        异常:
            ValueError: 当未加载任务定义时抛出
            TaskFailedError: 当任务执行失败时抛出
        """
        self.logger.info("任务流开始执行")
        self.context.update({"__status__": TaskStatus.RUNNING})
        try:
            # 任务执行循环
            task = None
            started = True
            while True:
                if self.scheduler.all_tasks_finished():
                    self.logger.info(f"所有任务已完成 {self.transaction}")
                    break
                # 1. 处理就绪任务
                next_task = await self.scheduler.get_next_task()
                if next_task:
                    if not started:
                        await self._notify(TaskStatus.STARTED, task)
                        started = True
                    task_name, task = next_task
                    self.logger.info(f"执行任务: {self.transaction}, {task_name}, 状态: {task.status}")
                    task.mark_running()
                    self.snapshot = task
                    await self._notify(TaskStatus.RUNNING, task)
                    success = await self._execute_task(task)
                    status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
                    await self.scheduler.update_task_status(task_name, status)

                    await self._notify(TaskStatus.RUNNING, task)

                    log_msg = f"已执行任务: {self.transaction}, {task_name}, 状态: {status}"
                    if status != TaskStatus.COMPLETED:
                        log_msg += f", 原因: {task.result.error if task.result else '未知错误'}"
                        self.logger.info(log_msg)
                        break
                    else:
                        log_msg += f", 输出: {task.result.output if task.result else None}"
                        self.logger.info(log_msg)
                    if task.definition.is_end_task:
                        break
                # 2. 检查是否有因参数缺失而阻塞的任务
                blocked_task = self._find_blocked_task()
                if blocked_task:
                    task_name, task, reason = blocked_task
                    await self._handle_blocked_task(task_name, reason)
                    self.logger.info(f"发现被阻塞的任务: {self.transaction}, {task_name}, 原因: {reason}")
                    self.snapshot = task
                    continue

                # 3. 避免CPU空转
                await asyncio.sleep(0.01)
        except Exception as e:
            self.logger.exception(f"任务流执行异常: {self.transaction}, {str(e)}")
            raise TaskFailedError("TaskManager", f"系统错误: {self.transaction}, {str(e)}") from e
        finally_status = self.finally_status()
        self.context.update({"__status__": finally_status})
        await self._notify(finally_status, self.snapshot)

    def _find_blocked_task(self) -> Optional[Tuple[str, Task, str]]:
        """
        查找因参数缺失而阻塞的任务

        返回:
            Optional[Tuple[str, Task, str]]: 任务名称、任务对象和阻塞原因的元组，如果没有找到则返回None
        """
        for task_name, task in self.tasks.items():
            if task.status != TaskStatus.PENDING:
                continue

            # 检查依赖是否满足
            if not self._check_dependencies_met(task):
                continue

            # 检查参数是否满足
            success, reason = task.resolve_parameters(self.context)
            if not success:
                return task_name, task, reason

        return None

    def _check_dependencies_met(self, task: Task) -> bool:
        """
        检查任务的依赖是否满足

        参数:
            task (Task): 要检查的任务

        返回:
            bool: 如果所有依赖都已完成则返回True
        """
        return all(self.tasks[dep].status == TaskStatus.COMPLETED for dep in task.definition.depends_on)

    async def _handle_blocked_task(self, task_name: str, reason: str) -> None:
        """
        处理被阻塞的任务

        参数:
            task_name (str): 任务名称
            reason (str): 阻塞原因
        """
        task = self.tasks[task_name]
        # 尝试通过外部服务获取参数
        try:
            response = await asyncio.wait_for(
                self.external_service.request_user_input(task_name, reason, task.missing_parameters),
                timeout=30.0,
            )
            self.logger.info(f"等待用户输入: {self.transaction}, {response}, {isinstance(response, dict)}")
            answers = response.answers if response else {}
            if response and isinstance(response, dict) and answers:
                # 更新参数
                self._update_task_parameters(task, answers)

                # 再次检查参数
                success, _ = task.resolve_parameters(self.context)
                if success:
                    await self.scheduler.ready_queue.put(task_name)
                    return

        except asyncio.TimeoutError:
            reason = f"等待用户输入超时: {self.transaction}"
        except Exception as e:
            reason = f"处理用户输入时出错: {self.transaction}, {str(e)}"

        # 标记任务失败
        self._mark_task_and_dependencies_failed(task_name, reason)

    def _update_task_parameters(self, task: Task, answers: Dict[str, Any]) -> None:
        """
        使用用户提供的答案更新任务参数

        参数:
            task (Task): 要更新的任务
            answers (Dict[str, Any]): 用户提供的参数值
        """
        for param in task.missing_parameters:
            if param in answers:
                task.definition.parameters[param] = answers[param]

    def _mark_task_and_dependencies_failed(self, task_name: str, reason: str) -> None:
        """
        标记任务及其依赖任务为失败或跳过

        参数:
            task_name (str): 任务名称
            reason (str): 失败原因
        """
        task = self.tasks[task_name]
        task.mark_failed(reason)
        asyncio.create_task(self.scheduler.update_task_status(task_name, TaskStatus.FAILED))

        # 跳过依赖此任务的所有后续任务
        for name, t in self.tasks.items():
            if task_name in t.definition.depends_on and t.status == TaskStatus.PENDING:
                t.mark_skipped(f"前置任务 {self.transaction}, {task_name} 失败: {reason}")
                asyncio.create_task(self.scheduler.update_task_status(name, TaskStatus.SKIPPED))

    async def _execute_task(self, task: Task) -> bool:
        """
        执行单个任务

        参数:
            task (Task): 要执行的任务

        返回:
            bool: 任务执行成功返回True，否则返回False
        """
        try:
            result = await self.tool_executor.execute(
                task.definition.name, self.context.copy(), task.resolved_parameters
            )

            # 判断任务执行结果
            if result is None:
                task.mark_failed("执行任务时未返回有效结果")
                return False

            if result.status == TaskStatus.COMPLETED:
                task.mark_completed(result)
                return True
            else:
                task.mark_failed(result.error or "", result.exception)
                return False

        except Exception as e:
            task.mark_failed(str(e), e)
            self.logger.exception(f"执行任务失败: {self.transaction}, {task.definition.name}")
            return False
