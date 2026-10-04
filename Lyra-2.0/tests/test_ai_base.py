from app.ai.base import AIProvider
from app.ai.models import AIResponse


class MockProvider(AIProvider):
    """Simple provider used only for testing."""

    def chat(
        self,
        messages,
        tools=None,
    ) -> AIResponse:
        return AIResponse(
            content="Mock response",
            tool_calls=[],
        )

    def health_check(self) -> bool:
        return True


def main() -> None:
    provider = MockProvider()

    print(
        "Provider type :",
        type(provider).__name__,
    )

    print(
        "Healthy       :",
        provider.health_check(),
    )

    response = provider.respond(
        "Hello Lyra"
    )

    print(
        "Response      :",
        response,
    )

    print(
        "\nAI provider interface test passed."
    )


if __name__ == "__main__":
    main()
