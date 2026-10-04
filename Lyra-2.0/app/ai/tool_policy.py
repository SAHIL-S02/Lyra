from __future__ import annotations

import re


def detect_required_tool(user_text: str) -> str | None:
    """Detect requests where a specific authoritative tool is required."""

    text = user_text.strip().lower()

    # Current time
    time_patterns = [
        r"\bwhat(?:'s| is) the time\b",
        r"\bwhat time is it\b",
        r"\bcurrent time\b",
        r"\btime right now\b",
        r"\btime now\b",
    ]

    if any(re.search(pattern, text) for pattern in time_patterns):
        return "get_current_time"

    # Basic machine/system information
    system_patterns = [
        r"\bsystem information\b",
        r"\bsystem info\b",
        r"\bcomputer information\b",
        r"\babout this computer\b",
        r"\bwhat operating system\b",
        r"\bwhich operating system\b",
    ]

    if any(re.search(pattern, text) for pattern in system_patterns):
        return "get_system_info"

    return None
