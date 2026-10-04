from app.ai.assistant import AssistantEngine
from app.ai.local_provider import LocalOllamaProvider
from app.memory.manager import MemoryManager
from app.tools.bootstrap import create_tool_system


def main() -> None:
    print("=== Lyra Web Grounding Test ===")

    memory = MemoryManager()
    provider = LocalOllamaProvider()

    registry, executor = create_tool_system(
        memory=memory,
    )

    assistant = AssistantEngine(
        provider=provider,
        registry=registry,
        executor=executor,
        memory=memory,
    )

    query = "What is the latest Python release?"

    print("\nUser:", query)

    response = assistant.respond(query)

    print("\nLyra:", response)

    assert "3.14.8" in response
    assert "September 20, 2024" not in response
    assert "2024" not in response

    # The current Python.org result should be reflected by the
    # grounded answer rather than the model falling back to old knowledge.
    assert "3.14.8" in response

    print("\nWeb grounding test passed.")


if __name__ == "__main__":
    main()
