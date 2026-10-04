from app.memory.manager import MemoryManager


def main() -> None:
    memory = MemoryManager()

    print("=== Lyra Memory Manager ===")

    # Start with a clean database for this test.
    memory.forget("test_name")

    print("\n1. Storing memory...")
    memory.remember(
        key="test_name",
        value="Sahil",
        category="fact",
    )

    print("Count:", memory.count())

    print("\n2. Retrieving memory...")
    result = memory.get("test_name")

    print(result)

    print("\n3. Updating memory...")
    updated = memory.update(
        key="test_name",
        value="SK Sahil Uddin",
        category="fact",
    )

    print("Updated:", updated)
    print("Result:", memory.get("test_name"))

    print("\n4. Searching memory...")
    results = memory.search("Sahil")

    for item in results:
        print(item)

    print("\n5. Forgetting memory...")
    deleted = memory.forget("test_name")

    print("Deleted:", deleted)
    print("Final count:", memory.count())

    print("\nMemory manager test passed.")


if __name__ == "__main__":
    main()
