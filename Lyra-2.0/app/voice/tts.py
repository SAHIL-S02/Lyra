from abc import ABC, abstractmethod


class TTSProvider(ABC):
    """Provider-independent text-to-speech interface."""

    @abstractmethod
    def speak(self, text: str) -> None:
        """Convert text to speech and play it."""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """Return True when the provider is ready."""
        raise NotImplementedError

    def stop(self) -> None:
        """Immediately stop current playback."""
        return None

    def close(self) -> None:
        """Release provider resources."""
        return None
