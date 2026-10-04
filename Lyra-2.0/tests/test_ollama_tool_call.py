from __future__ import annotations

import json
import urllib.request

from app.tools.bootstrap import create_tool_system


def ollama_chat(
    messages: list[dict],
    tools: list[dict],
) -> dict:
    payload = {
        "model": "qwen3:1.7b",
        "messages": messages,
        "tools": tools,
        "stream": False,
    }

    request = urllib.request.Request(
        "http://localhost:11434/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(
            response.read().decode("utf-8")
        )


def main() -> None:
    print("=== Ollama Tool Calling Test ===")

    registry, executor = create_tool_system()

    tools = registry.definitions()

    messages = [
        {
            "role": "system",
            "content": (
                "You are Lyra. "
                "When the user asks for the current time, "
                "use the get_current_time tool."
            ),
        },
        {
            "role": "user",
            "content": "What time is it right now?",
        },
    ]

    print("\n1. Sending request to Qwen3...")

    response = ollama_chat(
        messages=messages,
        tools=tools,
    )

    message = response.get("message", {})

    print("\nModel response:")
    print(message)

    tool_calls = message.get("tool_calls", [])

    print("\n2. Tool calls:")

    if not tool_calls:
        print("No tool call was produced.")
        print("\nRaw response:")
        print(response)
        return

    for call in tool_calls:
        function = call.get("function", {})

        name = function.get("name")
        arguments = function.get("arguments", {})

        print("Tool   :", name)
        print("Args   :", arguments)

        result = executor.execute(
            name,
            arguments,
        )

        print("Result :", result)

    print("\nNative tool-call test completed.")


if __name__ == "__main__":
    main()
