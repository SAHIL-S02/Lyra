from __future__ import annotations

from app.core.logging import logger
from app.core.runtime import LyraRuntime


def main() -> None:
    print("=" * 50)
    print("                 LYRA 2.0")
    print("=" * 50)
    print("Local AI Assistant")
    print("Type /clear to clear conversation.")
    print("Type exit or quit to stop Lyra.")
    print("=" * 50)

    try:
        runtime = LyraRuntime()
    except Exception as exc:
        logger.exception("Failed to initialize Lyra.")
        print(f"\nFailed to start Lyra: {exc}")
        return

    print("\nLyra is ready.\n")

    while True:
        try:
            user_input = input("You: ").strip()

        except (KeyboardInterrupt, EOFError):
            print("\n\nLyra stopped.")
            break

        if not user_input:
            continue

        command = user_input.lower()

        if command in {"exit", "quit"}:
            print("Lyra stopped.")
            break

        if command == "/clear":
            runtime.clear_conversation()
            print("Lyra: Conversation cleared.\n")
            continue

        try:
            response = runtime.respond(user_input)

            print(f"Lyra: {response}\n")

        except Exception as exc:
            logger.exception("Request processing failed.")
            print(f"Lyra: I encountered an error: {exc}\n")


if __name__ == "__main__":
    main()
