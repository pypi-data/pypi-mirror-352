import os
import json
import shutil
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Type
from pydantic import BaseModel, ValidationError


class StorageManager:
    def __init__(self, base_path: Path = Path("local_storage"), cleanup_interval: int = 3600):
        self.base_path = base_path
        self.cleanup_interval = cleanup_interval
        self._file_metadata: dict[Path, datetime] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task = None  # Таск теперь НЕ запускаем в __init__

    async def start_cleanup(self):
        """Запустить фоновую задачу очистки."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._auto_cleanup())

    async def _auto_cleanup(self):
        while True:
            await asyncio.sleep(self.cleanup_interval)
            await self._cleanup()

    async def _cleanup(self):
        now = datetime.utcnow()
        async with self._lock:
            to_delete = []
            for path, expiry in list(self._file_metadata.items()):
                if now > expiry and path.exists():
                    try:
                        path.unlink()
                        to_delete.append(path)
                    except Exception as e:
                        print(f"Ошибка при удалении {path}: {e}")
            for path in to_delete:
                del self._file_metadata[path]

    async def save_file(
        self,
        user_id: str,
        assistant_id: str,
        file_name: str,
        content: str,
        expiry_hours: int,
        schema: Optional[Type[BaseModel]] = None
    ) -> Path:
        file_path = self.base_path / user_id / assistant_id / file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Валидация JSON-файлов по Pydantic-схеме
        if file_path.suffix == ".json" and schema is not None:
            try:
                parsed = json.loads(content)
                schema.parse_obj(parsed)
            except (json.JSONDecodeError, ValidationError) as e:
                raise ValueError(f"Файл не прошёл валидацию: {e}")

        file_path.write_text(content, encoding="utf-8")
        expiry_time = datetime.utcnow() + timedelta(hours=expiry_hours)

        async with self._lock:
            self._file_metadata[file_path] = expiry_time

        return file_path

    async def delete_files(self, user_id: str, assistant_id: str, file_names: List[str]) -> None:
        for name in file_names:
            file_path = self.base_path / user_id / assistant_id / name
            if file_path.exists():
                try:
                    file_path.unlink()
                    async with self._lock:
                        self._file_metadata.pop(file_path, None)
                except Exception as e:
                    print(f"Ошибка при удалении {file_path}: {e}")

    async def list_files(self, user_id: str, assistant_id: str) -> List[str]:
        dir_path = self.base_path / user_id / assistant_id
        if not dir_path.exists():
            return []
        return [f.name for f in dir_path.iterdir() if f.is_file()]

    async def delete_assistant_folder(self, user_id: str, assistant_id: str) -> None:
        folder_path = self.base_path / user_id / assistant_id
        if folder_path.exists():
            shutil.rmtree(folder_path)
            async with self._lock:
                self._file_metadata = {
                    path: exp for path, exp in self._file_metadata.items()
                    if not str(path).startswith(str(folder_path))
                }

    async def get_file_path(self, user_id: str, assistant_id: str, file_name: str) -> Optional[Path]:
        file_path = self.base_path / user_id / assistant_id / file_name
        if file_path.exists():
            return file_path
        return None

    async def get_files_by_extension(self, user_id: str, assistant_id: str, extension: str) -> List[Path]:
        dir_path = self.base_path / user_id / assistant_id
        if not dir_path.exists():
            return []
        return [f for f in dir_path.iterdir() if f.is_file() and f.suffix == extension]
