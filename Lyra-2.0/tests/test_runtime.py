from app.core.runtime import LyraRuntime


def main() -> None:
    print("=== Lyra Runtime Test ===")

    runtime = LyraRuntime()

    print("\nRuntime initialized.")
    print("Model:", runtime.provider.model)
    print("Tools:", len(runtime.registry.list_tools()))

    response = runtime.respond(
        "Explain what an API is in one simple sentence."
    )

    print("\nLyra:", response)

    assert response.strip()
    assert runtime.provider.health_check()

    print("\nLyra runtime test passed.")


if __name__ == "__main__":
    main()
