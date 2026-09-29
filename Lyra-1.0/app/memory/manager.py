from __future__ import annotations

from datetime import datetime, timezone

from .database import MemoryDatabase


class MemoryManager:
    """
    High-level API for Lyra's long-term memory.

    Categories:
        fact
        preference
        event
        profile
        other

    Retention:
        permanent
        episodic
    """

    # Canonical keys for core Lyra identity.
    # This prevents Gemini from creating variants such as
    # creator_name, my_creator, or creator_full_name.
    KEY_ALIASES = {
        "creator_name": "creator",
        "creator_full_name": "creator",
        "my_creator": "creator",
        "assistant_creator": "creator",
        "lyra_creator": "creator",
        "version": "system_version",
        "lyra_version": "system_version",
    }

    VALID_CATEGORIES = {
        "fact",
        "preference",
        "event",
        "profile",
        "other",
    }

    VALID_RETENTION = {
        "permanent",
        "episodic",
    }

    def __init__(self, database: MemoryDatabase | None = None) -> None:
        self.db = database or MemoryDatabase()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def _normalize_key(cls, key: str) -> str:
        key = key.strip().lower()
        return cls.KEY_ALIASES.get(key, key)

    @staticmethod
    def _row_to_dict(row) -> dict:
        """
        Convert a tuple returned by MemoryDatabase.fetchall()
        into a normal dictionary.

        Column order:
            0 id
            1 key
            2 value
            3 category
            4 retention
            5 source
            6 created_at
            7 updated_at
            8 last_accessed_at
        """
        return {
            "id": row[0],
            "key": row[1],
            "value": row[2],
            "category": row[3],
            "retention": row[4],
            "source": row[5],
            "created_at": row[6],
            "updated_at": row[7],
            "last_accessed_at": row[8],
        }

    def remember(
        self,
        key: str,
        value: str,
        category: str = "fact",
        retention: str = "permanent",
        source: str = "voice",
    ) -> dict:
        """
        Create a memory if it does not exist.

        Update the existing memory when the same logical key/category
        already exists.

        Core identity aliases are normalized before database access.
        """

        key = self._normalize_key(key)
        value = value.strip()
        category = category.strip().lower()
        retention = retention.strip().lower()
        source = source.strip() or "voice"

        if not key:
            return {
                "success": False,
                "error": "Memory key cannot be empty.",
            }

        if not value:
            return {
                "success": False,
                "error": "Memory value cannot be empty.",
            }

        if category not in self.VALID_CATEGORIES:
            return {
                "success": False,
                "error": f"Invalid memory category: {category}",
            }

        if retention not in self.VALID_RETENTION:
            return {
                "success": False,
                "error": f"Invalid retention value: {retention}",
            }

        existing = self.db.fetchone(
            """
            SELECT id
            FROM memories
            WHERE key = ?
              AND category = ?
            LIMIT 1
            """,
            (key, category),
        )

        now = self._now()

        if existing:
            memory_id = existing["id"]

            self.db.execute(
                """
                UPDATE memories
                SET value = ?,
                    retention = ?,
                    source = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    value,
                    retention,
                    source,
                    now,
                    memory_id,
                ),
            )

            return {
                "success": True,
                "action": "updated",
                "memory": {
                    "id": memory_id,
                    "key": key,
                    "value": value,
                    "category": category,
                    "retention": retention,
                    "source": source,
                },
            }

        self.db.execute(
            """
            INSERT INTO memories (
                key,
                value,
                category,
                retention,
                source,
                created_at,
                updated_at,
                last_accessed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                key,
                value,
                category,
                retention,
                source,
                now,
                now,
                now,
            ),
        )

        # Read the inserted row back so the return shape is consistent.
        created = self.db.fetchone(
            """
            SELECT *
            FROM memories
            WHERE key = ?
              AND category = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (key, category),
        )

        return {
            "success": True,
            "action": "created",
            "memory": created or {
                "key": key,
                "value": value,
                "category": category,
                "retention": retention,
                "source": source,
            },
        }

    def recall(
        self,
        key: str,
        *,
        category: str | None = None,
    ) -> dict | None:
        key = self._normalize_key(key)

        if category:
            category = category.strip().lower()

            memory = self.db.fetchone(
                """
                SELECT *
                FROM memories
                WHERE key = ?
                  AND category = ?
                LIMIT 1
                """,
                (key, category),
            )
        else:
            memory = self.db.fetchone(
                """
                SELECT *
                FROM memories
                WHERE key = ?
                ORDER BY
                    CASE retention
                        WHEN 'permanent' THEN 0
                        ELSE 1
                    END,
                    updated_at DESC
                LIMIT 1
                """,
                (key,),
            )

        if memory:
            now = self._now()

            self.db.execute(
                """
                UPDATE memories
                SET last_accessed_at = ?
                WHERE id = ?
                """,
                (now, memory["id"]),
            )

            memory["last_accessed_at"] = now

        return memory

    def search(
        self,
        query: str,
        category: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        query = query.strip()

        if not query:
            return []

        try:
            limit = max(1, int(limit))
        except (TypeError, ValueError):
            limit = 10

        search_query = query.lower()

        sql = """
            SELECT
                id,
                key,
                value,
                category,
                retention,
                source,
                created_at,
                updated_at,
                last_accessed_at
            FROM memories
            WHERE
                (
                    LOWER(REPLACE(key, '_', ' ')) LIKE ?
                    OR LOWER(value) LIKE ?
                )
        """

        pattern = f"%{search_query}%"
        params: list = [pattern, pattern]

        if category:
            sql += " AND category = ?"
            params.append(category.strip().lower())

        sql += """
            ORDER BY
                CASE retention
                    WHEN 'permanent' THEN 0
                    ELSE 1
                END,
                updated_at DESC
            LIMIT ?
        """

        params.append(limit)

        rows = self.db.fetchall(sql, tuple(params))

        memories = [self._row_to_dict(row) for row in rows]

        # Mark returned memories as recently accessed.
        if memories:
            now = self._now()

            for memory in memories:
                self.db.execute(
                    """
                    UPDATE memories
                    SET last_accessed_at = ?
                    WHERE id = ?
                    """,
                    (now, memory["id"]),
                )
                memory["last_accessed_at"] = now

        return memories

    def forget(
        self,
        key: str,
        *,
        category: str | None = None,
    ) -> int:
        key = self._normalize_key(key)

        if category:
            category = category.strip().lower()

            result = self.db.fetchone(
                """
                SELECT COUNT(*) AS count
                FROM memories
                WHERE key = ?
                  AND category = ?
                """,
                (key, category),
            )

            count = result["count"]

            self.db.execute(
                """
                DELETE FROM memories
                WHERE key = ?
                  AND category = ?
                """,
                (key, category),
            )

            return count

        result = self.db.fetchone(
            """
            SELECT COUNT(*) AS count
            FROM memories
            WHERE key = ?
            """,
            (key,),
        )

        count = result["count"]

        self.db.execute(
            """
            DELETE FROM memories
            WHERE key = ?
            """,
            (key,),
        )

        return count

    def all_memories(
        self,
        *,
        category: str | None = None,
    ) -> list[dict]:
        if category:
            rows = self.db.fetchall(
                """
                SELECT
                    id,
                    key,
                    value,
                    category,
                    retention,
                    source,
                    created_at,
                    updated_at,
                    last_accessed_at
                FROM memories
                WHERE category = ?
                ORDER BY updated_at DESC
                """,
                (category.strip().lower(),),
            )
        else:
            rows = self.db.fetchall(
                """
                SELECT
                    id,
                    key,
                    value,
                    category,
                    retention,
                    source,
                    created_at,
                    updated_at,
                    last_accessed_at
                FROM memories
                ORDER BY updated_at DESC
                """
            )

        return [self._row_to_dict(row) for row in rows]

    def get_lyra_identity(self) -> dict[str, str]:
        """
        Load Lyra's persistent identity.

        Only canonical fact keys are accepted so unrelated profile
        or alias records cannot override core identity.
        """

        memories = self.all_memories(category="fact")

        identity: dict[str, str] = {}

        for memory in memories:
            key = self._normalize_key(memory["key"])
            value = memory["value"]

            if key in {"creator", "system_version"}:
                identity[key] = value

        return identity

    def update(
        self,
        key: str,
        value: str,
        category: str = "fact",
        retention: str | None = None,
        source: str | None = None,
    ) -> dict:
        """
        Explicitly update an existing memory.

        Unlike remember(), this never creates a new row.
        """

        key = self._normalize_key(key)
        value = value.strip()
        category = category.strip().lower()

        if not key:
            return {
                "success": False,
                "error": "Memory key cannot be empty.",
            }

        if not value:
            return {
                "success": False,
                "error": "Memory value cannot be empty.",
            }

        existing = self.db.fetchone(
            """
            SELECT *
            FROM memories
            WHERE key = ?
              AND category = ?
            LIMIT 1
            """,
            (key, category),
        )

        if not existing:
            return {
                "success": False,
                "error": f"No memory found for key '{key}'.",
            }

        now = self._now()

        new_retention = (
            retention.strip().lower()
            if retention is not None
            else existing["retention"]
        )

        new_source = (
            source.strip()
            if source is not None and source.strip()
            else existing["source"]
        )

        self.db.execute(
            """
            UPDATE memories
            SET value = ?,
                retention = ?,
                source = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                value,
                new_retention,
                new_source,
                now,
                existing["id"],
            ),
        )

        return {
            "success": True,
            "action": "updated",
            "memory": {
                "id": existing["id"],
                "key": key,
                "value": value,
                "category": category,
                "retention": new_retention,
                "source": new_source,
            },
        }
