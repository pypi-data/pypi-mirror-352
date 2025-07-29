ai-agent
ai-agent — библиотека для создания асинхронных GPT-агентов с поддержкой Tool Calling, Tool Dispatching, управлением файлами, автоматическим предсказанием Tool Calls на базе ML, легко интегрируется с LangChain и FastAPI.

Установка
bash
Копировать
Редактировать
pip install ai-agent
или локально из исходников:

bash
Копировать
Редактировать
pip install -e .
Основные компоненты
1️⃣ GptAgent
python
Копировать
Редактировать
from ai_agent import GptAgent

agent = GptAgent(
    openai_key="sk-...",
    instructions="Ты помощник.",
    name="MyAgent",
    model="gpt-4o"
)
Методы:
await create()
Создание Assistant и Thread в OpenAI API.

await update_agent(new_assistant_name, new_assistant_instructions, new_assistant_model)
Обновление параметров агента.

await update_memory()
Создание нового Thread (обновление памяти).

await send_text_message(text: str)
Отправка текстового сообщения.

await send_image_message(text: str, file_path: list[str])
Отправка изображения с текстом.

await message(text: str, file_path: Optional[list[str]])
Универсальный метод для отправки текста или изображения.

await get_image_description(image_path: str)
Генерация описания изображения.

Пример:
python
Копировать
Редактировать
await agent.create()
await agent.message("Привет, что ты умеешь?")
2️⃣ StorageManager
python
Копировать
Редактировать
from ai_agent.tools import StorageManager

storage = StorageManager()

await storage.start_cleanup()
Методы:
await save_file(user_id, assistant_id, file_name, content, expiry_hours, schema=None)
Сохранение файла.

await delete_files(user_id, assistant_id, file_names)
Удаление указанных файлов.

await list_files(user_id, assistant_id)
Список файлов.

await delete_assistant_folder(user_id, assistant_id)
Удаление папки ассистента.

await get_file_path(user_id, assistant_id, file_name)
Получение пути к файлу.

await get_files_by_extension(user_id, assistant_id, extension)
Получение файлов по расширению.

Пример:
python
Копировать
Редактировать
await storage.save_file("user1", "agent1", "test.txt", "Hello", 1)
files = await storage.list_files("user1", "agent1")
3️⃣ ToolCallPredictor
python
Копировать
Редактировать
from ai_agent.tools import ToolCallPredictor

predictor = ToolCallPredictor()
Методы:
await train(data)
Обучение модели.

await load_model()
Загрузка модели.

await predict_tools(text)
Предсказание инструментов для текста.

await predict_tools_batch(texts)
Пакетное предсказание.

await generate_tool_calls(text)
Генерация Tool Calls для текста.

await generate_tool_calls_batch(texts)
Пакетная генерация Tool Calls.

await prepare_user_message(text)
Генерация сообщения для Assistant API.

await prepare_user_messages_batch(texts)
Пакетная генерация сообщений.

Пример:
python
Копировать
Редактировать
data = [
    {"text": "translate", "tools": ["translator"]},
    {"text": "analyze image", "tools": ["analyzer"]}
]

await predictor.train(data)
await predictor.load_model()
tools = await predictor.predict_tools("translate")
4️⃣ ToolManager
python
Копировать
Редактировать
from ai_agent.tools import ToolManager, ToolCallPredictor, StorageManager, ToolsCollector

manager = ToolManager(
    assistant_id="aid",
    user_id="uid",
    predictor=ToolCallPredictor(),
    storage=StorageManager(),
    collector=ToolsCollector()
)
Методы:
await generate_tool_calls(text)
Генерация Tool Calls.

await generate_user_message(text)
Генерация пользовательского сообщения.

await handle_tool_calls(tool_calls)
Обработка Tool Calls.

get_generated_files()
Получение списка сгенерированных файлов.

5️⃣ ToolDispatcher
python
Копировать
Редактировать
from ai_agent.tools import ToolDispatcher
Методы:
await dispatch(tool_calls)
Обработка Tool Calls.

get_file_names()
Получение имён файлов.

6️⃣ ToolsCollector
python
Копировать
Редактировать
from ai_agent.tools import ToolsCollector

collector = ToolsCollector()
Методы:
@collector.tool(schema)
Декоратор для регистрации инструмента.

await get_tools()
Получение схем инструментов.

await get_function(name)
Получение функции по имени.

await get_all()
Получение всех зарегистрированных функций.

await call_tool(name, arguments)
Вызов инструмента с аргументами.

Пример:
python
Копировать
Редактировать
@collector.tool({
    "function": {
        "name": "multiply",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "integer"}
            },
            "required": ["x"]
        }
    }
})
def multiply(x):
    return {"result": x * 2}

tools = await collector.get_tools()
result = await collector.call_tool("multiply", {"x": 5})
Лицензия
MIT License.
