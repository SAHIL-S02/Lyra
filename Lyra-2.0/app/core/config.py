from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    """Central configuration for Lyra 2.0."""

    # Application
    app_name: str = "Lyra"
    version: str = "2.0.0"

    # Local LLM
    ollama_base_url: str = "http://localhost:11434"
    local_model: str = "qwen3:1.7b"

    # Web search
    web_search_url: str = "https://html.duckduckgo.com/html/"
    web_user_agent: str = (
        "Lyra/2.0 (personal AI assistant)"
    )

    # Voice
    sample_rate: int = 16000
    channels: int = 1

    # Paths
    data_dir: Path = PROJECT_ROOT / "data"
    models_dir: Path = PROJECT_ROOT / "models"

    @property
    def wakeword_dir(self) -> Path:
        return self.models_dir / "wakeword"

    @property
    def stt_dir(self) -> Path:
        return self.models_dir / "stt"

    @property
    def tts_dir(self) -> Path:
        return self.models_dir / "tts"

    @classmethod
    def from_environment(cls) -> "Settings":
        """Create settings using environment variables when provided."""

        return cls(
            app_name=os.getenv("LYRA_APP_NAME", "Lyra"),
            version=os.getenv("LYRA_VERSION", "2.0.0"),
            ollama_base_url=os.getenv(
                "LYRA_OLLAMA_URL",
                "http://localhost:11434",
            ),
            local_model=os.getenv(
                "LYRA_LOCAL_MODEL",
                "qwen3:1.7b",
            ),
            web_search_url=os.getenv(
                "LYRA_WEB_SEARCH_URL",
                "https://html.duckduckgo.com/html/",
            ),
            web_user_agent=os.getenv(
                "LYRA_WEB_USER_AGENT",
                "Lyra/2.0 (personal AI assistant)",
            ),
            sample_rate=int(
                os.getenv("LYRA_SAMPLE_RATE", "16000")
            ),
            channels=int(
                os.getenv("LYRA_CHANNELS", "1")
            ),
        )


settings = Settings.from_environment()
