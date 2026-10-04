from app.ai.context import ContextBuilder
from app.memory.context import MemoryContext
from app.memory.manager import MemoryManager


def main() -> None:
    print("=== Lyra Context Builder Test ===")

    memory = MemoryManager()

    test_key = "context_test_language"

    memory.forget(
        test_key,
        category="preference",
    )

    memory.remember(
        key=test_key,
        value="Java",
        category="preference",
    )

    builder = ContextBuilder(
        MemoryContext(memory)
    )

    history = [
        {
            "role": "user",
            "content": "I am working on a project.",
        },
        {
            "role": "assistant",
            "content": "Sounds good.",
        },
    ]

    messages = builder.build(
        user_text="What programming language do I prefer?",
        history=history,
        external_context=(
            "External context: This is test data."
        ),
    )

    print("\nGenerated messages:")

    for index, message in enumerate(
        messages,
        start=1,
    ):
        print(
            f"\n--- Message {index} ---"
        )
        print("Role:", message["role"])
        print("Content:")
        print(message["content"])

    combined = "\n".join(
        message["content"]
        for message in messages
    )

    assert "Lyra" in combined
    assert "Java" in combined
    assert "I am working on a project." in combined
    assert "External context: This is test data." in combined
    assert "What programming language do I prefer?" in combined

    memory.forget(
        test_key,
        category="preference",
    )

    print("\nContext builder test passed.")


if __name__ == "__main__":
    main()
