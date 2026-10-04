from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from app.ai.base import AIProvider
from app.ai.prompts import LYRA_SYSTEM_PROMPT
from app.core.logging import logger
from app.memory.context import MemoryContext


@dataclass(frozen=True)
class ConversationMessage:
    """A single message in a conversation."""

    role: str
    content: str


class ConversationEngine:
    """Manages short-term conversation and persistent memory context."""

    MAX_MESSAGES: Final[int] = 20

    def __init__(
        self,
        provider: AIProvider,
        memory_context: MemoryContext | None = None,
    ) -> None:
        self.provider = provider
        self.memory_context = memory_context or MemoryContext()
        self._messages: list[ConversationMessage] = []

        logger.info("Conversation engine initialized.")

    @property
    def messages(self) -> list[ConversationMessage]:
        """Return a copy of the current conversation history."""
        return list(self._messages)

    def clear(self) -> None:
        """Clear the current conversation."""
        self._messages.clear()
        logger.info("Conversation history cleared.")

    def _build_prompt(self, user_text: str) -> str:
        """Build the complete prompt sent to the AI provider."""

        sections = [
            f"System instructions:\n{LYRA_SYSTEM_PROMPT}",
        ]

        memory = self.memory_context.build(user_text)

        if memory:
            sections.append(
                "Long-term memory context:\n"
                f"{memory}\n\n"
                "Use these memories as background information. "
                "Do not claim to remember something that is not present."
            )

        if self._messages:
            history = "\n".join(
                f"{message.role.capitalize()}: {message.content}"
                for message in self._messages
            )

            sections.append(
                f"Current conversation:\n{history}"
            )

        sections.append(
            f"User: {user_text}\n"
            "Assistant:"
        )

        return "\n\n".join(sections)

    def respond(self, user_text: str) -> str:
        """Generate a response using conversation and memory context."""

        user_text = user_text.strip()

        if not user_text:
            raise ValueError("user_text cannot be empty.")

        prompt = self._build_prompt(user_text)

        logger.info("Processing conversational request.")

        response = self.provider.respond(prompt).strip()

        if not response:
            raise RuntimeError(
                "AI provider returned an empty response."
            )

        self._messages.append(
            ConversationMessage(
                role="user",
                content=user_text,
            )
        )

        self._messages.append(
            ConversationMessage(
                role="assistant",
                content=response,
            )
        )

        if len(self._messages) > self.MAX_MESSAGES:
            self._messages = self._messages[-self.MAX_MESSAGES:]

        return response
