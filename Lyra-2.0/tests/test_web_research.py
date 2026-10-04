from app.ai.web_research import WebResearchService
from app.memory.manager import MemoryManager
from app.tools.bootstrap import create_tool_system


def main() -> None:
    print("=== Lyra Web Research Test ===")

    memory = MemoryManager()

    _, executor = create_tool_system(
        memory=memory,
    )

    researcher = WebResearchService(
        executor=executor,
    )

    query = "What is the latest Python release?"

    print("\nQuery:", query)
    print("\nResearching...")

    response = researcher.research(
        query=query,
        max_search_results=5,
        max_sources=2,
        max_chars=12000,
    )

    print("\nSources found:", len(response.sources))

    for index, source in enumerate(
        response.sources,
        start=1,
    ):
        print(f"\n--- Source {index} ---")
        print("Title :", source.title)
        print("URL   :", source.url)
        print("Source:", source.source)
        print("Text  :", source.content[:500])

    assert len(response.sources) > 0

    combined = "\n".join(
        source.content
        for source in response.sources
    )

    assert "3.14.8" in combined

    print("\nWeb research test passed.")


if __name__ == "__main__":
    main()
