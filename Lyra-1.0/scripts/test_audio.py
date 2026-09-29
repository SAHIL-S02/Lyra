import time

import numpy as np
import sounddevice as sd


SAMPLE_RATE = 16_000
CHANNELS = 1
DURATION = 5


def main() -> None:
    print("Lyra Audio Test")
    print("=" * 40)

    print("\nAvailable audio devices:")
    print(sd.query_devices())

    print("\nStarting in:")
    for i in range(3, 0, -1):
        print(i)
        time.sleep(1)

    print("\n🎤 Speak now...")

    recording = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=np.int16,
    )

    sd.wait()

    print("✅ Recording finished.")

    print("🔊 Playing recording...")
    sd.play(recording, samplerate=SAMPLE_RATE)
    sd.wait()

    print("✅ Playback finished.")
    print("\nAudio test completed successfully.")


if __name__ == "__main__":
    main()