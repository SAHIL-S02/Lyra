from app.ai.agent import ToolCallingAgent
from app.ai.local_provider import LocalOllamaProvider
from app.tools.bootstrap import create_tool_system


def main() -> None:
    print("=== Lyra AI Tool Agent Test ===")

    provider = LocalOllamaProvider()

    registry, executor = create_tool_system()

    agent = ToolCallingAgent(
        provider=provider,
        registry=registry,
        executor=executor,
    )

    print("\nUser: What time is it right now?")

    response = agent.respond(
        "What time is it right now?"
    )

    print("\nLyra:", response)

    assert response.strip()

    print("\nAI tool agent test passed.")


if __name__ == "__main__":
    main()
