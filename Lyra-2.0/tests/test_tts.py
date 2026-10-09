from pathlib import Path

from app.voice.piper_tts_provider import PiperTTSProvider


def main() -> None:
    print("=== Lyra TTS Provider Test ===")

    provider = PiperTTSProvider()

    print("Provider:", type(provider).__name__)
    print("Model:", provider.model_path)
    print("Health:", provider.health_check())

    assert provider.health_check(), "Piper model or configuration is missing."

    print("\nSpeaking test sentence...")

    try:
        provider.speak(
            "Hello! I am Lyra, your personal AI assistant. "
            "My local text to speech system is working correctly."
        )

        assert provider.output_path.is_file(), "TTS audio file was not created."
        assert provider.output_path.stat().st_size > 44, "TTS audio file is empty."

        print("Audio file:", provider.output_path)
        print("File size:", provider.output_path.stat().st_size, "bytes")

    finally:
        provider.close()

    print("\nTTS provider test passed.")


if __name__ == "__main__":
    main()
