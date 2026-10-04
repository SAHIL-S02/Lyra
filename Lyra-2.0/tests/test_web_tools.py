from app.tools.web_tools import WebSearchTool


def main() -> None:
    print("=== Lyra Web Tool Test ===")

    tool = WebSearchTool()

    print("\nTool:")
    print(tool.name)

    print("\nDefinition:")
    print(tool.definition())

    print("\nSearching...")

    result = tool.execute(
        {
            "query": "latest Python release",
            "max_results": 5,
        }
    )

    print("\nSuccess:", result.success)
    print("Error  :", result.error)

    print("\nData:")

    print(result.data)

    assert result.success is True
    assert isinstance(result.data, dict)
    assert result.data["query"] == "latest Python release"
    assert len(result.data["results"]) > 0

    print("\nWeb tool test passed.")


if __name__ == "__main__":
    main()
