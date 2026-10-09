import os
import sys
from pathlib import Path

from app.voice.stt import STTProvider


# Keep Windows DLL directory handles alive for the process lifetime.
_DLL_DIRECTORY_HANDLES = []


def _configure_cuda_dlls() -> None:
    """Make pip-installed NVIDIA runtime DLLs discoverable on Windows."""
    if sys.platform != "win32":
        return

    nvidia_dir = Path(sys.prefix) / "Lib" / "site-packages" / "nvidia"

    directories = [
        nvidia_dir / "cublas" / "bin",
        nvidia_dir / "cudnn" / "bin",
    ]

    existing_paths = os.environ.get("PATH", "").split(os.pathsep)

    for directory in directories:
        if not directory.is_dir():
            continue

        directory_str = str(directory)

        if not any(
            path.casefold() == directory_str.casefold()
            for path in existing_paths
            if path
        ):
            existing_paths.insert(0, directory_str)

        if hasattr(os, "add_dll_directory"):
            try:
                handle = os.add_dll_directory(directory_str)
                _DLL_DIRECTORY_HANDLES.append(handle)
            except OSError:
                pass

    os.environ["PATH"] = os.pathsep.join(existing_paths)


# Configure DLL discovery before importing faster-whisper/CTranslate2.
_configure_cuda_dlls()

from faster_whisper import WhisperModel


class FasterWhisperProvider(STTProvider):
    """faster-whisper implementation behind Lyra's STT abstraction."""

    def __init__(
        self,
        model_name: str = "large-v3-turbo",
        device: str = "cuda",
        compute_type: str = "float16",
        language: str | None = "en",
        download_root: str | None = None,
    ) -> None:
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self.language = language
        self.download_root = download_root

        self._model = WhisperModel(
            model_name,
            device=device,
            compute_type=compute_type,
            download_root=download_root,
        )

    def transcribe(self, audio_path: str) -> str:
        path = Path(audio_path)

        if not path.is_file():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if self._model is None:
            raise RuntimeError("STT provider has been closed.")

        segments, _ = self._model.transcribe(
            str(path),
            language=self.language,
            beam_size=5,
            vad_filter=True,
        )

        return " ".join(
            segment.text.strip()
            for segment in segments
            if segment.text.strip()
        ).strip()

    def health_check(self) -> bool:
        return self._model is not None

    def close(self) -> None:
        self._model = None
