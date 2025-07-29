import os
import logging
import asyncio
from typing import Any, Dict, List
import openai

from agent_flowpilot.core import AgentFlowPilot
from agent_flowpilot.intent import IntentRecognizer
from agent_flowpilot.json import parse_json
from agent_flowpilot.message import MessageAdapter
from agent_flowpilot.tools import ToolBox
from agent_flowpilot.models import (
    TaskResult,
    TaskStatus,
    TaskNotification,
    TaskFailedError,
    UserResponse,
)
from agent_flowpilot.executor import ToolExecutor
from agent_flowpilot.validate import validate_tool_chain_output

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s"))
logger.addHandler(handler)


class MockMessageServiceAdapter(MessageAdapter):
    """消息服务适配器实现"""

    def __init__(self, message_service_client: Any):
        self.client = message_service_client

    async def request_user_input(self, task_id: str, question: str, params: List[str]) -> UserResponse:
        """通过消息服务发送输入请求"""
        # 实际调用消息服务
        # response = await self.client.send_message(message)
        response = UserResponse(task_id=task_id, question=question, answers={"vmid": 1, "vm_name": "test_vm"})
        return response

    async def notify(self, notification: TaskNotification):
        print("=================> notfication: ", notification.to_dict())


class SampleToolExecutor(ToolBox, ToolExecutor):
    def __init__(self):
        ToolBox.__init__(self)

    async def execute(self, tool_name: str, context: Dict[str, Any], parameters: Dict[str, Any]):
        method = getattr(self, tool_name)
        if not method:
            return TaskResult(output={}, error=f"Unknown tool: {tool_name}", status=TaskStatus.FAILED)
        try:
            result = await method(**parameters)
            result: Dict[str, Any] = result if isinstance(result, dict) else {"result": result}  # type: ignore
            return TaskResult(output=result, error=None, status=TaskStatus.COMPLETED)
        except Exception as e:
            return TaskResult(output={}, error=str(e), status=TaskStatus.FAILED)

    @ToolBox.tool(description="创建虚拟机")
    async def create_vm(self, vm_name: str = "") -> Dict[str, Any]:
        print(vm_name)
        return {"vmid": 1, "vm_name": "test_vm"}

    @ToolBox.tool(description="启动虚拟机")
    async def start_vm(self, vmid: int) -> Dict[str, Any]:
        return {}

    @ToolBox.tool(description="关闭虚拟机")
    async def shutdown_vm(self, vmid: int) -> Dict[str, Any]:
        return {}

    @ToolBox.tool(description="查询虚拟机状态")
    async def query_vm_status(self, vmid: int) -> Dict[str, Any]:
        return {}


async def completions(prompt, model="qwen3-32b", enable_thinking=True):  # type: ignore
    client = openai.OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    completion = client.chat.completions.create(
        model=model,
        # 此处以qwen3-32b为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        stream=True,
        extra_body={"enable_thinking": enable_thinking},
    )

    text = ""
    for txt in completion:
        text += txt.choices[0].delta.content or ""
    return text


async def demo():
    """演示完整工作流程"""
    # 初始化组件
    recognizer = IntentRecognizer()
    executor = SampleToolExecutor()
    message_service = MockMessageServiceAdapter(None)
    pilot = AgentFlowPilot(executor, message_service, logger)

    schema = executor.build()

    prompt = recognizer.format_prompt(
        "请创建一个虚拟机，并启动它",
        schema,
        context="",
        tips="非常抱歉! 我只是一个云主机管理助手，我可以提供这些服务: <tools info>",
    )

    completions_output = await completions(prompt)
    print("completions_output:")
    print(completions_output)

    task_definitions = parse_json(completions_output)
    if not task_definitions:
        return

    validate, message = validate_tool_chain_output(task_definitions)
    if not validate:
        raise RuntimeError(message)

    tool_chain = task_definitions["tool_chain"]

    # 加载并运行
    pilot.load_tool_chain("", tool_chain)

    try:
        await pilot.arun()
        report = pilot.get_execution_report()
        print("任务执行完成:")
        print(json.dumps(report, indent=2, ensure_ascii=False))
    except TaskFailedError as e:
        print(f"任务流失败: {e}")
        print("详细报告:", pilot.get_execution_report())


if __name__ == "__main__":
    import json

    asyncio.run(demo())
