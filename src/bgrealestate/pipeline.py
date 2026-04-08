from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha1
from typing import Any, Dict, Iterable, List, Optional

from .enums import LifecycleEventType, ListingIntent, PropertyCategory
from .models import BuildingEntity, CanonicalListing, ListingEvent, ParsedListing, PropertyEntity, RawCapture, SourceRegistryEntry


PHONE_RE = re.compile(r"\+?\d[\d\s\-()]{6,}\d")
JSON_LD_RE = re.compile(
    r"<script[^>]+type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
    re.IGNORECASE | re.DOTALL,
)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
META_IMAGE_RE = re.compile(
    r"<meta[^>]+property=[\"']og:image[\"'][^>]+content=[\"'](.*?)[\"']",
    re.IGNORECASE | re.DOTALL,
)
TAG_RE = re.compile(r"<[^>]+>")


def _clean_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = TAG_RE.sub(" ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def _load_json_ld_blocks(html: str) -> List[dict]:
    blocks: List[dict] = []
    for raw_block in JSON_LD_RE.findall(html):
        payload = raw_block.strip()
        if not payload:
            continue
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, list):
            blocks.extend(item for item in parsed if isinstance(item, dict))
        elif isinstance(parsed, dict):
            blocks.append(parsed)
    return blocks


