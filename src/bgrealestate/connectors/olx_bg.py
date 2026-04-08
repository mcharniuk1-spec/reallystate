from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from hashlib import sha1
from typing import Any

from ..enums import ListingIntent, PropertyCategory
from ..models import CanonicalListing, ParsedListing, RawCapture, SourceRegistryEntry
from ..source_registry import SourceRegistry
from .legal import assert_live_http_allowed
from .protocol import Connector, DiscoveryResult

PHONE_RE = re.compile(r"\+?\d[\d\s\-()]{6,}\d")
PARSER_VERSION = "olx_api_v1"


def _extract_param(params: list[dict], key: str) -> Any:
    for p in params:
        if p.get("key") == key:
            return p.get("value", {})
    return {}


def _infer_intent_from_category(title: str, description: str) -> ListingIntent:
    blob = f"{title} {description}".lower()
    if "наем" in blob or "rent" in blob:
        return ListingIntent.LONG_TERM_RENT
    return ListingIntent.SALE


def _infer_category(title: str, description: str, category_name: str) -> PropertyCategory:
    blob = f"{title} {description} {category_name}".lower()
    for needle, cat in (
        ("апартамент", PropertyCategory.APARTMENT),
        ("apartment", PropertyCategory.APARTMENT),
        ("студио", PropertyCategory.APARTMENT),
        ("къща", PropertyCategory.HOUSE),
        ("house", PropertyCategory.HOUSE),
        ("земя", PropertyCategory.LAND),
        ("парцел", PropertyCategory.LAND),
        ("land", PropertyCategory.LAND),
        ("plot", PropertyCategory.LAND),
        ("офис", PropertyCategory.OFFICE),
        ("office", PropertyCategory.OFFICE),
    ):
        if needle in blob:
            return cat
    return PropertyCategory.UNKNOWN


def parse_olx_api_response(
    source: SourceRegistryEntry,
    url: str,
    payload: dict[str, Any],
    fetched_at: datetime,
) -> tuple[ParsedListing, CanonicalListing]:
    """Parse an OLX.bg API single-offer JSON payload into ParsedListing + CanonicalListing."""
    if "error" in payload:
        ext_id = str(payload["id"]) if "id" in payload else sha1(url.encode()).hexdigest()[:12]
        parsed = ParsedListing(source_name=source.source_name, url=url, external_id=ext_id, currency="EUR")
        canonical = CanonicalListing(
            source_name=source.source_name,
            owner_group=source.owner_group,
            listing_url=url,
            external_id=ext_id,
            reference_id=f"{source.source_name}:{ext_id}",
            listing_intent=ListingIntent.MIXED,
            property_category=PropertyCategory.UNKNOWN,
            city=None, district=None, resort=None, region=None,
            address_text=None, latitude=None, longitude=None,
            geocode_confidence=None, building_name=None,
            area_sqm=None, rooms=None, floor=None, total_floors=None,
            construction_type=None, construction_year=None, stage=None,
            act16_present=None, price=None, currency="EUR", fees=None,
            price_per_sqm=None, broker_name=None, agency_name=None,
            owner_name=None, developer_name=None, phones=[], messenger_handles=[],
            outbound_channel_hints=[], description=None, amenities=[], image_urls=[],
            first_seen=fetched_at, last_seen=fetched_at, last_changed_at=fetched_at,
            removed_at=None, parser_version=PARSER_VERSION,
            crawl_provenance={"source_name": source.source_name, "captured_at": fetched_at.isoformat()},
        )
        return parsed, canonical

    ext_id = str(payload.get("id", sha1(url.encode()).hexdigest()[:12]))
    title = payload.get("title", "")
    description = payload.get("description", "")
    category_name = (payload.get("category") or {}).get("name", "")
    params = payload.get("params", [])

    price_param = _extract_param(params, "price")
    price_val = price_param.get("value") if isinstance(price_param, dict) else None
    currency = price_param.get("currency", "EUR") if isinstance(price_param, dict) else "EUR"

    m_param = _extract_param(params, "m")
    area_raw = m_param.get("key") if isinstance(m_param, dict) else None
    area_sqm = float(area_raw) if area_raw and str(area_raw).replace(".", "").isdigit() else None

    rooms_param = _extract_param(params, "rooms_num")
    rooms_raw = rooms_param.get("key") if isinstance(rooms_param, dict) else None
    rooms = float(rooms_raw) if rooms_raw and str(rooms_raw).replace(".", "").isdigit() else None

    floor_param = _extract_param(params, "floor_select")
    floor_raw = floor_param.get("key") if isinstance(floor_param, dict) else None
    floor = int(floor_raw) if floor_raw and str(floor_raw).isdigit() else None

    loc = payload.get("location") or {}
    city = (loc.get("city") or {}).get("name")
    district_raw = (loc.get("district") or {}).get("name")
    district = district_raw if district_raw else None
    region = (loc.get("region") or {}).get("name")

    geo = payload.get("map") or {}
    lat = geo.get("lat")
    lon = geo.get("lon")

    photos = payload.get("photos") or []
    image_urls = sorted(dict.fromkeys(p.get("link", "") for p in photos if p.get("link")))

    phones = sorted(set(PHONE_RE.findall(description)))

    intent = _infer_intent_from_category(title, description)
    prop_cat = _infer_category(title, description, category_name)

    parsed = ParsedListing(
        source_name=source.source_name,
        url=url,
        external_id=ext_id,
        title=title or None,
        listing_intent=intent,
        property_category=prop_cat,
        city=city,
        district=district,
        region=region,
        address_text=None,
        latitude=lat,
        longitude=lon,
        area_sqm=area_sqm,
        rooms=rooms,
        floor=floor,
        price=float(price_val) if price_val is not None else None,
        currency=currency,
        phones=phones,
        image_urls=image_urls,
        description=description or None,
        raw_payload={"api_response": payload, "fetched_at": fetched_at.isoformat()},
    )

    price_per_sqm = None
    if parsed.price and parsed.area_sqm:
        price_per_sqm = round(parsed.price / parsed.area_sqm, 2)

    canonical = CanonicalListing(
        source_name=source.source_name,
        owner_group=source.owner_group,
        listing_url=url,
        external_id=ext_id,
        reference_id=f"{source.source_name}:{ext_id}",
        listing_intent=intent,
        property_category=prop_cat,
        city=city,
        district=district,
        resort=None,
        region=region,
        address_text=None,
        latitude=lat,
        longitude=lon,
        geocode_confidence=None,
        building_name=None,
        area_sqm=area_sqm,
        rooms=rooms,
        floor=floor,
        total_floors=None,
        construction_type=None,
        construction_year=None,
        stage=None,
        act16_present=None,
        price=float(price_val) if price_val is not None else None,
        currency=currency,
        fees=None,
        price_per_sqm=price_per_sqm,
        broker_name=None,
        agency_name=None,
        owner_name=None,
        developer_name=None,
        phones=phones,
        messenger_handles=[],
        outbound_channel_hints=[],
        description=description or None,
        amenities=[],
        image_urls=image_urls,
        first_seen=fetched_at,
        last_seen=fetched_at,
        last_changed_at=fetched_at,
        removed_at=None,
        parser_version=PARSER_VERSION,
        crawl_provenance={"source_name": source.source_name, "captured_at": fetched_at.isoformat()},
    )
    return parsed, canonical


