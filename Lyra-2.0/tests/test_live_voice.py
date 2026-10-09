from app.core.runtime import LyraRuntime
from app.voice.audio_input import MicrophoneInput
from app.voice.controller import VoiceController
from app.voice.faster_whisper_provider import FasterWhisperProvider
from app.voice.piper_tts_provider import PiperTTSProvider


def main() -> None:
    print("=== Lyra Live Voice Integration Test ===")

    microphone = MicrophoneInput(
        sample_rate=16000,
        channels=1,
        device=2,
    )

    print("\nChecking microphone...")
    assert microphone.health_check(), "Microphone is unavailable."

    audio_path = microphone.record(
        output_path="data/voice_input.wav",
        duration_seconds=5,
    )

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
        print("\nProcessing your speech...")
        result = controller.process_audio_file(str(audio_path))

        print("\n========== RESULT ==========")
        print("You said :", result.transcript)
        print("Lyra     :", result.response)

        assert result.transcript, "No speech was recognized."
        assert result.response, "Lyra returned an empty response."

        print("\nLive voice integration test passed.")

    finally:
        controller.close()
        runtime.clear_conversation()


if __name__ == "__main__":
    main()
