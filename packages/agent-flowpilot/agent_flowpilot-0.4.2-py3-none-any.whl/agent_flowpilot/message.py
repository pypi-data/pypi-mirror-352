from typing import List
from abc import ABC, abstractmethod
from .models import TaskNotification, UserResponse

class MessageAdapter(ABC):
    """外部服务适配器抽象类"""

    @abstractmethod
    async def request_user_input(
        self, task_id: str, question: str, params: List[str]
    ) -> UserResponse:
        """通过外部服务请求用户输入"""
        pass

    @abstractmethod
    async def notify(self, notification: TaskNotification):
        pass
