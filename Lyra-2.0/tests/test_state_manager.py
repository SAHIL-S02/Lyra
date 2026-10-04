from app.core.state import LyraState
from app.core.state_manager import InvalidStateTransition, StateManager


def main() -> None:
    manager = StateManager()

    print("Initial state:", manager.state.value)

    manager.transition(LyraState.WAKE_DETECTED)
    manager.transition(LyraState.LISTENING)
    manager.transition(LyraState.PROCESSING)
    manager.transition(LyraState.SPEAKING)
    manager.transition(LyraState.IDLE)
    manager.transition(LyraState.SLEEPING)

    print("Final state:", manager.state.value)

    print("\nTesting invalid transition...")

    try:
        manager.transition(LyraState.SPEAKING)
    except InvalidStateTransition as exc:
        print("Correctly rejected:", exc)

    print("\nState manager test passed.")


if __name__ == "__main__":
    main()
