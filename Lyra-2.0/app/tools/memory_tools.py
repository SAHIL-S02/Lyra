from __future__ import annotations

from typing import Any

from app.memory.manager import MemoryManager
from app.tools.base import Tool, ToolResult


class RememberMemoryTool(Tool):
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Canonical memory key.",
                },
                "value": {
                    "type": "string",
                    "description": "Information to remember.",
                },
                "category": {
                    "type": "string",
                    "description": "Memory category such as fact or preference.",
                    "default": "fact",
                },
            },
            "required": ["key", "value"],
        }
    name = "remember_memory"
    description = (
        "Store a user fact, preference, profile detail, or other "
        "important information in Lyra's persistent memory. "
        "Use concise canonical keys such as "
        "'user_name' or 'favorite_programming_language'."
    )

    def __init__(self, memory: MemoryManager) -> None:
        self.memory = memory

    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        key = arguments.get("key")
        value = arguments.get("value")
        category = arguments.get("category", "fact")

        if not isinstance(key, str) or not key.strip():
            return ToolResult(
                success=False,
                error="Argument 'key' is required.",
            )

        if not isinstance(value, str) or not value.strip():
            return ToolResult(
                success=False,
                error="Argument 'value' is required.",
            )

        if not isinstance(category, str) or not category.strip():
            return ToolResult(
                success=False,
                error="Argument 'category' must be a non-empty string.",
            )

        try:
            self.memory.remember(
                key=key,
                value=value,
                category=category,
            )

            return ToolResult(
                success=True,
                data={
                    "key": key.strip(),
                    "value": value.strip(),
                    "category": category.strip(),
                },
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                error=str(exc),
            )


class SearchMemoryTool(Tool):
    
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural-language query to search memory.",
                },
                "category": {
                    "type": "string",
                    "description": "Optional memory category filter.",
                },
            },
            "required": ["query"],
        }
    
    
    name = "search_memory"
    description = "Search Lyra's persistent memory for relevant information."

    def __init__(self, memory: MemoryManager) -> None:
        self.memory = memory

    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        query = arguments.get("query")
        category = arguments.get("category")

        if not isinstance(query, str) or not query.strip():
            return ToolResult(
                success=False,
                error="Argument 'query' is required.",
            )

        if category is not None and not isinstance(category, str):
            return ToolResult(
                success=False,
                error="Argument 'category' must be a string.",
            )

        try:
            results = self.memory.search(
                query=query,
                category=category,
            )

            return ToolResult(
                success=True,
                data=results,
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                error=str(exc),
            )


class UpdateMemoryTool(Tool):
    
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Existing memory key.",
                },
                "value": {
                    "type": "string",
                    "description": "New memory value.",
                },
                "category": {
                    "type": "string",
                    "description": "Memory category.",
                    "default": "fact",
                },
            },
            "required": ["key", "value"],
        }
    
    
    name = "update_memory"
    description = "Update an existing memory in Lyra's persistent memory."

    def __init__(self, memory: MemoryManager) -> None:
        self.memory = memory

    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        key = arguments.get("key")
        value = arguments.get("value")
        category = arguments.get("category", "fact")

        if not isinstance(key, str) or not key.strip():
            return ToolResult(
                success=False,
                error="Argument 'key' is required.",
            )

        if not isinstance(value, str) or not value.strip():
            return ToolResult(
                success=False,
                error="Argument 'value' is required.",
            )

        if not isinstance(category, str) or not category.strip():
            return ToolResult(
                success=False,
                error="Argument 'category' must be a non-empty string.",
            )

        try:
            updated = self.memory.update(
                key=key,
                value=value,
                category=category,
            )

            if not updated:
                return ToolResult(
                    success=False,
                    error=f"Memory not found: {key}",
                )

            return ToolResult(
                success=True,
                data={
                    "key": key.strip(),
                    "value": value.strip(),
                    "category": category.strip(),
                },
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                error=str(exc),
            )


class ForgetMemoryTool(Tool):
    
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Memory key to delete.",
                },
                "category": {
                    "type": "string",
                    "description": "Memory category.",
                    "default": "fact",
                },
            },
            "required": ["key"],
        }
    
    name = "forget_memory"
    description = "Delete a memory from Lyra's persistent memory."

    def __init__(self, memory: MemoryManager) -> None:
        self.memory = memory

    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        key = arguments.get("key")
        category = arguments.get("category", "fact")

        if not isinstance(key, str) or not key.strip():
            return ToolResult(
                success=False,
                error="Argument 'key' is required.",
            )

        if not isinstance(category, str) or not category.strip():
            return ToolResult(
                success=False,
                error="Argument 'category' must be a non-empty string.",
            )

        try:
            deleted = self.memory.forget(
                key=key,
                category=category,
            )

            if not deleted:
                return ToolResult(
                    success=False,
                    error=f"Memory not found: {key}",
                )

            return ToolResult(
                success=True,
                data={
                    "key": key.strip(),
                    "category": category.strip(),
                },
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                error=str(exc),
            )


def create_memory_tools(
    memory: MemoryManager,
) -> list[Tool]:
    """Create all memory tools using the supplied memory manager."""

    return [
        RememberMemoryTool(memory),
        SearchMemoryTool(memory),
        UpdateMemoryTool(memory),
        ForgetMemoryTool(memory),
    ]
