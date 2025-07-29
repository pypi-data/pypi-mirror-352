
import pytest
import asyncio
import os
from ai_agent.tools.file_manager import StorageManager
from pydantic import BaseModel

class DummySchema(BaseModel):
    name: str
    value: int

@pytest.mark.asyncio
async def test_save_and_list_files(tmp_path):
    sm = StorageManager(base_path=tmp_path)
    path = await sm.save_file("user1", "agent1", "test.txt", "hello", 1)
    files = await sm.list_files("user1", "agent1")
    assert "test.txt" in files

@pytest.mark.asyncio
async def test_save_json_with_schema(tmp_path):
    sm = StorageManager(base_path=tmp_path)
    valid_json = '{"name": "test", "value": 123}'
    path = await sm.save_file("user1", "agent1", "data.json", valid_json, 1, schema=DummySchema)
    assert path.exists()

@pytest.mark.asyncio
async def test_delete_files(tmp_path):
    sm = StorageManager(base_path=tmp_path)
    await sm.save_file("user1", "agent1", "delete.txt", "data", 1)
    await sm.delete_files("user1", "agent1", ["delete.txt"])
    files = await sm.list_files("user1", "agent1")
    assert "delete.txt" not in files

@pytest.mark.asyncio
async def test_get_file_path(tmp_path):
    sm = StorageManager(base_path=tmp_path)
    await sm.save_file("user1", "agent1", "find.txt", "content", 1)
    path = await sm.get_file_path("user1", "agent1", "find.txt")
    assert path is not None

@pytest.mark.asyncio
async def test_get_files_by_extension(tmp_path):
    sm = StorageManager(base_path=tmp_path)
    await sm.save_file("user1", "agent1", "a.txt", "1", 1)
    await sm.save_file("user1", "agent1", "b.log", "2", 1)
    txt_files = await sm.get_files_by_extension("user1", "agent1", ".txt")
    assert len(txt_files) == 1
