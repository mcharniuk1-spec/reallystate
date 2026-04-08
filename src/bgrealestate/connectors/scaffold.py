from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin

from ..models import RawCapture
from ..pipeline import GenericHtmlListingParser, StandardIngestionPipeline
from ..source_registry import SourceRegistry
from .legal import LegalGateError, assert_live_http_allowed
from .protocol import Connector, DiscoveryResult


def _utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


_A_TAG_RE = re.compile(r"<a\s+([^>]+)>", re.IGNORECASE)
_ATTR_RE = re.compile(r'([a-zA-Z_:][a-zA-Z0-9_:\-]*)\s*=\s*"([^"]*)"')
_PAGE_RE = re.compile(r"[?&]page=(\d+)", re.IGNORECASE)
_PRICE_RE = re.compile(r"(\d[\d\s]{1,}\d)")


def _attrs(raw: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in _ATTR_RE.findall(raw):
        out[key.lower()] = value
    return out


def _intent_from_text(blob: str) -> str:
    low = blob.lower()
    if "наем" in low or "rent" in low:
        return "long_term_rent"
    return "sale"


def parse_discovery_html(
    source_name: str, html: str, *, base_url: str
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    """Parse a tier-1 discovery page into preview entries + next cursor."""
    entries: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    for match in _A_TAG_RE.finditer(html):
        attrs = _attrs(match.group(1))
        href = attrs.get("href", "").strip()
        if not href:
            continue
        if "/listing/" not in href and "/property/" not in href and "/ad/" not in href and "adv=" not in href:
            continue
        full_url = urljoin(base_url, href)
        if full_url in seen_urls:
            continue
        seen_urls.add(full_url)
        ext_id = attrs.get("data-ext-id") or hashlib.sha1(full_url.encode("utf-8")).hexdigest()[:12]

        preview_price: float | None = None
        if attrs.get("data-price"):
            try:
                preview_price = float(attrs["data-price"])
            except ValueError:
                preview_price = None
        else:
            price_match = _PRICE_RE.search(match.group(0))
            if price_match:
                try:
                    preview_price = float(price_match.group(1).replace(" ", ""))
                except ValueError:
                    preview_price = None

        preview_intent = attrs.get("data-intent") or _intent_from_text(match.group(0))
        entries.append(
            {
                "url": full_url,
                "external_id": ext_id,
                "preview_price": preview_price,
                "preview_intent": preview_intent,
            }
        )

    next_cursor: dict[str, Any] | None = None
    for match in _A_TAG_RE.finditer(html):
        attrs = _attrs(match.group(1))
        klass = attrs.get("class", "")
        rel = attrs.get("rel", "")
        href = attrs.get("href", "")
        if "next-page" not in klass and rel != "next":
            continue
        page_match = _PAGE_RE.search(href)
        if page_match:
            next_cursor = {"page": int(page_match.group(1))}
            break

    return entries, next_cursor


class HtmlPortalConnector(Connector):
    """Generic HTML portal/classifieds/agency connector with registry-backed legal gates.

    Per-source HTML parsers are added incrementally; discovery remains a placeholder until
    fixtures exist for each site.
    """

    def __init__(self, source_name: str, registry: SourceRegistry, *, client: Any | None = None) -> None:
        self.source_name = source_name
        self._registry = registry
        self._client = client

    def _entry(self):
        source = self._registry.by_name(self.source_name)
        if not source:
            raise RuntimeError(f"source not found in registry: {self.source_name}")
        return source

    def _entry_for_fetch(self):
        source = self._entry()
        assert_live_http_allowed(source)
        return source

    def discover_listing_urls(self, *, cursor: dict[str, Any] | None = None) -> DiscoveryResult:
        if self._client is None:
            return DiscoveryResult(urls=[], next_cursor=cursor, discovered_at=_utc_now())
        source = self._entry_for_fetch()
        page = (cursor or {}).get("page", 1)
        base_url = (source.primary_url or "").rstrip("/") or f"https://{self.source_name}"
        resp = self._client.get(f"{base_url}/search?page={page}")
        entries, next_cursor = parse_discovery_html(self.source_name, resp.text, base_url=base_url)
        return DiscoveryResult(urls=[e["url"] for e in entries], next_cursor=next_cursor, discovered_at=_utc_now())

    def fetch_listing_detail(self, *, url: str, fetched_at: datetime) -> RawCapture:
        source = self._entry_for_fetch()
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
        source = self._entry()
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


__all__ = ["HtmlPortalConnector", "LegalGateError", "parse_discovery_html"]
