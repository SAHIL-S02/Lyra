from app.tools.bootstrap import create_tool_system


def main() -> None:
    print("=== Lyra Tool Bootstrap Test ===")

    registry, executor = create_tool_system()

    tools = registry.list_tools()

    print("\nRegistered tools:")

    for tool in tools:
        print(f"- {tool.name}")

    print("\nTotal tools:", len(tools))

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
        tool.name
        for tool in tools
    }

    assert actual == expected
    assert len(tools) == 8
    assert executor is not None

    print("\nTool bootstrap test passed.")


if __name__ == "__main__":
    main()
