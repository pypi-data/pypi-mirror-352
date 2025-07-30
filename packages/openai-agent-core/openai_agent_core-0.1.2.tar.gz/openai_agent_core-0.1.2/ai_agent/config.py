import asyncio
import joblib
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


class ToolCallPredictor:
    def __init__(self, model_path: str = "toolcall_model.pkl"):
        self.model_path = model_path
        self.pipeline: Pipeline | None = None
        self.label_binarizer: MultiLabelBinarizer | None = None

    async def train(self, data: List[Dict[str, Any]]) -> None:
        """Асинхронно обучает модель на размеченных данных"""
        texts = [item["text"] for item in data]
        labels = [item["tools"] for item in data]

        self.label_binarizer = MultiLabelBinarizer()
        y = self.label_binarizer.fit_transform(labels)

        pipeline = Pipeline([
            ('vectorizer', TfidfVectorizer()),
            ('classifier', OneVsRestClassifier(LogisticRegression(solver="liblinear")))
        ])

        # Обучение модели в отдельном потоке
        self.pipeline = await asyncio.to_thread(pipeline.fit, texts, y)

        # Сохранение модели и бинализатора
        await asyncio.to_thread(joblib.dump, (self.pipeline, self.label_binarizer), self.model_path)

    async def load_model(self) -> None:
        """Загружает модель и бинализатор из файла"""
        self.pipeline, self.label_binarizer = await asyncio.to_thread(joblib.load, self.model_path)

    async def predict_tools(self, text: str) -> List[str]:
        """Предсказывает список tool names на основе текста"""
        if not self.pipeline or not self.label_binarizer:
            raise RuntimeError("Модель не загружена")

        prediction = await asyncio.to_thread(self.pipeline.predict, [text])
        tools = self.label_binarizer.inverse_transform(prediction)[0]
        return list(tools)

    async def generate_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        """Формирует список toolcalls в нужном формате"""
        tools = await self.predict_tools(text)
        return [
            {
                "name": tool_name,
                "arguments": {"query": text}  # Здесь может быть более умная логика
            } for tool_name in tools
        ]

    async def prepare_user_message(self, text: str) -> Dict[str, Any]:
        """Генерирует финальное сообщение для Assistant API"""
        tool_calls = await self.generate_tool_calls(text)
        return {
            "role": "user",
            "content": text,
            "tool_calls": tool_calls
        }