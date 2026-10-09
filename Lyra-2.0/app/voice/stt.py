from abc import ABC, abstractmethod


class STTProvider(ABC):
    """Provider-independent speech-to-text interface."""

    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        """Transcribe an audio file into text."""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """Return True when the provider is ready."""
        raise NotImplementedError

    def close(self) -> None:
        """Release provider resources."""
        return None
