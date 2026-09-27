from __future__ import annotations

import webrtcvad


class ClientVAD:
    """
    Lightweight local Voice Activity Detector.

    Input:
        16-bit mono PCM, 16 kHz, 20 ms frames.

    The VAD is mainly used to detect the END of a user's utterance.
    Gemini's server-side VAD remains enabled for speech-start detection.
    """

    SAMPLE_RATE = 16_000
    FRAME_MS = 20
    FRAME_BYTES = int(SAMPLE_RATE * FRAME_MS / 1000) * 2

    def __init__(
        self,
        aggressiveness: int = 2,
        silence_ms: int = 500,
    ) -> None:
        if not 0 <= aggressiveness <= 3:
            raise ValueError("Aggressiveness must be between 0 and 3.")

        if silence_ms < 500:
            raise ValueError(
                "Use at least 500 ms of silence to avoid cutting speech."
            )

        if silence_ms % self.FRAME_MS != 0:
            raise ValueError(
                "silence_ms must be a multiple of 20 ms."
            )

        self.vad = webrtcvad.Vad(aggressiveness)

        self.silence_frames_required = silence_ms // self.FRAME_MS

        self.speaking = False
        self.silent_frames = 0

    def process(self, frame: bytes) -> tuple[bool, bool, bool]:
        """
        Returns:
            is_speech
            speech_started
            speech_ended
        """

        if len(frame) != self.FRAME_BYTES:
            raise ValueError(
                f"Invalid frame size: expected "
                f"{self.FRAME_BYTES} bytes, got {len(frame)}."
            )

        is_speech = self.vad.is_speech(
            frame,
            self.SAMPLE_RATE,
        )

        speech_started = False
        speech_ended = False

        if is_speech:
            self.silent_frames = 0

            if not self.speaking:
                self.speaking = True
                speech_started = True

        else:

            if self.speaking:
                self.silent_frames += 1

                if (
                    self.silent_frames
                    >= self.silence_frames_required
                ):
                    self.speaking = False
                    self.silent_frames = 0
                    speech_ended = True

        return (
            is_speech,
            speech_started,
            speech_ended,
        )

    def reset(self) -> None:
        self.speaking = False
        self.silent_frames = 0