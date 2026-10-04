from app.memory.manager import MemoryManager


MEMORY_KEY = "persistence_test"


def main() -> None:
    print("=== Lyra Persistent Memory Test ===")

    # First manager instance.
    memory1 = MemoryManager()

    # Clean up any previous test data.
    memory1.forget(MEMORY_KEY)

    print("\n1. Creating memory...")
    memory1.remember(
        key=MEMORY_KEY,
        value="Lyra persistent memory works",
        category="fact",
    )

    print("Stored:", memory1.get(MEMORY_KEY))

    # Simulate a restart by creating a completely new manager.
    print("\n2. Creating new memory manager...")
    memory2 = MemoryManager()

    print("\n3. Reading memory after restart...")
    result = memory2.get(MEMORY_KEY)

    print("Retrieved:", result)

    assert result is not None
    assert result["value"] == "Lyra persistent memory works"

    # Clean up.
    print("\n4. Cleaning test memory...")
    deleted = memory2.forget(MEMORY_KEY)

    print("Deleted:", deleted)
    print("Final count:", memory2.count())

    print("\nPersistent memory test passed.")


if __name__ == "__main__":
    main()
