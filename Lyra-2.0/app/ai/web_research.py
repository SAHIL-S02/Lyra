from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from app.ai.web_models import SearchResult
from app.tools.executor import ToolExecutor


@dataclass(frozen=True)
class ResearchSource:
    """A source selected and fetched for research."""

    title: str
    url: str
    source: str
    snippet: str
    content: str


@dataclass(frozen=True)
class ResearchResponse:
    """Structured research result."""

    query: str
    sources: list[ResearchSource]


class WebResearchService:
    """Searches the web and fetches the most useful sources."""

    TRUSTED_DOMAINS = {
        "python.org",
        "docs.python.org",
        "wikipedia.org",
        "github.com",
        "microsoft.com",
        "developer.mozilla.org",
        "oracle.com",
        "nasa.gov",
        "openai.com",
        "ollama.com",
    }

    def __init__(
        self,
        executor: ToolExecutor,
    ) -> None:
        self.executor = executor

    @classmethod
    def _domain_score(
        cls,
        url: str,
    ) -> int:
        """Score a URL based on source authority."""

        try:
            hostname = urlparse(url).hostname or ""
        except ValueError:
            return 0

        hostname = hostname.lower()

        for domain in cls.TRUSTED_DOMAINS:
            if (
                hostname == domain
                or hostname.endswith(f".{domain}")
            ):
                return 100

        # Prefer HTTPS.
        if url.lower().startswith("https://"):
            return 10

        return 0

    @classmethod
    def _rank_results(
        cls,
        results: list[dict],
    ) -> list[dict]:
        """Rank search results by source quality."""

        return sorted(
            results,
            key=lambda item: cls._domain_score(
                str(item.get("url", ""))
            ),
            reverse=True,
        )

    def research(
        self,
        query: str,
        max_search_results: int = 5,
        max_sources: int = 2,
        max_chars: int = 12000,
    ) -> ResearchResponse:
        """Search and fetch useful web sources."""

        query = query.strip()

        if not query:
            raise ValueError("query cannot be empty.")

        search_result = self.executor.execute(
            name="web_search",
            arguments={
                "query": query,
                "max_results": max_search_results,
            },
        )

        if not search_result.success:
            raise RuntimeError(
                f"Web search failed: {search_result.error}"
            )

        data = search_result.data

        if not isinstance(data, dict):
            raise RuntimeError(
                "Web search returned invalid data."
            )

        raw_results = data.get("results", [])

        if not isinstance(raw_results, list):
            raise RuntimeError(
                "Web search returned invalid results."
            )

        ranked_results = self._rank_results(
            raw_results
        )

        sources: list[ResearchSource] = []

        for result in ranked_results:
            if len(sources) >= max_sources:
                break

            if not isinstance(result, dict):
                continue

            title = str(
                result.get("title", "")
            ).strip()

            url = str(
                result.get("url", "")
            ).strip()

            snippet = str(
                result.get("snippet", "")
            ).strip()

            source = str(
                result.get("source", "")
            ).strip()

            if not url:
                continue

            fetch_result = self.executor.execute(
                name="web_fetch",
                arguments={
                    "url": url,
                    "max_chars": max_chars,
                },
            )

            if not fetch_result.success:
                continue

            fetch_data = fetch_result.data

            if not isinstance(fetch_data, dict):
                continue

            content = str(
                fetch_data.get("text", "")
            ).strip()

            if not content:
                continue

            sources.append(
                ResearchSource(
                    title=title,
                    url=url,
                    source=source,
                    snippet=snippet,
                    content=content,
                )
            )

        return ResearchResponse(
            query=query,
            sources=sources,
        )
