
import pytest
import asyncio
import os
from ai_agent.tools.tool_call_predictor import ToolCallPredictor

@pytest.mark.asyncio
async def test_train_and_predict(tmp_path):
    model_path = tmp_path / "model.pkl"
    predictor = ToolCallPredictor(model_path=str(model_path))
    data = [
        {"text": "analyze image", "tools": ["analyzer"]},
        {"text": "translate text", "tools": ["translator"]},
    ]
    await predictor.train(data)
    await predictor.load_model()
    tools = await predictor.predict_tools("translate text")
    assert "translator" in tools
