from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from ..models import RawCapture, SourceRegistryEntry
from ..source_registry import SourceRegistry
from .legal import assert_live_http_allowed
from .protocol import Connector, DiscoveryResult

PARTNER_PARSER_VERSION = "tier3_partner_template_v1"
LICENSED_PARSER_VERSION = "tier3_licensed_template_v1"
OFFICIAL_REGISTER_PARSER_VERSION = "tier3_official_register_template_v1"
BCPEA_PARSER_VERSION = "tier3_public_auction_template_v1"

DATE_RANGE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})")


class PartnerContractRequired(RuntimeError):
    """Raised when partner-feed source is used without an active contract."""


class OperatorConsentRequired(RuntimeError):
    """Raised when consent/manual source is queried without explicit operator approval."""


@dataclass(frozen=True)
class StrMarketMetrics:
    source_name: str
    market: str
    period: str
    occupancy_rate: float | None
    adr_eur: float | None
    revpar_eur: float | None
    active_listings: int | None
    parser_version: str = LICENSED_PARSER_VERSION


def _utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _source_entry(registry: SourceRegistry, source_name: str) -> SourceRegistryEntry:
    source = registry.by_name(source_name)
    if not source:
        raise RuntimeError(f"source not found in registry: {source_name}")
    return source


class PartnerFeedStubConnector(Connector):
    """Fixture-first connector for partner-feed sources until contracts are active."""

    def __init__(
        self,
        source_name: str,
        registry: SourceRegistry,
        *,
        contract_id: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.source_name = source_name
        self._registry = registry
        self._contract_id = contract_id
        self._client = client

    def discover_listing_urls(self, *, cursor: dict[str, Any] | None = None) -> DiscoveryResult:
        return DiscoveryResult(urls=[], next_cursor=cursor, discovered_at=_utc_now())

    def fetch_listing_detail(self, *, url: str, fetched_at: datetime) -> RawCapture:
        _ = fetched_at
        if not self._contract_id:
            raise PartnerContractRequired(
                f"{self.source_name} requires an active partner contract before live feed access."
            )
        source = _source_entry(self._registry, self.source_name)
        # Even with contract present, generic web crawling is not permitted for partner-only sources.
        assert_live_http_allowed(source)
        raise PartnerContractRequired(
            f"{self.source_name} live partner feed not configured; use official contract feed client."
        )

    def parse_partner_payload(self, *, json_text: str) -> dict[str, Any]:
        payload = json.loads(json_text)
        listing = payload.get("listing") or {}
        external_id = str(listing.get("external_id", ""))
        lat = (listing.get("coordinates") or {}).get("lat")
        lon = (listing.get("coordinates") or {}).get("lon")
        nightly = listing.get("nightly_price") or {}
        return {
            "source_name": self.source_name,
            "external_id": external_id,
            "reference_id": f"{self.source_name}:{external_id}" if external_id else None,
            "listing_intent": "short_term_rent",
            "property_category": "apartment",
            "city": listing.get("city"),
            "price": float(nightly["amount"]) if nightly.get("amount") is not None else None,
            "currency": nightly.get("currency"),
            "latitude": lat,
            "longitude": lon,
            "listing_url": listing.get("url"),
            "image_urls": listing.get("images") or [],
            "parser_version": PARTNER_PARSER_VERSION,
        }


class LicensedStrDataConnector:
    """Parser for licensed STR analytics payloads (fixture-first)."""

    def __init__(self, source_name: str, registry: SourceRegistry) -> None:
        self.source_name = source_name
        self._registry = registry

    def parse_metrics_payload(self, *, json_text: str) -> StrMarketMetrics:
        _ = _source_entry(self._registry, self.source_name)
        payload = json.loads(json_text)
        metrics = payload.get("metrics") or {}
        return StrMarketMetrics(
            source_name=self.source_name,
            market=str(payload.get("market", "")),
            period=str(payload.get("period", "")),
            occupancy_rate=float(metrics["occupancy_rate"]) if metrics.get("occupancy_rate") is not None else None,
            adr_eur=float(metrics["adr_eur"]) if metrics.get("adr_eur") is not None else None,
            revpar_eur=float(metrics["revpar_eur"]) if metrics.get("revpar_eur") is not None else None,
            active_listings=int(metrics["active_listings"]) if metrics.get("active_listings") is not None else None,
        )

    @staticmethod
    def metrics_to_dict(metrics: StrMarketMetrics) -> dict[str, Any]:
        return {
            "source_name": metrics.source_name,
            "dataset_type": "short_term_rent_metrics",
            "market": metrics.market,
            "period": metrics.period,
            "metrics": {
                "occupancy_rate": metrics.occupancy_rate,
                "adr_eur": metrics.adr_eur,
                "revpar_eur": metrics.revpar_eur,
                "active_listings": metrics.active_listings,
            },
            "parser_version": metrics.parser_version,
        }


class OfficialRegisterWrapper:
    """Manual/consent wrapper for Property Register and KAIS flows."""

    def __init__(self, source_name: str, registry: SourceRegistry, *, operator_approval_id: str | None = None) -> None:
        self.source_name = source_name
        self._registry = registry
        self._operator_approval_id = operator_approval_id

    def query_live(self, *, query: dict[str, Any]) -> dict[str, Any]:
        _ = query
        if not self._operator_approval_id:
            raise OperatorConsentRequired(
                f"{self.source_name} requires explicit operator approval for live official-service queries."
            )
        raise OperatorConsentRequired(
            f"{self.source_name} live wrapper requires operator-driven workflow and is not auto-enabled."
        )

    def parse_official_response(self, *, json_text: str) -> dict[str, Any]:
        payload = json.loads(json_text)
        query = payload.get("query") or {}
        response = payload.get("response") or {}
        reference_id = query.get("parcel_or_property_id")
        verification_type = "parcel_validation" if self.source_name == "KAIS Cadastre" else "ownership_verification"
        return {
            "source_name": self.source_name,
            "verification_type": verification_type,
            "reference_id": f"{self.source_name}:{reference_id}" if reference_id else None,
            "query_status": response.get("status"),
            "encumbrance_flag": bool(response.get("encumbrance_flag", False)),
            "consent_mode": "operator_approved" if payload.get("operator_approval_id") else "manual_only",
            "parser_version": OFFICIAL_REGISTER_PARSER_VERSION,
        }


class BcpeaAuctionConnector(Connector):
    source_name = "BCPEA property auctions"

    def __init__(self, registry: SourceRegistry, *, client: Any | None = None) -> None:
        self._registry = registry
        self._client = client

    def _entry(self) -> SourceRegistryEntry:
        source = _source_entry(self._registry, self.source_name)
        return source

    def discover_listing_urls(self, *, cursor: dict[str, Any] | None = None) -> DiscoveryResult:
        return DiscoveryResult(urls=[], next_cursor=cursor, discovered_at=_utc_now())

    def fetch_listing_detail(self, *, url: str, fetched_at: datetime) -> RawCapture:
        source = self._entry()
        assert_live_http_allowed(source)
        if self._client is None:
            import httpx  # type: ignore

            self._client = httpx.Client(timeout=30.0, follow_redirects=True, headers={"User-Agent": "bgrealestate-mvp/0.1"})
        resp = self._client.get(url)
        return RawCapture(
            source_name=source.source_name,
            url=url,
            content_type=resp.headers.get("content-type", "text/html"),
            body=resp.text,
            fetched_at=fetched_at,
            parser_version=BCPEA_PARSER_VERSION,
            metadata={"http_status": resp.status_code, "headers": dict(resp.headers)},
        )

    def parse_auction_html(self, *, html: str) -> dict[str, Any]:
        ext_id = self._extract_text(r'<div class="auction-id">([^<]+)</div>', html)
        price_text = self._extract_text(r'<div class="price">([^<]+)</div>', html)
        area_text = self._extract_text(r'<div class="area">([^<]+)</div>', html)
        address_text = self._extract_text(r'<div class="address">([^<]+)</div>', html)
        court = self._extract_text(r'<div class="court">([^<]+)</div>', html)
        bailiff = self._extract_text(r'<div class="bailiff">([^<]+)</div>', html)
        dates = self._extract_text(r'<div class="dates">([^<]+)</div>', html)
        match = DATE_RANGE_RE.search(dates or "")
        start_date = match.group(1) if match else None
        end_date = match.group(2) if match else None
        city, district = self._split_city_district(address_text)
        return {
            "source_name": self.source_name,
            "external_id": ext_id,
            "listing_intent": "auction_sale",
            "price": self._extract_float(price_text),
            "currency": "EUR" if "EUR" in (price_text or "").upper() else None,
            "area_sqm": self._extract_float(area_text),
            "city": city,
            "district": district,
            "court": court.replace("Court: ", "") if court else None,
            "bailiff": bailiff.replace("Bailiff: ", "") if bailiff else None,
            "auction_start_date": start_date,
            "auction_end_date": end_date,
            "parser_version": BCPEA_PARSER_VERSION,
        }

    @staticmethod
    def _extract_text(pattern: str, html: str) -> str | None:
        m = re.search(pattern, html, flags=re.IGNORECASE)
        return m.group(1).strip() if m else None

    @staticmethod
    def _extract_float(text: str | None) -> float | None:
        if not text:
            return None
        m = re.search(r"(\d+(?:\.\d+)?)", text.replace(",", "."))
        return float(m.group(1)) if m else None

    @staticmethod
    def _split_city_district(address_text: str | None) -> tuple[str | None, str | None]:
        if not address_text:
            return None, None
        cleaned = address_text.replace("Address:", "").strip()
        parts = [part.strip() for part in cleaned.split(",") if part.strip()]
        if len(parts) >= 2:
            return parts[0], parts[1]
        return (parts[0], None) if parts else (None, None)
