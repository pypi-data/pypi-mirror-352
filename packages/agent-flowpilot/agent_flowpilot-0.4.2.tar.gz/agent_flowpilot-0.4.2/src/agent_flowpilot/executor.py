from typing import Dict, Any
from abc import ABC, abstractmethod
from .models import TaskResult


class ToolExecutor(ABC):
    """工具执行器抽象类"""

    @abstractmethod
    async def execute(self, tool_name: str, context: Dict[str, Any], parameters: Dict[str, Any]) -> TaskResult | None:
        """
        执行工具并返回结果
        return: TaskResult
        """
        pass
