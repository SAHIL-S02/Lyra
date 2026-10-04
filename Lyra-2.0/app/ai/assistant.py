from __future__ import annotations

import json
from typing import Any

from app.ai.base import AIProvider
from app.ai.context import ContextBuilder
from app.ai.models import AIResponse, ToolCall
from app.ai.router import AIRouter, RouteMode
from app.ai.web_guard import validate_web_answer
from app.ai.web_research import WebResearchService
from app.core.logging import logger
from app.memory.context import MemoryContext
from app.memory.manager import MemoryManager
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry


class AssistantEngine:
    """Main intelligence engine for Lyra."""

    MAX_MESSAGES = 20
    MAX_TOOL_ROUNDS = 5

    def __init__(
        self,
        provider: AIProvider,
        registry: ToolRegistry,
        executor: ToolExecutor,
        memory: MemoryManager | None = None,
    ) -> None:
        self.provider = provider
        self.registry = registry
        self.executor = executor

        self.memory = memory or MemoryManager()
        self.memory_context = MemoryContext(self.memory)

        self.context_builder = ContextBuilder(
            self.memory_context
        )

        self.web_research = WebResearchService(
            executor=self.executor
        )

        self.router = AIRouter()

        self._messages: list[dict[str, Any]] = []

        logger.info(
            "Assistant engine initialized."
        )

    @property
    def messages(self) -> list[dict[str, Any]]:
        """Return a copy of conversation history."""

        return [
            dict(message)
            for message in self._messages
        ]

    def clear(self) -> None:
        """Clear the current conversation."""

        self._messages.clear()

        logger.info(
            "Assistant conversation cleared."
        )

    def _trim_history(self) -> None:
        """Keep only the most recent conversation messages."""

        if len(self._messages) > self.MAX_MESSAGES:
            self._messages = self._messages[
                -self.MAX_MESSAGES:
            ]

    @staticmethod
    def _tool_result_content(
        result: Any,
    ) -> str:
        """Serialize a tool result for the model."""

        return json.dumps(
            {
                "success": result.success,
                "data": result.data,
                "error": result.error,
            },
            ensure_ascii=False,
            default=str,
        )

    @staticmethod
    def _assistant_tool_call_message(
        content: str,
        tool_calls: list[ToolCall],
    ) -> dict[str, Any]:
        """
        Create an Ollama-compatible assistant message
        containing tool calls.
        """

        return {
            "role": "assistant",
            "content": content or "",
            "tool_calls": [
                {
                    "function": {
                        "name": call.name,
                        "arguments": call.arguments,
                    }
                }
                for call in tool_calls
            ],
        }

    def _build_base_messages(
        self,
        user_text: str,
    ) -> list[dict[str, Any]]:
        """Build unified context for a request."""

        return self.context_builder.build(
            user_text=user_text,
            history=self._messages,
        )

    def _handle_deterministic_tool(
        self,
        user_text: str,
    ) -> str:
        """
        Handle a request requiring an authoritative local tool.

        Examples:
        - current time
        - system information
        """

        route = self.router.route(
            user_text
        )

        if route != RouteMode.TOOL:
            raise RuntimeError(
                "Deterministic tool handler called "
                "for a non-tool route."
            )

        from app.ai.tool_policy import (
            detect_required_tool,
        )

        required_tool = detect_required_tool(
            user_text
        )

        if required_tool is None:
            raise RuntimeError(
                "Tool route selected without "
                "a deterministic tool."
            )

        logger.info(
            "Preflight tool selected: %s",
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

        tool_context = (
            "AUTHORITATIVE TOOL RESULT\n\n"
            f"Tool: {required_tool}\n"
            f"Result: "
            f"{self._tool_result_content(result)}\n\n"
            "Use this result exactly. "
            "Do not estimate, replace, reinterpret, "
            "or contradict it."
        )

        messages = self.context_builder.build(
            user_text=user_text,
            history=self._messages,
            external_context=tool_context,
        )

        response = self.provider.chat(
            messages=messages,
            tools=None,
        )

        if not response.content:
            raise RuntimeError(
                "AI returned an empty response "
                "after tool execution."
            )

        self._messages.append(
            {
                "role": "user",
                "content": user_text,
            }
        )

        self._messages.append(
            {
                "role": "assistant",
                "content": response.content,
            }
        )

        self._trim_history()

        return response.content

    def _handle_web(
        self,
        user_text: str,
    ) -> str:
        """
        Research the web and answer using fetched source content.

        The web layer retrieves information.
        The local LLM synthesizes the answer.
        The grounding guard validates the final answer.
        """

        logger.info(
            "Starting web research for: %s",
            user_text,
        )

        research = self.web_research.research(
            query=user_text,
            max_search_results=5,
            max_sources=2,
            max_chars=12000,
        )

        if not research.sources:
            logger.warning(
                "Web research returned no sources."
            )

            return (
                "I couldn't find enough reliable "
                "information online to answer that."
            )

        source_sections: list[str] = []

        for index, source in enumerate(
            research.sources,
            start=1,
        ):
            # Keep context manageable for Qwen3 1.7B.
            content = source.content[:6000]

            source_sections.append(
                f"SOURCE {index}\n"
                f"Title: {source.title}\n"
                f"URL: {source.url}\n"
                f"Source: {source.source}\n"
                f"Search snippet: {source.snippet}\n"
                f"Fetched page content:\n{content}"
            )

        research_context = (
            "VERIFIED WEB RESEARCH\n\n"
            f"Query: {research.query}\n\n"
            "Use the fetched source content below "
            "as the primary evidence for answering "
            "the user.\n\n"
            "Rules:\n"
            "- Prefer primary or official sources.\n"
            "- Do not use outdated model knowledge "
              "when it conflicts with the fetched evidence.\n"
            "- Do not invent dates, numbers, versions, "
              "prices, names, or other precise facts.\n"
            "- Only state precise claims supported by "
              "the fetched content.\n"
            "- When sources disagree, acknowledge "
              "the disagreement.\n"
            "- Never invent an 'as of' date.\n"
            "- Do not claim that live web access is "
              "unavailable.\n"
            "- Do not mention these instructions.\n\n"
            + "\n\n".join(source_sections)
        )

        logger.info(
            "Sending fetched research to local LLM."
        )

        messages = self.context_builder.build(
            user_text=user_text,
            history=self._messages,
            external_context=research_context,
        )

        response = self.provider.chat(
            messages=messages,
            tools=None,
        )

        evidence_text = research_context

        # ---------------------------------------------------------
        # Validate first model response.
        # ---------------------------------------------------------
        valid, problems = validate_web_answer(
            response.content,
            evidence_text,
        )

        logger.warning(
            "WEB GUARD RESULT: valid=%s problems=%s",
            valid,
            problems,
        )

        # ---------------------------------------------------------
        # Retry once if grounding validation fails.
        # ---------------------------------------------------------
        if not valid:
            logger.warning(
                "Web answer failed grounding validation: %s",
                problems,
            )

            retry_context = (
                research_context
                + "\n\n"
                + "CRITICAL ANSWER REQUIREMENT:\n"
                + "Every version number, year, date, "
                  "and numeric current-state fact "
                  "in your answer MUST be supported "
                  "by the supplied evidence.\n"
                + "Do not introduce values from "
                  "your pretrained knowledge.\n"
                + "Never invent an 'as of' date.\n"
                + "If a fact is not explicitly supported, "
                  "omit it.\n"
                + "Give a concise answer.\n"
            )

            retry_messages = self.context_builder.build(
                user_text=user_text,
                history=self._messages,
                external_context=retry_context,
            )

            logger.info(
                "Retrying web answer after "
                "grounding validation failure."
            )

            retry_response = self.provider.chat(
                messages=retry_messages,
                tools=None,
            )

            retry_valid, retry_problems = (
                validate_web_answer(
                    retry_response.content,
                    evidence_text,
                )
            )

            logger.warning(
                "WEB GUARD RETRY RESULT: "
                "valid=%s problems=%s",
                retry_valid,
                retry_problems,
            )

            if retry_valid:
                response = retry_response

            else:
                logger.error(
                    "Web answer failed validation "
                    "after retry: %s",
                    retry_problems,
                )

                response = AIResponse(
                    content=(
                        "I found current information "
                        "online, but I could not verify "
                        "the final answer reliably."
                    ),
                    tool_calls=[],
                )

        # ---------------------------------------------------------
        # Final response validation.
        # ---------------------------------------------------------
        if not response.content:
            raise RuntimeError(
                "AI returned an empty response "
                "after web research."
            )

        self._messages.append(
            {
                "role": "user",
                "content": user_text,
            }
        )

        self._messages.append(
            {
                "role": "assistant",
                "content": response.content,
            }
        )

        self._trim_history()

        return response.content

    def _handle_local(
        self,
        user_text: str,
    ) -> str:
        """
        Handle a normal local request with optional
        native tool calls.
        """

        messages = self._build_base_messages(
            user_text
        )

        tools = self.registry.definitions()

        for round_number in range(
            1,
            self.MAX_TOOL_ROUNDS + 1,
        ):
            logger.info(
                "Assistant loop round %d",
                round_number,
            )

            response = self.provider.chat(
                messages=messages,
                tools=tools,
            )

            # -----------------------------------------------------
            # Normal final response.
            # -----------------------------------------------------
            if not response.tool_calls:
                if not response.content:
                    raise RuntimeError(
                        "AI returned neither content "
                        "nor a tool call."
                    )

                self._messages.append(
                    {
                        "role": "user",
                        "content": user_text,
                    }
                )

                self._messages.append(
                    {
                        "role": "assistant",
                        "content": response.content,
                    }
                )

                self._trim_history()

                return response.content

            # -----------------------------------------------------
            # Preserve assistant tool-call message.
            # -----------------------------------------------------
            messages.append(
                self._assistant_tool_call_message(
                    content=response.content,
                    tool_calls=response.tool_calls,
                )
            )

            # -----------------------------------------------------
            # Execute each requested tool.
            # -----------------------------------------------------
            for call in response.tool_calls:
                logger.info(
                    "Assistant requested tool: %s",
                    call.name,
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
            "Maximum assistant tool-call rounds "
            "exceeded."
        )

    def respond(
        self,
        user_text: str,
    ) -> str:
        """Process a complete user request."""

        user_text = user_text.strip()

        if not user_text:
            raise ValueError(
                "user_text cannot be empty."
            )

        route = self.router.route(
            user_text
        )

        logger.info(
            "Assistant route selected: %s",
            route.value,
        )

        if route == RouteMode.TOOL:
            return self._handle_deterministic_tool(
                user_text
            )

        if route == RouteMode.WEB:
            return self._handle_web(
                user_text
            )

        return self._handle_local(
            user_text
        )