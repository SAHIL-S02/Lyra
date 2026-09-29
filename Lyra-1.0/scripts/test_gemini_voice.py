import asyncio
from app.voice.vad import ClientVAD
import sounddevice as sd

from app.ai.gemini_live import GeminiLiveProvider
from app.voice.audio_output import AudioPlayback


INPUT_SAMPLE_RATE = 16_000
CHANNELS = 1
DTYPE = "int16"

# 100 ms at 16 kHz
BLOCK_SIZE = 320


async def main() -> None:
    audio_queue: asyncio.Queue[
    tuple[str, bytes | None]
] = asyncio.Queue()
    loop = asyncio.get_running_loop()

    print("=" * 50)
    print("          LYRA CONTINUOUS VOICE TEST")
    print("=" * 50)
    print()
    print("Lyra is preparing...")
    print("Speak normally after the countdown.")
    print("Press Ctrl+C to stop.")
    print()

    
    client_vad = ClientVAD(
        aggressiveness=2,
        silence_ms=500,
    )
    # ---------------------------------------------------------
    # Microphone callback
    # ---------------------------------------------------------

    def audio_callback(indata, frames, time_info, status) -> None:
        if status:
            print(f"\nAudio input status: {status}")

        audio = bytes(indata)

        try:
            _, speech_started, speech_ended = client_vad.process(audio)

            if speech_started:
                print("\n🎤 Speech detected", flush=True)

            # Always send the current audio first.
            loop.call_soon_threadsafe(
                audio_queue.put_nowait,
                ("AUDIO", audio),
            )

            if speech_ended:
                print(
                    "\n🛑 Local VAD: speech ended",
                    flush=True,
                )

                loop.call_soon_threadsafe(
                    audio_queue.put_nowait,
                    ("END_OF_TURN", None),
                )

        except ValueError:
            pass

    # ---------------------------------------------------------
    # Audio playback
    # ---------------------------------------------------------

    playback = AudioPlayback()

    # ---------------------------------------------------------
    # Microphone
    # ---------------------------------------------------------

    input_stream = sd.RawInputStream(
        samplerate=INPUT_SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        channels=CHANNELS,
        dtype=DTYPE,
        callback=audio_callback,
    )

    playback.start()
    input_stream.start()

    for number in range(3, 0, -1):
        print(number)
        await asyncio.sleep(1)

    print()
    print("🎤 Lyra is listening...")
    print("Speak naturally.")
    print("Try interrupting Lyra while it is speaking.")
    print()

    provider = GeminiLiveProvider()

    try:
        await provider.run_voice_session(
            audio_queue,
            playback,
        )

    except asyncio.CancelledError:
        pass

    finally:
        if input_stream.active:
            input_stream.stop()

        input_stream.close()

        await audio_queue.put(("STOP", None))

        playback.stop()

    print("\n✅ Lyra voice session ended.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ Lyra stopped.")