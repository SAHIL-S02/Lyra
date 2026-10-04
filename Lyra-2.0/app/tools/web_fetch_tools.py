from __future__ import annotations

from typing import Any

from app.ai.web_fetcher import fetch_web_page
from app.tools.base import Tool, ToolResult


class WebFetchTool(Tool):
    name = "web_fetch"
    description = (
        "Fetch a public web page and extract its readable text "
        "from a URL."
    )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Public HTTP or HTTPS URL to fetch.",
                },
                "max_chars": {
                    "type": "integer",
                    "description": "Maximum amount of page text to return.",
                    "default": 12000,
                },
            },
            "required": ["url"],
        }

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> ToolResult:
        url = arguments.get("url")
        max_chars = arguments.get("max_chars", 12000)

        if not isinstance(url, str) or not url.strip():
            return ToolResult(
                success=False,
                error="Argument 'url' is required.",
            )

        if not isinstance(max_chars, int):
            return ToolResult(
                success=False,
                error="Argument 'max_chars' must be an integer.",
            )

        if max_chars < 500:
            return ToolResult(
                success=False,
                error="Argument 'max_chars' must be at least 500.",
            )

        if max_chars > 30000:
            max_chars = 30000

        try:
            text = fetch_web_page(
                url=url,
                max_chars=max_chars,
            )

            return ToolResult(
                success=True,
                data={
                    "url": url.strip(),
                    "text": text,
                    "characters": len(text),
                },
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                error=str(exc),
            )


def create_web_fetch_tools() -> list[Tool]:
    """Create Lyra's web-fetching tools."""

    return [
        WebFetchTool(),
    ]
