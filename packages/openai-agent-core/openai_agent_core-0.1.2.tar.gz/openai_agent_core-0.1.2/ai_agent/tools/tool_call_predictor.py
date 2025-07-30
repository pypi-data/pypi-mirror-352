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
        # Путь к файлу, где будет сохранена обученная модель и бинаризатор
        self.model_path = model_path
        self.pipeline: Pipeline | None = None  # ML-пайплайн (Tfidf + OneVsRestClassifier)
        self.label_binarizer: MultiLabelBinarizer | None = None  # Бинаризатор мульти-меток

    async def init_from_collector(self, collector) -> None:
        """Автоматически обучает модель по descriptions из collector."""
        tools = await collector.get_tools()
        data = []
        for tool in tools:
            description = tool["function"].get("description", "")
            name = tool["function"].get("name", "")
            if description and name:
                data.append({
                    "text": description,
                    "tools": [name]
                })

        if not data:
            print("[ToolCallPredictor] ⚠️ Нет descriptions в collector — пропускаем init_from_collector")
            return

        print(f"[ToolCallPredictor] ⚙️ Инициализация модели по {len(data)} tools из collector...")
        await self.train(data)
        await self.load_model()
        print("[ToolCallPredictor] ✅ Init from collector завершён")

    async def train(self, data: List[Dict[str, Any]]) -> None:
        """Асинхронно обучает модель на размеченных данных."""
        texts = [item["text"] for item in data]  # Список текстов
        labels = [item["tools"] for item in data]  # Список списков инструментов

        # Преобразуем список списков в бинарную матрицу
        self.label_binarizer = MultiLabelBinarizer()
        y = self.label_binarizer.fit_transform(labels)

        # Создаем pipeline: TF-IDF векторизация + логистическая регрессия в One-vs-Rest схеме
        pipeline = Pipeline([
            ('vectorizer', TfidfVectorizer()),
            ('classifier', OneVsRestClassifier(LogisticRegression(solver="liblinear")))
        ])

        # Обучаем модель в отдельном потоке, чтобы не блокировать event loop
        self.pipeline = await asyncio.to_thread(pipeline.fit, texts, y)

        # Сохраняем модель и бинаризатор в файл
        await asyncio.to_thread(joblib.dump, (self.pipeline, self.label_binarizer), self.model_path)
        return self.model_path

    async def load_model(self) -> None:
        """Загружает обученную модель и бинаризатор из файла."""
        self.pipeline, self.label_binarizer = await asyncio.to_thread(joblib.load, self.model_path)

    async def predict_tools(self, text: str) -> List[str]:
        """Предсказывает список названий инструментов для одного текста."""
        if not self.pipeline or not self.label_binarizer:
            raise RuntimeError("Модель не загружена")

        prediction = await asyncio.to_thread(self.pipeline.predict, [text])
        tools = self.label_binarizer.inverse_transform(prediction)[0]
        return list(tools)

    async def predict_tools_batch(self, texts: List[str]) -> List[List[str]]:
        """Пакетное предсказание списков инструментов для каждого текста."""
        if not self.pipeline or not self.label_binarizer:
            raise RuntimeError("Модель не загружена")

        predictions = await asyncio.to_thread(self.pipeline.predict, texts)
        return self.label_binarizer.inverse_transform(predictions)

    async def generate_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        """Генерирует tool_calls (название + аргументы) для одного текста."""
        tools = await self.predict_tools(text)
        return [
            {
                "name": tool_name,
                "arguments": {"query": text}  # Можно заменить на кастомную логику
            } for tool_name in tools
        ]

    async def generate_tool_calls_batch(self, texts: List[str]) -> List[List[Dict[str, Any]]]:
        """Пакетная генерация tool_calls для каждого текста."""
        all_tools = await self.predict_tools_batch(texts)
        return [
            [
                {
                    "name": tool_name,
                    "arguments": {"query": text}  # Можно заменить на продвинутый парсинг
                }
                for tool_name in tools
            ]
            for text, tools in zip(texts, all_tools)
        ]

    async def prepare_user_message(self, text: str) -> Dict[str, Any]:
        """Формирует одно сообщение пользователя для Assistant API с tool_calls."""
        tool_calls = await self.generate_tool_calls(text)
        return {
            "role": "user",
            "content": text,
            "tool_calls": tool_calls
        }

    async def prepare_user_messages_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Формирует список сообщений для Assistant API для каждого входного текста."""
        tool_calls_list = await self.generate_tool_calls_batch(texts)
        return [
            {
                "role": "user",
                "content": text,
                "tool_calls": tool_calls
            }
            for text, tool_calls in zip(texts, tool_calls_list)
        ]
