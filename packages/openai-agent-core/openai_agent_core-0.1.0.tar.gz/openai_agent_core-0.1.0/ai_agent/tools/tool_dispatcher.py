import json
from typing import List, Dict, Any
from .file_manager import StorageManager
from .tools_collector import ToolsCollector

OPENAI_SAFE_OUTPUT_CHUNK = 3000


class ToolDispatcher:
    def __init__(self, assistant_id: str, user_id: str, storage_manager: StorageManager, tools_collector: ToolsCollector):
        self.assistant_id = assistant_id
        self.user_id = user_id
        self.storage_manager = storage_manager
        self.tools_collector = tools_collector
        self.collected_file_names: List[str] = []

    def _split_output_text(self, text: str, max_len: int = OPENAI_SAFE_OUTPUT_CHUNK) -> List[str]:
        return [text[i:i + max_len] for i in range(0, len(text), max_len)]

    async def dispatch(self, tool_calls: List[Any]) -> List[Dict[str, Any]]:
        results = []

        for call in tool_calls:
            try:
                function_name = call.function.name
                arguments_str = call.function.arguments or "{}"

                try:
                    arguments = json.loads(arguments_str)
                except json.JSONDecodeError:
                    print(f"[ToolDispatcher] Ошибка парсинга JSON: {arguments_str}")
                    arguments = {}

                # Преобразование вложенных строковых JSON-полей в словари
                for key in [
                    "downloaded_all_files", "downloaded_media_files", "downloaded_text_files",
                    "downloaded_image", "downloaded_video", "downloaded_audio",
                    "downloaded_tables", "downloaded_documents", "downloaded_drawings",
                    "downloaded_archives", "actions_per_file"
                ]:
                    if key in arguments and isinstance(arguments[key], str):
                        try:
                            arguments[key] = json.loads(arguments[key].replace("'", '"'))
                        except Exception as e:
                            print(f"[ToolDispatcher] Не удалось преобразовать {key} в dict: {e}")
                            arguments[key] = {}

                try:
                    result = await self.tools_collector.call_tool(function_name, arguments)
                except Exception as tool_error:
                    results.append({
                        "tool_call_id": call.id,
                        "output": f"❌ Ошибка вызова инструмента '{function_name}': {tool_error}"
                    })
                    continue

                if isinstance(result, dict):
                    summary = str(result.get("summary", "✅ Операция выполнена успешно."))
                    message_content = result.get("message", {})

                    # Добавляем возвращённые пути к новым файлам
                    if "new_file_path" in result:
                        new_paths = result["new_file_path"]
                        if isinstance(new_paths, list):
                            self.collected_file_names.extend([str(p) for p in new_paths])

                    output_json_str = json.dumps(message_content, ensure_ascii=False, indent=2) \
                        if isinstance(message_content, dict) else str(message_content)

                    if len(output_json_str) > OPENAI_SAFE_OUTPUT_CHUNK:
                        chunks = self._split_output_text(output_json_str)
                        filename = f"result_{function_name}_{call.id}.json"

                        await self.storage_manager.save_file(
                            user_id=self.user_id,
                            assistant_id=self.assistant_id,
                            file_name=filename,
                            content="\n".join(chunks),
                            expiry_hours=48
                        )

                        self.collected_file_names.append(filename)

                        output_text = json.dumps({
                            "summary": summary,
                            "note": f"📎 Подробный результат сохранён как `{filename}` в папке ассистента.",
                            "filename": filename
                        }, ensure_ascii=False, indent=2)
                    else:
                        output_text = summary + "\n" + output_json_str

                    results.append({
                        "tool_call_id": call.id,
                        "output": output_text
                    })
                else:
                    results.append({
                        "tool_call_id": call.id,
                        "output": str(result)
                    })

            except Exception as e:
                results.append({
                    "tool_call_id": getattr(call, "id", "undefined"),
                    "output": f"❌ Общая ошибка при обработке: {e}"
                })

        return results

    def get_file_names(self) -> List[str]:
        return self.collected_file_names