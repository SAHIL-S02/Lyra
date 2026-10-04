from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolCall:
    """A tool call requested by the AI model."""

    id: str | None
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class AIResponse:
    """Structured response returned by an AI provider."""

    content: str
    tool_calls: list[ToolCall]
