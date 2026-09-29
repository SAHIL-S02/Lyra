import asyncio

from app.ai.gemini import GeminiProvider


async def main() -> None:
    ai = GeminiProvider()

    response = await ai.respond(
        "Hello. You are connected to the Lyra project. "
        "Reply with a short confirmation."
    )

    print("\nLyra AI Response:")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())