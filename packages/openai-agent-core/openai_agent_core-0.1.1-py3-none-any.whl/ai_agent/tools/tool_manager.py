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
        tool_module_path: str = "custom_tools.py"
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
        self._load_custom_tools(tool_module_path)

    def _load_custom_tools(self, module_path: str):
        """
        Импортирует модуль с инструментами, регистрируя все tool-функции.
        """
        module_path = Path(module_path)
        if not module_path.exists():
            print(f"[ToolManager] ⚠️ Файл {module_path} не найден — инструменты не загружены.")
            return

        spec = importlib.util.spec_from_file_location("custom_tools", str(module_path))
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"[ToolManager] ✅ Инструменты загружены из {module_path}")
        else:
            print(f"[ToolManager] ❌ Не удалось загрузить модуль инструментов из {module_path}")

    async def generate_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        return await self.predictor.generate_tool_calls(text)

    async def generate_user_message(self, text: str) -> Dict[str, Any]:
        return await self.predictor.prepare_user_message(text)

    async def handle_tool_calls(self, tool_calls: list) -> List[Dict[str, Any]]:
        return await self.dispatcher.dispatch(tool_calls)

    def get_generated_files(self) -> List[str]:
        return self.dispatcher.get_file_names()