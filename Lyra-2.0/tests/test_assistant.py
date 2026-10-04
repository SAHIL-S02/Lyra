from app.ai.assistant import AssistantEngine
from app.ai.local_provider import LocalOllamaProvider
from app.memory.manager import MemoryManager
from app.tools.bootstrap import create_tool_system


TEST_VALUE = "Java"


def main() -> None:
    print("=== Lyra Assistant Engine Test ===")

    memory = MemoryManager()

    # Remove previous test memories containing Java.
    existing = memory.search("Java")

    for item in existing:
        memory.forget(
            item["key"],
            category=item["category"],
        )

    provider = LocalOllamaProvider()

    registry, executor = create_tool_system(memory)

    assistant = AssistantEngine(
        provider=provider,
        registry=registry,
        executor=executor,
        memory=memory,
    )

    print("\n1. Teaching Lyra a preference...")

    response1 = assistant.respond(
        "Remember that my favorite programming language is Java."
    )

    print("\nLyra:", response1)

    print("\nStored memories:")

    stored_memories = memory.search("Java")

    for item in stored_memories:
        print(item)

    assert len(stored_memories) >= 1

    assert any(
        item["value"].lower() == TEST_VALUE.lower()
        for item in stored_memories
    )

    print("\n2. Asking Lyra about the preference...")

    response2 = assistant.respond(
        "What is my favorite programming language?"
    )

    print("\nLyra:", response2)

    assert response2.strip()

    print("\n3. Cleaning test memories...")

    for item in memory.search("Java"):
        memory.forget(
            item["key"],
            category=item["category"],
        )

    print("Final memory count:", memory.count())

    print("\nAssistant engine test passed.")


if __name__ == "__main__":
    main()
