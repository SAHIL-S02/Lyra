from __future__ import annotations

import time

import sounddevice as sd

from app.voice.wake_word import WakeWordDetector


SAMPLE_RATE = 16_000
CHANNELS = 1

# 20 ms microphone callback.
BLOCK_SIZE = 320


def main() -> None:
    print("=" * 50)
    print("           LYRA WAKE WORD TEST")
    print("=" * 50)
    print()
    print("Temporary wake word: 'Hey Jarvis'")
    print("The real 'Hey Lyra' model comes later.")
    print()
    print("Press Ctrl+C to stop.")
    print()

    detector = WakeWordDetector(
        threshold=0.5,
    )

    last_detection = 0.0
    cooldown_seconds = 2.0

    def callback(indata, frames, time_info, status) -> None:
        nonlocal last_detection

        if status:
            print(
                f"\nAudio status: {status}",
                flush=True,
            )

        detected, score = detector.process(
            bytes(indata)
        )

        now = time.monotonic()

        if detected and (
            now - last_detection >= cooldown_seconds
        ):
            last_detection = now

            print(
                f"\n🎯 Wake word detected "
                f"(score={score:.3f})",
                flush=True,
            )

            detector.reset()

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        channels=CHANNELS,
        dtype="int16",
        callback=callback,
    ):
        print("🎤 Listening...\n")

        while True:
            time.sleep(0.1)


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\n\n✅ Wake-word test stopped.")