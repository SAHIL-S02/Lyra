from dataclasses import dataclass
from typing import Callable

from app.voice.stt import STTProvider
from app.voice.tts import TTSProvider


@dataclass(frozen=True)
class VoiceTurnResult:
    """Result of one voice interaction."""

    transcript: str
    response: str


class VoiceController:
    """Coordinates speech recognition, AI response, and speech output."""

    def __init__(
        self,
        stt: STTProvider,
        tts: TTSProvider,
        respond: Callable[[str], str],
    ) -> None:
        self.stt = stt
        self.tts = tts
        self.respond = respond

    def process_audio_file(self, audio_path: str) -> VoiceTurnResult:
        """Process an audio file and speak the generated response."""

        if not self.stt.health_check():
            raise RuntimeError("STT provider is not ready.")

        if not self.tts.health_check():
            raise RuntimeError("TTS provider is not ready.")

        transcript = self.stt.transcribe(audio_path).strip()

        if not transcript:
            return VoiceTurnResult(
                transcript="",
                response="",
            )

        response = self.respond(transcript)

        if not isinstance(response, str):
            raise TypeError("The AI response function must return a string.")

        response = response.strip()

        if response:
            self.tts.speak(response)

        return VoiceTurnResult(
            transcript=transcript,
            response=response,
        )

    def close(self) -> None:
        """Release STT and TTS resources."""

        try:
            self.tts.close()
        finally:
            self.stt.close()
