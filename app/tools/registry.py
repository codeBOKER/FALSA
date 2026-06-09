from collections.abc import Awaitable, Callable
from typing import Any

from app.models.domain import ToolResult

ToolHandler = Callable[[dict[str, Any]], Awaitable[ToolResult]]


class ToolRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, ToolHandler] = {}

    def register(self, name: str, handler: ToolHandler) -> None:
        self._handlers[name] = handler

    async def execute(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        handler = self._handlers.get(name)
        if handler is None:
            return ToolResult(ok=False, data={}, error=f"Unknown tool: {name}")
        try:
            return await handler(arguments)
        except Exception as exc:  # noqa: BLE001
            return ToolResult(ok=False, data={}, error=f"Tool {name} failed: {exc}")
