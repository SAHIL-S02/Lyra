from __future__ import annotations

from typing import Any

from app.core.logging import logger
from app.tools.base import ToolResult
from app.tools.registry import ToolRegistry


class ToolExecutor:
    """Executes tools registered in the ToolRegistry."""

    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

        logger.info("Tool executor initialized.")

    def execute(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
    ) -> ToolResult:
        """Execute a registered tool."""

        arguments = arguments or {}

        tool = self.registry.get(name)

        if tool is None:
            logger.warning("Unknown tool requested: %s", name)

            return ToolResult(
                success=False,
                error=f"Unknown tool: {name}",
            )

        try:
            logger.info(
                "Executing tool: %s",
                name,
            )

            result = tool.execute(arguments)

            if not isinstance(result, ToolResult):
                return ToolResult(
                    success=False,
                    error=(
                        f"Tool '{name}' returned an invalid result."
                    ),
                )

            return result

        except Exception as exc:
            logger.exception(
                "Tool execution failed: %s",
                name,
            )

            return ToolResult(
                success=False,
                error=str(exc),
            )
