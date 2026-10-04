from __future__ import annotations

from typing import Any

from app.ai.duckduckgo_provider import DuckDuckGoProvider
from app.tools.base import Tool, ToolResult


class WebSearchTool(Tool):
    name = "web_search"
    description = (
        "Search the internet for current or external information "
        "and return relevant search results."
    )

    def __init__(
        self,
        provider: DuckDuckGoProvider | None = None,
    ) -> None:
        self.provider = provider or DuckDuckGoProvider()

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for the internet.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return.",
                    "default": 5,
                },
            },
            "required": ["query"],
        }

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> ToolResult:
        query = arguments.get("query")
        max_results = arguments.get("max_results", 5)

        if not isinstance(query, str) or not query.strip():
            return ToolResult(
                success=False,
                error="Argument 'query' is required.",
            )

        if not isinstance(max_results, int):
            return ToolResult(
                success=False,
                error="Argument 'max_results' must be an integer.",
            )

        if max_results < 1:
            return ToolResult(
                success=False,
                error="Argument 'max_results' must be at least 1.",
            )

        if max_results > 10:
            max_results = 10

        try:
            response = self.provider.search(
                query=query,
                max_results=max_results,
            )

            return ToolResult(
                success=True,
                data={
                    "query": response.query,
                    "results": [
                        {
                            "title": result.title,
                            "url": result.url,
                            "snippet": result.snippet,
                            "source": result.source,
                            "published": result.published,
                        }
                        for result in response.results
                    ],
                },
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                error=str(exc),
            )


def create_web_tools() -> list[Tool]:
    """Create Lyra's web tools."""

    return [
        WebSearchTool(),
    ]
