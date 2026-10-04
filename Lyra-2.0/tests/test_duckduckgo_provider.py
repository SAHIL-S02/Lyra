from app.ai.duckduckgo_provider import DuckDuckGoProvider


def main() -> None:
    print("=== DuckDuckGo Web Search Test ===")

    provider = DuckDuckGoProvider()

    print("\nHealth check:", provider.health_check())

    print("\nSearching the web...")

    response = provider.search(
        "Python programming language",
        max_results=5,
    )

    print("\nQuery:", response.query)
    print("Results:", len(response.results))

    for index, result in enumerate(
        response.results,
        start=1,
    ):
        print(f"\n--- Result {index} ---")
        print("Title  :", result.title)
        print("URL    :", result.url)
        print("Snippet:", result.snippet)
        print("Source :", result.source)

    assert response.query == "Python programming language"
    assert len(response.results) > 0

    for result in response.results:
        assert result.title
        assert result.url
        assert result.source == "duckduckgo"

    print("\nDuckDuckGo provider test passed.")


if __name__ == "__main__":
    main()
