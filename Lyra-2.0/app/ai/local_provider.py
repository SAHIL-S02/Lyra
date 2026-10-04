from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from app.ai.base import AIProvider
from app.ai.models import AIResponse, ToolCall
from app.core.config import settings


class LocalLLMError(RuntimeError):
    """Raised when the local LLM cannot be reached or returns invalid data."""


class LocalOllamaProvider(AIProvider):
    """AI provider backed by a local Ollama model."""

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        timeout: int = 120,
    ) -> None:
        self.model = model or settings.local_model
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.timeout = timeout

    def _request(
        self,
        method: str,
        endpoint: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{endpoint}"

        data = None

        if payload is not None:
            data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            url=url,
            data=data,
            headers={
                "Content-Type": "application/json",
            },
            method=method,
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
            ) as response:
                raw = response.read().decode("utf-8")

        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")

            raise LocalLLMError(
                f"Ollama HTTP error {exc.code}: {body}"
            ) from exc

        except urllib.error.URLError as exc:
            raise LocalLLMError(
                f"Cannot connect to Ollama at {self.base_url}: {exc}"
            ) from exc

        except TimeoutError as exc:
            raise LocalLLMError(
                "Ollama request timed out."
            ) from exc

        try:
            result = json.loads(raw)

        except json.JSONDecodeError as exc:
            raise LocalLLMError(
                "Ollama returned invalid JSON."
            ) from exc

        if not isinstance(result, dict):
            raise LocalLLMError(
                "Ollama returned an unexpected response format."
            )

        return result

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> AIResponse:
        """Send a chat request to Ollama."""

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "think": False,
            "keep_alive": "10m",
        }

        if tools:
            payload["tools"] = tools

        result = self._request(
            method="POST",
            endpoint="/api/chat",
            payload=payload,
        )

        message = result.get("message")

        if not isinstance(message, dict):
            raise LocalLLMError(
                "Ollama response is missing the message object."
            )

        content = message.get("content", "")

        if not isinstance(content, str):
            content = ""

        raw_tool_calls = message.get("tool_calls", [])

        if raw_tool_calls is None:
            raw_tool_calls = []

        if not isinstance(raw_tool_calls, list):
            raise LocalLLMError(
                "Ollama returned invalid tool_calls data."
            )

        tool_calls: list[ToolCall] = []

        for raw_call in raw_tool_calls:
            if not isinstance(raw_call, dict):
                continue

            function = raw_call.get("function")

            if not isinstance(function, dict):
                continue

            name = function.get("name")

            if not isinstance(name, str) or not name:
                continue

            arguments = function.get("arguments", {})

            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError as exc:
                    raise LocalLLMError(
                        f"Invalid arguments for tool '{name}'."
                    ) from exc

            if not isinstance(arguments, dict):
                raise LocalLLMError(
                    f"Invalid arguments for tool '{name}'."
                )

            call_id = raw_call.get("id")

            if call_id is not None and not isinstance(call_id, str):
                call_id = None

            tool_calls.append(
                ToolCall(
                    id=call_id,
                    name=name,
                    arguments=arguments,
                )
            )

        return AIResponse(
            content=content.strip(),
            tool_calls=tool_calls,
        )

    def health_check(self) -> bool:
        """Check whether Ollama is running and the configured model exists."""

        try:
            result = self._request(
                method="GET",
                endpoint="/api/tags",
            )

        except LocalLLMError:
            return False

        models = result.get("models", [])

        if not isinstance(models, list):
            return False

        return any(
            isinstance(model_info, dict)
            and model_info.get("name") == self.model
            for model_info in models
        )
