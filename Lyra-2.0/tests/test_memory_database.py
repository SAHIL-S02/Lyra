from app.memory.database import MemoryDatabase


def main() -> None:
    database = MemoryDatabase()

    print("=== Lyra Memory Database ===")
    print("Database:", database.db_path)
    print("Memories:", database.count())

    print("\nMemory database test passed.")


if __name__ == "__main__":
    main()
