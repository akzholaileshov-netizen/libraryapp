"""Wikimedia REST API арқылы мақала HTML жүктеу."""

from __future__ import annotations

import html as html_lib
import re
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

WIKI_HOSTS = {
    "kk": "kk.wikipedia.org",
    "en": "en.wikipedia.org",
    "ru": "ru.wikipedia.org",
}

USER_AGENT = "LibraryApp/1.0 (educational; Flask electronic library)"


class _BodyExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._capture = False
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        low = tag.lower()
        if low == "body":
            self._capture = True
            return
        if not self._capture:
            return
        if low in {"script", "style", "noscript"}:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        attr_map = {k: (v or "") for k, v in attrs}
        # Drop edit / navigation chrome
        classes = attr_map.get("class", "")
        if any(
            x in classes
            for x in (
                "mw-editsection",
                "navbox",
                "noprint",
                "reference",
                "mw-empty-elt",
            )
        ):
            # still open tag but keep simple content; skip editsection entirely
            if "mw-editsection" in classes:
                self._skip_depth += 1
                return
        cleaned = []
        for k, v in attrs:
            if k in {"onclick", "onerror", "onload", "style"}:
                continue
            if k in {"href", "src"} and v:
                cleaned.append((k, v))
            elif k not in {"id"} or not (v or "").startswith("mw"):
                cleaned.append((k, v))
        attr_html = "".join(
            f' {html_lib.escape(k)}="{html_lib.escape(v or "", quote=True)}"'
            for k, v in cleaned
        )
        self._parts.append(f"<{low}{attr_html}>")

    def handle_endtag(self, tag: str) -> None:
        low = tag.lower()
        if low == "body":
            self._capture = False
            return
        if not self._capture:
            return
        if low in {"script", "style", "noscript"}:
            if self._skip_depth:
                self._skip_depth -= 1
            return
        if self._skip_depth:
            if low in {"span", "div", "sup"}:
                # best-effort exit for skipped editsection wrappers
                self._skip_depth = max(0, self._skip_depth - 1)
            return
        self._parts.append(f"</{low}>")

    def handle_data(self, data: str) -> None:
        if self._capture and not self._skip_depth:
            self._parts.append(html_lib.escape(data))

    def handle_entityref(self, name: str) -> None:
        if self._capture and not self._skip_depth:
            self._parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if self._capture and not self._skip_depth:
            self._parts.append(f"&#{name};")

    def get_html(self) -> str:
        return "".join(self._parts)


def wiki_page_url(lang: str, title: str) -> str:
    host = WIKI_HOSTS.get(lang, WIKI_HOSTS["kk"])
    slug = title.replace(" ", "_")
    return f"https://{host}/wiki/{urllib.parse.quote(slug)}"


def fetch_wikipedia_html(lang: str, title: str, timeout: float = 12.0) -> tuple[str | None, str | None]:
    """Мақала HTML фрагментін қайтарады. (html, error)."""
    title = (title or "").strip()
    if not title:
        return None, "empty_title"

    host = WIKI_HOSTS.get(lang)
    if not host:
        return None, "bad_lang"

    slug = urllib.parse.quote(title.replace(" ", "_"), safe="")
    url = f"https://{host}/api/rest_v1/page/html/{slug}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html; charset=utf-8",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return None, f"http_{exc.code}"
    except Exception as exc:  # noqa: BLE001
        return None, str(exc.__class__.__name__)

    cleaned = sanitize_wikipedia_html(raw, host)
    if not cleaned.strip():
        return None, "empty_body"
    return cleaned, None


def sanitize_wikipedia_html(raw_html: str, host: str) -> str:
    """Script-сіз body мәтіні; салыстырмалы сілтемелерді абсолют қылу."""
    parser = _BodyExtractor()
    try:
        parser.feed(raw_html)
        parser.close()
    except Exception:
        # fallback: strip tags crudely between body
        m = re.search(r"<body[^>]*>(.*)</body>", raw_html, re.I | re.S)
        fragment = m.group(1) if m else raw_html
        fragment = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", fragment, flags=re.I | re.S)
        return _absolutize_urls(fragment, host)

    return _absolutize_urls(parser.get_html(), host)


def _absolutize_urls(fragment: str, host: str) -> str:
    base = f"https://{host}"

    def repl_href(match: re.Match[str]) -> str:
        q = match.group(1)
        url = match.group(2)
        if url.startswith("//"):
            return f"href={q}https:{url}{q}"
        if url.startswith("/"):
            return f"href={q}{base}{url}{q}"
        if url.startswith("./") or url.startswith("../"):
            return f"href={q}{base}/{url.lstrip('./')}{q}"
        return match.group(0)

    def repl_src(match: re.Match[str]) -> str:
        q = match.group(1)
        url = match.group(2)
        if url.startswith("//"):
            return f"src={q}https:{url}{q}"
        if url.startswith("/"):
            return f"src={q}{base}{url}{q}"
        return match.group(0)

    fragment = re.sub(r'href=(["\'])([^"\']+)\1', repl_href, fragment)
    fragment = re.sub(r'src=(["\'])([^"\']+)\1', repl_src, fragment)
    return fragment
