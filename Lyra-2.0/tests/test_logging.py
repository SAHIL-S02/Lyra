from app.core.logging import logger


def main() -> None:
    logger.info("Lyra logging system initialized.")
    logger.warning("This is a test warning.")
    logger.error("This is a test error.")

    print("\nLogging test completed.")


if __name__ == "__main__":
    main()
