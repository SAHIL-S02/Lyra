import asyncio

from app.tools.bootstrap import register_all_tools
from app.tools.executor import tool_executor
from app.tools.registry import tool_registry


async def main() -> None:
    register_all_tools()

    print("=" * 50)
    print("LYRA SYSTEM TOOLS TEST")
    print("=" * 50)

    print("\nRegistered tools:")

    for name in tool_registry.names():
        print(f"  - {name}")

    print("\nTesting current time:")

    result = await tool_executor.execute(
        "get_current_time"
    )

    print(result)

    print("\nTesting system info:")

    result = await tool_executor.execute(
        "get_system_info"
    )

    print(result)

    print("\nTesting unknown tool:")

    result = await tool_executor.execute(
        "unknown_system_tool"
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())