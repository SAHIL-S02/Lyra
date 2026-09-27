from __future__ import annotations

import platform
import socket
import sys
from datetime import datetime

from .registry import tool_registry


def get_current_time() -> dict:
    """
    Return the current local date and time.
    """

    now = datetime.now().astimezone()

    return {
        "success": True,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%I:%M:%S %p"),
        "timezone": now.tzname() or "unknown",
        "iso": now.isoformat(),
    }


def get_system_info() -> dict:
    """
    Return basic information about the machine running Lyra.
    """

    return {
        "success": True,
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": sys.version.split()[0],
        "processor": platform.processor() or "unknown",
    }


def register_system_tools() -> None:
    """
    Register Lyra's system-related tools.
    """

    tool_registry.register(
        name="get_current_time",
        description=(
            "Get the current local date, time, and timezone "
            "of the computer running Lyra."
        ),
        handler=get_current_time,
        parameters={
            "type": "object",
            "properties": {},
        },
    )

    tool_registry.register(
        name="get_system_info",
        description=(
            "Get basic information about the computer running Lyra, "
            "including operating system, architecture, Python version, "
            "hostname, and processor."
        ),
        handler=get_system_info,
        parameters={
            "type": "object",
            "properties": {},
        },
    )