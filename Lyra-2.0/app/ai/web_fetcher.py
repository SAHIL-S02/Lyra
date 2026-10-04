from __future__ import annotations

import gzip
import re
import zlib
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class WebFetchError(RuntimeError):
    """Raised when a web page cannot be fetched."""


class _HTMLTextParser(HTMLParser):
    """Extract readable text from HTML."""

    IGNORED_TAGS = {
        "script",
        "style",
        "noscript",
        "svg",
        "head",
    }

    def __init__(self) -> None:
        super().__init__()

        self.parts: list[str] = []
        self._ignored_depth = 0

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        if tag.lower() in self.IGNORED_TAGS:
            self._ignored_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self.IGNORED_TAGS:
            if self._ignored_depth > 0:
                self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._ignored_depth > 0:
            return

        text = data.strip()

        if text:
            self.parts.append(text)

    def text(self) -> str:
        """Return normalized extracted text."""

        text = " ".join(self.parts)

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()


def _decode_response(
    raw: bytes,
    content_encoding: str,
) -> str:
    """Decode an HTTP response body."""

    encoding = content_encoding.lower().strip()

    try:
        if encoding == "gzip":
            raw = gzip.decompress(raw)

        elif encoding == "deflate":
            try:
                raw = zlib.decompress(raw)
            except zlib.error:
                raw = zlib.decompress(
                    raw,
                    -zlib.MAX_WBITS,
                )

        elif encoding in {"", "identity"}:
            pass

        else:
            raise WebFetchError(
                f"Unsupported content encoding: {content_encoding}"
            )

        return raw.decode(
            "utf-8",
            errors="replace",
        )

    except WebFetchError:
        raise

    except (OSError, zlib.error, UnicodeDecodeError) as exc:
        raise WebFetchError(
            f"Failed to decode web response: {exc}"
        ) from exc


def fetch_web_page(
    url: str,
    timeout: int = 15,
    max_chars: int = 12000,
) -> str:
    """Fetch a public web page and return readable text."""

    url = url.strip()

    if not url:
        raise ValueError("url cannot be empty.")

    if not url.startswith(("http://", "https://")):
        raise WebFetchError(
            "Only HTTP and HTTPS URLs are supported."
        )

    request = Request(
        url=url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/142.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml"
            ),
            # Ask the server not to compress the response.
            "Accept-Encoding": "identity",
        },
        method="GET",
    )

    try:
        with urlopen(
            request,
            timeout=timeout,
        ) as response:
            content_type = response.headers.get(
                "Content-Type",
                "",
            )

            if (
                "text/html" not in content_type.lower()
                and "application/xhtml+xml" not in content_type.lower()
            ):
                raise WebFetchError(
                    f"Unsupported content type: {content_type}"
                )

            raw = response.read(
                2 * 1024 * 1024
            )

            content_encoding = response.headers.get(
                "Content-Encoding",
                "identity",
            )

            html = _decode_response(
                raw,
                content_encoding,
            )

    except HTTPError as exc:
        raise WebFetchError(
            f"HTTP error {exc.code}: {url}"
        ) from exc

    except URLError as exc:
        raise WebFetchError(
            f"Could not fetch page: {exc}"
        ) from exc

    except TimeoutError as exc:
        raise WebFetchError(
            f"Page fetch timed out: {url}"
        ) from exc

    parser = _HTMLTextParser()
    parser.feed(html)

    text = parser.text()

    if not text:
        raise WebFetchError(
            "The page contained no readable text."
        )

    return text[:max_chars]
