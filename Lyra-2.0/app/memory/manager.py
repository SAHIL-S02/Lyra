from __future__ import annotations
from app.memory.policy import normalize_memory
from datetime import datetime, timezone
from typing import Any

from app.core.logging import logger
from app.memory.database import MemoryDatabase


class MemoryManager:
    """High-level interface for Lyra's persistent memory."""

    def __init__(self, database: MemoryDatabase | None = None) -> None:
        self.database = database or MemoryDatabase()

        logger.info(
            "Memory manager initialized: %s",
            self.database.db_path,
        )

    @staticmethod
    def _timestamp() -> str:
        """Return the current UTC timestamp."""

        return datetime.now(timezone.utc).isoformat()

    def remember(
        self,
        key: str,
        value: str,
        category: str = "fact",
    ) -> None:
        """Store or replace a memory."""

        key, category = normalize_memory(key, category)
        value = value.strip()

        if not key:
            raise ValueError("Memory key cannot be empty.")

        if not value:
            raise ValueError("Memory value cannot be empty.")

        if not category:
            raise ValueError("Memory category cannot be empty.")

        timestamp = self._timestamp()

        with self.database._connect() as connection:
            connection.execute(
                """
                INSERT INTO memories (
                    key,
                    value,
                    category,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?)

                ON CONFLICT(key, category)
                DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
                """,
                (
                    key,
                    value,
                    category,
                    timestamp,
                    timestamp,
                ),
            )

            connection.commit()

        logger.info(
            "Memory stored: %s [%s]",
            key,
            category,
        )

    def get(
        self,
        key: str,
        category: str = "fact",
    ) -> dict[str, Any] | None:
        """Retrieve one memory."""

        key, category = normalize_memory(key, category)

        with self.database._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    key,
                    value,
                    category,
                    created_at,
                    updated_at
                FROM memories
                WHERE key = ?
                  AND category = ?
                """,
                (key, category),
            ).fetchone()

        if row is None:
            return None

        return dict(row)

    def search(
    self,
    query: str,
    category: str | None = None,
) -> list[dict[str, Any]]:
        """Search memories using flexible word matching."""

        import re

        query = query.strip()

        if not query:
            return []

        # Convert natural-language queries into useful search terms.
        terms = [
            term
            for term in re.findall(r"[A-Za-z0-9_]+", query.lower())
            if len(term) >= 3
        ]

        if not terms:
            return []

        conditions: list[str] = []
        parameters: list[str] = []

        for term in terms:
            pattern = f"%{term}%"

            conditions.append(
                """
                (
                    LOWER(key) LIKE ?
                    OR LOWER(REPLACE(key, '_', ' ')) LIKE ?
                    OR LOWER(value) LIKE ?
                )
                """
            )

            parameters.extend(
                [
                    pattern,
                    pattern,
                    pattern,
                ]
            )

        where_clause = " OR ".join(conditions)

        with self.database._connect() as connection:
            if category is None:
                rows = connection.execute(
                    f"""
                    SELECT
                        id,
                        key,
                        value,
                        category,
                        created_at,
                        updated_at
                    FROM memories
                    WHERE {where_clause}
                    ORDER BY updated_at DESC
                    """,
                    parameters,
                ).fetchall()

            else:
                rows = connection.execute(
                    f"""
                    SELECT
                        id,
                        key,
                        value,
                        category,
                        created_at,
                        updated_at
                    FROM memories
                    WHERE category = ?
                    AND ({where_clause})
                    ORDER BY updated_at DESC
                    """,
                    [category, *parameters],
                ).fetchall()

        return [dict(row) for row in rows]

    def update(
        self,
        key: str,
        value: str,
        category: str = "fact",
    ) -> bool:
        """Update an existing memory.

        Returns:
            True if a memory was updated, otherwise False.
        """

        key, category = normalize_memory(key, category)

        if not key or not value or not category:
            raise ValueError(
                "Key, value, and category cannot be empty."
            )

        timestamp = self._timestamp()

        with self.database._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE memories
                SET
                    value = ?,
                    updated_at = ?
                WHERE key = ?
                  AND category = ?
                """,
                (
                    value,
                    timestamp,
                    key,
                    category,
                ),
            )

            connection.commit()

        updated = cursor.rowcount > 0

        if updated:
            logger.info(
                "Memory updated: %s [%s]",
                key,
                category,
            )

        return updated

    def forget(
        self,
        key: str,
        category: str = "fact",
    ) -> bool:
        """Delete a memory.

        Returns:
            True if a memory was deleted, otherwise False.
        """

        key, category = normalize_memory(key, category)

        with self.database._connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM memories
                WHERE key = ?
                  AND category = ?
                """,
                (key, category),
            )

            connection.commit()

        deleted = cursor.rowcount > 0

        if deleted:
            logger.info(
                "Memory forgotten: %s [%s]",
                key,
                category,
            )

        return deleted

    def count(self) -> int:
        """Return the total number of memories."""

        return self.database.count()
