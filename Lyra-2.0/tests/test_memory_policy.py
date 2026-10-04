from app.memory.policy import normalize_memory


def main() -> None:
    print("=== Lyra Memory Policy Test ===")

    print("\n1. Alias normalization")

    key, category = normalize_memory(
        "favorite_language",
        "fact",
    )

    print("Key     :", key)
    print("Category:", category)

    assert key == "favorite_programming_language"
    assert category == "preference"

    print("\n2. Canonical key normalization")

    key, category = normalize_memory(
        "favorite_programming_language",
        "fact",
    )

    print("Key     :", key)
    print("Category:", category)

    assert key == "favorite_programming_language"
    assert category == "preference"

    print("\n3. User name normalization")

    key, category = normalize_memory(
        "name",
        "fact",
    )

    print("Key     :", key)
    print("Category:", category)

    assert key == "user_name"
    assert category == "profile"

    print("\n4. Standard category")

    key, category = normalize_memory(
        "creator",
        "fact",
    )

    print("Key     :", key)
    print("Category:", category)

    assert key == "creator"
    assert category == "fact"

    print("\n5. Invalid category")

    try:
        normalize_memory(
            "something",
            "invalid_category",
        )
    except ValueError as exc:
        print("Correctly rejected:", exc)
    else:
        raise AssertionError(
            "Invalid category was not rejected."
        )

    print("\nMemory policy test passed.")


if __name__ == "__main__":
    main()
