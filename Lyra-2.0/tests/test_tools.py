from typing import Any

from app.tools.base import Tool, ToolResult
from app.tools.registry import ToolRegistry


class EchoTool(Tool):
    name = "echo"
    description = "Returns the provided text."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to return.",
                }
            },
            "required": ["text"],
        }

    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        text = arguments.get("text")

        return ToolResult(
            success=True,
            data=text,
        )


def main() -> None:
    print("=== Tool Schema Test ===")

    registry = ToolRegistry()

    tool = EchoTool()

    registry.register(tool)

    definition = tool.definition()

    print("\nTool definition:")
    print(definition)

    assert definition["type"] == "function"
    assert definition["function"]["name"] == "echo"
    assert "description" in definition["function"]
    assert "parameters" in definition["function"]

    parameters = definition["function"]["parameters"]

    assert parameters["type"] == "object"
    assert "text" in parameters["properties"]
    assert parameters["required"] == ["text"]

    print("\nTool schema test passed.")


if __name__ == "__main__":
    main()
