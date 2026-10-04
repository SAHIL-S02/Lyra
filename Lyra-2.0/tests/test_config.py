from app.core.config import settings


def main() -> None:
    print("=== Lyra Configuration ===")
    print("App Name       :", settings.app_name)
    print("Version        :", settings.version)
    print("Ollama URL     :", settings.ollama_base_url)
    print("Local Model    :", settings.local_model)
    print("Sample Rate    :", settings.sample_rate)
    print("Channels       :", settings.channels)
    print("Project Root   :", settings.data_dir.parent)
    print("Data Directory :", settings.data_dir)
    print("Models         :", settings.models_dir)
    print("Wake Word      :", settings.wakeword_dir)
    print("STT            :", settings.stt_dir)
    print("TTS            :", settings.tts_dir)


if __name__ == "__main__":
    main()
