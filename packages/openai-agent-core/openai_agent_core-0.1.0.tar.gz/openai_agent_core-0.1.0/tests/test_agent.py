import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_create(gpt_agent):
    assistant_id, thread_id = await gpt_agent.create()
    assert assistant_id == "assistant-123"
    assert thread_id == "thread-456"
    assert gpt_agent.initialized is True

@pytest.mark.asyncio
async def test_update_agent(gpt_agent):
    await gpt_agent.create()
    response = await gpt_agent.update_agent(
        new_assistant_name="NewName",
        new_assistant_instructions="New instructions",
        new_assistant_model="gpt-4o"
    )
    assert gpt_agent.name == "NewName"
    assert gpt_agent.instructions == "New instructions"
    assert gpt_agent.model == "gpt-4o"

@pytest.mark.asyncio
async def test_update_memory(gpt_agent):
    await gpt_agent.create()
    new_thread_id = await gpt_agent.update_memory()
    assert new_thread_id == "thread-456"

@pytest.mark.asyncio
async def test_send_text_message(gpt_agent):
    await gpt_agent.create()
    run_id = await gpt_agent.send_text_message(text="Hello, world!")
    assert run_id == "run-789"

@pytest.mark.asyncio
async def test_send_image_message(gpt_agent):
    await gpt_agent.create()
    gpt_agent.get_image_description = AsyncMock(return_value="Test image description")
    run_id = await gpt_agent.send_image_message(text="Hello image", file_path=["test.jpg"])
    assert run_id == "run-789"

@pytest.mark.asyncio
async def test_message_text(gpt_agent):
    await gpt_agent.create()
    await gpt_agent.message(text="Test text", file_path=None)

@pytest.mark.asyncio
async def test_message_image(gpt_agent):
    await gpt_agent.create()
    gpt_agent.get_image_description = AsyncMock(return_value="Test image description")
    await gpt_agent.message(text="Test image", file_path=["test.jpg"])

@pytest.mark.asyncio
async def test_get_image_description(gpt_agent):
    await gpt_agent.create()
    gpt_agent.get_image_description = AsyncMock(return_value="Test image description")
    description = await gpt_agent.get_image_description("fake_image.jpg")
    assert description == "Test image description"