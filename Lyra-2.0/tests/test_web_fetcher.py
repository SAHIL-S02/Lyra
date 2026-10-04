from app.ai.web_fetcher import fetch_web_page


def main() -> None:
    print("=== Web Page Fetch Test ===")

    url = "https://www.python.org/downloads/"

    print("\nURL:", url)
    print("\nFetching...")

    text = fetch_web_page(
        url,
        max_chars=5000,
    )

    print("\nCharacters:", len(text))

    print("\nFirst 1500 characters:\n")
    print(text[:1500])

    assert len(text) > 0
    assert "Python" in text

    print("\nWeb page fetch test passed.")


if __name__ == "__main__":
    main()
