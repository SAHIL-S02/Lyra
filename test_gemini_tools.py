from app.tools.bootstrap import register_all_tools
from app.tools.registry import tool_registry


register_all_tools()

print("=" * 50)
print("LYRA GEMINI TOOL REGISTRY")
print("=" * 50)

print("\nRegistered tools:")

for name in tool_registry.names():
    print(f"  - {name}")

print("\nGemini declarations:")

for declaration in tool_registry.gemini_declarations():
    print(f"\nName: {declaration['name']}")
    print(f"Description: {declaration['description']}")
    print(f"Parameters: {declaration['parameters']}")