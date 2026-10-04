from __future__ import annotations

from app.memory.manager import MemoryManager
from app.tools.executor import ToolExecutor
from app.tools.memory_tools import create_memory_tools
from app.tools.registry import ToolRegistry
from app.tools.system_tools import create_system_tools
from app.tools.web_tools import create_web_tools
from app.tools.web_fetch_tools import create_web_fetch_tools


def create_tool_system(
    memory: MemoryManager | None = None,
) -> tuple[ToolRegistry, ToolExecutor]:
    """Create and initialize Lyra's complete tool system."""

    memory = memory or MemoryManager()

    registry = ToolRegistry()

    for tool in create_memory_tools(memory):
        registry.register(tool)

    for tool in create_system_tools():
        registry.register(tool)

    for tool in create_web_tools():
        registry.register(tool)

    for tool in create_web_fetch_tools():
        registry.register(tool)

    executor = ToolExecutor(registry)

    return registry, executor
