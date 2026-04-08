from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from ..models import RawCapture
from ..pipeline import GenericHtmlListingParser, StandardIngestionPipeline
from ..source_registry import SourceRegistry
from .protocol import Connector, DiscoveryResult


class LegalGateError(RuntimeError):
    pass


def _utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


class HomesBgConnector(Connector):
    source_name = "Homes.bg"

    def __init__(self, registry: SourceRegistry, *, client: Any | None = None) -> None:
        self._registry = registry
        self._client = client

    def _source(self):
        source = self._registry.by_name(self.source_name)
        if not source:
            raise RuntimeError(f"source not found in registry: {self.source_name}")
        # Fail-closed: only allow sources explicitly in crawl-review mode in this MVP slice.
        if source.legal_mode not in {"public_crawl_with_review", "official_api_allowed", "public_or_contract_review"}:
            raise LegalGateError(f"live fetch blocked by legal_mode={source.legal_mode} for {source.source_name}")
        return source

    def discover_listing_urls(self, *, cursor: dict[str, Any] | None = None) -> DiscoveryResult:
        # MVP placeholder: discovery endpoints vary; implement after fixtures capture.
        return DiscoveryResult(urls=[], next_cursor=cursor, discovered_at=_utc_now())

    def fetch_listing_detail(self, *, url: str, fetched_at: datetime) -> RawCapture:
        source = self._source()
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
        source = self._source()
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

