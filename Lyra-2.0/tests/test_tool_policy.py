from app.ai.tool_policy import detect_required_tool


def main() -> None:
    print("=== Lyra Tool Policy Test ===")

    cases = {
        "What time is it?": "get_current_time",
        "What's the current time?": "get_current_time",
        "Tell me the time right now.": "get_current_time",
        "What is my computer information?": "get_system_info",
        "Tell me about this computer.": "get_system_info",
        "What is recursion?": None,
    }

    for text, expected in cases.items():
        actual = detect_required_tool(text)

        print(f"\n{text}")
        print("Expected:", expected)
        print("Actual  :", actual)

        assert actual == expected

    print("\nTool policy test passed.")


if __name__ == "__main__":
    main()
