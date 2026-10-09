from pathlib import Path
import subprocess
import sys

import sounddevice as sd
from scipy.io import wavfile

from app.voice.tts import TTSProvider


class PiperTTSProvider(TTSProvider):
    """Local Piper text-to-speech provider with speaker playback."""

    def __init__(
        self,
        model_path: str = "models/tts/en_US-lessac-medium.onnx",
        output_path: str = "data/tts_output.wav",
    ) -> None:
        self.model_path = Path(model_path)
        self.output_path = Path(output_path)
        self._process: subprocess.Popen | None = None

    def speak(self, text: str) -> None:
        text = text.strip()

        if not text:
            return

        if not self.health_check():
            raise FileNotFoundError(
                f"Piper model or configuration not found: {self.model_path}"
            )

        self.stop()
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        self._process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "piper",
                "-m",
                str(self.model_path),
                "-f",
                str(self.output_path),
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            _, stderr = self._process.communicate(
                input=text + "\n",
                timeout=120,
            )

            if self._process.returncode != 0:
                raise RuntimeError(
                    f"Piper synthesis failed: {stderr.strip()}"
                )

        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.communicate()
            raise TimeoutError("Piper synthesis timed out.")

        finally:
            self._process = None

        sample_rate, audio = wavfile.read(str(self.output_path))

        sd.play(audio, samplerate=sample_rate)
        sd.wait()

    def health_check(self) -> bool:
        config_path = Path(str(self.model_path) + ".json")
        return self.model_path.is_file() and config_path.is_file()

    def stop(self) -> None:
        if self._process is not None and self._process.poll() is None:
            self._process.terminate()

            try:
                self._process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()

        self._process = None
        sd.stop()

    def close(self) -> None:
        self.stop()
