from __future__ import annotations

from abc import ABC, abstractmethod

from app.ai.web_models import WebSearchResponse


class WebSearchProvider(ABC):
    """Base interface for Lyra web-search providers."""

    @abstractmethod
    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> WebSearchResponse:
        """Search the web and return structured results."""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """Return True when the provider is available."""
        raise NotImplementedError
