from __future__ import annotations

from typing import Any

from app.ai.prompts import LYRA_SYSTEM_PROMPT
from app.memory.context import MemoryContext


class ContextBuilder:
    """Builds the complete context sent to Lyra's AI provider."""

    def __init__(
        self,
        memory_context: MemoryContext,
    ) -> None:
        self.memory_context = memory_context

    def build(
        self,
        user_text: str,
        history: list[dict[str, Any]] | None = None,
        external_context: str | None = None,
    ) -> list[dict[str, Any]]:
        """Build a unified AI message list."""

        user_text = user_text.strip()

        if not user_text:
            raise ValueError("user_text cannot be empty.")

        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": LYRA_SYSTEM_PROMPT,
            }
        ]

        memory = self.memory_context.build(user_text)

        if memory:
            messages.append(
                {
                    "role": "system",
                    "content": (
                        "Relevant long-term memory:\n"
                        f"{memory}\n\n"
                        "Use this memory as background information. "
                        "Do not invent memories that are not provided."
                    ),
                }
            )

        if history:
            messages.extend(history)

        if external_context:
            messages.append(
                {
                    "role": "system",
                    "content": external_context,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": user_text,
            }
        )

        return messages
