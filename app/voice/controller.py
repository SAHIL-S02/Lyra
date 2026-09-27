from __future__ import annotations

import asyncio
import threading
import time
from contextlib import suppress

import sounddevice as sd

from app.ai.gemini_live import GeminiLiveProvider
from app.core.state import LyraState
from app.voice.audio_output import AudioPlayback
from app.voice.vad import ClientVAD
from app.voice.wake_word import WakeWordDetector


class LyraVoiceController:
    """Main voice controller for Lyra."""

    SAMPLE_RATE = 16_000
    BLOCK_SIZE = 320  # 20 ms

    # Put Lyra to sleep after this much time without
    # detecting user speech.
    IDLE_TIMEOUT = 30.0

    def __init__(self) -> None:
        self.state = LyraState.SLEEPING

        self.wake_word = WakeWordDetector()
        self.gemini = GeminiLiveProvider()

    async def run(self) -> None:
        print("=" * 60)
        print("                         LYRA")
        print("=" * 60)
        print("Wake word: Hey Lyra")
        print("Inactivity timeout: 30 seconds")
        print("Press Ctrl+C to stop")
        print("=" * 60)

        try:
            while True:
                # --------------------------------------------------
                # SLEEP
                # --------------------------------------------------

                self.state = LyraState.SLEEPING

                print("\n💤 Lyra sleeping...")

                await asyncio.to_thread(
                    self.wake_word.listen
                )

                # --------------------------------------------------
                # WAKE DETECTED
                # --------------------------------------------------

                self.state = LyraState.WAKE_DETECTED

                print("\n🔥 Hey Lyra detected!")

                # --------------------------------------------------
                # ACTIVE SESSION
                # --------------------------------------------------

                self.state = LyraState.LISTENING

                await self._run_active_session()

        except KeyboardInterrupt:
            print("\n\n🛑 Lyra stopped.")

        finally:
            self.state = LyraState.IDLE

    async def _run_active_session(self) -> None:
        """
        Run one Gemini Live conversation.

        Session ends when:
        - inactivity timeout is reached
        - Gemini Live ends
        - an error occurs
        - Lyra is interrupted/stopped
        """

        audio_queue: asyncio.Queue = asyncio.Queue()

        # Async event used by Gemini Live
        # to terminate the session.
        stop_event = asyncio.Event()

        # Thread event used by sounddevice capture.
        capture_stop = threading.Event()

        # Shared activity timestamp.
        # The microphone thread updates this whenever
        # local VAD detects user speech.
        activity = {
            "last_speech": time.monotonic()
        }

        playback = AudioPlayback()

        capture_task: asyncio.Task | None = None
        idle_task: asyncio.Task | None = None

        try:
            playback.start()

            loop = asyncio.get_running_loop()

            # --------------------------------------------------
            # MICROPHONE
            # --------------------------------------------------

            capture_task = asyncio.create_task(
                asyncio.to_thread(
                    self._capture_microphone,
                    audio_queue,
                    capture_stop,
                    loop,
                    activity,
                )
            )

            print("\n🚀 Starting Gemini Live...")
            print("🎙️ Gemini Live microphone active.")
            print(
                f"⏱️ Sleep after {self.IDLE_TIMEOUT:.0f}s "
                "of no user speech."
            )

            # --------------------------------------------------
            # GEMINI
            # --------------------------------------------------

            gemini_task = asyncio.create_task(
                self.gemini.run_voice_session(
                    audio_queue=audio_queue,
                    playback=playback,
                    stop_event=stop_event,
                )
            )

            # --------------------------------------------------
            # INACTIVITY WATCHER
            # --------------------------------------------------

            idle_task = asyncio.create_task(
                self._watch_inactivity(
                    stop_event,
                    activity,
                )
            )

            # Wait until Gemini ends OR inactivity timeout occurs.
            done, pending = await asyncio.wait(
                {
                    gemini_task,
                    idle_task,
                },
                return_when=asyncio.FIRST_COMPLETED,
            )

            # If inactivity watcher finished first,
            # explicitly stop Gemini.
            if idle_task in done:
                stop_event.set()

            # If Gemini finished first, stop inactivity watcher.
            if gemini_task in done:
                stop_event.set()

            for task in pending:
                task.cancel()

            await asyncio.gather(
                *pending,
                return_exceptions=True,
            )

        except asyncio.CancelledError:
            stop_event.set()
            raise

        except Exception as exc:
            print(
                f"\n❌ Voice session error: "
                f"{type(exc).__name__}: {exc}"
            )

        finally:
            # Stop both microphone and Gemini.
            stop_event.set()
            capture_stop.set()

            # Tell Gemini sender to stop if it is still waiting
            # on the queue.
            with suppress(Exception):
                audio_queue.put_nowait(
                    ("STOP", b"")
                )

            # Stop the microphone thread.
            if capture_task is not None:
                with suppress(Exception):
                    await capture_task

            playback.clear()

            with suppress(Exception):
                playback.stop()

            print(
                "\n💤 Returning to wake-word mode..."
            )

    async def _watch_inactivity(
        self,
        stop_event: asyncio.Event,
        activity: dict,
    ) -> None:
        """
        Put Lyra to sleep when no user speech is detected
        for IDLE_TIMEOUT seconds.
        """

        while not stop_event.is_set():

            elapsed = (
                time.monotonic()
                - activity["last_speech"]
            )

            if elapsed >= self.IDLE_TIMEOUT:

                print(
                    "\n💤 No user speech for "
                    f"{self.IDLE_TIMEOUT:.0f} seconds."
                )

                print(
                    "😴 Putting Lyra to sleep..."
                )

                stop_event.set()
                return

            await asyncio.sleep(0.5)

    def _capture_microphone(
        self,
        audio_queue: asyncio.Queue,
        stop_event: threading.Event,
        loop: asyncio.AbstractEventLoop,
        activity: dict,
    ) -> None:
        """
        Capture 16 kHz mono PCM and send it to Gemini Live.

        sounddevice executes the callback on its own thread,
        so asyncio queue operations are scheduled safely
        onto the event loop.
        """

        vad = ClientVAD(
            aggressiveness=2,
            silence_ms=500,
        )

        def push_audio(data: bytes) -> None:
            if stop_event.is_set():
                return

            loop.call_soon_threadsafe(
                audio_queue.put_nowait,
                ("AUDIO", data),
            )

        def push_end_of_turn() -> None:
            if stop_event.is_set():
                return

            loop.call_soon_threadsafe(
                audio_queue.put_nowait,
                ("END_OF_TURN", b""),
            )

        def callback(
            indata,
            frames,
            time_info,
            status,
        ) -> None:

            if status:
                print(
                    f"\n🎙️ Microphone status: {status}"
                )

            data = bytes(indata)

            try:
                is_speech, _, speech_ended = (
                    vad.process(data)
                )

            except ValueError as exc:
                print(
                    f"\n❌ VAD error: {exc}"
                )
                return

            # ----------------------------------------------
            # USER ACTIVITY
            # ----------------------------------------------

            if is_speech:
                activity["last_speech"] = (
                    time.monotonic()
                )

            # ----------------------------------------------
            # SEND AUDIO TO GEMINI
            # ----------------------------------------------

            push_audio(data)

            # ----------------------------------------------
            # END OF USER UTTERANCE
            # ----------------------------------------------

            if speech_ended:
                push_end_of_turn()

        try:
            with sd.RawInputStream(
                samplerate=self.SAMPLE_RATE,
                blocksize=self.BLOCK_SIZE,
                channels=1,
                dtype="int16",
                callback=callback,
            ):

                while not stop_event.is_set():
                    time.sleep(0.02)

        except Exception as exc:

            print(
                f"\n❌ Microphone error: "
                f"{type(exc).__name__}: {exc}"
            )

            loop.call_soon_threadsafe(
                audio_queue.put_nowait,
                ("STOP", b""),
            )