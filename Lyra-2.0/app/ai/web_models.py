from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchResult:
    """A single web search result."""

    title: str
    url: str
    snippet: str
    source: str
    published: str | None = None


@dataclass(frozen=True)
class WebSearchResponse:
    """Structured result returned by a web search provider."""

    query: str
    results: list[SearchResult]
