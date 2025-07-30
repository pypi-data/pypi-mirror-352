from typing import Callable, Dict, List, Any
import inspect
import asyncio
import jsonschema



class ToolsCollector:
    def __init__(self):
        self._tools: Dict[str, Dict] = {}         # Словарь инструкций tool calling
        self._functions: Dict[str, Callable] = {} # Словарь самих функций

    def tool(self, schema: Dict) -> Callable:
        """
        Декоратор для регистрации tool-функции с инструкцией и схемой параметров.
        """
        def decorator(func: Callable) -> Callable:
            name = schema.get("function", {}).get("name", func.__name__)
            self._tools[name] = schema
            self._functions[name] = func
            return func
        return decorator

    async def get_tools(self) -> List[Dict]:
        """Возвращает все tool-схемы для Assistant API."""
        return list(self._tools.values())

    async def get_function(self, name: str) -> Callable:
        """Возвращает зарегистрированную функцию по имени."""
        if name not in self._functions:
            raise KeyError(f"Tool '{name}' не зарегистрирован.")
        return self._functions[name]

    async def get_all(self) -> Dict[str, Callable]:
        """Возвращает словарь всех зарегистрированных функций."""
        return self._functions

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """
        Асинхронно вызывает функцию по имени, валидируя входные аргументы по JSON Schema.
        Поддерживает как обычные, так и async-функции.
        """
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' не зарегистрирован.")

        schema = self._tools[name]["function"]["parameters"]
        try:
            jsonschema.validate(instance=arguments, schema=schema)
        except jsonschema.exceptions.ValidationError as e:
            raise ValueError(f"Невалидные аргументы для '{name}': {e.message}")

        func = self._functions[name]
        if inspect.iscoroutinefunction(func):
            return await func(**arguments)
        else:
            return await asyncio.to_thread(func, **arguments)

# Глобальный экземпляр, импортируемый везде
collector = ToolsCollector()