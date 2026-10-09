from pathlib import Path

from app.voice.faster_whisper_provider import FasterWhisperProvider


def main() -> None:
    print("=== Lyra STT Provider Test ===")

    audio_path = Path("data/stt_test.wav")

    assert audio_path.is_file(), f"Test audio not found: {audio_path}"

    provider = FasterWhisperProvider(
        model_name="large-v3-turbo",
        device="cuda",
        compute_type="float16",
        language="en",
    )

    print("Provider      :", type(provider).__name__)
    print("Model         :", provider.model_name)
    print("Device        :", provider.device)
    print("Compute type  :", provider.compute_type)
    print("Language      :", provider.language)
    print("Health        :", provider.health_check())

    assert provider.health_check()

    text = provider.transcribe(str(audio_path))

    print("Transcription :", text)

    assert text.strip(), "STT returned empty transcription."

    provider.close()

    print("\nSTT provider test passed.")


if __name__ == "__main__":
    main()
