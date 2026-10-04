from app.ai.local_provider import LocalOllamaProvider


def main() -> None:
    provider = LocalOllamaProvider()

    print("=== Local Ollama Provider ===")
    print("Model      :", provider.model)
    print("Ollama URL :", provider.base_url)
    print("Available  :", provider.health_check())

    print("\nSending test message...")

    response = provider.respond(
        "Hello Lyra. Explain recursion in exactly two simple sentences."
    )

    print("\nLyra:")
    print(response)

    print("\nLocal Ollama provider test passed.")


if __name__ == "__main__":
    main()
