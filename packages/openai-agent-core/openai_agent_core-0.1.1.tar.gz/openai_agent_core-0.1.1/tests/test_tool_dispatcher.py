
import pytest
from unittest.mock import AsyncMock, MagicMock
from ai_agent.tools.tool_dispatcher import ToolDispatcher
from ai_agent.tools.file_manager import StorageManager
from ai_agent.tools.tools_collector import ToolsCollector

@pytest.mark.asyncio
async def test_dispatch_no_calls(tmp_path):
    dispatcher = ToolDispatcher(
        assistant_id="aid", user_id="uid",
        storage_manager=StorageManager(base_path=tmp_path),
        tools_collector=ToolsCollector()
    )
    result = await dispatcher.dispatch([])
    assert result == []
