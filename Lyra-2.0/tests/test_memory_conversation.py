from app.ai.conversation import ConversationEngine
from app.ai.local_provider import LocalOllamaProvider
from app.memory.context import MemoryContext
from app.memory.manager import MemoryManager


TEST_KEY = "favorite_programming_language"


def main() -> None:
    print("=== Lyra Memory + Conversation Test ===")

    memory = MemoryManager()

    # Clean previous test data.
    memory.forget(TEST_KEY, category="preference")

    print("\n1. Storing persistent memory...")

    memory.remember(
        key=TEST_KEY,
        value="Java",
        category="preference",
    )

    print("Stored:", memory.get(
        TEST_KEY,
        category="preference",
    ))

    print("\n2. Starting conversation engine...")

    provider = LocalOllamaProvider()
    context = MemoryContext(memory)

    conversation = ConversationEngine(
        provider=provider,
        memory_context=context,
    )

    print("\n3. Asking Lyra about the memory...")

    response = conversation.respond(
        "What programming language do I prefer?"
    )

    print("\nLyra:", response)

    print("\n4. Cleaning test memory...")

    deleted = memory.forget(
        TEST_KEY,
        category="preference",
    )

    print("Deleted:", deleted)
    print("Final memory count:", memory.count())

    print("\nMemory + conversation test passed.")


if __name__ == "__main__":
    main()
