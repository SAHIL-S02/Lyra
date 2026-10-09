from pathlib import Path

from app.voice.controller import VoiceController
from app.voice.faster_whisper_provider import FasterWhisperProvider
from app.voice.piper_tts_provider import PiperTTSProvider


def mock_ai_response(user_text: str) -> str:
    """Temporary response function for testing voice integration."""
    print(f"\n[Mock AI] Received: {user_text}")
    return f"I heard you say: {user_text}"


def main() -> None:
    print("=== Lyra Integrated Voice Pipeline Test ===")

    audio_path = Path("data/stt_test.wav")
    assert audio_path.is_file(), f"Test audio not found: {audio_path}"

    stt = FasterWhisperProvider(
        model_name="large-v3-turbo",
        device="cuda",
        compute_type="float16",
        language="en",
    )

    tts = PiperTTSProvider()

    controller = VoiceController(
        stt=stt,
        tts=tts,
        respond=mock_ai_response,
    )

    try:
        print("\nProcessing recorded audio...")
        result = controller.process_audio_file(str(audio_path))

        print("\nRecognized text:", result.transcript)
        print("AI response    :", result.response)

        assert result.transcript, "Speech recognition returned empty text."
        assert result.response, "AI response was empty."

        print("\nVoice pipeline test passed.")

    finally:
        controller.close()


if __name__ == "__main__":
    main()
