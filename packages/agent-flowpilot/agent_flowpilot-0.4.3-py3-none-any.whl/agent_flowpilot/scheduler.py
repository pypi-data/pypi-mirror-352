import asyncio
import logging
from typing import Any, Dict, Optional, Tuple

from .models import Task, TaskStatus


class TaskScheduler:
    """任务调度器"""

    def __init__(self, context: Dict[str, Any], logger: logging.Logger):
        self.tasks: Dict[str, Task] = {}
        self.context = context
        self.ready_queue: asyncio.Queue[str] = asyncio.Queue()
        self.logger: logging.Logger = logger

    def _check_dependencies(self, task_name: str) -> bool:
        """检查任务依赖是否就绪"""
        for dep in self.tasks[task_name].definition.depends_on:
            if self.tasks[dep].status != TaskStatus.COMPLETED:
                return True
        return False

    def _dependencies_failed(self, task_name: str) -> bool:
        """检查任务依赖是否失败"""
        for dep in self.tasks[task_name].definition.depends_on:
            if self.tasks[dep].status in [TaskStatus.FAILED, TaskStatus.SKIPPED]:
                return True
        return False

    def _is_task_ready(self, task_name: str) -> bool:
        """检查任务是否就绪"""
        task = self.tasks[task_name]
        # 检查依赖
        if self._check_dependencies(task_name):
            return False

        # 检查参数
        success, _ = task.resolve_parameters(self.context)
        return success

    async def scheduler_loop(self):
        """调度器主循环，监控任务状态并填充就绪队列"""
        self.logger.debug("任务调度器启动")
        try:
            while True:
                if self.all_tasks_finished():
                    break
                # 检查所有待处理任务，将就绪任务加入队列
                for name, task in self.tasks.items():
                    if self._dependencies_failed(name):
                        self.logger.error(f"任务 {name} 依赖失败，跳过")
                        task.mark_skipped("prev task failed")
                        continue
                    if task.status == TaskStatus.PENDING and self._is_task_ready(name):
                        await self.ready_queue.put(name)
                        self.logger.debug(
                            f"任务 {name} 已加入就绪队列 {self.ready_queue} {task.definition.is_end_task}"
                        )
                        task.mark_ready()
                        if task.definition.is_end_task:
                            break

                await asyncio.sleep(0.1)
        except Exception as e:
            self.logger.exception(f"调度器异常: {e}")

        self.logger.debug(f"就绪队列已终止 {self.ready_queue}")

    async def get_next_task(self, timeout: float = 0.1) -> Optional[Tuple[str, Task]]:
        """
        获取下一个就绪任务

        Args:
            timeout: 等待任务的最大时间（秒）

        Returns:
            如果有就绪任务，返回(任务名, 任务对象)的元组；否则返回None
        """
        try:
            task_name = await asyncio.wait_for(self.ready_queue.get(), timeout=timeout)
            return task_name, self.tasks[task_name]
        except asyncio.TimeoutError:
            return None

    async def update_task_status(self, task_name: str, status: TaskStatus):
        """更新任务状态并处理后续逻辑"""
        self.tasks[task_name].status = status

        if status == TaskStatus.COMPLETED:
            # 添加到已完成任务集合
            # 将输出添加到上下文
            if self.tasks[task_name].result:
                result = self.tasks[task_name].result
                if result:
                    self.context.update(result.output)

            # 标记队列项为已完成
            self.ready_queue.task_done()

    def all_tasks_finished(self) -> bool:
        """检查所有任务是否已完成"""
        status = [TaskStatus.PENDING, TaskStatus.STARTED, TaskStatus.RUNNING]
        return [task.status in status for task in self.tasks.values()] == 0
