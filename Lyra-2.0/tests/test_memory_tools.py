from app.memory.manager import MemoryManager
from app.tools.executor import ToolExecutor
from app.tools.memory_tools import create_memory_tools
from app.tools.registry import ToolRegistry


TEST_KEY = "tool_test_memory_unique"
TEST_VALUE = "LYRA_TEST_VALUE_BEFORE"
UPDATED_VALUE = "LYRA_TEST_VALUE_AFTER"


def main() -> None:
    print("=== Lyra Memory Tools Test ===")

    memory = MemoryManager()

    # Preserve the database state that existed before the test.
    baseline_count = memory.count()

    # Clean up only our own previous test record.
    memory.forget(
        TEST_KEY,
        category="fact",
    )

    # Recalculate baseline after cleanup in case an old test record existed.
    baseline_count = memory.count()

    registry = ToolRegistry()

    for tool in create_memory_tools(memory):
        registry.register(tool)

    print("\nRegistered tools:")

    for tool in registry.list_tools():
        print(
            f"- {tool.name}: {tool.description}"
        )

    executor = ToolExecutor(registry)

    print("\n1. Remembering...")

    result = executor.execute(
        "remember_memory",
        {
            "key": TEST_KEY,
            "value": TEST_VALUE,
            "category": "fact",
        },
    )

    print("Success:", result.success)
    print("Data   :", result.data)
    print("Error  :", result.error)

    assert result.success is True

    print("\n2. Searching...")

    result = executor.execute(
        "search_memory",
        {
            "query": TEST_VALUE,
        },
    )

    print("Success:", result.success)
    print("Data   :", result.data)
    print("Error  :", result.error)

    assert result.success is True
    assert len(result.data) == 1
    assert result.data[0]["key"] == TEST_KEY
    assert result.data[0]["value"] == TEST_VALUE

    print("\n3. Updating...")

    result = executor.execute(
        "update_memory",
        {
            "key": TEST_KEY,
            "value": UPDATED_VALUE,
            "category": "fact",
        },
    )

    print("Success:", result.success)
    print("Data   :", result.data)
    print("Error  :", result.error)

    assert result.success is True

    print("\n4. Searching updated memory...")

    result = executor.execute(
        "search_memory",
        {
            "query": UPDATED_VALUE,
        },
    )

    print("Data:", result.data)

    assert result.success is True
    assert len(result.data) == 1
    assert result.data[0]["key"] == TEST_KEY
    assert result.data[0]["value"] == UPDATED_VALUE

    print("\n5. Forgetting...")

    result = executor.execute(
        "forget_memory",
        {
            "key": TEST_KEY,
            "category": "fact",
        },
    )

    print("Success:", result.success)
    print("Data   :", result.data)
    print("Error  :", result.error)

    assert result.success is True

    print("\n6. Verifying deletion...")

    result = executor.execute(
        "search_memory",
        {
            "query": UPDATED_VALUE,
        },
    )

    print("Data:", result.data)

    assert result.success is True
    assert result.data == []

    final_count = memory.count()

    print("\nBaseline memory count:", baseline_count)
    print("Final memory count   :", final_count)

    # The test must restore the database to the state it had
    # before the test. It must NOT require an empty database.
    assert final_count == baseline_count

    print("\nMemory tools test passed.")


if __name__ == "__main__":
    main()