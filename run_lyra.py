import asyncio

from app.voice.controller import LyraVoiceController


async def main() -> None:
    controller = LyraVoiceController()
    await controller.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Lyra stopped.")