import asyncio

from app.ai.gemini_live import GeminiLiveProvider


async def main() -> None:
    print("Connecting to Gemini Live...")

    live = GeminiLiveProvider()

    response = await live.test_connection()

    print("\nLyra Live Response:")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())