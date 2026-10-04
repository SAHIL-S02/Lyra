from __future__ import annotations

import platform
import time
from datetime import datetime
from typing import Any

from app.tools.base import Tool, ToolResult


class GetCurrentTimeTool(Tool):
    name = "get_current_time"
    description = (
        "Get the current local date and time from the computer running Lyra."
    )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
        }

    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        now = datetime.now().astimezone()

        return ToolResult(
            success=True,
            data={
                "iso": now.isoformat(),
                "date": now.strftime("%A, %d %B %Y"),
                "time": now.strftime("%I:%M:%S %p"),
                "timezone": now.tzname(),
                "formatted": now.strftime(
                    "%A, %d %B %Y at %I:%M:%S %p %Z"
                ),
                "unix_timestamp": int(time.time()),
            },
        )


class GetSystemInfoTool(Tool):
    name = "get_system_info"
    description = (
        "Get basic information about the operating system and machine."
    )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
        }

    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
            },
        )


def create_system_tools() -> list[Tool]:
    """Create Lyra's built-in system tools."""

    return [
        GetCurrentTimeTool(),
        GetSystemInfoTool(),
    ]
