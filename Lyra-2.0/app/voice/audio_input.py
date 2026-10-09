from pathlib import Path

import sounddevice as sd
from scipy.io.wavfile import write


class MicrophoneInput:
    """Capture audio from a configurable microphone."""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        device: int | None = 2,
    ) -> None:
        self.sample_rate = sample_rate
        self.channels = channels
        self.device = device

    def health_check(self) -> bool:
        """Check whether the selected microphone is available."""

        try:
            info = sd.query_devices(self.device, kind="input")
            return info["max_input_channels"] >= self.channels
        except (ValueError, sd.PortAudioError):
            return False

    def record(
        self,
        output_path: str = "data/voice_input.wav",
        duration_seconds: float = 5.0,
    ) -> Path:
        """Record audio for a fixed duration and save it as a WAV file."""

        if duration_seconds <= 0:
            raise ValueError("Recording duration must be positive.")

        if not self.health_check():
            raise RuntimeError(
                f"Microphone device {self.device} is unavailable."
            )

        info = sd.query_devices(self.device, kind="input")
        print(f"Microphone: {info['name']}")
        print(f"Recording for {duration_seconds:g} seconds... Speak now.")

        audio = sd.rec(
            int(round(duration_seconds * self.sample_rate)),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="int16",
            device=self.device,
        )
        sd.wait()

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        write(str(path), self.sample_rate, audio)

        print(f"Recording saved: {path}")
        return path
