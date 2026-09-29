from __future__ import annotations

from .manager import MemoryManager


# One memory manager for the running Lyra process.
memory_manager = MemoryManager()


def remember_memory(
    key: str,
    value: str,
    category: str = "fact",
    retention: str = "permanent",
    source: str = "voice",
) -> dict:
    """
    Create a memory or update the existing memory with the same
    logical key/category.
    """
    return memory_manager.remember(
        key=key,
        value=value,
        category=category,
        retention=retention,
        source=source,
    )


def search_memory(
    query: str,
    category: str | None = None,
    limit: int = 10,
) -> dict:
    """
    Search long-term memory.
    """
    memories = memory_manager.search(
        query=query,
        category=category,
        limit=limit,
    )

    return {
        "success": True,
        "count": len(memories),
        "memories": memories,
    }


def update_memory(
    key: str,
    value: str,
    category: str = "fact",
    retention: str | None = None,
    source: str | None = None,
) -> dict:
    """
    Update an existing memory.

    IMPORTANT:
    This operation never creates a new memory. The key should come
    from search_memory when modifying an existing memory.
    """
    return memory_manager.update(
        key=key,
        value=value,
        category=category,
        retention=retention,
        source=source,
    )


def forget_memory(
    key: str,
    category: str | None = None,
) -> dict:
    """
    Delete a memory.
    """
    deleted = memory_manager.forget(
        key=key,
        category=category,
    )

    return {
        "success": True,
        "deleted_count": deleted,
        "key": key,
        "category": category,
    }


MEMORY_FUNCTIONS = {
    "remember_memory": remember_memory,
    "search_memory": search_memory,
    "update_memory": update_memory,
    "forget_memory": forget_memory,
}


MEMORY_TOOL_DECLARATIONS = [
    {
        "name": "remember_memory",
        "description": (
            "Create a new long-term memory or update an existing memory. "
            "Use only when the user explicitly asks Lyra to remember, save, "
            "keep, or not forget something. For an existing fact, use the "
            "exact existing key whenever possible."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "key": {
                    "type": "STRING",
                    "description": (
                        "Stable memory key such as 'creator', 'user_name', "
                        "or 'favorite_programming_language'."
                    ),
                },
                "value": {
                    "type": "STRING",
                    "description": "The information to store.",
                },
                "category": {
                    "type": "STRING",
                    "description": (
                        "Memory category: fact, preference, event, profile, or other."
                    ),
                    "enum": [
                        "fact",
                        "preference",
                        "event",
                        "profile",
                        "other",
                    ],
                },
                "retention": {
                    "type": "STRING",
                    "description": "Memory retention policy.",
                    "enum": [
                        "permanent",
                        "episodic",
                    ],
                },
                "source": {
                    "type": "STRING",
                    "description": "Where the memory came from.",
                },
            },
            "required": [
                "key",
                "value",
            ],
        },
    },
    {
        "name": "search_memory",
        "description": (
            "Search Lyra's long-term memory for previously stored "
            "information. Use this when an answer depends on remembered "
            "user information."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {
                    "type": "STRING",
                    "description": "Words describing the information to find.",
                },
                "category": {
                    "type": "STRING",
                    "description": (
                        "Optional category filter."
                    ),
                    "enum": [
                        "fact",
                        "preference",
                        "event",
                        "profile",
                        "other",
                    ],
                },
                "limit": {
                    "type": "INTEGER",
                    "description": "Maximum number of memories to return.",
                },
            },
            "required": [
                "query",
            ],
        },
    },
    {
        "name": "update_memory",
        "description": (
            "Update an existing long-term memory. This tool NEVER creates "
            "a new memory. First search for the existing memory when the "
            "correct key is not already known, then use the exact key "
            "returned by search_memory. Never invent variants such as "
            "'creator_name', 'my_creator', or 'creator_full_name' when "
            "the existing key is 'creator'."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "key": {
                    "type": "STRING",
                    "description": "Exact existing memory key.",
                },
                "value": {
                    "type": "STRING",
                    "description": "The new memory value.",
                },
                "category": {
                    "type": "STRING",
                    "description": "Category of the existing memory.",
                    "enum": [
                        "fact",
                        "preference",
                        "event",
                        "profile",
                        "other",
                    ],
                },
                "retention": {
                    "type": "STRING",
                    "description": "Optional new retention policy.",
                    "enum": [
                        "permanent",
                        "episodic",
                    ],
                },
                "source": {
                    "type": "STRING",
                    "description": "Optional new source value.",
                },
            },
            "required": [
                "key",
                "value",
            ],
        },
    },
    {
        "name": "forget_memory",
        "description": (
            "Delete a previously stored memory only when the user "
            "explicitly asks Lyra to forget or remove it."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "key": {
                    "type": "STRING",
                    "description": "Memory key to delete.",
                },
                "category": {
                    "type": "STRING",
                    "description": "Optional category filter.",
                    "enum": [
                        "fact",
                        "preference",
                        "event",
                        "profile",
                        "other",
                    ],
                },
            },
            "required": [
                "key",
            ],
        },
    },
]
