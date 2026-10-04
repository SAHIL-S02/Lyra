from datetime import datetime


def build_web_context(
    query: str,
    sources: list[dict],
) -> str:
    """
    Build strict grounding context for current/external-information queries.

    The model must rely only on the supplied research evidence and the
    runtime date. It must not invent dates, versions, or current-state facts.
    """

    current_date = datetime.now().astimezone().strftime("%Y-%m-%d")

    lines = [
        "WEB SEARCH EVIDENCE",
        "",
        f"USER QUERY: {query}",
        f"CURRENT RUNTIME DATE: {current_date}",
        "",
        "GROUNDING RULES:",
        "1. Use the retrieved web evidence as the authoritative source.",
        "2. Do not use prior model knowledge for current, latest, recent, or live information.",
        "3. Do not invent facts, dates, versions, prices, release dates, or status.",
        "4. Never invent an 'as of' date.",
        "5. Only state a date if it appears in the supplied evidence or is the runtime date above.",
        "6. If the evidence does not contain a requested fact, say that it was not found.",
        "7. Prefer official/primary sources when multiple sources are available.",
        "8. Do not claim that you visited a source unless it appears in the evidence.",
        "",
        "RETRIEVED SOURCES:",
    ]

    for index, source in enumerate(sources, start=1):
        lines.extend(
            [
                "",
                f"[SOURCE {index}]",
                f"Title: {source.get('title', '')}",
                f"URL: {source.get('url', '')}",
                f"Source: {source.get('source', '')}",
                f"Published: {source.get('published', '') or 'Not provided'}",
                f"Snippet: {source.get('snippet', '')}",
                f"Content: {source.get('content', '')}",
            ]
        )

    return "\n".join(lines)