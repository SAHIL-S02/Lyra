import asyncio

from app.tools.registry import tool_registry
from app.tools.executor import tool_executor


def say_hello(name: str) -> str:
    return f"Hello, {name}!"


async def get_status() -> dict:
    return {
        "status": "online",
        "assistant": "Lyra",
    }


tool_registry.register(
    name="say_hello",
    description="Say hello to a person.",
    handler=say_hello,
    parameters={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the person.",
            }
        },
        "required": ["name"],
    },
)


tool_registry.register(
    name="get_status",
    description="Get Lyra's current status.",
    handler=get_status,
    parameters={
        "type": "object",
        "properties": {},
    },
)


async def main() -> None:
    print("=" * 50)
    print("LYRA TOOL SYSTEM TEST")
    print("=" * 50)

    print("\nRegistered tools:")
    for name in tool_registry.names():
        print(f"  - {name}")

    print("\nTesting say_hello:")
    result = await tool_executor.execute(
        "say_hello",
        {"name": "Sahil"},
    )
    print(result)

    print("\nTesting get_status:")
    result = await tool_executor.execute(
        "get_status",
    )
    print(result)

    print("\nTesting unknown tool:")
    result = await tool_executor.execute(
        "does_not_exist",
    )
    print(result)

    print("\nTesting complete.")


if __name__ == "__main__":
    asyncio.run(main())