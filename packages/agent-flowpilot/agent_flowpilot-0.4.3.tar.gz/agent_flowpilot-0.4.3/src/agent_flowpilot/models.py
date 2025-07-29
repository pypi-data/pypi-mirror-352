# ========== 基础类型定义 ==========
from dataclasses import asdict, dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple


class TaskStatus(Enum):
    PENDING = auto()
    WAITING_FOR_INPUT = auto()
    READY = auto()
    STARTED = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    SKIPPED = auto()


@dataclass
class TaskDefinition:
    name: str
    description: str
    parameters: Dict[str, Any]
    required_parameters: List[str]
    optional_parameters: List[str]
    execution_mode: str  # 'sequential', 'parallel'
    depends_on: List[str]  # 任务名称列表
    is_end_task: bool = False  # 是否是结束任务

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class TaskResult:
    status: TaskStatus
    output: Dict[str, Any]
    error: Optional[str] = None
    exception: Optional[Exception] = None

    def __post_init__(self):
        """验证状态一致性"""
        if self.status == TaskStatus.COMPLETED and self.error:
            raise ValueError("Completed task cannot have error")
        if self.status == TaskStatus.FAILED and not self.error:
            raise ValueError("Failed task must have error message")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


# ========== 异常定义 ==========
class TaskFailedError(Exception):
    """自定义任务失败异常"""

    def __init__(self, task_name: str, reason: str, dependency_chain: List[str] | None = None):
        self.task_name = task_name
        self.reason = reason
        self.dependency_chain = dependency_chain or []
        message = f"task: '{task_name}' failed: {reason}"
        if dependency_chain:
            message += f"dependency: {' → '.join(dependency_chain)}"
        super().__init__(message)


# ========== 核心类实现 ==========
class Task:
    """
    表示一个任务的类，包含任务的定义、状态、执行结果等信息。
    """

    def __init__(self, definition: TaskDefinition):
        """
        初始化任务对象。

        参数:
            definition (TaskDefinition): 任务的定义对象，包含任务的名称、描述、参数等信息。
        """

        self.definition = definition
        self.status: TaskStatus = TaskStatus.PENDING
        self.result: Optional[TaskResult] = None
        self._resolved_parameters = {}
        self._missing_parameters = []
        self.is_end_task = definition.is_end_task  # 新增：标记是否为结束任务

    def resolve_parameters(self, context: Dict[str, Any]) -> Tuple[bool, str]:
        """
        解析参数
        返回: (是否成功, 失败原因)
        """
        self._resolved_parameters: Dict[str, Any] = {}
        self._missing_parameters = []

        # 1. 合并默认参数
        for param, value in self.definition.parameters.items():
            if value:
                self._resolved_parameters[param] = value

        # 2. 检查必需参数
        missing_required: List[str] = []
        for param in self.definition.required_parameters:
            if param not in self._resolved_parameters or not self._resolved_parameters[param]:
                # 尝试从上下文获取
                if param in context and context[param]:
                    self._resolved_parameters[param] = context[param]
                else:
                    missing_required.append(param)
        # 3. 检查可选参数
        for param in self.definition.optional_parameters:
            if param not in self._resolved_parameters or not self._resolved_parameters[param]:
                # 尝试从上下文获取
                if param in context and context[param]:
                    self._resolved_parameters[param] = context[param]

        # 4. 记录缺失参数
        self._missing_parameters = missing_required

        if missing_required:
            return False, f"Missing required parameters: {missing_required}"
        return True, ""

    @property
    def resolved_parameters(self) -> Dict[str, Any]:
        return self._resolved_parameters

    @property
    def missing_parameters(self) -> List[str]:
        return self._missing_parameters

    def mark_ready(self):
        self.status = TaskStatus.READY

    def mark_started(self):
        self.status = TaskStatus.STARTED

    def mark_running(self):
        self.status = TaskStatus.RUNNING

    def mark_completed(self, result: TaskResult):
        self.result = result
        self.status = TaskStatus.COMPLETED

    def mark_failed(self, error: str, exception: Exception | None = None):
        self.result = TaskResult(output={}, error=error, status=TaskStatus.FAILED, exception=exception)
        self.status = TaskStatus.FAILED

    def mark_skipped(self, reason: str = ""):
        self.result = TaskResult(output={}, error=reason, status=TaskStatus.SKIPPED)
        self.status = TaskStatus.SKIPPED

    def __repr__(self):
        return f"<Task name={self.definition.name} status={self.status} depends_on={self.definition.depends_on} is_end_task={self.is_end_task}>"

    def to_dict(self):
        return {
            "name": self.definition.name,
            "status": self.status.name,
            "definition": self.definition.to_dict(),
            "depends_on": self.definition.depends_on,
            "is_end_task": self.is_end_task,
            "result": self.result.to_dict() if self.result else None,
        }


@dataclass
# 定义任务通知类，用于在任务状态发生变化时传递相关信息
class TaskNotification:
    """
    任务通知类，用于在任务状态发生变化时传递相关信息。

    Attributes:
        transaction (str): 事务ID，用于标识任务的执行上下文。
        status (TaskStatus): 任务的当前状态，使用 TaskStatus 枚举类型。
        task (Task): 当前正在执行任务信息.
        output (Dict[str, Any]): 任务执行的输出结果，以字典形式存储。
        error (Optional[str]): 任务执行过程中可能出现的错误信息，可选参数。
        exception (Optional[Exception]): 任务执行过程中可能抛出的异常对象，可选参数。
    """

    transaction: str
    status: TaskStatus
    task: Task
    context: Dict[str, Any] | None = None
    error: Optional[str] = None

    def to_dict(self):
        """
        将 TaskNotification 实例转换为字典。

        Returns:
            dict: 包含任务通知信息的字典。
        """
        result = {
            "status": self.status.name,
            "task": self.task.to_dict(),
            "context": self.context,
            "error": self.error,
        }
        return result

    def __repr__(self):
        """
        返回任务通知对象的字符串表示形式。

        Returns:
            str: 包含任务状态、错误信息和输出结果的字符串。
        """
        return f"<TaskNotification status={self.status} task={self.task.definition.name} error={self.error}>"


@dataclass
class UserResponse:
    """
    用户输入请求类，用于在任务执行过程中请求用户输入。
    Attributes:
        task_id (str): 任务的唯一标识符。
        question (str): 向用户提问的问题。
        params (List[str]): 需要用户输入的参数列表。
    """

    task_id: str
    question: str
    answers: Dict[str, Any]
