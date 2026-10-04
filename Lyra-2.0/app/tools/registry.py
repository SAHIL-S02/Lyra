from __future__ import annotations

from typing import Any

from app.core.logging import logger
from app.tools.base import Tool


class ToolRegistry:
    """Central registry containing all available Lyra tools."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

        logger.info("Tool registry initialized.")

    def register(self, tool: Tool) -> None:
        """Register a tool."""

        if not tool.name.strip():
            raise ValueError("Tool name cannot be empty.")

        if tool.name in self._tools:
            raise ValueError(
                f"Tool already registered: {tool.name}"
            )

        self._tools[tool.name] = tool

        logger.info("Tool registered: %s", tool.name)

    def get(self, name: str) -> Tool | None:
        """Return a registered tool."""

        return self._tools.get(name)

    def list_tools(self) -> list[Tool]:
        """Return all registered tools."""

        return list(self._tools.values())

    def has(self, name: str) -> bool:
        """Check whether a tool exists."""

        return name in self._tools

    def definitions(self) -> list[dict[str, Any]]:
        """Return all tool definitions for an LLM."""

        return [
            tool.definition()
            for tool in self._tools.values()
        ]
