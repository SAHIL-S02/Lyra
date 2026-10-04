from __future__ import annotations

from app.ai.assistant import AssistantEngine
from app.ai.local_provider import LocalOllamaProvider
from app.core.logging import logger
from app.memory.manager import MemoryManager
from app.tools.bootstrap import create_tool_system


class LyraRuntime:
    """Constructs and owns Lyra's core runtime components."""

    def __init__(self) -> None:
        logger.info("Initializing Lyra runtime...")

        self.memory = MemoryManager()

        self.provider = LocalOllamaProvider()

        if not self.provider.health_check():
            raise RuntimeError(
                "Ollama is unavailable or the configured model "
                "is not installed."
            )

        self.registry, self.executor = create_tool_system(
            memory=self.memory,
        )

        self.assistant = AssistantEngine(
            provider=self.provider,
            registry=self.registry,
            executor=self.executor,
            memory=self.memory,
        )

        logger.info("Lyra runtime initialized successfully.")

    def respond(self, user_text: str) -> str:
        """Send a user message to Lyra."""

        return self.assistant.respond(user_text)

    def clear_conversation(self) -> None:
        """Clear current conversation context."""

        self.assistant.clear()
