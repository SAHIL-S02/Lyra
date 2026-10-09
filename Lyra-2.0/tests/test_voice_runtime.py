from pathlib import Path

from app.core.runtime import LyraRuntime
from app.voice.controller import VoiceController
from app.voice.faster_whisper_provider import FasterWhisperProvider
from app.voice.piper_tts_provider import PiperTTSProvider


def main() -> None:
    print("=== Lyra Real AI Voice Integration Test ===")

    audio_path = Path("data/stt_test.wav")
    assert audio_path.is_file(), f"Test audio not found: {audio_path}"

    print("\nInitializing Lyra AI runtime...")
    runtime = LyraRuntime()

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
        respond=runtime.respond,
    )

    try:
        print("\nProcessing recorded speech...")
        result = controller.process_audio_file(str(audio_path))

        print("\nRecognized text:", result.transcript)
        print("Lyra's response:", result.response)

        assert result.transcript, "Speech recognition returned empty text."
        assert result.response, "Lyra returned an empty response."

        print("\nReal AI voice integration test passed.")

    finally:
        controller.close()
        runtime.clear_conversation()


if __name__ == "__main__":
    main()
