from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.ai.models import AIResponse


class AIProvider(ABC):
    """Base interface for all Lyra AI providers."""

    @abstractmethod
    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> AIResponse:
        """Generate a structured AI response."""
        raise NotImplementedError

    def respond(self, user_text: str) -> str:
        """Simple text-only interface for providers."""

        response = self.chat(
            messages=[
                {
                    "role": "user",
                    "content": user_text,
                }
            ]
        )

        return response.content
