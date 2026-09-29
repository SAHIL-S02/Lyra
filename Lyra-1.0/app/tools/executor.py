from __future__ import annotations

import inspect
from typing import Any

from .registry import tool_registry


class ToolExecutionError(Exception):
    """Raised when a Lyra tool cannot be executed."""


class ToolExecutor:
    """
    Executes tools registered in Lyra's central ToolRegistry.
    """

    async def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        arguments = arguments or {}

        if not tool_registry.exists(tool_name):
            return {
                "success": False,
                "tool": tool_name,
                "error": f"Unknown tool: {tool_name}",
            }

        tool = tool_registry.get(tool_name)

        if tool.requires_confirmation:
            return {
                "success": False,
                "tool": tool_name,
                "requires_confirmation": True,
                "error": "User confirmation is required before executing this tool.",
            }

        try:
            result = tool.handler(**arguments)

            if inspect.isawaitable(result):
                result = await result

            return {
                "success": True,
                "tool": tool_name,
                "result": result,
            }

        except Exception as exc:
            return {
                "success": False,
                "tool": tool_name,
                "error": str(exc),
            }


tool_executor = ToolExecutor()