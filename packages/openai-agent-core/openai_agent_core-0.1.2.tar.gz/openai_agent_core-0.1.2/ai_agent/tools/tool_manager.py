import importlib.util
from typing import List, Dict, Any
from .tool_call_predictor import ToolCallPredictor
from .tool_dispatcher import ToolDispatcher
from .tools_collector import ToolsCollector
from .file_manager import StorageManager
from pathlib import Path


class ToolManager:
    def __init__(
        self,
        assistant_id: str,
        user_id: str,
        predictor: ToolCallPredictor,
        storage: StorageManager,
        collector: ToolsCollector,
    ):
        self.assistant_id = assistant_id
        self.user_id = user_id
        self.predictor = predictor
        self.collector = collector
        self.storage = storage
        self.dispatcher = ToolDispatcher(
            assistant_id=assistant_id,
            user_id=user_id,
            storage_manager=storage,
            tools_collector=collector
        )
        self._load_custom_tools()


    def _load_custom_tools(self):
        """
        Импортирует модуль с инструментами, регистрируя все tool-функции.
        """
        self.predictor.init_from_collector(self.collector)


    async def generate_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        return await self.predictor.generate_tool_calls(text)

    async def generate_user_message(self, text: str) -> Dict[str, Any]:
        return await self.predictor.prepare_user_message(text)

    async def handle_tool_calls(self, tool_calls: list) -> List[Dict[str, Any]]:
        return await self.dispatcher.dispatch(tool_calls)

    def get_generated_files(self) -> List[str]:
        return self.dispatcher.get_file_names()