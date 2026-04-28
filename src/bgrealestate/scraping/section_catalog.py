"""Curated Varna controlled-crawl bucket catalog for tier-1/2 sources.

This is the durable source of truth for Stage 2 activation planning:

- one logical bucket per ``source x segment`` (verticals are metadata within the bucket)
- exact Varna entrypoints where known; national fallback routes where not
- strict separation between:
  - ``pattern_status`` (can detail pages be parsed end-to-end?)
  - ``support_status`` (is this source/segment ready for controlled crawl planning?)

The actual persisted manifest is generated from this catalog.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..source_registry import SourceRegistry

REPO = Path(__file__).resolve().parents[3]
PATTERN_STATUS_PATH = REPO / "docs" / "exports" / "tier12-pattern-status.json"

SEGMENT_ORDER: tuple[str, ...] = (
    "buy_personal",
    "buy_commercial",
    "rent_personal",
    "rent_commercial",
)

RUNTIME_SOURCE_KEYS: dict[str, str] = {
    "Homes.bg": "homes_bg",
    "imot.bg": "imot_bg",
    "alo.bg": "alo_bg",
    "Address.bg": "address_bg",
    "BulgarianProperties": "bulgarianproperties",
    "SUPRIMMO": "suprimmo",
    "LUXIMMO": "luximmo",
    "property.bg": "property_bg",
    "Bazar.bg": "bazar_bg",
    "Domaza": "domaza",
    "Yavlena": "yavlena",
    "Home2U": "home2u",
    "OLX.bg": "olx_bg",
}

COMMON_VARNA_FILTER: dict[str, Any] = {
    "mode": "strict_varna_only",
    "enforced_at": ["source_entry", "list_page", "detail_page", "parse", "validation"],
    "city_tokens_bg": ["варна", "гр. варна", "област варна"],
    "city_tokens_lat": ["varna", "varna city", "varna region"],
    "region_tokens_bg": ["варненска област", "обл. варна"],
    "region_tokens_lat": ["varna province", "varna municipality"],
    "reject_other_major_cities": True,
}

DEFAULT_DETAIL_FIELDS: list[str] = [
    "source_name",
    "source_section_id",
    "segment_key",
    "vertical_key",
    "listing_url",
    "detail_url_canonical",
    "external_id",
    "title",
    "price",
    "currency",
    "area_sqm",
    "rooms",
    "floor",
    "total_floors",
    "construction_type",
    "property_category",
    "address_text",
    "region_key",
    "city",
    "district",
    "description",
    "combined_text",
    "raw_text_fallback",
    "structured_extra",
    "image_urls",
    "crawl_provenance",
]

DEFAULT_STRUCTURED_SIGNALS: list[str] = [
    "price",
    "area_sqm",
    "rooms",
    "floor",
    "city_or_address",
]


@dataclass(frozen=True)
class SegmentBlueprint:
    segment_key: str
    entry_urls: tuple[str, ...] = ()
    supported_verticals: tuple[str, ...] = ("all",)
    discovery_mode: str = "list_page_html"
    entry_scope: str = "national_fallback_with_varna_filter"
    listing_pattern: str | None = None
    page_suffix: str | None = None
    support_status: str = "supported"
    skip_reason: str | None = None
    implementation_notes: str = ""
    discovery_templates: dict[str, Any] | None = None
    default_active: bool = True


def _pattern_status_index() -> dict[str, dict[str, Any]]:
    if not PATTERN_STATUS_PATH.exists():
        return {}
    payload = json.loads(PATTERN_STATUS_PATH.read_text(encoding="utf-8"))
    return {row["source_name"]: row for row in payload.get("sources", [])}


def _allowed_by_legal_mode(legal_mode: str) -> bool:
    return legal_mode in {"public_crawl_with_review", "official_api_allowed"}


def _empty_segment(segment_key: str, *, reason: str, status: str = "unsupported") -> SegmentBlueprint:
    return SegmentBlueprint(
        segment_key=segment_key,
        support_status=status,
        skip_reason=reason,
        default_active=False,
    )


def _curated_blueprints() -> dict[str, dict[str, SegmentBlueprint]]:
    return {
        "Homes.bg": {
            "buy_personal": SegmentBlueprint(
                segment_key="buy_personal",
                discovery_mode="api_results",
                entry_scope="varna_only_api_filter",
                supported_verticals=("apartments", "houses", "land", "new_build"),
                implementation_notes="Use Homes API offerType=1 with city=varna; classify personal residential from cards/detail pages.",
                discovery_templates={
                    "api_templates": [
                        "https://www.homes.bg/api/offers?currPage={page}&lang=bg&offerType=1&city=varna",
                    ],
                },
            ),
            "buy_commercial": _empty_segment(
                "buy_commercial",
                reason="Commercial category filter is not yet locked for the Homes Varna API path.",
                status="pattern_incomplete",
            ),
            "rent_personal": SegmentBlueprint(
                segment_key="rent_personal",
                discovery_mode="api_results",
                entry_scope="varna_only_api_filter",
                supported_verticals=("apartments", "houses"),
                implementation_notes="Use Homes API offerType=2 with city=varna; classify residential rent on card/detail.",
                discovery_templates={
                    "api_templates": [
                        "https://www.homes.bg/api/offers?currPage={page}&lang=bg&offerType=2&city=varna",
                    ],
                },
            ),
            "rent_commercial": _empty_segment(
                "rent_commercial",
                reason="Commercial rental filter is not yet locked for the Homes Varna API path.",
                status="pattern_incomplete",
            ),
        },
        "imot.bg": {
            "buy_personal": SegmentBlueprint(
                segment_key="buy_personal",
                entry_urls=("https://www.imot.bg/obiavi/prodazhbi/grad-varna",),
                supported_verticals=("apartments", "houses", "land", "new_build"),
                listing_pattern=r"imot\.bg/obiava-",
                page_suffix="/p-{}",
                entry_scope="varna_only_url",
                implementation_notes="Exact Varna sales route exists; residential and land classes are separated during list/detail parsing.",
            ),
            "buy_commercial": _empty_segment(
                "buy_commercial",
                reason="Commercial-specific Varna discovery routes are not yet persisted separately.",
                status="pattern_incomplete",
            ),
            "rent_personal": SegmentBlueprint(
                segment_key="rent_personal",
                entry_urls=("https://www.imot.bg/obiavi/naemi/grad-varna",),
                supported_verticals=("apartments", "houses"),
                listing_pattern=r"imot\.bg/obiava-",
                page_suffix="/p-{}",
                entry_scope="varna_only_url",
                implementation_notes="Exact Varna rentals route exists; residential classes are filtered at card/detail parse.",
            ),
            "rent_commercial": _empty_segment(
                "rent_commercial",
                reason="Commercial rental routes for Varna are not yet persisted as reusable patterns.",
                status="pattern_incomplete",
            ),
        },
        "Address.bg": {
            "buy_personal": SegmentBlueprint(
                segment_key="buy_personal",
                entry_urls=("https://address.bg/sale/varna/l4694",),
                supported_verticals=("apartments", "houses", "land", "new_build"),
                listing_pattern=r"address\.bg/.+-offer\d{5,}",
                page_suffix="?page={}",
                entry_scope="varna_only_url",
                implementation_notes="Exact Varna sales entry is known and saved.",
            ),
            "buy_commercial": _empty_segment(
                "buy_commercial",
                reason="Commercial route split on Address.bg is not yet expressed as a reusable Varna bucket.",
                status="pattern_incomplete",
            ),
            "rent_personal": SegmentBlueprint(
                segment_key="rent_personal",
                entry_urls=("https://address.bg/rent",),
                supported_verticals=("apartments", "houses"),
                listing_pattern=r"address\.bg/.+-offer\d{5,}",
                page_suffix="?page={}",
                implementation_notes="Varna rental route is not yet persisted separately; current fallback uses rent listing pages plus strict Varna filtering.",
            ),
            "rent_commercial": _empty_segment(
                "rent_commercial",
                reason="Commercial rental route split on Address.bg is not yet saved as a reusable Varna bucket.",
                status="pattern_incomplete",
            ),
        },
        "BulgarianProperties": {
            "buy_personal": SegmentBlueprint(
                segment_key="buy_personal",
                entry_urls=(
                    "https://www.bulgarianproperties.com/properties_for_sale_in_Bulgaria/index.html",
                    "https://www.bulgarianproperties.com/1-bedroom_apartments_in_Bulgaria/index.html",
                    "https://www.bulgarianproperties.com/2-bedroom_apartments_in_Bulgaria/index.html",
                    "https://www.bulgarianproperties.com/3-bedroom_apartments_in_Bulgaria/index.html",
                    "https://www.bulgarianproperties.com/houses_in_Bulgaria/index.html",
                    "https://www.bulgarianproperties.com/land_for_sale_in_Bulgaria/index.html",
                ),
                supported_verticals=("apartments", "houses", "land", "new_build"),
                listing_pattern=r"bulgarianproperties\.com/.+AD\d+BG",
                page_suffix="?page={}",
                implementation_notes="National entrypoints only; enforce Varna at card/detail/validation stages.",
            ),
            "buy_commercial": _empty_segment(
                "buy_commercial",
                reason="Commercial routes are not yet separated in the saved BulgarianProperties pattern set.",
                status="pattern_incomplete",
            ),
            "rent_personal": SegmentBlueprint(
                segment_key="rent_personal",
                entry_urls=("https://www.bulgarianproperties.com/properties_for_rent_in_Bulgaria/index.html",),
                supported_verticals=("apartments", "houses"),
                listing_pattern=r"bulgarianproperties\.com/.+AD\d+BG",
                page_suffix="?page={}",
                implementation_notes="National rental entrypoint; enforce Varna at downstream stages.",
            ),
            "rent_commercial": _empty_segment(
                "rent_commercial",
                reason="Commercial rental routes are not yet separated in the saved BulgarianProperties pattern set.",
                status="pattern_incomplete",
            ),
        },
        "SUPRIMMO": {
            "buy_personal": SegmentBlueprint(
                segment_key="buy_personal",
                entry_urls=(
                    "https://www.suprimmo.bg/bulgaria/apartamenti/",
                    "https://www.suprimmo.bg/bulgaria/kushti-vili/",
                    "https://www.suprimmo.bg/bulgaria/partseli/",
                ),
                supported_verticals=("apartments", "houses", "land", "new_build"),
                listing_pattern=r"suprimmo\.bg/imot-\d{5,}",
                page_suffix="/page/{}/",
                implementation_notes="National vertical routes; Varna enforced in list/detail/validation.",
            ),
            "buy_commercial": _empty_segment(
                "buy_commercial",
                reason="Commercial category routes are not yet saved as reusable SUPRIMMO Varna sections.",
                status="pattern_incomplete",
            ),
            "rent_personal": SegmentBlueprint(
                segment_key="rent_personal",
                entry_urls=("https://www.suprimmo.bg/naem/bulgaria/selectsya/",),
                supported_verticals=("apartments", "houses"),
                listing_pattern=r"suprimmo\.bg/imot-\d{5,}",
                page_suffix="/page/{}/",
                implementation_notes="Rental selection route exists, but requires downstream Varna filtering.",
            ),
            "rent_commercial": _empty_segment(
                "rent_commercial",
                reason="Commercial rental route split is not yet mapped for SUPRIMMO.",
                status="pattern_incomplete",
            ),
        },
        "LUXIMMO": {
            "buy_personal": SegmentBlueprint(
                segment_key="buy_personal",
                entry_urls=("https://www.luximmo.bg/apartamenti/",),
                supported_verticals=("apartments", "houses", "new_build"),
                listing_pattern=r"luximmo\.bg/.+-\d{5,}-[^\"'<> ]+\.html",
                page_suffix="index{}.html",
                implementation_notes="Saved routes focus on apartments; additional residential classes still classify via detail pages.",
            ),
            "buy_commercial": _empty_segment(
                "buy_commercial",
                reason="Commercial LUXIMMO routes are not yet persisted in the reusable bucket catalog.",
                status="pattern_incomplete",
            ),
            "rent_personal": _empty_segment(
                "rent_personal",
                reason="Saved LUXIMMO runtime currently proves sale detail capture, not reusable rent discovery.",
                status="pattern_incomplete",
            ),
            "rent_commercial": _empty_segment(
                "rent_commercial",
                reason="Commercial rental routes are not yet mapped for LUXIMMO.",
                status="pattern_incomplete",
            ),
        },
        "property.bg": {
            "buy_personal": SegmentBlueprint(
                segment_key="buy_personal",
                entry_urls=(
                    "https://www.property.bg/bulgaria/apartments/",
                    "https://www.property.bg/sales/bulgaria/selection/",
                ),
                supported_verticals=("apartments", "houses", "land", "new_build"),
                listing_pattern=r"property\.bg/property-\d{5,}",
                page_suffix="/page/{}/",
                implementation_notes="National sale routes are saved; Varna enforced downstream.",
            ),
            "buy_commercial": _empty_segment(
                "buy_commercial",
                reason="Commercial-specific property.bg routes are not yet saved as reusable Varna buckets.",
                status="pattern_incomplete",
            ),
            "rent_personal": SegmentBlueprint(
                segment_key="rent_personal",
                entry_urls=("https://www.property.bg/rentals/bulgaria/selection/",),
                supported_verticals=("apartments", "houses"),
                listing_pattern=r"property\.bg/property-\d{5,}",
                page_suffix="/page/{}/",
                implementation_notes="National rent route exists; enforce Varna in list/detail/validation.",
            ),
            "rent_commercial": _empty_segment(
                "rent_commercial",
                reason="Commercial rental property.bg routes are not yet saved as reusable Varna buckets.",
                status="pattern_incomplete",
            ),
        },
        "Bazar.bg": {
            "buy_personal": SegmentBlueprint(
                segment_key="buy_personal",
                entry_urls=(
                    "https://bazar.bg/obiavi/apartamenti",
                    "https://bazar.bg/obiavi/kashti-i-vili",
                    "https://bazar.bg/obiavi/zemya",
                    "https://bazar.bg/obiavi/garazhi-i-parkoingi",
                ),
                supported_verticals=("apartments", "houses", "land", "garages"),
                listing_pattern=r"bazar\.bg/obiava-\d{5,}",
                page_suffix="?page={}",
                implementation_notes="National classifieds routes; Varna enforced downstream.",
            ),
            "buy_commercial": _empty_segment(
                "buy_commercial",
                reason="Commercial verticals are not yet persisted as reusable Bazar.bg buckets.",
                status="pattern_incomplete",
            ),
            "rent_personal": _empty_segment(
                "rent_personal",
                reason="Saved Bazar.bg runtime currently proves sale-side discovery only.",
                status="pattern_incomplete",
            ),
            "rent_commercial": _empty_segment(
                "rent_commercial",
                reason="Commercial rental routes are not yet mapped for Bazar.bg.",
                status="pattern_incomplete",
            ),
        },
        "alo.bg": {
            "buy_personal": SegmentBlueprint(
                segment_key="buy_personal",
                entry_urls=(
                    "https://www.alo.bg/obiavi/imoti-prodajbi/apartamenti-stai/",
                    "https://www.alo.bg/obiavi/imoti-prodajbi/kashti-vili/",
                    "https://www.alo.bg/obiavi/imoti-prodajbi/parzeli-za-zastroiavane-investicionni-proekti/",
                    "https://www.alo.bg/obiavi/imoti-prodajbi/zemedelska-zemia-gradini-lozia-gora/",
                ),
                supported_verticals=("apartments", "houses", "land"),
                listing_pattern=r"alo\.bg/.+-\d{5,}",
                page_suffix="?page={}",
                implementation_notes="National ALO routes; no locked reusable Varna entry URLs yet.",
            ),
            "buy_commercial": _empty_segment(
                "buy_commercial",
                reason="Commercial sale routes are not yet saved as reusable ALO buckets.",
                status="pattern_incomplete",
            ),
            "rent_personal": SegmentBlueprint(
                segment_key="rent_personal",
                entry_urls=("https://www.alo.bg/obiavi/imoti-naemi/apartamenti-stai/",),
                supported_verticals=("apartments",),
                listing_pattern=r"alo\.bg/.+-\d{5,}",
                page_suffix="?page={}",
                implementation_notes="National rent route; strict Varna filtering required downstream.",
            ),
            "rent_commercial": _empty_segment(
                "rent_commercial",
                reason="Commercial rental routes are not yet saved as reusable ALO buckets.",
                status="pattern_incomplete",
            ),
        },
        "OLX.bg": {
            "buy_personal": SegmentBlueprint(
                segment_key="buy_personal",
                entry_urls=("https://www.olx.bg/nedvizhimi-imoti/",),
                supported_verticals=("apartments", "houses", "land", "garages"),
                listing_pattern=r"olx\.bg/d/ad/",
                page_suffix="?page={}",
                implementation_notes="National OLX real-estate route; Varna must be enforced on list cards and detail pages.",
            ),
            "buy_commercial": _empty_segment(
                "buy_commercial",
                reason="Commercial OLX route split is not yet locked in the saved pattern set.",
                status="pattern_incomplete",
            ),
            "rent_personal": SegmentBlueprint(
                segment_key="rent_personal",
                entry_urls=("https://www.olx.bg/nedvizhimi-imoti/",),
                supported_verticals=("apartments", "houses"),
                listing_pattern=r"olx\.bg/d/ad/",
                page_suffix="?page={}",
                implementation_notes="OLX mixes sale/rent in one route; operation segment is assigned from detail/card parsing.",
            ),
            "rent_commercial": _empty_segment(
                "rent_commercial",
                reason="Commercial OLX split is not yet locked in reusable filters.",
                status="pattern_incomplete",
            ),
        },
        "Domaza": {
            "buy_personal": SegmentBlueprint(
                segment_key="buy_personal",
                entry_urls=(
                    "https://www.domaza.bg/property/index/search/1/s/572da6146f10beb4bf6333d75039731a4d2b9902",
                    "https://www.domaza.bg/property/index/search/1/s/c8a3ad4db8f37d4e8b31fe9db66bc4d1f537ba5a",
                ),
                supported_verticals=("apartments", "houses", "land", "new_build"),
                listing_pattern=r"domaza\.(bg|biz)/.+ID\d+",
                page_suffix="?page={}",
                support_status="pattern_incomplete",
                default_active=False,
                implementation_notes="Search routes are known, but source is not yet patterned enough for controlled activation.",
            ),
            "buy_commercial": _empty_segment(
                "buy_commercial",
                reason="Commercial routes are not yet saved as reusable Domaza buckets.",
                status="pattern_incomplete",
            ),
            "rent_personal": SegmentBlueprint(
                segment_key="rent_personal",
                entry_urls=("https://www.domaza.bg/property/index/search/1/s/e8780bcda8fa201940f1ce87e404f870d0c5c3fc",),
                supported_verticals=("apartments", "houses"),
                listing_pattern=r"domaza\.(bg|biz)/.+ID\d+",
                page_suffix="?page={}",
                support_status="pattern_incomplete",
                default_active=False,
                implementation_notes="Rent route exists but reusable detail/media proof is not yet complete.",
            ),
            "rent_commercial": _empty_segment(
                "rent_commercial",
                reason="Commercial rental routes are not yet saved for Domaza.",
                status="pattern_incomplete",
            ),
        },
        "Home2U": {
            "buy_personal": SegmentBlueprint(
                segment_key="buy_personal",
                entry_urls=("https://home2u.bg/nedvizhimi-imoti-varna/",),
                supported_verticals=("apartments", "houses", "land", "new_build"),
                listing_pattern=r"home2u\.bg/.+-[a-z0-9]{5,}",
                page_suffix="?page={}",
                support_status="pattern_incomplete",
                default_active=False,
                entry_scope="varna_only_url",
                implementation_notes="Varna route exists but source is not yet patterned enough for activation.",
            ),
            "buy_commercial": _empty_segment(
                "buy_commercial",
                reason="Commercial Home2U routes are not yet saved as reusable buckets.",
                status="pattern_incomplete",
            ),
            "rent_personal": SegmentBlueprint(
                segment_key="rent_personal",
                entry_urls=("https://home2u.bg/apartamenti-pod-naem-varna/",),
                supported_verticals=("apartments",),
                listing_pattern=r"home2u\.bg/.+-[a-z0-9]{5,}",
                page_suffix="?page={}",
                support_status="pattern_incomplete",
                default_active=False,
                entry_scope="varna_only_url",
                implementation_notes="Varna rental route exists but detail/media pattern is not yet complete.",
            ),
            "rent_commercial": _empty_segment(
                "rent_commercial",
                reason="Commercial rental Home2U routes are not yet saved.",
                status="pattern_incomplete",
            ),
        },
        "Yavlena": {
            "buy_personal": SegmentBlueprint(
                segment_key="buy_personal",
                entry_urls=("https://www.yavlena.com/bg/sales",),
                supported_verticals=("apartments", "houses", "land"),
                listing_pattern=r"yavlena\.com/bg/\d{5,}",
                page_suffix="?page={}",
                implementation_notes="National sales route; Varna enforced downstream.",
            ),
            "buy_commercial": _empty_segment(
                "buy_commercial",
                reason="Commercial Yavlena route split is not yet saved in reusable patterns.",
                status="pattern_incomplete",
            ),
            "rent_personal": SegmentBlueprint(
                segment_key="rent_personal",
                entry_urls=("https://www.yavlena.com/bg/rentals",),
                supported_verticals=("apartments", "houses"),
                listing_pattern=r"yavlena\.com/bg/\d{5,}",
                page_suffix="?page={}",
                implementation_notes="National rentals route; Varna enforced downstream.",
            ),
            "rent_commercial": _empty_segment(
                "rent_commercial",
                reason="Commercial rental Yavlena routes are not yet saved separately.",
                status="pattern_incomplete",
            ),
        },
    }


def _generic_segment_support(entry: Any, segment_key: str) -> str:
    listing_types = set(entry.listing_types or [])
    if segment_key == "buy_personal":
        return "pattern_incomplete" if {"sale", "land", "new_build"} & listing_types else "unsupported"
    if segment_key == "buy_commercial":
        return "pattern_incomplete" if {"sale", "new_build"} & listing_types else "unsupported"
    if segment_key == "rent_personal":
        return "pattern_incomplete" if "long_term_rent" in listing_types else "unsupported"
    if segment_key == "rent_commercial":
        return "pattern_incomplete" if "long_term_rent" in listing_types else "unsupported"
    return "unsupported"


def _generic_verticals(entry: Any, segment_key: str) -> tuple[str, ...]:
    listing_types = set(entry.listing_types or [])
    verticals: list[str] = []
    if segment_key.startswith("buy") and {"sale", "new_build"} & listing_types:
        verticals.extend(["apartments", "houses"])
        if "new_build" in listing_types:
            verticals.append("new_build")
    if segment_key.startswith("rent") and "long_term_rent" in listing_types:
        verticals.extend(["apartments", "houses"])
    if "land" in listing_types and segment_key.startswith("buy"):
        verticals.append("land")
    if segment_key.endswith("commercial"):
        verticals.extend(["commercial_properties", "offices"])
    return tuple(dict.fromkeys(verticals or ["all"]))


def _generic_skip_reason(entry: Any, segment_key: str) -> str:
    listing_types = set(entry.listing_types or [])
    if segment_key in {"buy_personal", "buy_commercial"} and not ({"sale", "land", "new_build"} & listing_types):
        return "Source registry does not declare sale/new-build/land support for this source."
    if segment_key in {"rent_personal", "rent_commercial"} and "long_term_rent" not in listing_types:
        return "Source registry does not declare long-term rent support for this source."
    if "short_term_rent" in listing_types and "long_term_rent" not in listing_types and segment_key.startswith("rent"):
        return "Short-term rent is outside the Stage 2 controlled-crawl segment set; keep this source out of long-term rent buckets."
    return "Source/segment route is not yet saved as a production-ready reusable pattern."


def _source_spec(
    *,
    entry: Any,
    pattern_row: dict[str, Any] | None,
    runtime_source_key: str | None,
    bucket: SegmentBlueprint,
) -> dict[str, Any]:
    pattern_status = (pattern_row or {}).get("pattern_status", "Unknown")
    pattern_issue = (pattern_row or {}).get("pattern_issue", "No saved pattern-status evidence yet.")
    legal_mode = entry.legal_mode
    support_status = bucket.support_status
    activation_ready = (
        support_status == "supported"
        and pattern_status == "Patterned"
        and runtime_source_key is not None
        and _allowed_by_legal_mode(legal_mode)
    )
    if not _allowed_by_legal_mode(legal_mode):
        support_status = "legal_blocked"
        activation_ready = False
    return {
        "layer": "source",
        "status": support_status,
        "source_key": runtime_source_key,
        "pattern_status": pattern_status,
        "pattern_issue": pattern_issue,
        "support_status": support_status,
        "activation_ready": activation_ready,
        "legal_mode": legal_mode,
        "best_extraction_method": entry.best_extraction_method,
        "source_family": str(entry.source_family.value) if hasattr(entry.source_family, "value") else str(entry.source_family),
        "supported_listing_types": list(entry.listing_types or []),
        "full_detail_contract": {
            "structured_attributes": "required",
            "description_text": "required",
            "combined_text": "required",
            "gallery_all_images_ordered": "required",
            "raw_html_snapshot": "required",
            "list_page_url": "required",
            "detail_canonical_url": "required",
        },
        "varna_enforcement": COMMON_VARNA_FILTER,
        "activation_notes": bucket.implementation_notes,
    }


def _section_spec(
    bucket: SegmentBlueprint,
    *,
    entry: Any,
    pattern_row: dict[str, Any] | None,
    skip_reason: str | None = None,
) -> dict[str, Any]:
    source_spec = _source_spec(entry=entry, pattern_row=pattern_row, runtime_source_key=RUNTIME_SOURCE_KEYS.get(entry.source_name), bucket=bucket)
    return {
        "layer": "section",
        "status": source_spec["support_status"],
        "support_status": source_spec["support_status"],
        "skip_reason": skip_reason or bucket.skip_reason,
        "segment_key": bucket.segment_key,
        "supported_verticals": list(bucket.supported_verticals),
        "entry_scope": bucket.entry_scope,
        "runtime_mode": "backfill_then_incremental",
        "target_valid_listings": 100,
        "validity_policy": {
            "belongs_to_varna": "required",
            "belongs_to_correct_source": "required",
            "belongs_to_correct_segment": "required",
            "detail_page_parse": "required",
            "identity": "reference_id or (source_name + external_id)",
            "minimal_fields": DEFAULT_STRUCTURED_SIGNALS,
            "media_required_for_threshold": False,
            "missing_gallery_flag": "separate_quality_signal",
        },
    }


def _list_page_spec(bucket: SegmentBlueprint) -> dict[str, Any]:
    return {
        "layer": "list_page",
        "status": bucket.support_status,
        "discovery_mode": bucket.discovery_mode,
        "entry_urls": list(bucket.entry_urls),
        "entry_scope": bucket.entry_scope,
        "page_suffix": bucket.page_suffix,
        "listing_pattern": bucket.listing_pattern,
        "discovery_templates": bucket.discovery_templates or {},
        "varna_enforcement": COMMON_VARNA_FILTER,
        "pagination_stop_rule": "stop when page yields no new URLs or bucket threshold is reached",
        "dedupe_rule": "unique detail URL before enqueue",
    }


def _detail_page_spec(bucket: SegmentBlueprint) -> dict[str, Any]:
    return {
        "layer": "detail_page",
        "status": bucket.support_status,
        "required_fields": list(DEFAULT_DETAIL_FIELDS),
        "required_structured_signals": list(DEFAULT_STRUCTURED_SIGNALS),
        "nullability_policy": "nullable when source truly lacks the field; save raw_text_fallback and structured_extra for any unmapped attribute block",
        "combined_text_policy": "build from title + description + structured extra + location hints",
        "provenance_urls": ["listing_url", "detail_url_canonical", "list_page_url", "image_urls"],
    }


def _media_spec(bucket: SegmentBlueprint) -> dict[str, Any]:
    return {
        "layer": "media_gallery",
        "status": bucket.support_status,
        "gallery_policy": {
            "extract_all_available_images": True,
            "preserve_order": True,
            "store_image_urls": True,
            "store_local_file_keys": True,
            "patterned_requires_full_gallery": True,
            "threshold_count_requires_media": False,
            "missing_gallery_action": "count may still pass threshold but must be flagged as media_incomplete",
        },
    }


def _build_bucket(
    *,
    entry: Any,
    pattern_row: dict[str, Any] | None,
    bucket: SegmentBlueprint,
) -> dict[str, Any]:
    source_key = RUNTIME_SOURCE_KEYS.get(entry.source_name)
    source_spec = _source_spec(entry=entry, pattern_row=pattern_row, runtime_source_key=source_key, bucket=bucket)
    skip_reason = bucket.skip_reason
    if source_spec["support_status"] != "supported" and not skip_reason:
        skip_reason = bucket.implementation_notes or "This bucket is not yet activation-ready."
    active = bool(bucket.default_active and source_spec["activation_ready"])
    section_id = f"{(source_key or entry.source_name.lower().replace(' ', '_').replace('.', '').replace('-', '_'))}__varna__{bucket.segment_key}__all"
    return {
        "section_id": section_id,
        "source_name": entry.source_name,
        "region_key": "varna",
        "segment_key": bucket.segment_key,
        "vertical_key": "all",
        "section_label": f"{entry.source_name} — {bucket.segment_key.replace('_', ' ')} — Varna",
        "entry_urls": list(bucket.entry_urls),
        "active": active,
        "patterns": {
            "target_valid_listings": 100,
            "legal_notes": "Operator approval required before unpausing runner; do not start live crawl automatically.",
            "varna_enforcement": COMMON_VARNA_FILTER,
            "source": source_spec,
            "section": _section_spec(bucket, entry=entry, pattern_row=pattern_row, skip_reason=skip_reason),
            "list_page": _list_page_spec(bucket),
            "detail_page": _detail_page_spec(bucket),
            "media_gallery": _media_spec(bucket),
        },
    }


def build_varna_sections(registry: SourceRegistry) -> list[dict[str, Any]]:
    pattern_index = _pattern_status_index()
    curated = _curated_blueprints()
    sections: list[dict[str, Any]] = []
    for entry in registry.all():
        if entry.tier not in {1, 2}:
            continue
        pattern_row = pattern_index.get(entry.source_name)
        source_blueprints = curated.get(entry.source_name, {})
        for segment_key in SEGMENT_ORDER:
            bucket = source_blueprints.get(segment_key)
            if bucket is None:
                support_status = _generic_segment_support(entry, segment_key)
                bucket = SegmentBlueprint(
                    segment_key=segment_key,
                    supported_verticals=_generic_verticals(entry, segment_key),
                    support_status=support_status,
                    skip_reason=None if support_status == "supported" else _generic_skip_reason(entry, segment_key),
                    default_active=False,
                    implementation_notes="Generic fallback from source_registry; a reusable section-level route still needs to be locked before activation.",
                )
            sections.append(_build_bucket(entry=entry, pattern_row=pattern_row, bucket=bucket))
    return sections


def build_varna_matrix(registry: SourceRegistry) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for section in build_varna_sections(registry):
        pats = section["patterns"]
        source_spec = pats["source"]
        sec_spec = pats["section"]
        list_spec = pats["list_page"]
        rows.append(
            {
                "section_id": section["section_id"],
                "source_name": section["source_name"],
                "segment_key": section["segment_key"],
                "active": section["active"],
                "source_key": source_spec.get("source_key"),
                "pattern_status": source_spec.get("pattern_status"),
                "support_status": sec_spec.get("support_status"),
                "activation_ready": source_spec.get("activation_ready"),
                "skip_reason": sec_spec.get("skip_reason"),
                "supported_verticals": sec_spec.get("supported_verticals", []),
                "entry_scope": list_spec.get("entry_scope"),
                "entry_urls": section.get("entry_urls", []),
                "legal_mode": source_spec.get("legal_mode"),
            }
        )
    rows.sort(key=lambda row: (row["source_name"], SEGMENT_ORDER.index(row["segment_key"])))
    return rows


__all__ = ["SEGMENT_ORDER", "build_varna_sections", "build_varna_matrix"]
