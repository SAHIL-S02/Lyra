from __future__ import annotations

from enum import Enum


class LyraState(str, Enum):
    """Possible runtime states of Lyra."""

    SLEEPING = "sleeping"
    WAKE_DETECTED = "wake_detected"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    IDLE = "idle"
    ERROR = "error"
