from app.ai.conversation import ConversationEngine
from app.ai.local_provider import LocalOllamaProvider


def main() -> None:
    provider = LocalOllamaProvider()

    conversation = ConversationEngine(provider)

    print("=== Lyra Conversation Test ===")

    first = conversation.respond(
        "My name is Sahil. Remember it only for this conversation."
    )

    print("\nLyra:", first)

    second = conversation.respond(
        "What is my name?"
    )

    print("\nLyra:", second)

    print("\nConversation messages:")

    for message in conversation.messages:
        print(f"{message.role}: {message.content}")

    print("\nConversation engine test passed.")


if __name__ == "__main__":
    main()
