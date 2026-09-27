from app.memory.tools import (
    remember_memory,
    search_memory,
    update_memory,
    forget_memory,
)

from .registry import tool_registry


def register_memory_tools() -> None:
    tool_registry.register(
        name="remember_memory",
        description=(
            "Store information in Lyra's persistent memory. "
            "Use only when the user explicitly asks Lyra to remember something."
        ),
        handler=remember_memory,
        parameters={
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Memory key.",
                },
                "value": {
                    "type": "string",
                    "description": "Information to remember.",
                },
                "category": {
                    "type": "string",
                    "description": "Memory category.",
                },
            },
            "required": ["key", "value"],
        },
    )

    tool_registry.register(
        name="search_memory",
        description=(
            "Search Lyra's persistent memory for information "
            "that may already be remembered."
        ),
        handler=search_memory,
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Information to search for.",
                }
            },
            "required": ["query"],
        },
    )

    tool_registry.register(
        name="update_memory",
        description=(
            "Update an existing memory. "
            "Do not create a new memory when updating."
        ),
        handler=update_memory,
        parameters={
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Existing memory key.",
                },
                "value": {
                    "type": "string",
                    "description": "New value.",
                },
                "category": {
                    "type": "string",
                    "description": "Memory category.",
                },
            },
            "required": ["key", "value"],
        },
    )

    tool_registry.register(
        name="forget_memory",
        description=(
            "Delete information from Lyra's persistent memory. "
            "Use only when the user explicitly asks Lyra to forget it."
        ),
        handler=forget_memory,
        parameters={
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Memory key to forget.",
                },
                "category": {
                    "type": "string",
                    "description": "Memory category.",
                },
            },
            "required": ["key"],
        },
    )