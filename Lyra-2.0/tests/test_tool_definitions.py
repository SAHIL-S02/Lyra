from app.tools.bootstrap import create_tool_system


def main() -> None:
    print("=== Lyra Tool Definitions Test ===")

    registry, _ = create_tool_system()

    definitions = registry.definitions()

    print("\nTotal definitions:", len(definitions))

    for definition in definitions:
        function = definition["function"]

        print(f"\nTool: {function['name']}")
        print(f"Description: {function['description']}")
        print(f"Parameters: {function['parameters']}")

        assert definition["type"] == "function"
        assert isinstance(function["name"], str)
        assert isinstance(function["description"], str)
        assert isinstance(function["parameters"], dict)
        assert function["parameters"]["type"] == "object"

    expected = {
        "remember_memory",
        "search_memory",
        "update_memory",
        "forget_memory",
        "get_current_time",
        "get_system_info",
        "web_search",
        "web_fetch",
    }

    actual = {
        definition["function"]["name"]
        for definition in definitions
    }

    assert actual == expected

    print("\nAll tool schemas are valid.")
    print("Tool definition test passed.")


if __name__ == "__main__":
    main()
