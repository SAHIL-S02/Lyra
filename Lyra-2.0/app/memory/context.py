from __future__ import annotations

from app.memory.manager import MemoryManager


class MemoryContext:
    """Provides relevant persistent memories to Lyra's AI layer."""

    def __init__(self, memory: MemoryManager | None = None) -> None:
        self.memory = memory or MemoryManager()

    def build(self, query: str) -> str:
        """Find relevant memories and format them for the AI prompt."""

        memories = self.memory.search(query)

        if not memories:
            return ""

        lines = [
            "Relevant long-term memories:"
        ]

        for item in memories:
            lines.append(
                f"- {item['key']}: {item['value']}"
            )

        return "\n".join(lines)
