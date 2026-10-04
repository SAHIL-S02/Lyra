import re
from datetime import datetime


_VERSION_PATTERN = re.compile(
    r"\b\d+\.\d+(?:\.\d+)?\b"
)

_AS_OF_PATTERN = re.compile(
    r"\bas\s+of\s+\*{0,2}[A-Za-z]+\s+((?:19|20)\d{2})\*{0,2}\b",
    re.IGNORECASE,
)

_SOURCE_PATTERN = re.compile(
    r"SOURCE\s+(\d+)\n(.*?)(?=\n\nSOURCE\s+\d+\n|\Z)",
    re.DOTALL,
)


def _extract_versions(text: str) -> set[str]:
    return set(_VERSION_PATTERN.findall(text))


def _extract_sources(evidence: str) -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []

    for match in _SOURCE_PATTERN.finditer(evidence):
        block = match.group(2)

        title_match = re.search(
            r"Title:\s*(.+)",
            block,
        )

        snippet_match = re.search(
            r"Search snippet:\s*(.+)",
            block,
        )

        title = title_match.group(1).strip() if title_match else ""
        snippet = (
            snippet_match.group(1).strip()
            if snippet_match
            else ""
        )

        sources.append(
            {
                "title": title,
                "snippet": snippet,
            }
        )

    return sources


def _extract_query(evidence: str) -> str:
    match = re.search(
        r"Query:\s*(.+)",
        evidence,
        re.IGNORECASE,
    )

    return match.group(1).strip() if match else ""


def _is_current_query(query: str) -> bool:
    query = query.lower()

    triggers = (
        "latest",
        "current",
        "today",
        "recent",
        "live",
        "newest",
        "current version",
    )

    return any(trigger in query for trigger in triggers)


def _version_supported(
    version: str,
    authoritative_versions: set[str],
) -> bool:
    """
    Allow a shorter major/minor version when it is the prefix
    of an authoritative full version.

    Example:
        3.14 is supported by 3.14.8
    """

    if version in authoritative_versions:
        return True

    for authoritative in authoritative_versions:
        if authoritative.startswith(version + "."):
            return True

    return False


def validate_web_answer(
    answer: str,
    evidence: str,
) -> tuple[bool, list[str]]:
    """
    Validate current/latest web answers against the actual
    VERIFIED WEB RESEARCH context produced by AssistantEngine.
    """

    problems: list[str] = []

    query = _extract_query(evidence)
    sources = _extract_sources(evidence)

    current_year = datetime.now().astimezone().year

    # ---------------------------------------------------------
    # 1. Reject stale/invented "As of YEAR" claims.
    # ---------------------------------------------------------
    if _is_current_query(query):
        for year_text in _AS_OF_PATTERN.findall(answer):
            year = int(year_text)

            if year != current_year:
                problems.append(
                    f"Invalid current-date claim: 'As of {year}'"
                )

    # ---------------------------------------------------------
    # 2. Extract authoritative versions from search metadata.
    #
    # We deliberately use TITLE + SEARCH SNIPPET only.
    # Full page content may contain historical versions.
    # ---------------------------------------------------------
    authoritative_versions: set[str] = set()

    if sources:
        first_source = sources[0]

        authoritative_versions.update(
            _extract_versions(first_source["title"])
        )

        authoritative_versions.update(
            _extract_versions(first_source["snippet"])
        )

    # ---------------------------------------------------------
    # 3. Reject competing versions for latest/current queries.
    # ---------------------------------------------------------
    if authoritative_versions and _is_current_query(query):
        answer_versions = _extract_versions(answer)

        for version in sorted(answer_versions):
            if not _version_supported(
                version,
                authoritative_versions,
            ):
                problems.append(
                    f"Unsupported competing version: {version}"
                )

    # ---------------------------------------------------------
    # 4. Return validation result.
    # ---------------------------------------------------------
    return len(problems) == 0, problems
