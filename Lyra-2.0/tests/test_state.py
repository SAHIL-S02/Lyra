from app.core.state import LyraState


def main() -> None:
    print("=== Lyra States ===")

    for state in LyraState:
        print(f"{state.name:<15} -> {state.value}")

    print("\nTotal states:", len(LyraState))


if __name__ == "__main__":
    main()
