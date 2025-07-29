from agent_flowpilot.tools import ToolBox


class ShellCommnd(ToolBox):
    @classmethod
    @ToolBox.tool()
    async def run_command(cls, command, *, capture_output=True, text=True, check=False, shell=None):  # type: ignore
        pass


def test_tools():
    async def sum_func(a: int, b: int) -> int:  # type: ignore
        return a + b

    ShellCommnd()
    # toolbox = ToolBox()
    # toolbox.register("sum_tool", sum_func, "计算两个数的和")
    # print(toolbox.build())
