from collections.abc import Callable, Awaitable
import inspect
import functools
from typing import Any, Tuple, Dict
from .function import func_to_function_calling


class ToolBox:
    """
    工具盒
    1. 使用方式1 初始化实例，调用register接口注册工具
        def sum_func(a, b):
            return a + b
        toolbox = ToolBox()
        toolbox.register("sum_tool", sum_func, "计算两个数的和")
    2. 使用方式2 装饰器方式注册工具
        class ExampleTool(ToolBox):
            def __init__(self):
                super().__init__()

            @ToolBox.tool(name="example_tool", description="这是一个示例工具")
            def example_method(self, arg1, arg2):
                return arg1 + arg2
        example_tool = ExampleTool()
        tools = example_tool.to_schema()
    """

    def __init__(self):
        self.tools: Dict[str, Any] = {}
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if getattr(method, "_is_tool", False):
                tool_name = getattr(method, "_tool_name") or name
                self.tools[tool_name] = method

    def get(self, name: str):
        """
        获取工具
        """
        return self.tools.get(name, None)

    def register(self, name: str, func: Callable[..., Awaitable[Any]], description: str = ""):
        """
        注册工具
        """
        if not inspect.iscoroutinefunction(func):
            raise TypeError(f"decorated func <{name}> must be an async function.")

        self.tools[name] = func
        setattr(func, "_is_tool", True)
        setattr(func, "_tool_name", name)
        setattr(func, "_tool_description", description or func.__doc__)

    def is_args_satisfied(self, func: Callable[..., Any], args_dict: Dict[str, Any]):
        """
        判断给定的 args_dict 是否满足 func 的参数要求。
        """
        sig = inspect.signature(func)
        for name, param in sig.parameters.items():
            if param.default is param.empty and param.kind in (
                param.POSITIONAL_ONLY,
                param.POSITIONAL_OR_KEYWORD,
                param.KEYWORD_ONLY,
            ):
                if name not in args_dict:
                    return False  # 缺少必需参数

        return True  # 所有必需参数都在 args_dict 中

    def build(self):
        """
        转换为函数列表open ai 格式的tools
        @https://platform.openai.com/docs/guides/function-calling?api-mode=responses
        """
        return [{"type": "function", "function": func_to_function_calling(func)} for _, func in self.tools.items()]

    @classmethod
    def tool(cls, name: str | None = None, description: str = ""):
        """
        工具装饰器, 必须是一个继承了ToolBox的类的方法
        只标记，不立即注册
        """

        def decorator(func: Any) -> Any:
            func._is_tool = True
            func._tool_name = name or func.__name__
            func._tool_description = description or func.__doc__

            if not inspect.iscoroutinefunction(func):
                raise TypeError(f"decorated func <{func._tool_name}> must be an async function.")

            @functools.wraps(func)
            async def async_wrapper(*args: Tuple[Any], **kwargs: Dict[str, Any]) -> Callable[..., Awaitable[Any]]:
                return await func(*args, **kwargs)

            return async_wrapper

        return decorator
