from __future__ import annotations

from enum import Enum

from app.ai.tool_policy import detect_required_tool


class RouteMode(str, Enum):
    """Processing modes available to Lyra."""

    LOCAL = "local"
    TOOL = "tool"
    WEB = "web"
    HYBRID = "hybrid"


CURRENT_INFO_TERMS = {
    "current",
    "currently",
    "today",
    "now",
    "latest",
    "recent",
    "recently",
    "live",
    "this week",
    "this month",
    "this year",
}

WEB_REQUEST_TERMS = {
    "search the web",
    "search online",
    "search internet",
    "look online",
    "look it up",
    "look up online",
    "find online",
    "check the internet",
    "browse the web",
}

EXTERNAL_DATA_TERMS = {
    "weather",
    "news",
    "stock price",
    "share price",
    "exchange rate",
    "price",
    "release date",
    "version",
}


class AIRouter:
    """Determines how Lyra should process a user request."""

    def route(self, user_text: str) -> RouteMode:
        """Return the appropriate processing mode."""

        text = user_text.strip().lower()

        if not text:
            raise ValueError("user_text cannot be empty.")

        # Deterministic tools take priority.
        if detect_required_tool(text) is not None:
            return RouteMode.TOOL

        # Explicit web requests always require web access.
        if any(term in text for term in WEB_REQUEST_TERMS):
            return RouteMode.WEB

        # Requests containing clearly time-sensitive or external
        # information should use the web layer.
        if any(term in text for term in CURRENT_INFO_TERMS):
            return RouteMode.WEB

        if any(term in text for term in EXTERNAL_DATA_TERMS):
            return RouteMode.WEB

        return RouteMode.LOCAL
