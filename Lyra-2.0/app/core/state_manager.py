from __future__ import annotations

from threading import Lock

from app.core.logging import logger
from app.core.state import LyraState


class InvalidStateTransition(Exception):
    """Raised when Lyra attempts an invalid state transition."""


class StateManager:
    """Controls Lyra's runtime state and valid state transitions."""

    _TRANSITIONS: dict[LyraState, set[LyraState]] = {
        LyraState.SLEEPING: {
            LyraState.WAKE_DETECTED,
            LyraState.ERROR,
        },
        LyraState.WAKE_DETECTED: {
            LyraState.LISTENING,
            LyraState.SLEEPING,
            LyraState.ERROR,
        },
        LyraState.LISTENING: {
            LyraState.PROCESSING,
            LyraState.SLEEPING,
            LyraState.ERROR,
        },
        LyraState.PROCESSING: {
            LyraState.SPEAKING,
            LyraState.IDLE,
            LyraState.ERROR,
        },
        LyraState.SPEAKING: {
            LyraState.IDLE,
            LyraState.LISTENING,
            LyraState.SLEEPING,
            LyraState.ERROR,
        },
        LyraState.IDLE: {
            LyraState.LISTENING,
            LyraState.SLEEPING,
            LyraState.ERROR,
        },
        LyraState.ERROR: {
            LyraState.SLEEPING,
        },
    }

    def __init__(self, initial_state: LyraState = LyraState.SLEEPING) -> None:
        self._state = initial_state
        self._lock = Lock()

        logger.info("State manager initialized: %s", self._state.value)

    @property
    def state(self) -> LyraState:
        """Return the current Lyra state."""
        with self._lock:
            return self._state

    def can_transition(self, target: LyraState) -> bool:
        """Check whether a transition is allowed."""
        with self._lock:
            return target in self._TRANSITIONS.get(self._state, set())

    def transition(self, target: LyraState) -> LyraState:
        """Transition Lyra to a new state."""

        with self._lock:
            current = self._state

            if target not in self._TRANSITIONS.get(current, set()):
                raise InvalidStateTransition(
                    f"Invalid transition: "
                    f"{current.value} -> {target.value}"
                )

            self._state = target

        logger.info(
            "State transition: %s -> %s",
            current.value,
            target.value,
        )

        return target

    def reset(self) -> LyraState:
        """Return Lyra to the sleeping state."""

        with self._lock:
            previous = self._state
            self._state = LyraState.SLEEPING

        logger.info(
            "State reset: %s -> %s",
            previous.value,
            LyraState.SLEEPING.value,
        )

        return self._state
