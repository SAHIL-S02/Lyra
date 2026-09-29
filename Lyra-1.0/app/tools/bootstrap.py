from .registry import tool_registry
from .memory_tools import register_memory_tools
from .system_tools import register_system_tools


def register_all_tools() -> None:
    """
    Register every Lyra tool group.

    Add future tool registration functions here:
    - memory
    - system
    - web
    - spotify
    - smart home
    """

    if not tool_registry.exists("remember_memory"):
        register_memory_tools()

    if not tool_registry.exists("get_current_time"):
        register_system_tools()