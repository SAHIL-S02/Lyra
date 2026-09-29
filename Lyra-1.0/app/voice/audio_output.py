from __future__ import annotations

import threading

import numpy as np
import sounddevice as sd


class AudioPlayback:
    """
    Low-latency audio playback buffer.

    Gemini sends audio in chunks.
    We queue those chunks and allow the queue
    to be cleared immediately when Lyra is interrupted.
    """

    SAMPLE_RATE = 24_000
    CHANNELS = 1
    DTYPE = np.int16

    def __init__(self, block_size: int = 480) -> None:
        """
        960 samples = 40 ms at 24 kHz.

        Small blocks help make interruption responsive.
        """

        self.block_size = block_size

        self._buffer = bytearray()
        self._lock = threading.Lock()

        self._stream = sd.RawOutputStream(
            samplerate=self.SAMPLE_RATE,
            blocksize=self.block_size,
            channels=self.CHANNELS,
            dtype="int16",
            callback=self._callback,
        )

    def start(self) -> None:
        self._stream.start()

    def stop(self) -> None:
        if self._stream.active:
            self._stream.stop()

        self._stream.close()

    def add(self, audio_data: bytes) -> None:
        if not audio_data:
            return

        with self._lock:
            self._buffer.extend(audio_data)

    def clear(self) -> None:
        """
        Immediately discard all queued response audio.
        """

        with self._lock:
            self._buffer.clear()

    def _callback(self, outdata, frames, time_info, status) -> None:
        if status:
            print(f"\nAudio output status: {status}")

        required_bytes = frames * 2  # int16 = 2 bytes

        with self._lock:

            available = min(
                required_bytes,
                len(self._buffer),
            )

            if available > 0:
                outdata[:available] = self._buffer[:available]
                del self._buffer[:available]

            if available < required_bytes:
                outdata[available:required_bytes] = b"\x00" * (
                    required_bytes - available
                )