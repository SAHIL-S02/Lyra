from app.tools.web_fetch_tools import WebFetchTool


def main() -> None:
    print("=== Lyra Web Fetch Tool Test ===")

    tool = WebFetchTool()

    print("\nTool:", tool.name)

    print("\nDefinition:")
    print(tool.definition())

    print("\nFetching Python.org...")

    result = tool.execute(
        {
            "url": "https://www.python.org/downloads/",
            "max_chars": 5000,
        }
    )

    print("\nSuccess:", result.success)
    print("Error  :", result.error)

    assert result.success is True
    assert isinstance(result.data, dict)
    assert result.data["url"] == "https://www.python.org/downloads/"
    assert "Python" in result.data["text"]
    assert len(result.data["text"]) > 0

    print("\nExtracted characters:", result.data["characters"])

    print("\nFirst 1000 characters:")
    print(result.data["text"][:1000])

    print("\nWeb fetch tool test passed.")


if __name__ == "__main__":
    main()