def _flatten_json_ld(blocks: Iterable[dict]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    for block in blocks:
        merged.update(block)
        offer = block.get("offers")
        if isinstance(offer, dict):
            for key, value in offer.items():
                merged[f"offers.{key}"] = value
        address = block.get("address")
        if isinstance(address, dict):
            for key, value in address.items():
                merged[f"address.{key}"] = value
        geo = block.get("geo")
        if isinstance(geo, dict):
            for key, value in geo.items():
                merged[f"geo.{key}"] = value
    return merged


def _infer_listing_intent(seed: Dict[str, Any], text: str) -> ListingIntent:
    intent = (seed.get("listing_intent") or "").lower()
    if intent in {"sale", "sell"} or "for sale" in text.lower():
        return ListingIntent.SALE
    if intent in {"short_term_rent", "short-term"}:
        return ListingIntent.SHORT_TERM_RENT
    if intent in {"rent", "long_term_rent"} or "for rent" in text.lower():
        return ListingIntent.LONG_TERM_RENT
    low = text.lower()
    if "продажба" in low or "продава" in low:
        return ListingIntent.SALE
    if "наем" in low or "под наем" in low:
        return ListingIntent.LONG_TERM_RENT
    return ListingIntent.MIXED


def _infer_property_category(seed: Dict[str, Any], text: str) -> PropertyCategory:
    category = (seed.get("property_category") or "").lower()
    mapping = {
        "apartment": PropertyCategory.APARTMENT,
        "house": PropertyCategory.HOUSE,
        "building": PropertyCategory.BUILDING,
        "land": PropertyCategory.LAND,
        "project": PropertyCategory.PROJECT,
        "office": PropertyCategory.OFFICE,
        "villa": PropertyCategory.VILLA,
        "hotel": PropertyCategory.HOTEL,
    }
    if category in mapping:
        return mapping[category]
    lowered = text.lower()
    # e.g. "2-стаен апартамент" (common portal copy; not always "двустаен")
    if re.search(r"\d+\s*[-–]?\s*стаен", lowered):
        return PropertyCategory.APARTMENT
    for needle, category_enum in (
        ("apartment", PropertyCategory.APARTMENT),
        ("апартамент", PropertyCategory.APARTMENT),
        ("studio", PropertyCategory.APARTMENT),
        ("студио", PropertyCategory.APARTMENT),
        ("едностаен", PropertyCategory.APARTMENT),
        ("двустаен", PropertyCategory.APARTMENT),
        ("тристаен", PropertyCategory.APARTMENT),
        ("многостаен", PropertyCategory.APARTMENT),
        ("house", PropertyCategory.HOUSE),
        ("къща", PropertyCategory.HOUSE),
        ("building", PropertyCategory.BUILDING),
        ("сграда", PropertyCategory.BUILDING),
        ("land", PropertyCategory.LAND),
        ("plot", PropertyCategory.LAND),
        ("земя", PropertyCategory.LAND),
        ("парцел", PropertyCategory.LAND),
        ("project", PropertyCategory.PROJECT),
        ("office", PropertyCategory.OFFICE),
        ("офис", PropertyCategory.OFFICE),
        ("villa", PropertyCategory.VILLA),
        ("вила", PropertyCategory.VILLA),
        ("hotel", PropertyCategory.HOTEL),
        ("хотел", PropertyCategory.HOTEL),
    ):
        if needle in lowered:
            return category_enum
    return PropertyCategory.UNKNOWN


def _extract_numeric(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = str(value).replace(",", ".")
    matches = re.findall(r"\d+(?:\.\d+)?", cleaned)
    if not matches:
        return None
    try:
        if len(matches) > 1 and all(len(part) == 3 for part in matches[1:]):
            return float("".join(matches))
        return float(matches[0])
    except ValueError:
        return None


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    return 2 * radius * math.asin(math.sqrt(a))


@dataclass
class PipelineResult:
    raw_capture: RawCapture
    parsed_listing: ParsedListing
    canonical_listing: CanonicalListing
    property_entity: PropertyEntity
    building_match: Optional[BuildingEntity]
    listing_event: ListingEvent


class GenericHtmlListingParser:
    parser_version = "v1"

    def parse(
        self,
        source: SourceRegistryEntry,
        url: str,
        html: str,
        discovered_at: datetime,
        seed: Optional[Dict[str, Any]] = None,
    ) -> ParsedListing:
        seed = seed or {}
        json_ld_blocks = _load_json_ld_blocks(html)
        flat_ld = _flatten_json_ld(json_ld_blocks)
        title_match = TITLE_RE.search(html)
        title = _clean_text(seed.get("title") or flat_ld.get("name") or (title_match.group(1) if title_match else None))
        address = seed.get("address_text") or flat_ld.get("address.streetAddress")
        city = seed.get("city") or flat_ld.get("address.addressLocality")
        region = seed.get("region") or flat_ld.get("address.addressRegion")
        price = _extract_numeric(seed.get("price") or flat_ld.get("offers.price") or flat_ld.get("price"))
        area_sqm = _extract_numeric(seed.get("area_sqm") or flat_ld.get("floorSize") or flat_ld.get("areaServed"))
        lat = _extract_numeric(seed.get("latitude") or flat_ld.get("geo.latitude"))
        lon = _extract_numeric(seed.get("longitude") or flat_ld.get("geo.longitude"))
        phones = sorted(set(PHONE_RE.findall(html) + seed.get("phones", [])))
        image_urls = list(seed.get("image_urls", []))
        image_urls.extend(
            image
            for image in [flat_ld.get("image"), flat_ld.get("photo"), *(flat_ld.get("images", []) or [])]
            if isinstance(image, str)
        )
        meta_image_match = META_IMAGE_RE.search(html)
        if meta_image_match:
            image_urls.append(meta_image_match.group(1).strip())
        image_urls = sorted(dict.fromkeys(url for url in image_urls if isinstance(url, str)))

        text_blob = " ".join(filter(None, [_clean_text(html), title, address, city, region]))

        external_id = str(seed.get("external_id") or flat_ld.get("sku") or flat_ld.get("@id") or sha1(url.encode("utf-8")).hexdigest()[:12])
        return ParsedListing(
            source_name=source.source_name,
            url=url,
            external_id=external_id,
            title=title,
            listing_intent=_infer_listing_intent(seed, text_blob),
            property_category=_infer_property_category(seed, text_blob),
            city=city,
            district=seed.get("district"),
            resort=seed.get("resort"),
            region=region,
            address_text=address,
            latitude=lat,
            longitude=lon,
            geocode_confidence=_extract_numeric(seed.get("geocode_confidence")),
            building_name=seed.get("building_name"),
            area_sqm=area_sqm,
            rooms=_extract_numeric(seed.get("rooms")),
            floor=int(seed["floor"]) if str(seed.get("floor", "")).isdigit() else None,
            total_floors=int(seed["total_floors"]) if str(seed.get("total_floors", "")).isdigit() else None,
            construction_type=seed.get("construction_type"),
            construction_year=int(seed["construction_year"]) if str(seed.get("construction_year", "")).isdigit() else None,
            stage=seed.get("stage"),
            act16_present=seed.get("act16_present"),
            price=price,
            currency=seed.get("currency") or flat_ld.get("offers.priceCurrency") or flat_ld.get("priceCurrency") or "EUR",
            fees=_extract_numeric(seed.get("fees")),
            agency_name=seed.get("agency_name"),
            owner_name=seed.get("owner_name"),
            developer_name=seed.get("developer_name"),
            broker_name=seed.get("broker_name"),
            phones=phones,
            messenger_handles=list(seed.get("messenger_handles", [])),
            outbound_channel_hints=list(seed.get("outbound_channel_hints", [])),
            description=_clean_text(seed.get("description") or flat_ld.get("description")),
            amenities=list(seed.get("amenities", [])),
            image_urls=image_urls,
            raw_payload={"json_ld": json_ld_blocks, "seed": seed, "discovered_at": discovered_at.isoformat()},
        )


class ListingNormalizer:
    @staticmethod
    def normalize(source: SourceRegistryEntry, parsed: ParsedListing, captured_at: datetime, parser_version: str) -> CanonicalListing:
        price_per_sqm = None
        if parsed.price and parsed.area_sqm:
            price_per_sqm = round(parsed.price / parsed.area_sqm, 2)
        reference_id = f"{source.source_name}:{parsed.external_id}"
        return CanonicalListing(
            source_name=parsed.source_name,
            owner_group=source.owner_group,
            listing_url=parsed.url,
            external_id=parsed.external_id,
            reference_id=reference_id,
            listing_intent=parsed.listing_intent,
            property_category=parsed.property_category,
            city=parsed.city,
            district=parsed.district,
            resort=parsed.resort,
            region=parsed.region,
            address_text=parsed.address_text,
            latitude=parsed.latitude,
            longitude=parsed.longitude,
            geocode_confidence=parsed.geocode_confidence,
            building_name=parsed.building_name,
            area_sqm=parsed.area_sqm,
            rooms=parsed.rooms,
            floor=parsed.floor,
            total_floors=parsed.total_floors,
            construction_type=parsed.construction_type,
            construction_year=parsed.construction_year,
            stage=parsed.stage,
            act16_present=parsed.act16_present,
            price=parsed.price,
            currency=parsed.currency,
            fees=parsed.fees,
            price_per_sqm=price_per_sqm,
            broker_name=parsed.broker_name,
            agency_name=parsed.agency_name,
            owner_name=parsed.owner_name,
            developer_name=parsed.developer_name,
            phones=parsed.phones,
            messenger_handles=parsed.messenger_handles,
            outbound_channel_hints=parsed.outbound_channel_hints,
            description=parsed.description,
            amenities=parsed.amenities,
            image_urls=parsed.image_urls,
            first_seen=captured_at,
            last_seen=captured_at,
            last_changed_at=captured_at,
            removed_at=None,
            parser_version=parser_version,
            crawl_provenance={"source_name": source.source_name, "captured_at": captured_at.isoformat()},
        )


class DeduplicationScorer:
    @staticmethod
    def score(left: CanonicalListing, right: CanonicalListing) -> float:
        score = 0.0
        if left.reference_id == right.reference_id:
            return 1.0
        if left.address_text and right.address_text and left.address_text.lower() == right.address_text.lower():
            score += 0.35
        if left.city and right.city and left.city.lower() == right.city.lower():
            score += 0.1
        if left.building_name and right.building_name and left.building_name.lower() == right.building_name.lower():
            score += 0.15
        if left.phones and right.phones and set(left.phones) & set(right.phones):
            score += 0.2
        if left.price and right.price:
            delta = abs(left.price - right.price) / max(left.price, right.price)
            score += max(0.0, 0.1 - min(delta, 0.1))
        if left.area_sqm and right.area_sqm:
            delta = abs(left.area_sqm - right.area_sqm) / max(left.area_sqm, right.area_sqm)
            score += max(0.0, 0.1 - min(delta, 0.1))
        if None not in (left.latitude, left.longitude, right.latitude, right.longitude):
            distance = haversine_km(left.latitude, left.longitude, right.latitude, right.longitude)
            score += 0.1 if distance < 0.1 else 0.05 if distance < 0.5 else 0.0
        return round(min(score, 0.99), 4)


class BuildingMatcher:
    @staticmethod
    def match(listing: CanonicalListing, buildings: Iterable[BuildingEntity], max_distance_km: float = 0.15) -> Optional[BuildingEntity]:
        if listing.latitude is None or listing.longitude is None:
            return None
        best_match: Optional[BuildingEntity] = None
        best_distance = max_distance_km
        for building in buildings:
            distance = haversine_km(listing.latitude, listing.longitude, building.latitude, building.longitude)
            if distance <= best_distance:
                best_distance = distance
                best_match = building
        return best_match


class EntityMatcher:
    @staticmethod
    def property_entity_for(listing: CanonicalListing) -> PropertyEntity:
        dedupe_components = [
            listing.city or "",
            listing.address_text or "",
            listing.building_name or "",
            str(round(listing.area_sqm or 0.0, 1)),
        ]
        dedupe_key = sha1("|".join(dedupe_components).lower().encode("utf-8")).hexdigest()
        return PropertyEntity(
            property_id=dedupe_key[:16],
            dedupe_key=dedupe_key,
            canonical_address=listing.address_text,
            canonical_city=listing.city,
            canonical_building_name=listing.building_name,
            latitude=listing.latitude,
            longitude=listing.longitude,
        )


class StandardIngestionPipeline:
    def __init__(self, parser: Optional[GenericHtmlListingParser] = None):
        self.parser = parser or GenericHtmlListingParser()

    def process_listing_detail(
        self,
        source: SourceRegistryEntry,
        url: str,
        html: str,
        captured_at: Optional[datetime] = None,
        summary_fields: Optional[Dict[str, Any]] = None,
        buildings: Iterable[BuildingEntity] = (),
    ) -> PipelineResult:
        captured_at = captured_at or datetime.utcnow()

        raw_capture = RawCapture(
            source_name=source.source_name,
            url=url,
            content_type="text/html",
            body=html,
            fetched_at=captured_at,
            parser_version=self.parser.parser_version,
            metadata={"summary_fields": summary_fields or {}},
        )

        parsed = self.parser.parse(source, url, html, captured_at, summary_fields)
        canonical = ListingNormalizer.normalize(source, parsed, captured_at, self.parser.parser_version)
        property_entity = EntityMatcher.property_entity_for(canonical)
        building_match = BuildingMatcher.match(canonical, buildings)
        event = ListingEvent(
            event_id=sha1(f"{canonical.reference_id}:{captured_at.isoformat()}".encode("utf-8")).hexdigest()[:18],
            listing_reference_id=canonical.reference_id,
            event_type=LifecycleEventType.CREATED,
            emitted_at=captured_at,
            details={"building_id": getattr(building_match, "building_id", None)},
        )

        return PipelineResult(
            raw_capture=raw_capture,
            parsed_listing=parsed,
            canonical_listing=canonical,
            property_entity=property_entity,
            building_match=building_match,
            listing_event=event,
        )
