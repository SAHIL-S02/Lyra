from __future__ import annotations

from ddgs import DDGS

from app.ai.web_models import SearchResult, WebSearchResponse
from app.ai.web_provider import WebSearchProvider


class WebSearchError(RuntimeError):
    """Raised when a web search request fails."""


class DuckDuckGoProvider(WebSearchProvider):
    """DuckDuckGo-backed web search provider."""

    def __init__(self, timeout: int = 15) -> None:
        self.timeout = timeout

    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> WebSearchResponse:
        """Search DuckDuckGo and return normalized results."""

        query = query.strip()

        if not query:
            raise ValueError("query cannot be empty.")

        if max_results <= 0:
            raise ValueError(
                "max_results must be greater than zero."
            )

        try:
            searcher = DDGS(
                timeout=self.timeout
            )

            raw_results = searcher.text(
                query,
                max_results=max_results,
            )

        except Exception as exc:
            raise WebSearchError(
                f"DuckDuckGo search failed: {exc}"
            ) from exc

        results: list[SearchResult] = []

        for item in raw_results:
            if not isinstance(item, dict):
                continue

            title = str(
                item.get("title", "")
            ).strip()

            url = str(
                item.get("href", "")
            ).strip()

            snippet = str(
                item.get("body", "")
            ).strip()

            raw_date = item.get("date")

            published = None

            if raw_date is not None:
                published = str(
                    raw_date
                ).strip() or None

            if not title or not url:
                continue

            results.append(
                SearchResult(
                    title=title,
                    url=url,
                    snippet=snippet,
                    source="duckduckgo",
                    published=published,
                )
            )

            if len(results) >= max_results:
                break

        return WebSearchResponse(
            query=query,
            results=results,
        )

    def health_check(self) -> bool:
        """Check whether DuckDuckGo search is available."""

        try:
            response = self.search(
                "Python programming language",
                max_results=1,
            )

            return len(response.results) > 0

        except Exception:
            return False
