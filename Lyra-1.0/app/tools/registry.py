from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict


@dataclass
class ToolDefinition:
    name: str
    description: str
    handler: Callable[..., Any]
    parameters: Dict[str, Any]
    requires_confirmation: bool = False


class ToolRegistry:
    """
    Central registry for all Lyra tools.

    The registry stores:
    - tool name
    - description
    - handler
    - parameter schema
    - confirmation requirement
    """

    
    
    
    def __init__(self) -> None:
        self._tools: Dict[str, ToolDefinition] = {}

    def register(
        self,
        name: str,
        description: str,
        handler: Callable[..., Any],
        parameters: Dict[str, Any] | None = None,
        requires_confirmation: bool = False,
    ) -> None:
        if not name:
            raise ValueError("Tool name cannot be empty.")

        if name in self._tools:
            raise ValueError(f"Tool already registered: {name}")

        self._tools[name] = ToolDefinition(
            name=name,
            description=description,
            handler=handler,
            parameters=parameters or {},
            requires_confirmation=requires_confirmation,
        )

    def get(self, name: str) -> ToolDefinition:
        try:
            return self._tools[name]
        except KeyError:
            raise KeyError(f"Unknown tool: {name}")

    def exists(self, name: str) -> bool:
        return name in self._tools

    def all(self) -> Dict[str, ToolDefinition]:
        return self._tools.copy()

    def names(self) -> list[str]:
        return list(self._tools.keys())

    def clear(self) -> None:
        self._tools.clear()
    
    
    def gemini_declarations(self) -> list[dict[str, Any]]:
        """
        Return registered tools in the format expected by Gemini Live.
        """

        def normalize_schema(value: Any) -> Any:
            if isinstance(value, dict):
                result = {}

                for key, item in value.items():
                    if key == "type" and isinstance(item, str):
                        result[key] = item.upper()
                    else:
                        result[key] = normalize_schema(item)

                return result

            if isinstance(value, list):
                return [normalize_schema(item) for item in value]

            return value

        declarations = []

        for tool in self._tools.values():
            declarations.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": normalize_schema(tool.parameters),
                }
            )

        return declarations


# Global registry used by Lyra
tool_registry = ToolRegistry()