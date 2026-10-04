from app.ai.router import AIRouter, RouteMode


def main() -> None:
    print("=== Lyra AI Router Test ===")

    router = AIRouter()

    cases = {
        "What time is it?": RouteMode.TOOL,
        "Tell me about recursion.": RouteMode.LOCAL,
        "What is the latest Python version?": RouteMode.WEB,
        "Search the web for the best Java IDEs.": RouteMode.WEB,
        "What is the weather today?": RouteMode.WEB,
        "What is my favorite programming language?": RouteMode.LOCAL,
        "Explain binary trees.": RouteMode.LOCAL,
    }

    for text, expected in cases.items():
        actual = router.route(text)

        print(f"\n{text}")
        print("Expected:", expected.value)
        print("Actual  :", actual.value)

        assert actual == expected

    print("\nAI router test passed.")


if __name__ == "__main__":
    main()
