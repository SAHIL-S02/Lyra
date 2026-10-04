from __future__ import annotations


ALLOWED_CATEGORIES = {
    "fact",
    "preference",
    "profile",
    "event",
    "other",
}


KEY_ALIASES: dict[str, tuple[str, str]] = {
    "favorite_language": (
        "favorite_programming_language",
        "preference",
    ),
    "programming_language": (
        "favorite_programming_language",
        "preference",
    ),
    "preferred_language": (
        "favorite_programming_language",
        "preference",
    ),
    "my_name": (
        "user_name",
        "profile",
    ),
    "name": (
        "user_name",
        "profile",
    ),
}


CANONICAL_CATEGORIES: dict[str, str] = {
    "favorite_programming_language": "preference",
    "user_name": "profile",
}


def normalize_memory(
    key: str,
    category: str,
) -> tuple[str, str]:
    """Normalize memory keys and enforce canonical categories."""

    normalized_key = key.strip().lower()
    normalized_category = category.strip().lower()

    replacement = KEY_ALIASES.get(normalized_key)

    if replacement is not None:
        normalized_key, normalized_category = replacement

    canonical_category = CANONICAL_CATEGORIES.get(normalized_key)

    if canonical_category is not None:
        normalized_category = canonical_category

    if normalized_category not in ALLOWED_CATEGORIES:
        raise ValueError(
            f"Invalid memory category: {normalized_category}. "
            f"Allowed categories: {sorted(ALLOWED_CATEGORIES)}"
        )

    return normalized_key, normalized_category
