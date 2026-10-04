from app.ai.web_models import SearchResult, WebSearchResponse
from app.ai.web_provider import WebSearchProvider


class MockWebProvider(WebSearchProvider):
    """Fake web provider used only for testing."""

    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> WebSearchResponse:

        results = [
            SearchResult(
                title="Example Result",
                url="https://example.com",
                snippet="Example search result.",
                source="mock",
            )
        ]

        return WebSearchResponse(
            query=query,
            results=results[:max_results],
        )

    def health_check(self) -> bool:
        return True


def main() -> None:
    print("=== Web Search Provider Test ===")

    provider = MockWebProvider()

    print("Healthy:", provider.health_check())

    response = provider.search(
        "Python programming",
        max_results=3,
    )

    print("\nQuery:", response.query)

    for result in response.results:
        print("\nTitle  :", result.title)
        print("URL    :", result.url)
        print("Snippet:", result.snippet)
        print("Source :", result.source)

    assert provider.health_check() is True
    assert response.query == "Python programming"
    assert len(response.results) == 1
    assert response.results[0].title == "Example Result"

    print("\nWeb search provider test passed.")


if __name__ == "__main__":
    main()
