from __future__ import annotations

import json
from typing import Any

from app.ai.base import AIProvider
from app.ai.models import ToolCall
from app.ai.prompts import LYRA_SYSTEM_PROMPT
from app.core.logging import logger
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry


class ToolCallingAgent:
    """Runs the AI + tool execution loop."""

    MAX_TOOL_ROUNDS = 5

    def __init__(
        self,
        provider: AIProvider,
        registry: ToolRegistry,
        executor: ToolExecutor,
    ) -> None:
        self.provider = provider
        self.registry = registry
        self.executor = executor

    @staticmethod
    def _tool_result_content(result: Any) -> str:
        """Convert a tool result into model-readable JSON."""

        if hasattr(result, "success"):
            payload = {
                "success": result.success,
                "data": result.data,
                "error": result.error,
            }
        else:
            payload = result

        return json.dumps(
            payload,
            ensure_ascii=False,
            default=str,
        )

    @staticmethod
    def _assistant_tool_calls_message(
        content: str,
        tool_calls: list[ToolCall],
    ) -> dict[str, Any]:
        """Build the assistant message containing requested tools."""

        return {
            "role": "assistant",
            "content": content or "",
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.name,
                        "arguments": call.arguments,
                    },
                }
                for call in tool_calls
            ],
        }

    def _handle_deterministic_tool(
        self,
        user_text: str,
        required_tool: str,
    ) -> str:
        """
        Execute deterministic tools before asking the LLM.

        The LLM must never be allowed to estimate values such as
        the current time or current system information.
        """

        logger.info(
            "Preflight deterministic tool selected: %s",
            required_tool,
        )

        result = self.executor.execute(
            name=required_tool,
            arguments={},
        )

        if not result.success:
            raise RuntimeError(
                f"Tool '{required_tool}' failed: "
                f"{result.error}"
            )

        logger.info(
            "Deterministic tool completed: %s | success=%s",
            required_tool,
            result.success,
        )

        data = result.data

        # ---------------------------------------------------------
        # Current time/date
        # ---------------------------------------------------------
        if required_tool == "get_current_time":
            if not isinstance(data, dict):
                return self._tool_result_content(result)

            time_value = data.get("time")
            date_value = data.get("date")
            timezone_value = data.get("timezone")

            if time_value and date_value:
                if timezone_value:
                    return (
                        f"The current local date is {date_value}, "
                        f"and the current local time is "
                        f"{time_value} ({timezone_value})."
                    )

                return (
                    f"The current local date is {date_value}, "
                    f"and the current local time is {time_value}."
                )

            if time_value:
                return (
                    f"The current local time is {time_value}."
                )

            if date_value:
                return (
                    f"The current local date is {date_value}."
                )

        # ---------------------------------------------------------
        # System information
        # ---------------------------------------------------------
        if required_tool == "get_system_info":
            if not isinstance(data, dict):
                return self._tool_result_content(result)

            parts: list[str] = []

            system = data.get("system")
            release = data.get("release")
            version = data.get("version")
            machine = data.get("machine")
            processor = data.get("processor")
            python_version = data.get("python_version")

            if system:
                parts.append(f"OS: {system}")

            if release:
                parts.append(f"Release: {release}")

            if version:
                parts.append(f"Version: {version}")

            if machine:
                parts.append(f"Architecture: {machine}")

            if processor:
                parts.append(f"Processor: {processor}")

            if python_version:
                parts.append(
                    f"Python: {python_version}"
                )

            if parts:
                return " | ".join(parts)

        # ---------------------------------------------------------
        # Fallback for deterministic tools.
        # ---------------------------------------------------------
        return self._tool_result_content(result)

    def respond(self, user_text: str) -> str:
        """Process a user request, including deterministic tools."""

        user_text = user_text.strip()

        if not user_text:
            raise ValueError(
                "user_text cannot be empty."
            )

        # ---------------------------------------------------------
        # Deterministic tool preflight.
        #
        # Do this BEFORE giving the request to Qwen's tool loop.
        # ---------------------------------------------------------
        from app.ai.tool_policy import detect_required_tool

        required_tool = detect_required_tool(
            user_text
        )

        if required_tool is not None:
            return self._handle_deterministic_tool(
                user_text=user_text,
                required_tool=required_tool,
            )

        # ---------------------------------------------------------
        # Normal AI + tool-calling flow.
        # ---------------------------------------------------------
        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": LYRA_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_text,
            },
        ]

        tools = self.registry.definitions()

        for round_number in range(
            1,
            self.MAX_TOOL_ROUNDS + 1,
        ):
            logger.info(
                "AI tool loop round %d",
                round_number,
            )

            response = self.provider.chat(
                messages=messages,
                tools=tools,
            )

            # -----------------------------------------------------
            # Final answer.
            # -----------------------------------------------------
            if not response.tool_calls:
                if not response.content:
                    raise RuntimeError(
                        "AI returned neither content "
                        "nor a tool call."
                    )

                return response.content

            # -----------------------------------------------------
            # Preserve the assistant's tool-call message.
            # -----------------------------------------------------
            messages.append(
                self._assistant_tool_calls_message(
                    content=response.content,
                    tool_calls=response.tool_calls,
                )
            )

            # -----------------------------------------------------
            # Execute requested tools.
            # -----------------------------------------------------
            for call in response.tool_calls:
                logger.info(
                    "AI requested tool: %s",
                    call.name,
                )

                logger.info(
                    "Tool arguments: %s",
                    call.arguments,
                )

                result = self.executor.execute(
                    name=call.name,
                    arguments=call.arguments,
                )

                logger.info(
                    "Tool completed: %s | success=%s",
                    call.name,
                    result.success,
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_name": call.name,
                        "content": self._tool_result_content(
                            result
                        ),
                    }
                )

        raise RuntimeError(
            "Maximum AI tool-call rounds exceeded."
        )