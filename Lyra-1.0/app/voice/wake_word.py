from __future__ import annotations

from pathlib import Path

import numpy as np
import sounddevice as sd
from openwakeword.model import Model


class WakeWordDetector:
    """
    Local wake-word detector.

    Input:
        16-bit PCM
        mono
        16 kHz

    The custom Hey Lyra model is used through ONNX Runtime.
    """

    SAMPLE_RATE = 16_000
    FRAME_SAMPLES = 1_280
    FRAME_BYTES = FRAME_SAMPLES * 2
    STREAM_BLOCK = 320  # 20 ms

    def __init__(
        self,
        model_path: str = "models/wakeword/hey_lyra.onnx",
        threshold: float = 0.5,
    ) -> None:
        self.threshold = threshold

        path = Path(model_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Wake-word model not found: {path.resolve()}"
            )

        self.model = Model(
            wakeword_models=[str(path)],
            inference_framework="onnx",
        )

        self._buffer = bytearray()

    def process(self, audio: bytes) -> tuple[bool, float]:
        """
        Feed microphone audio into the detector.

        Returns:
            detected, best_score
        """

        self._buffer.extend(audio)

        detected = False
        best_score = 0.0

        while len(self._buffer) >= self.FRAME_BYTES:
            frame_bytes = bytes(
                self._buffer[: self.FRAME_BYTES]
            )

            del self._buffer[: self.FRAME_BYTES]

            frame = np.frombuffer(
                frame_bytes,
                dtype=np.int16,
            )

            prediction = self.model.predict(frame)

            for name, score in prediction.items():
                score = float(score)

                if name == "hey_lyra":
                    best_score = max(best_score, score)

                    if score >= self.threshold:
                        detected = True

        return detected, best_score

    def reset(self) -> None:
        self._buffer.clear()
        self.model.reset()

    def listen(self) -> bool:
        """
        Block until Hey Lyra is detected.
        """

        self.reset()

        detected = False

        def callback(indata, frames, time_info, status):
            nonlocal detected

            if status:
                print(f"\nWake audio status: {status}")

            audio = bytes(indata)

            found, score = self.process(audio)

            if found:
                print(
                    f"\n🔥 Hey Lyra detected "
                    f"(score={score:.3f})"
                )
                detected = True

        with sd.RawInputStream(
            samplerate=self.SAMPLE_RATE,
            blocksize=self.STREAM_BLOCK,
            channels=1,
            dtype="int16",
            callback=callback,
        ):
            print(
                "Sleeping — listening for "
                "\"Hey Lyra\"..."
            )

            while not detected:
                sd.sleep(20)

        return True
