import inspect
from typing import Any, get_type_hints, Callable, Dict, List


def python_type_to_json_type(py_type: Any):
    if py_type in [str]:
        return "string"
    elif py_type in [int]:
        return "integer"
    elif py_type in [float]:
        return "number"
    elif py_type in [bool]:
        return "boolean"
    elif py_type in [list, tuple]:
        return "array"
    elif py_type in [dict]:
        return "object"
    else:
        return "string"  # fallback


def func_to_function_calling(func: Callable[..., Any]) -> Any:
    """
    # 将 Python 函数转换为 OpenAI 的函数调用模式
    """

    if not callable(func):
        raise ValueError("Input must be a callable function.")
    sig = inspect.signature(func)
    hints = get_type_hints(func)

    properties = {}
    required: List[str] = []

    for name, param in sig.parameters.items():
        param_type = hints.get(name, str)
        json_type = python_type_to_json_type(param_type)

        properties[name] = {"type": json_type, "description": f"{name}"}

        if param.default is inspect.Parameter.empty:
            required.append(name)

    data: Dict[str, Any] = {
        "name": getattr(func, "_tool_name") or func.__name__,
        "description": (getattr(func, "_tool_description") or func.__doc__ or "").rstrip("\n"),
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }
    return data
