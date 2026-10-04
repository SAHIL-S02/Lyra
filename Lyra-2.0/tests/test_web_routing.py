from app.ai.assistant import AssistantEngine
from app.ai.local_provider import LocalOllamaProvider
from app.memory.manager import MemoryManager
from app.tools.bootstrap import create_tool_system


def main() -> None:
    print("=== Lyra Web Routing Test ===")

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

    print("\nUser: What is the latest Python release?")

    response = assistant.respond(
        "What is the latest Python release?"
    )

    print("\nLyra:", response)

    assert response.strip()

    print("\nWeb routing test passed.")


if __name__ == "__main__":
    main()
