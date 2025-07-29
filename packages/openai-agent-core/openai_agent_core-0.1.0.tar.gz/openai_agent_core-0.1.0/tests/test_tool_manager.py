import pytest
from unittest.mock import AsyncMock
from ai_agent.tools.tool_manager import ToolManager
from ai_agent.tools.tool_call_predictor import ToolCallPredictor
from ai_agent.tools.file_manager import StorageManager
from ai_agent.tools.tools_collector import ToolsCollector

@pytest.mark.asyncio
async def test_generate_user_message(tmp_path):
    predictor = ToolCallPredictor()
    predictor.pipeline = None
    predictor.label_binarizer = None
    predictor.generate_tool_calls = AsyncMock(return_value=[])
    predictor.prepare_user_message = AsyncMock(return_value={"role": "user", "content": "hello", "tool_calls": []})

    manager = ToolManager(
        assistant_id="aid",
        user_id="uid",
        predictor=predictor,
        storage=StorageManager(base_path=tmp_path),
        collector=ToolsCollector()
    )
    msg = await manager.generate_user_message("hello")
    assert msg["role"] == "user"
