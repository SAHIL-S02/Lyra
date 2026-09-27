import asyncio

from app.tools.bootstrap import register_all_tools
from app.tools.registry import tool_registry
from app.voice.controller import LyraVoiceController


async def main() -> None:
    # Initialize Lyra tools
    register_all_tools()

    print("\n🔧 Registered Lyra tools:")
    for name in tool_registry.names():
        print(f"   • {name}")

    print()

    controller = LyraVoiceController()
    await controller.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Lyra stopped.")