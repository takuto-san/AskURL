from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

MAX_PAGE_BYTES = 256 * 1024
MAX_PROMPT_CHARS = 6500
SKIP_TAGS = {"style", "script", "noscript", "template", "svg"}


class PageText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs) -> None:
        if tag in SKIP_TAGS:
            self.skip_depth += 1

    def handle_endtag(self, tag) -> None:
        if tag in SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data) -> None:
        if not self.skip_depth and data.strip():
            self.parts.append(data.strip())


def read_page(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme not in {"https", "http"} or not parsed.hostname:
        raise ValueError("http:// または https:// で始まるURLを指定してください。")

    request = Request(url, headers={"User-Agent": "QA-Agent-Smoke-Test/0.1"})
    try:
        with urlopen(request, timeout=15) as response:
            media_type = response.headers.get_content_type()
            if media_type not in {"text/html", "text/plain", "application/xhtml+xml"}:
                raise ValueError(f"本文を読み取れる形式を指定してください（取得形式: {media_type}）。")
            charset = response.headers.get_content_charset() or "utf-8"
            raw = response.read(MAX_PAGE_BYTES).decode(charset, errors="replace")
    except HTTPError as exc:
        raise OSError(f"ページを取得できませんでした（HTTP {exc.code}）。") from exc
    except (URLError, TimeoutError, LookupError) as exc:
        raise OSError(f"ページを読み込めませんでした（{exc}）。") from exc

    if media_type != "text/plain":
        parser = PageText()
        parser.feed(raw)
        raw = " ".join(parser.parts)

    text = " ".join(raw.split())[:MAX_PROMPT_CHARS]
    if not text:
        raise ValueError("ページから本文を抽出できませんでした。")
    return text