class OlxBgConnector(Connector):
    source_name = "OLX.bg"

    def __init__(self, registry: SourceRegistry, *, client: Any | None = None) -> None:
        self._registry = registry
        self._client = client

    def _entry(self) -> SourceRegistryEntry:
        source = self._registry.by_name(self.source_name)
        if not source:
            raise RuntimeError(f"source not found in registry: {self.source_name}")
        assert_live_http_allowed(source)
        return source

    def discover_listing_urls(self, *, cursor: dict[str, Any] | None = None) -> DiscoveryResult:
        return DiscoveryResult(urls=[], next_cursor=cursor, discovered_at=datetime.now(tz=timezone.utc))

    def fetch_listing_detail(self, *, url: str, fetched_at: datetime) -> RawCapture:
        source = self._entry()
        if self._client is None:
            import httpx  # type: ignore
            self._client = httpx.Client(timeout=30.0, headers={"User-Agent": "bgrealestate-mvp/0.1"})
        resp = self._client.get(url)
        return RawCapture(
            source_name=source.source_name,
            url=url,
            content_type=resp.headers.get("content-type", "application/json"),
            body=resp.text,
            fetched_at=fetched_at,
            parser_version=PARSER_VERSION,
            metadata={"http_status": resp.status_code, "headers": dict(resp.headers)},
        )

    def parse_api_response(
        self,
        *,
        url: str,
        json_text: str,
        fetched_at: datetime,
        seed: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        source = self._entry()
        payload = json.loads(json_text)
        if seed and "external_id" in seed:
            payload.setdefault("id", seed["external_id"])
        parsed, canonical = parse_olx_api_response(source, url, payload, fetched_at)
        raw_capture = RawCapture(
            source_name=source.source_name,
            url=url,
            content_type="application/json",
            body=json_text,
            fetched_at=fetched_at,
            parser_version=PARSER_VERSION,
            metadata={},
        )
        return {
            "raw_capture": raw_capture,
            "parsed_listing": parsed,
            "canonical_listing": canonical,
        }
