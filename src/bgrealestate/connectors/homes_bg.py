from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin

from ..models import RawCapture
from ..pipeline import GenericHtmlListingParser, StandardIngestionPipeline
from ..source_registry import SourceRegistry
from .legal import assert_live_http_allowed
from .protocol import Connector, DiscoveryResult

BASE_URL = "https://www.homes.bg"
LISTING_HREF_RE = re.compile(r'href="(/listing/[^"]+)"', re.IGNORECASE)
# Opening <a ...> may have href before class or vice versa (fixture + live HTML vary).
_NEXT_PAGE_OPEN_RE = re.compile(r"<a\s+([^>]+)>", re.IGNORECASE)
_ATTR_HREF_RE = re.compile(r'href="([^"]+)"', re.IGNORECASE)


def _utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def parse_discovery_html(html: str) -> tuple[list[str], dict[str, Any] | None]:
    """Extract listing URLs and next-page cursor from a Homes.bg search results page."""
    seen: dict[str, None] = {}
    for href in LISTING_HREF_RE.findall(html):
        full = urljoin(BASE_URL, href)
        seen.setdefault(full)
    urls = list(seen)

    next_cursor: dict[str, Any] | None = None
    for open_m in _NEXT_PAGE_OPEN_RE.finditer(html):
        attrs = open_m.group(1)
        if not re.search(r'class="[^"]*next-page', attrs, re.IGNORECASE):
            continue
        href_m = _ATTR_HREF_RE.search(attrs)
        if not href_m:
            continue
        page_m = re.search(r"[?&]page=(\d+)", href_m.group(1))
        if page_m:
            next_cursor = {"page": int(page_m.group(1))}
            break

    return urls, next_cursor


class HomesBgConnector(Connector):
    source_name = "Homes.bg"

    def __init__(self, registry: SourceRegistry, *, client: Any | None = None) -> None:
        self._registry = registry
        self._client = client

    def _source(self):
        source = self._registry.by_name(self.source_name)
        if not source:
            raise RuntimeError(f"source not found in registry: {self.source_name}")
        return source

    def _source_for_fetch(self):
        source = self._source()
        assert_live_http_allowed(source)
        return source

    def discover_listing_urls(self, *, cursor: dict[str, Any] | None = None) -> DiscoveryResult:
        """Fetch a search page and return listing URLs + pagination cursor.

        When called without a client (offline/fixture mode), returns empty.
        Use ``parse_discovery_html`` directly for fixture tests.
        """
        if self._client is None:
            return DiscoveryResult(urls=[], next_cursor=cursor, discovered_at=_utc_now())
        self._source_for_fetch()
        page = (cursor or {}).get("page", 1)
        url = f"{BASE_URL}/search?page={page}"
        resp = self._client.get(url)
        urls, next_cursor = parse_discovery_html(resp.text)
        return DiscoveryResult(urls=urls, next_cursor=next_cursor, discovered_at=_utc_now())

    def fetch_listing_detail(self, *, url: str, fetched_at: datetime) -> RawCapture:
        source = self._source_for_fetch()
        # Import lazily so stdlib-only test environments can still run fixture parsing.
        if self._client is None:
            import httpx  # type: ignore

            self._client = httpx.Client(
                timeout=30.0,
                follow_redirects=True,
                headers={"User-Agent": "bgrealestate-mvp/0.1"},
            )
        resp = self._client.get(url)
        content_type = resp.headers.get("content-type", "text/html")
        return RawCapture(
            source_name=source.source_name,
            url=url,
            content_type=content_type,
            body=resp.text,
            fetched_at=fetched_at,
            parser_version=GenericHtmlListingParser.parser_version,
            metadata={"http_status": resp.status_code, "headers": dict(resp.headers)},
        )

    @staticmethod
    def sha256_body(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def parse_and_normalize_from_html(
        self,
        *,
        url: str,
        html: str,
        discovered_at: datetime,
        seed: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        source = self._source()  # parse only — no fetch gate
        pipeline = StandardIngestionPipeline(parser=GenericHtmlListingParser())
        result = pipeline.process_listing_detail(
            source=source,
            url=url,
            html=html,
            captured_at=discovered_at,
            summary_fields=seed or {},
        )
        return {
            "raw_capture": result.raw_capture,
            "parsed_listing": result.parsed_listing,
            "canonical_listing": result.canonical_listing,
        }

