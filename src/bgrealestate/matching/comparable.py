"""Conservative property fingerprinting and comparable-search scoring.

This module is intentionally pure and fixture-friendly. Live scraping, DB access,
and source-specific parsing stay outside this layer so tests can exercise the
matching rules without network or runtime state.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from hashlib import sha1
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import urlparse


_PUNCT_RE = re.compile(r"[.,;:!?\"'()\[\]{}]")
_SPACE_RE = re.compile(r"\s+")
_TOKEN_RE = re.compile(r"[\w\u0400-\u04ff]+", re.UNICODE)
_ON_REQUEST_STATUSES = {"on_request", "undefined", "not_listed", "price_on_request"}
_BAD_PUBLICATION_TYPES = {"multi_unit_or_development", "grouped_publication", "development"}
_BAD_ACCEPTANCE = {"not_single_entity", "grouped_publication", "lost", "rejected"}
_INACTIVE_STATUSES = {"inactive", "removed", "expired", "lost"}
_COMPATIBLE_CATEGORY_GROUPS = (
    {"apartment", "studio", "flat"},
    {"house", "villa"},
    {"land", "plot", "parcel"},
    {"office", "commercial", "shop"},
    {"building", "project", "development"},
)


@dataclass(frozen=True)
class PropertyFingerprint:
    source_name: str = ""
    source_tier: int | None = None
    reference_id: str = ""
    listing_url: str = ""
    external_id: str = ""
    title: str = ""
    description: str = ""
    listing_intent: str = ""
    property_category: str = ""
    city: str = ""
    district: str = ""
    address_text: str = ""
    latitude: float | None = None
    longitude: float | None = None
    price: float | None = None
    currency: str = ""
    price_status: str = ""
    area_sqm: float | None = None
    rooms: float | None = None
    floor: int | None = None
    total_floors: int | None = None
    image_urls: tuple[str, ...] = ()
    local_image_files: tuple[str, ...] = ()
    phones: tuple[str, ...] = ()
    agency_name: str = ""
    source_publication_type: str = ""
    scrape_status: str = ""
    scrape_acceptance_status: str = ""
    listing_status: str = ""
    provenance: Mapping[str, Any] = field(default_factory=dict)

    @property
    def has_coordinates(self) -> bool:
        return self.latitude is not None and self.longitude is not None

    @property
    def stable_url_key(self) -> str:
        return normalize_url_key(self.listing_url)


@dataclass(frozen=True)
class MatchDecision:
    classification: str
    is_single_unit_candidate: bool
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class MatchResult:
    candidate: PropertyFingerprint
    score: float
    match_class: str
    score_components: Mapping[str, float]
    evidence: tuple[str, ...]
    conflicts: tuple[str, ...]


def normalize_text(value: Any) -> str:
    text = str(value or "").lower().strip()
    text = _PUNCT_RE.sub(" ", text)
    return _SPACE_RE.sub(" ", text).strip()


def normalize_url_key(url: str | None) -> str:
    if not url:
        return ""
    try:
        parsed = urlparse(str(url))
    except Exception:
        return normalize_text(url)
    host = parsed.netloc.lower().removeprefix("www.")
    path = re.sub(r"/+", "/", parsed.path).rstrip("/")
    return f"{host}{path}"


def token_set(*values: Any) -> set[str]:
    joined = " ".join(str(v or "") for v in values)
    return {tok for tok in _TOKEN_RE.findall(joined.lower()) if len(tok) >= 3}


def jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _as_str_tuple(value: Any) -> tuple[str, ...]:
    if not value:
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(str(item) for item in value if item)


def _provenance_field(row: Mapping[str, Any], key: str) -> Any:
    if key in row:
        return row.get(key)
    provenance = row.get("crawl_provenance")
    if isinstance(provenance, Mapping):
        return provenance.get(key)
    return None


def fingerprint_from_mapping(
    row: Mapping[str, Any],
    *,
    source_tier: int | None = None,
    source_name: str | None = None,
) -> PropertyFingerprint:
    provenance = dict(row.get("crawl_provenance") or {})
    for key in (
        "price_status",
        "source_publication_type",
        "scrape_status",
        "scrape_acceptance_status",
        "listing_status",
        "suspected_multi_unit_publication",
        "photo_count_remote",
        "photo_count_local",
    ):
        if key in row and key not in provenance:
            provenance[key] = row.get(key)

    return PropertyFingerprint(
        source_name=str(source_name or row.get("source_name") or ""),
        source_tier=source_tier,
        reference_id=str(row.get("reference_id") or ""),
        listing_url=str(row.get("listing_url") or row.get("canonical_url") or ""),
        external_id=str(row.get("external_id") or ""),
        title=str(row.get("title") or ""),
        description=str(row.get("description") or ""),
        listing_intent=normalize_text(row.get("listing_intent") or ""),
        property_category=normalize_text(row.get("property_category") or ""),
        city=normalize_text(row.get("city") or ""),
        district=normalize_text(row.get("district") or ""),
        address_text=normalize_text(row.get("address_text") or ""),
        latitude=_as_float(row.get("latitude")),
        longitude=_as_float(row.get("longitude")),
        price=_as_float(row.get("price")),
        currency=str(row.get("currency") or ""),
        price_status=normalize_text(_provenance_field(row, "price_status") or ""),
        area_sqm=_as_float(row.get("area_sqm")),
        rooms=_as_float(row.get("rooms")),
        floor=_as_int(row.get("floor")),
        total_floors=_as_int(row.get("total_floors")),
        image_urls=tuple(dict.fromkeys(_as_str_tuple(row.get("image_urls")))),
        local_image_files=tuple(dict.fromkeys(_as_str_tuple(row.get("local_image_files")))),
        phones=tuple(dict.fromkeys(_as_str_tuple(row.get("phones")))),
        agency_name=str(row.get("agency_name") or ""),
        source_publication_type=normalize_text(_provenance_field(row, "source_publication_type") or ""),
        scrape_status=normalize_text(_provenance_field(row, "scrape_status") or ""),
        scrape_acceptance_status=normalize_text(_provenance_field(row, "scrape_acceptance_status") or ""),
        listing_status=normalize_text(_provenance_field(row, "listing_status") or ""),
        provenance=provenance,
    )


def classify_source_publication(fp: PropertyFingerprint) -> MatchDecision:
    blockers: list[str] = []
    if not fp.listing_url:
        blockers.append("missing_detail_url")
    if fp.provenance.get("suspected_multi_unit_publication") is True:
        blockers.append("grouped_or_development_publication")
    if fp.source_publication_type in _BAD_PUBLICATION_TYPES:
        blockers.append("grouped_or_development_publication")
    if fp.scrape_acceptance_status in _BAD_ACCEPTANCE:
        blockers.append("not_accepted_single_entity")
    if fp.listing_status in _INACTIVE_STATUSES:
        blockers.append("inactive_or_removed_source_listing")
    if fp.price is None and fp.price_status not in _ON_REQUEST_STATUSES:
        blockers.append("missing_price_or_explicit_price_status")
    if fp.area_sqm is None and not fp.address_text and not fp.has_coordinates:
        blockers.append("missing_area_and_location_evidence")

    if blockers:
        return MatchDecision("source_publication_only", False, tuple(dict.fromkeys(blockers)))
    return MatchDecision("single_unit_candidate", True, ())


def category_compatible(left: str, right: str) -> bool:
    left = normalize_text(left)
    right = normalize_text(right)
    if not left or not right:
        return True
    if left == right:
        return True
    return any(left in group and right in group for group in _COMPATIBLE_CATEGORY_GROUPS)


def intent_compatible(left: str, right: str) -> bool:
    left = normalize_text(left)
    right = normalize_text(right)
    if not left or not right:
        return True
    if left == right:
        return True
    rent_terms = {"rent", "long_term_rent", "short_term_rent"}
    return left in rent_terms and right in rent_terms


def _ratio_closeness(left: float | None, right: float | None, *, perfect: float, good: float, weak: float) -> tuple[float, str | None]:
    if left is None or right is None or left <= 0 or right <= 0:
        return 0.0, None
    delta = abs(left - right) / max(left, right)
    if delta <= perfect:
        return 1.0, None
    if delta <= good:
        return 0.75, None
    if delta <= weak:
        return 0.4, None
    return 0.0, "too_different"


def haversine_km(left: PropertyFingerprint, right: PropertyFingerprint) -> float | None:
    if not left.has_coordinates or not right.has_coordinates:
        return None
    assert left.latitude is not None and left.longitude is not None
    assert right.latitude is not None and right.longitude is not None
    radius = 6371.0
    d_lat = math.radians(right.latitude - left.latitude)
    d_lon = math.radians(right.longitude - left.longitude)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(left.latitude))
        * math.cos(math.radians(right.latitude))
        * math.sin(d_lon / 2) ** 2
    )
    return 2 * radius * math.asin(math.sqrt(a))


def image_overlap(left: Sequence[str], right: Sequence[str]) -> float:
    left_keys = {normalize_url_key(u) for u in left if u}
    right_keys = {normalize_url_key(u) for u in right if u}
    return jaccard(left_keys, right_keys)


def score_property_pair(
    query: PropertyFingerprint,
    candidate: PropertyFingerprint,
    *,
    include_same_source: bool = False,
) -> MatchResult | None:
    if not include_same_source and query.source_name and query.source_name == candidate.source_name:
        return None
    if query.stable_url_key and query.stable_url_key == candidate.stable_url_key:
        return None

    components: dict[str, float] = {}
    evidence: list[str] = []
    conflicts: list[str] = []

    if intent_compatible(query.listing_intent, candidate.listing_intent):
        components["intent"] = 0.08 if query.listing_intent and query.listing_intent == candidate.listing_intent else 0.04
    else:
        conflicts.append("intent_mismatch")

    if category_compatible(query.property_category, candidate.property_category):
        components["category"] = 0.08 if query.property_category and query.property_category == candidate.property_category else 0.04
    else:
        conflicts.append("category_mismatch")

    if query.city and candidate.city:
        if query.city == candidate.city:
            components["city"] = 0.08
        else:
            conflicts.append("city_mismatch")
    if query.district and candidate.district and query.district == candidate.district:
        components["district"] = 0.06
    if query.address_text and candidate.address_text:
        if query.address_text == candidate.address_text:
            components["address"] = 0.18
            evidence.append("same_normalized_address")
        else:
            address_overlap = jaccard(token_set(query.address_text), token_set(candidate.address_text))
            if address_overlap >= 0.55:
                components["address"] = 0.1
                evidence.append("similar_address_tokens")

    distance = haversine_km(query, candidate)
    if distance is not None:
        if distance <= 0.05:
            components["geo"] = 0.18
            evidence.append("coordinates_within_50m")
        elif distance <= 0.25:
            components["geo"] = 0.13
            evidence.append("coordinates_within_250m")
        elif distance <= 1.0:
            components["geo"] = 0.07
        elif distance > 15.0:
            conflicts.append("coordinates_far_apart")

    area_factor, area_conflict = _ratio_closeness(query.area_sqm, candidate.area_sqm, perfect=0.03, good=0.10, weak=0.20)
    if area_factor:
        components["area"] = round(0.15 * area_factor, 4)
        evidence.append("similar_area")
    elif area_conflict:
        conflicts.append("area_too_different")

    price_factor, price_conflict = _ratio_closeness(query.price, candidate.price, perfect=0.03, good=0.12, weak=0.25)
    if price_factor:
        components["price"] = round(0.14 * price_factor, 4)
        evidence.append("similar_price")
    elif price_conflict:
        conflicts.append("price_too_different")
    elif query.price_status and query.price_status == candidate.price_status and query.price_status in _ON_REQUEST_STATUSES:
        components["price_status"] = 0.04

    if query.rooms is not None and candidate.rooms is not None:
        if query.rooms == candidate.rooms:
            components["rooms"] = 0.05
        elif abs(query.rooms - candidate.rooms) <= 1:
            components["rooms"] = 0.02
    if query.floor is not None and candidate.floor is not None and query.floor == candidate.floor:
        components["floor"] = 0.03

    text_overlap = jaccard(token_set(query.title, query.description), token_set(candidate.title, candidate.description))
    if text_overlap >= 0.25:
        components["text"] = min(0.08, round(text_overlap * 0.16, 4))
        evidence.append("similar_title_or_description")

    image_score = image_overlap(query.image_urls, candidate.image_urls)
    if image_score >= 0.2:
        components["image_overlap"] = min(0.16, round(image_score * 0.2, 4))
        evidence.append("shared_image_urls")

    phone_overlap = jaccard(set(query.phones), set(candidate.phones))
    if phone_overlap > 0:
        components["contact_overlap"] = 0.03
        evidence.append("shared_contact_hint")

    candidate_decision = classify_source_publication(candidate)
    if candidate_decision.is_single_unit_candidate:
        components["candidate_quality"] = 0.03
    else:
        conflicts.extend(f"candidate_{blocker}" for blocker in candidate_decision.blockers)

    raw_score = round(min(sum(components.values()), 1.0), 4)
    identity_strength = sum(components.get(k, 0.0) for k in ("address", "geo", "image_overlap", "text"))
    comparable_strength = sum(components.get(k, 0.0) for k in ("city", "district", "area", "price", "rooms", "category", "intent"))

    if raw_score >= 0.68 and identity_strength >= 0.28 and not {"city_mismatch", "category_mismatch", "intent_mismatch"} & set(conflicts):
        match_class = "same_property_candidate"
    elif raw_score >= 0.38 and comparable_strength >= 0.26 and not {"city_mismatch", "category_mismatch", "intent_mismatch"} & set(conflicts):
        match_class = "comparable_property"
    else:
        match_class = "weak_candidate"

    return MatchResult(
        candidate=candidate,
        score=raw_score,
        match_class=match_class,
        score_components=components,
        evidence=tuple(dict.fromkeys(evidence)),
        conflicts=tuple(dict.fromkeys(conflicts)),
    )


def rank_comparable_properties(
    query: PropertyFingerprint,
    candidates: Iterable[PropertyFingerprint],
    *,
    include_same_source: bool = False,
    min_score: float = 0.25,
    limit: int = 50,
) -> list[MatchResult]:
    results: list[MatchResult] = []
    for candidate in candidates:
        result = score_property_pair(query, candidate, include_same_source=include_same_source)
        if result is None or result.score < min_score:
            continue
        results.append(result)
    results.sort(key=lambda item: (item.match_class == "same_property_candidate", item.score), reverse=True)
    return results[:limit]


def fingerprint_id(fp: PropertyFingerprint) -> str:
    seed = "|".join(
        [
            fp.source_name,
            fp.reference_id,
            fp.stable_url_key,
            fp.city,
            fp.address_text,
            str(round(fp.area_sqm or 0, 1)),
        ]
    )
    return sha1(seed.encode("utf-8")).hexdigest()[:16]
