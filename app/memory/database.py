from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


# ============================================================
# Project structure
#
# Lyra/
# ├── app/
# │   └── memory/
# │       └── database.py
# └── data/
#     └── lyra_memory.db
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

DB_PATH = DATA_DIR / "lyra_memory.db"


class MemoryDatabase:
    """
    SQLite database wrapper for Lyra's long-term memory.
    """

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize()

    # --------------------------------------------------------
    # Connection
    # --------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,
        )

    # --------------------------------------------------------
    # Initialize database
    # --------------------------------------------------------

    def _initialize(self) -> None:
        with self._connect() as conn:

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    key TEXT NOT NULL,
                    value TEXT NOT NULL,

                    category TEXT NOT NULL
                        DEFAULT 'other',

                    retention TEXT NOT NULL
                        DEFAULT 'permanent',

                    source TEXT,

                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_accessed_at TEXT,

                    UNIQUE(key, category)
                )
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_memories_key
                ON memories(key)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_memories_category
                ON memories(category)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_memories_retention
                ON memories(retention)
                """
            )

            conn.commit()

    # --------------------------------------------------------
    # Execute
    # --------------------------------------------------------

    def execute(
        self,
        query: str,
        params: tuple[Any, ...] = (),
    ) -> sqlite3.Cursor:

        with self._connect() as conn:
            cursor = conn.execute(query, params)
            conn.commit()

            return cursor

    # --------------------------------------------------------
    # Fetch one row as a MUTABLE dictionary
    # --------------------------------------------------------

    def fetchone(
        self,
        query: str,
        params: tuple[Any, ...] = (),
    ) -> dict[str, Any] | None:

        with self._connect() as conn:

            cursor = conn.execute(
                query,
                params,
            )

            row = cursor.fetchone()

            if row is None:
                return None

            columns = [
                column[0]
                for column in cursor.description
            ]

            return dict(
                zip(columns, row)
            )

    # --------------------------------------------------------
    # Fetch all rows as MUTABLE dictionaries
    # --------------------------------------------------------

    def fetchall(
    self,
    query: str,
    params: tuple[Any, ...] = (),
):
        with self._connect() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()
    # --------------------------------------------------------
    # Database path
    # --------------------------------------------------------

    @property
    def path(self) -> str:
        return str(self.db_path)