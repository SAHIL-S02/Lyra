import time
from pathlib import Path

import numpy as np
import sounddevice as sd
from openwakeword.model import Model


SAMPLE_RATE = 16000
BLOCK_SIZE = 1280          # 80 ms
THRESHOLD = 0.5
COOLDOWN = 1.0


class WakeWordDetector:
    def __init__(
        self,
        model_path: str = "models/wakeword/hey_lyra.onnx",
        threshold: float = THRESHOLD,
    ):
        path = Path(model_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Wake-word model not found: {path.resolve()}"
            )

        self.threshold = threshold
        self.last_detection = 0.0

        self.model = Model(
            wakeword_models=[str(path)],
            inference_framework="onnx",
        )

    def process(self, audio: np.ndarray) -> bool:
        """
        Process one int16 mono PCM chunk.
        Returns True when Hey Lyra is detected.
        """
        prediction = self.model.predict(audio)

        score = float(prediction.get("hey_lyra", 0.0))

        now = time.monotonic()

        if score >= self.threshold:
            if now - self.last_detection >= COOLDOWN:
                self.last_detection = now
                return True

        return False

    def listen(self):
        """
        Blocking wake-word listener.
        Yields when Hey Lyra is detected.
        """
        detected = False

        def callback(indata, frames, time_info, status):
            nonlocal detected

            if status:
                print(f"Audio status: {status}")

            audio = (
                np.clip(indata[:, 0], -1.0, 1.0) * 32767
            ).astype(np.int16)

            if self.process(audio):
                detected = True

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=BLOCK_SIZE,
            callback=callback,
        ):
            while not detected:
                time.sleep(0.01)

        return True