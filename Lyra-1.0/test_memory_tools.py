import asyncio

from app.tools.registry import tool_registry
from app.tools.executor import tool_executor
from app.tools.memory_tools import register_memory_tools


async def main():
    register_memory_tools()

    print("=" * 50)
    print("LYRA MEMORY TOOL TEST")
    print("=" * 50)

    print("\nRegistered tools:")
    for name in tool_registry.names():
        print(f"  - {name}")

    print("\nSearching memory:")
    result = await tool_executor.execute(
        "search_memory",
        {"query": "creator"},
    )
    print(result)

    print("\nTesting unknown tool:")
    result = await tool_executor.execute(
        "something_that_does_not_exist",
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())