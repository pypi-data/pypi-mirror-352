
import pytest
import asyncio
from ai_agent.tools.tools_collector import ToolsCollector

@pytest.mark.asyncio
async def test_tool_registration_and_call():
    collector = ToolsCollector()

    @collector.tool(schema={
        "function": {
            "name": "test_tool",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer"}
                },
                "required": ["x"]
            }
        }
    })
    def test_tool(x):
        return {"result": x * 2}

    tools = await collector.get_tools()
    assert any(t["function"]["name"] == "test_tool" for t in tools)

    func = await collector.get_function("test_tool")
    assert callable(func)

    result = await collector.call_tool("test_tool", {"x": 5})
    assert result["result"] == 10
