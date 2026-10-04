from __future__ import annotations

import sqlite3
from pathlib import Path

from app.core.config import settings


class MemoryDatabase:
    """SQLite database for Lyra's persistent memory."""

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or (
            Path(settings.data_dir) / "lyra_memory.db"
        )

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)

        connection.row_factory = sqlite3.Row

        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'fact',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                    UNIQUE(key, category)
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_memories_key
                ON memories(key)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_memories_category
                ON memories(category)
                """
            )

            connection.commit()

    def count(self) -> int:
        """Return the number of stored memories."""

        with self._connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM memories"
            ).fetchone()

        return int(row["count"])
