from app.memory.manager import MemoryManager
from app.memory.context import MemoryContext


TEST_KEY = "favorite_language"
EXPECTED_KEY = "favorite_programming_language"


def main() -> None:
    print("=== Lyra Memory Context Test ===")

    memory = MemoryManager()

    # Ensure the test memory does not already exist.
    memory.forget(
        TEST_KEY,
        category="preference",
    )

    memory.forget(
        EXPECTED_KEY,
        category="preference",
    )

    print("\n1. Storing test memory...")

    memory.remember(
        key=TEST_KEY,
        value="Java",
        category="preference",
    )

    print("Memory stored.")

    # Verify that the alias was normalized correctly.
    stored = memory.get(
        EXPECTED_KEY,
        category="preference",
    )

    print("Stored memory:", stored)

    assert stored is not None
    assert stored["key"] == EXPECTED_KEY
    assert stored["value"] == "Java"
    assert stored["category"] == "preference"

    print("\n2. Building context...")

    context = MemoryContext(memory)

    result = context.build(
        "What programming language do I like?"
    )

    print(result)

    # Canonical key must appear in the generated context.
    assert EXPECTED_KEY in result
    assert "Java" in result

    print("\n3. Cleaning test memory...")

    deleted = memory.forget(
        EXPECTED_KEY,
        category="preference",
    )

    print("Deleted:", deleted)

    assert deleted >= 1

    # Verify cleanup.
    remaining = memory.get(
        EXPECTED_KEY,
        category="preference",
    )

    assert remaining is None

    print("\nMemory context test passed.")


if __name__ == "__main__":
    main()