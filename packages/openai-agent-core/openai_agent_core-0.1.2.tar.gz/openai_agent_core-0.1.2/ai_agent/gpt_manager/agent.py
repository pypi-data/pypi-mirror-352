import os
import base64
import openai
import asyncio
from ai_agent.tools import ToolManager, ToolCallPredictor, StorageManager, collector

# Функция для кодирования изображения в Base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

class GptAgent:
    def __init__(self, openai_key, instructions: str, name: str, model: str, assistant_id=None, thread_id: str = None):
        self.client = openai.AsyncOpenAI(api_key=openai_key)
        self.instructions = instructions
        self.name = name
        self.model = model
        self.assistant_id = assistant_id
        self.thread_id = thread_id
        self.initialized = False  # Флаг инициализации

        # ✅ Инициализация ToolManager
        self.tool_manager = ToolManager(
            assistant_id=self.assistant_id or "pending",  # пока не создано — заглушка
            user_id="user-001",
            predictor=ToolCallPredictor(),
            storage=StorageManager(),
            collector=collector
        )

    async def create(self):
        assistant = await self.client.beta.assistants.create(
            name=self.name,
            instructions=self.instructions,
            model=self.model
        )
        self.assistant_id = assistant.id
        thread = await self.client.beta.threads.create()
        self.thread_id = thread.id
        self.initialized = True

        # Обновляем ToolManager на правильный assistant_id
        self.tool_manager.assistant_id = self.assistant_id
        self.tool_manager.dispatcher.assistant_id = self.assistant_id

        return assistant.id, thread.id

    async def update_agent(self, new_assistant_name: str = None, new_assistant_instructions: str = None, new_assistant_model: str = None):
        l_name = self.name
        l_instructions = self.instructions
        l_model = self.model

        if new_assistant_name and new_assistant_name != self.name:
            l_name = new_assistant_name
        if new_assistant_instructions and new_assistant_instructions != self.instructions:
            l_instructions = new_assistant_instructions
        if new_assistant_model and new_assistant_model != self.model:
            l_model = new_assistant_model

        response = await self.client.beta.assistants.update(
            assistant_id=self.assistant_id,
            name=l_name,
            instructions=l_instructions,
            model=l_model
        )
        self.name = l_name
        self.instructions = l_instructions
        self.model = l_model

        return response

    async def update_memory(self):
        thread = await self.client.beta.threads.create()
        if thread.id and thread.id != self.thread_id:
            await self.client.beta.threads.delete(thread_id=self.thread_id)
            self.thread_id = thread.id
        return thread.id

    async def message(self, text: str, file_path: list[str] = None):
        # Если агент ещё не создан — создаём
        if not self.initialized and not (self.assistant_id and self.thread_id):
            await self.create()

        # Дождаться завершения последнего run (если есть)
        last_runs = await self.client.beta.threads.runs.list(thread_id=self.thread_id, limit=1)
        if last_runs.data:
            while True:
                run_status = await self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread_id,
                    run_id=last_runs.data[0].id
                )
                if run_status.status == "completed":
                    break
                else:
                    await asyncio.sleep(1)

        # Определение расширений файлов
        image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
        is_image = False

        if file_path:
            for path in file_path:
                ext = os.path.splitext(path)[1].lower()
                if ext in image_extensions:
                    is_image = True
                    break

        # Отправляем сообщение в зависимости от типа
        if is_image:
            run_id = await self.send_image_message(text=text, file_path=file_path)
        else:
            run_id = await self.send_text_message(text=text, file_path=file_path)

        # Цикл обработки run (встроенная обработка tool_calls через ToolManager)
        while True:
            run = await self.client.beta.threads.runs.retrieve(thread_id=self.thread_id, run_id=run_id)
            if run.status == "completed":
                print("[GptAgent] ✅ Run completed.")
                break
            elif run.status == "requires_action":
                if run.required_action.type == "submit_tool_outputs":
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    print(f"[GptAgent] ⚙️ Handling {len(tool_calls)} tool_calls...")

                    # Используем ToolManager для обработки tool_calls
                    tool_outputs = await self.tool_manager.handle_tool_calls(tool_calls)

                    # Отправляем результаты обратно в run
                    await self.client.beta.threads.runs.submit_tool_outputs(
                        thread_id=self.thread_id,
                        run_id=run_id,
                        tool_outputs=tool_outputs
                    )
                    print("[GptAgent] ✅ Tool outputs submitted.")
            else:
                await asyncio.sleep(1)

        response_text = None
        if hasattr(run, "response") and run.response is not None:
            # Если response - это строка с текстом
            response_text = run.response
        elif hasattr(run, "outputs") and run.outputs is not None:
            # Если outputs - список или словарь с результатами, нужно извлечь текст
            # Например, если outputs - список сообщений
            if isinstance(run.outputs, list) and len(run.outputs) > 0:
                # Найдем первый текстовый ответ
                for output in run.outputs:
                    if hasattr(output, "text"):
                        response_text = output.text
                        break
                    elif isinstance(output, dict) and "text" in output:
                        response_text = output["text"]
                        break

        # Если ничего не нашли, response_text останется None
        if response_text is None:
            print("[GptAgent] ⚠️ Не удалось извлечь текст ответа из run.")
        else:
            print("[GptAgent] Ответ модели:", response_text)

        # Верни или обработай response_text по назначению
        return response_text

    async def send_text_message(self, text: str, file_path: list[str] = None):
        file_descriptions = []
        if file_path:
            for path in file_path:
                filename = os.path.basename(path)
                file_descriptions.append(f"\nfile_name: '{filename}'")

        if file_descriptions:
            files_str = ", ".join(file_descriptions)
            prompt = text + f"\nИмена документов (файлов): {files_str}"
        else:
            prompt = text

        await self.client.beta.threads.messages.create(thread_id=self.thread_id, role="user", content=prompt)
        run = await self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id
        )
        return run.id

    async def send_image_message(self, text: str, file_path: list[str] = None):
        image_list = []
        for idx, path in enumerate(file_path):
            filename = os.path.basename(path)
            path_description = await self.get_image_description(image_path=path)
            image_string = f"{idx+1}) image_name: '{filename}', image_description: '{path_description}'"
            image_list.append(image_string)

        complex_image_string = "\n".join(image_list)
        prompt = text + "\n" + complex_image_string

        await self.client.beta.threads.messages.create(thread_id=self.thread_id, role="user", content=prompt)
        run = await self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id
        )
        return run.id

    async def get_image_description(self, image_path: str):
        # Кодируем изображение в Base64
        base64_image = encode_image(image_path)

        # Выполняем запрос к OpenAI API для обработки изображения
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Что на изображении?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }]
        )

        # Получаем описание изображения от модели
        image_description = response.choices[0].message.content.strip()
        return image_description
