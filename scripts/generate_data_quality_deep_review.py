#!/usr/bin/env python3
"""Generate a file-backed deep review for scraped-property DB readiness.

The report is intentionally offline. It reads saved corpus JSON, existing
quality-gate exports, source registry entries, and local code/schema files.
It does not scrape live websites and does not mutate raw scraped data.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
SCRAPED_ROOT = REPO / "data/scraped"
EXPORTS = REPO / "docs/exports"
DASHBOARD = REPO / "docs/dashboard"
REPORT_DATE = "2026-05-13"
REPORT_JSON = EXPORTS / f"data-quality-deep-review-{REPORT_DATE}.json"
REPORT_MD = EXPORTS / f"data-quality-deep-review-{REPORT_DATE}.md"
DB_REVIEW_MD = EXPORTS / f"bd18-database-review-and-correction-spec-{REPORT_DATE}.md"
DASHBOARD_HTML = DASHBOARD / "data-quality-dashboard.html"

ACTION1_SOURCES = {
    "address_bg",
    "bulgarianproperties",
    "homes_bg",
    "imot_bg",
    "luximmo",
    "property_bg",
    "suprimmo",
}

STATUS_BLOCKED = {
    "PENDING_QA",
    "UNKNOWN",
    "LOST",
    "GROUPED_PUBLICATION",
    "DEVELOPMENT_PUBLICATION",
    "UNSAFE_FOR_CANONICAL_IMPORT",
    "STALE_REVIEW_REQUIRED",
    "EXPIRED_SOURCE",
    "SOLD_CONFIRMED",
    "RENTED_CONFIRMED",
}

SOURCE_REPAIR_HINTS: dict[str, dict[str, str]] = {
    "address_bg": {
        "wrong": "Large pending QA queue, many one-photo suspect rows, missing city/address in some categories, and high invalid/duplicated phone extraction.",
        "likely_reason": "List-card/detail merge and contact block extraction over-capture repeated boilerplate; QA state was not finalized after offline estimate.",
        "inspect": "Address detail parser, location selectors, gallery expansion, contact-block normalization, pending-to-accepted quality writeback.",
        "fixture": "Use one accepted city row, one missing-location row, one one-photo row, and one commercial/rent row.",
        "acceptance": "Fixture rows preserve source URL, price/status, city/address, full gallery counts, valid contact provenance, and accepted QA only when single-unit evidence is present.",
        "blocked": "Pending QA, one-photo suspect, missing location, invalid contact-only, and missing/undefined price without source evidence.",
    },
    "alo_bg": {
        "wrong": "All current rows lack explicit QA/source-publication fields even though estimate marks them OK.",
        "likely_reason": "Legacy parser predates Action1 QA field writeback.",
        "inspect": "Alo detail parser output envelope, QA field defaults, bucket assignment, phone/contact provenance.",
        "fixture": "Varna sale fixture with full gallery and phone block; add missing/expired page fixture if available.",
        "acceptance": "Every saved row gets scrape_status, scrape_acceptance_status, source_publication_type, listing_status, bucket_key, and media counts.",
        "blocked": "All missing-QA rows until explicit Action1 fields exist.",
    },
    "bazar_bg": {
        "wrong": "Missing QA, partial local galleries, missing city/address, numeric zero-price rows, and noisy phone extraction.",
        "likely_reason": "Classified detail pages have variable location/price blocks and legacy parser did not enforce price_status.",
        "inspect": "Price parser, location parser, gallery downloader, phone extraction boundaries, accepted-only QA writer.",
        "fixture": "Zero-price fixture, partial-gallery fixture, missing-location fixture, active/rent fixture.",
        "acceptance": "Numeric 0 becomes null plus price_status, location is present or blocked, and local gallery count matches remote count before acceptance.",
        "blocked": "Zero price, missing location, partial gallery, missing QA, LOST, inactive/stale classified rows.",
    },
    "bulgarianproperties": {
        "wrong": "Very high LOST estimate, missing area, partial galleries, and agency contact over-capture.",
        "likely_reason": "Agency pages mix full property pages, area/plot fields, language variants, and boilerplate phone lists.",
        "inspect": "Area/plot parser, language canonicalization, gallery carousel extraction, contact-list scoping.",
        "fixture": "House with plot area, apartment with built area, missing-area page, full-gallery page.",
        "acceptance": "Area field has correct semantics, full gallery evidence is durable, and contact provenance identifies agency-level phone lists.",
        "blocked": "Missing area, partial gallery, LOST, grouped/new-build/project pages without unit evidence.",
    },
    "domaza": {
        "wrong": "Small tier-2 corpus includes residential-complex/grouped pages and missing area rows.",
        "likely_reason": "Portal exposes project pages and multi-language/category pages that resemble unit pages.",
        "inspect": "Publication-type classifier, area field selectors, complex/development wording, per-language canonical URL mapping.",
        "fixture": "Residential complex page, single unit page, missing-area page.",
        "acceptance": "Grouped/development pages are marked source publications; only unit URLs with price/status, area, and media can be accepted.",
        "blocked": "Complex/project pages, missing-area rows, ambiguous grouped offers.",
    },
    "home2u": {
        "wrong": "Small sample has thin titles, missing QA fields, and limited contact evidence.",
        "likely_reason": "Agency template parser extracts short headline but not enough detail/context.",
        "inspect": "Title/detail selector, description body, contact provenance, listing_status markers.",
        "fixture": "Rent listing, sale listing, missing detail page, inactive page if saved.",
        "acceptance": "Title and description are complete enough for dedupe/search and QA fields are explicit.",
        "blocked": "Missing QA, thin title-only rows, missing area/contact provenance.",
    },
    "homes_bg": {
        "wrong": "Duplicate listing URLs, many LOST rows, local-gallery gaps, and some grouped/development rows.",
        "likely_reason": "Offline reparsing recovered fields but source URL/reference normalization and media backfill are inconsistent.",
        "inspect": "Reference-id normalization, duplicate URL handling, gallery downloader, inactive/removed detection.",
        "fixture": "Duplicate URL pair, accepted row with full gallery, LOST row, grouped/new-build row.",
        "acceptance": "Duplicate source URLs collapse to one source publication; accepted rows have local gallery and QA state; LOST stays quarantined.",
        "blocked": "LOST, duplicate unresolved URL clusters, grouped/development, local-gallery-missing rows.",
    },
    "imot_bg": {
        "wrong": "Largest source with many pending QA rows, grouped/development pages, missing/unknown categories, thin descriptions, and duplicate IDs risk.",
        "likely_reason": "High-volume portal mixes unit listings, project ads, agency reposts, and short list-card descriptions.",
        "inspect": "Detail-page parser, project-page classifier, category mapping, duplicate external_id/reference logic, stale listing markers.",
        "fixture": "Sale unit, rent unit, project page, short-description page, duplicate/external-id row.",
        "acceptance": "Only unit-level detail pages with stable URL, price/status, area, media, and active status are accepted.",
        "blocked": "Pending QA, grouped/development, unknown category, missing area, inactive/stale rows.",
    },
    "luximmo": {
        "wrong": "Luxury agency rows have missing area, grouped/development pages, partial galleries, and large contact lists.",
        "likely_reason": "Agency template mixes project, office, and luxury descriptions; contact blocks include sitewide phone variants.",
        "inspect": "Area parser, offer-kind classifier, gallery carousel, contact block scoping, language/region parser.",
        "fixture": "Long-term rent apartment, sale apartment, project/development page, missing-area row.",
        "acceptance": "Offer kind, area, price/status, and contact provenance are preserved; grouped pages remain source publications.",
        "blocked": "Missing area, grouped/development, LOST, contact-only unsafe rows, image gaps.",
    },
    "olx_bg": {
        "wrong": "Missing QA, volatile classified inventory, missing location/area, and excessive phone extraction.",
        "likely_reason": "API/HTML payloads vary and legacy rows lack Action1 quality fields.",
        "inspect": "Official API parser, location payload mapping, stale/deleted status, phone extraction allowlist.",
        "fixture": "Active listing, deleted/inactive listing, missing-price row, missing-location row.",
        "acceptance": "Official/source status is preserved; missing or deleted rows are stale/review, not active public offers.",
        "blocked": "Missing QA, deleted/stale/volatile rows, missing price/status/location, owner-contact uncertainty.",
    },
    "property_bg": {
        "wrong": "Many thin descriptions, unknown categories, and possible gallery over-count/duplicate variants.",
        "likely_reason": "English/Bulgarian agency pages include repeated marketing boilerplate and large gallery variants.",
        "inspect": "Description extraction, category mapper, gallery de-duplication, SUPRIMMO-group dedupe hints.",
        "fixture": "High-photo listing, thin-description listing, unknown-category listing, accepted row.",
        "acceptance": "Description has property-specific text, category is mapped, duplicate image variants are not overstated.",
        "blocked": "Thin-description-only, unknown category, grouped/development, media duplicate variants until reviewed.",
    },
    "suprimmo": {
        "wrong": "Large grouped/development queue, missing area, unknown categories, and contact over-capture.",
        "likely_reason": "Agency/developer inventory mixes houses, projects, resorts, and repeated contact blocks.",
        "inspect": "Project/development classifier, area parser, gallery extraction, contact provenance, category mapper.",
        "fixture": "Project page, single house, rent unit, missing-area page.",
        "acceptance": "Grouped/development source publications never become canonical units without unit-level evidence.",
        "blocked": "Grouped/development, missing area, LOST, contact-only unsafe rows, pending QA.",
    },
    "yavlena": {
        "wrong": "Many missing descriptions, one-photo rows, unknown categories, and zero-price rows.",
        "likely_reason": "Parser under-extracts detail body/category and treats placeholder price/media as real evidence.",
        "inspect": "Detail description selector, category mapper, price parser, gallery selector, active/inactive markers.",
        "fixture": "Hotel/commercial page, apartment unit, zero-price page, one-photo page.",
        "acceptance": "Commercial category is explicit, zero price is null plus status, and one-photo rows are blocked unless source truly has one image.",
        "blocked": "Missing description, unknown category, zero price, one-photo suspect, missing QA.",
    },
}

REQUIRED_DB_CONCEPTS = [
    {
        "concept": "source_publications",
        "existing": ["source_listing", "source_listing_snapshot", "raw_capture", "source_publication_qa_review", "status_history"],
        "status": "partial",
        "gap": "Publication-level evidence exists and BD-18 added QA/status tables; PostgreSQL migration/import proof is still pending.",
    },
    {
        "concept": "canonical_properties",
        "existing": ["property_entity"],
        "status": "partial",
        "gap": "Entity table exists but current promotion can happen before reviewed source-publication import and dedupe confidence gates.",
    },
    {
        "concept": "listing_offers",
        "existing": ["property_offer"],
        "status": "partial",
        "gap": "Offer table exists but sale/long-term/short-term/commercial flows lack price_status, availability status, and offer-kind constraints.",
    },
    {
        "concept": "qa_reviews",
        "existing": ["source_publication_qa_review"],
        "status": "implemented_pending_db_proof",
        "gap": "First-class QA review table is defined; it still needs PostgreSQL migration, smoke import, and count parity verification.",
    },
    {
        "concept": "status_history",
        "existing": ["status_history", "listing_event", "price_history"],
        "status": "implemented_pending_db_proof",
        "gap": "Generic status-history table is defined; runtime migration/import proof is still pending.",
    },
    {
        "concept": "contacts",
        "existing": ["contact_entity", "person_contact", "contact_method", "property_contact_link"],
        "status": "partial",
        "gap": "Contact provenance, permission/source, inferred/agency/owner/company type, and mass-enrichment guardrails are not first-class.",
    },
    {
        "concept": "media_assets",
        "existing": ["media_asset", "listing_media", "property_media"],
        "status": "partial",
        "gap": "Local/source media exists, but source photo count, local count, storage keys, hash variants, and evidence status need source-publication linkage.",
    },
    {
        "concept": "media_descriptions",
        "existing": ["media_description"],
        "status": "implemented_pending_action0_and_db_proof",
        "gap": "Table is defined, but semantic image descriptions are inactive until local-gallery verification, Action0 approval, and DB proof.",
    },
    {
        "concept": "entity_resolution_candidates",
        "existing": ["entity_resolution_candidate", "entity_resolution_review_event", "property_entity.dedupe_key"],
        "status": "implemented_pending_db_proof",
        "gap": "Reviewable candidate/review-event tables are defined; canonical promotion remains blocked until accepted-only DB proof and review policy pass.",
    },
    {
        "concept": "availability_calendars",
        "existing": ["availability_calendar"],
        "status": "implemented_pending_db_proof",
        "gap": "Calendar table is defined; short-term availability logic and migration/import proof remain pending.",
    },
    {
        "concept": "availability_slots",
        "existing": ["availability_slot"],
        "status": "implemented_pending_db_proof",
        "gap": "Slot table is defined; viewing/booking semantics and runtime proof remain pending.",
    },
    {
        "concept": "availability_observations",
        "existing": ["availability_observation"],
        "status": "implemented_pending_db_proof",
        "gap": "Observation table is defined; timestamped source-observed availability evidence still needs ingest/read-model proof.",
    },
    {
        "concept": "viewing_or_inquiry_requests",
        "existing": ["viewing_inquiry_request", "lead_thread", "lead_thread_property_link"],
        "status": "implemented_pending_db_proof",
        "gap": "Request table is defined; platform-to-owner/realtor/company workflow still needs API/review implementation and DB proof.",
    },
    {
        "concept": "external_chat_refs",
        "existing": ["external_chat_ref", "user_property_chat", "lead_thread"],
        "status": "implemented_pending_db_proof",
        "gap": "External chat-ref table is defined; safe handoff metadata still needs runtime verification and API policy.",
    },
]

REQUIRED_FIELDS = [
    "qa_state",
    "qa_reviewer",
    "qa_reviewed_at",
    "source_publication_type",
    "source_publication_status",
    "listing_status",
    "listing_status_history",
    "price_status",
    "price_currency",
    "price_period",
    "price_provenance",
    "offer_kind",
    "use_class",
    "property_type",
    "building_or_development_flag",
    "canonical_property_id",
    "canonical_listing_offer_id",
    "source_publication_id",
    "duplicate_cluster_id",
    "entity_resolution_confidence",
    "photo_count_from_source",
    "local_image_count",
    "local_image_storage_keys",
    "image_hash",
    "image_perceptual_hash",
    "image_description_coverage",
    "image_evidence_status",
    "contact_provenance",
    "contact_type",
    "contact_permission_source",
    "geo_scope",
    "bucket_key",
    "inactive_expired_sold_rented_stale_markers",
    "last_seen_at",
    "first_seen_at",
    "source_observed_at",
    "import_eligibility_reason",
    "blocked_import_reason",
]


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def compact_quality_gate(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at": data.get("generated_at"),
        "applied": data.get("applied"),
        "quality_rollup": data.get("quality_rollup", {}),
        "sources": data.get("sources", {}),
        "lost_queue_count": len(data.get("lost_queue") or []),
        "multi_unit_publications_count": len(data.get("multi_unit_publications") or []),
        "items_count": len(data.get("items") or []),
    }


def compact_scrape_status(data: dict[str, Any]) -> dict[str, Any]:
    sources = []
    for source in data.get("sources", []):
        if not isinstance(source, dict):
            continue
        sources.append({key: value for key, value in source.items() if key not in {"item_rows", "combo_rows"}})
    return {
        "generated_at": data.get("generated_at"),
        "totals": data.get("totals", {}),
        "sources": sources,
    }


def norm_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def text_len(value: Any) -> int:
    if not isinstance(value, str):
        return 0
    return len(value.strip())


def first_non_empty(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def price_status(row: dict[str, Any]) -> str:
    provenance = row.get("crawl_provenance") if isinstance(row.get("crawl_provenance"), dict) else {}
    return str(row.get("price_status") or provenance.get("price_status") or "").strip().lower()


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def media_counts(row: dict[str, Any]) -> tuple[int, int]:
    remote = row.get("photo_count_remote")
    local = row.get("photo_count_local")
    remote_n = len(row.get("image_urls") or []) if remote in (None, "") else int(remote or 0)
    local_n = len(row.get("local_image_files") or []) if local in (None, "") else int(local or 0)
    return remote_n, local_n


def is_grouped(row: dict[str, Any]) -> bool:
    return (
        row.get("source_publication_type") == "multi_unit_or_development"
        or row.get("scrape_acceptance_status") == "not_single_entity"
        or row.get("suspected_multi_unit_publication") is True
    )


def is_import_candidate(row: dict[str, Any]) -> bool:
    status = str(row.get("scrape_status") or "")
    acceptance = str(row.get("scrape_acceptance_status") or "")
    listing_status = str(row.get("listing_status") or "").lower()
    return (
        status not in {"", "PENDING_QA", "UNKNOWN", "LOST"}
        and row.get("needs_rescrape") is not True
        and not is_grouped(row)
        and acceptance == "accepted_single_entity_candidate"
        and listing_status not in {"inactive", "removed", "expired", "sold", "rented"}
    )


def classify_bad_rules(row: dict[str, Any]) -> list[str]:
    rules: list[str] = []
    status = str(row.get("scrape_status") or "")
    acceptance = str(row.get("scrape_acceptance_status") or "")
    listing_status = str(row.get("listing_status") or "").lower()
    price = as_float(row.get("price"))
    remote, local = media_counts(row)
    category = str(row.get("property_category") or "unknown")

    if status in {"", "PENDING_QA", "UNKNOWN"}:
        rules.append("missing_or_unreviewed_qa")
    if status == "LOST" or row.get("needs_rescrape") is True:
        rules.append("lost_or_rescrape_required")
    if is_grouped(row):
        rules.append("grouped_or_development_publication")
    if listing_status in {"inactive", "removed", "expired"}:
        rules.append("inactive_removed_or_expired")
    if listing_status in {"sold", "rented"}:
        rules.append("sold_or_rented_marker")
    if price == 0:
        rules.append("numeric_zero_price")
    if price is None and price_status(row) not in {"on_request", "undefined"}:
        rules.append("missing_price_without_status")
    if not row.get("listing_url"):
        rules.append("missing_source_url")
    if not row.get("area_sqm"):
        rules.append("missing_area")
    if not first_non_empty(row.get("city"), row.get("address_text"), row.get("district")):
        rules.append("missing_location_evidence")
    if category == "unknown":
        rules.append("unknown_property_category")
    if text_len(row.get("description")) == 0:
        rules.append("missing_description")
    elif text_len(row.get("description")) < 80:
        rules.append("thin_description")
    if text_len(row.get("title")) < 10:
        rules.append("thin_title")
    if remote <= 0:
        rules.append("missing_remote_gallery")
    elif remote == 1:
        rules.append("one_remote_photo_gallery_suspect")
    if remote > 0 and local <= 0:
        rules.append("remote_gallery_without_local_files")
    elif remote > 0 and local < remote:
        rules.append("partial_local_gallery")
    if local > remote > 0:
        rules.append("local_gallery_exceeds_remote_variants")
    if len(set(row.get("image_urls") or [])) < len(row.get("image_urls") or []):
        rules.append("duplicate_remote_image_urls")
    if len(set(row.get("local_image_files") or [])) < len(row.get("local_image_files") or []):
        rules.append("duplicate_local_image_paths")
    if not row.get("source_publication_type"):
        rules.append("missing_source_publication_type")
    if acceptance in {"", "MISSING"}:
        rules.append("missing_acceptance_status")
    if not row.get("local_image_storage_keys") and local:
        rules.append("missing_local_image_storage_keys")
    if not row.get("image_report_status") and not row.get("image_description_coverage"):
        rules.append("image_semantic_description_unverified")
    if row.get("phones") and len(row.get("phones") or []) > 10:
        rules.append("contact_overcapture_suspect")
    return rules


def classify_offer_kind(row: dict[str, Any]) -> str:
    intent = str(row.get("listing_intent") or "")
    bucket = str(row.get("bucket_key") or row.get("segment_key") or "")
    category = str(row.get("property_category") or "")
    if intent in {"short_term_rent", "sale", "long_term_rent"}:
        offer = intent
    elif "rent" in bucket:
        offer = "long_term_rent"
    elif "buy" in bucket:
        offer = "sale"
    else:
        offer = intent or "unknown"
    if category in {"office", "shop", "commercial", "industrial", "warehouse"} or "commercial" in bucket:
        return f"{offer}_commercial" if offer != "unknown" else "commercial_unknown"
    return offer


def load_registry() -> dict[str, dict[str, Any]]:
    data = read_json(REPO / "data/source_registry.json", {"sources": []})
    registry: dict[str, dict[str, Any]] = {}
    for source in data.get("sources", []):
        key = norm_key(str(source.get("source_name") or ""))
        registry[key] = source
    return registry


def scan_corpus() -> dict[str, Any]:
    sources: dict[str, dict[str, Any]] = {}
    totals = Counter()
    market = {
        "accepted_by_city": Counter(),
        "accepted_by_offer_kind": Counter(),
        "accepted_by_category": Counter(),
        "all_by_city": Counter(),
        "all_by_offer_kind": Counter(),
        "price_by_offer_kind": defaultdict(list),
    }
    samples: dict[str, dict[str, str]] = defaultdict(dict)

    for source_dir in sorted(path for path in SCRAPED_ROOT.iterdir() if path.is_dir()):
        listings_dir = source_dir / "listings"
        if not listings_dir.exists():
            continue
        source_key = source_dir.name
        stats = sources.setdefault(
            source_key,
            {
                "source_key": source_key,
                "source_names": Counter(),
                "rows": 0,
                "action1_scope": source_key in ACTION1_SOURCES,
                "qa_state": Counter(),
                "acceptance_state": Counter(),
                "publication_type": Counter(),
                "listing_status": Counter(),
                "buckets": Counter(),
                "offer_kinds": Counter(),
                "categories": Counter(),
                "cities": Counter(),
                "bad_rules": Counter(),
                "examples": {},
                "prices": [],
                "remote_photos": 0,
                "local_photos": 0,
                "rows_remote_photos": 0,
                "rows_local_photos": 0,
                "rows_full_gallery": 0,
                "rows_partial_gallery": 0,
                "rows_one_photo": 0,
                "rows_duplicate_remote_urls": 0,
                "rows_duplicate_local_paths": 0,
                "rows_local_exceeds_remote": 0,
                "rows_with_description": 0,
                "rows_thin_description": 0,
                "rows_with_contact": 0,
                "rows_contact_overcapture": 0,
                "image_report_status": Counter(),
                "image_description_rows": 0,
                "import_default_candidates": 0,
                "blocked_default_import": 0,
                "zero_price_rows": 0,
                "missing_price_without_status": 0,
                "missing_location_rows": 0,
                "missing_area_rows": 0,
                "accepted_media_gaps": 0,
                "accepted_missing_location": 0,
                "accepted_missing_area": 0,
                "sample_file": "",
            },
        )
        for listing_file in sorted(listings_dir.glob("*.json")):
            try:
                row = json.loads(listing_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                stats["bad_rules"]["bad_json"] += 1
                totals["bad_json"] += 1
                continue

            source_name = str(row.get("source_name") or source_key)
            source_name_key = norm_key(source_name)
            stats["source_names"][source_name] += 1
            stats["rows"] += 1
            totals["rows"] += 1
            if not stats["sample_file"]:
                stats["sample_file"] = str(listing_file.relative_to(REPO))

            status = str(row.get("scrape_status") or "MISSING")
            acceptance = str(row.get("scrape_acceptance_status") or "MISSING")
            publication_type = str(row.get("source_publication_type") or "MISSING")
            listing_status = str(row.get("listing_status") or "unknown")
            bucket = str(row.get("bucket_key") or row.get("segment_key") or "MISSING")
            offer_kind = classify_offer_kind(row)
            category = str(row.get("property_category") or "unknown")
            city = first_non_empty(row.get("city"), row.get("region"), "MISSING")
            price = as_float(row.get("price"))
            remote, local = media_counts(row)
            rules = classify_bad_rules(row)

            stats["qa_state"][status] += 1
            stats["acceptance_state"][acceptance] += 1
            stats["publication_type"][publication_type] += 1
            stats["listing_status"][listing_status] += 1
            stats["buckets"][bucket] += 1
            stats["offer_kinds"][offer_kind] += 1
            stats["categories"][category] += 1
            stats["cities"][city] += 1
            stats["remote_photos"] += remote
            stats["local_photos"] += local
            stats["rows_remote_photos"] += 1 if remote else 0
            stats["rows_local_photos"] += 1 if local else 0
            stats["rows_full_gallery"] += 1 if remote and local >= remote else 0
            stats["rows_partial_gallery"] += 1 if remote and 0 < local < remote else 0
            stats["rows_one_photo"] += 1 if remote == 1 else 0
            stats["rows_local_exceeds_remote"] += 1 if local > remote > 0 else 0
            stats["rows_duplicate_remote_urls"] += 1 if len(set(row.get("image_urls") or [])) < len(row.get("image_urls") or []) else 0
            stats["rows_duplicate_local_paths"] += 1 if len(set(row.get("local_image_files") or [])) < len(row.get("local_image_files") or []) else 0
            stats["rows_with_description"] += 1 if text_len(row.get("description")) else 0
            stats["rows_thin_description"] += 1 if 0 < text_len(row.get("description")) < 80 else 0
            stats["rows_with_contact"] += 1 if row.get("phones") or row.get("agency_name") or row.get("broker_name") else 0
            stats["rows_contact_overcapture"] += 1 if row.get("phones") and len(row.get("phones") or []) > 10 else 0
            stats["image_report_status"][str(row.get("image_report_status") or "missing")] += 1
            stats["image_description_rows"] += 1 if row.get("image_description_coverage") or row.get("image_descriptions") else 0
            stats["zero_price_rows"] += 1 if price == 0 else 0
            stats["missing_price_without_status"] += 1 if price is None and price_status(row) not in {"on_request", "undefined"} else 0
            stats["missing_location_rows"] += 1 if "missing_location_evidence" in rules else 0
            stats["missing_area_rows"] += 1 if "missing_area" in rules else 0

            if price and price > 0:
                stats["prices"].append(price)
                market["price_by_offer_kind"][offer_kind].append(price)
            market["all_by_city"][city] += 1
            market["all_by_offer_kind"][offer_kind] += 1

            for rule in rules:
                stats["bad_rules"][rule] += 1
                if rule not in samples[source_key]:
                    samples[source_key][rule] = str(listing_file.relative_to(REPO))

            if is_import_candidate(row):
                stats["import_default_candidates"] += 1
                market["accepted_by_city"][city] += 1
                market["accepted_by_offer_kind"][offer_kind] += 1
                market["accepted_by_category"][category] += 1
                stats["accepted_media_gaps"] += 1 if remote == 0 or local < remote else 0
                stats["accepted_missing_location"] += 1 if "missing_location_evidence" in rules else 0
                stats["accepted_missing_area"] += 1 if "missing_area" in rules else 0
            else:
                stats["blocked_default_import"] += 1

            if status in {"MISSING", "PENDING_QA", "UNKNOWN"}:
                totals["missing_pending_unknown_qa"] += 1
            if status == "LOST":
                totals["lost"] += 1
            if is_grouped(row):
                totals["grouped_or_development"] += 1
            if listing_status.lower() in {"inactive", "removed", "expired"}:
                totals["inactive_or_expired"] += 1
            if price == 0:
                totals["numeric_zero_price"] += 1
            if source_name_key != source_key:
                totals["source_name_key_variants"] += 1

    for source_key, stats in sources.items():
        stats["source_names"] = dict(stats["source_names"])
        stats["qa_state"] = dict(stats["qa_state"])
        stats["acceptance_state"] = dict(stats["acceptance_state"])
        stats["publication_type"] = dict(stats["publication_type"])
        stats["listing_status"] = dict(stats["listing_status"])
        stats["buckets"] = dict(stats["buckets"])
        stats["offer_kinds"] = dict(stats["offer_kinds"])
        stats["categories"] = dict(stats["categories"])
        stats["cities_top"] = dict(stats["cities"].most_common(12))
        del stats["cities"]
        stats["bad_rules_top"] = dict(stats["bad_rules"].most_common(18))
        del stats["bad_rules"]
        stats["image_report_status"] = dict(stats["image_report_status"])
        stats["examples"] = samples.get(source_key, {})
        prices = stats.pop("prices")
        stats["price_summary"] = summarize_prices(prices)
        stats["risk_level"] = source_risk_level(stats)
        stats["repair_plan"] = SOURCE_REPAIR_HINTS.get(source_key, default_source_repair(stats))

    market_out = {
        "accepted_by_city": dict(market["accepted_by_city"].most_common(20)),
        "accepted_by_offer_kind": dict(market["accepted_by_offer_kind"].most_common()),
        "accepted_by_category": dict(market["accepted_by_category"].most_common()),
        "all_by_city": dict(market["all_by_city"].most_common(20)),
        "all_by_offer_kind": dict(market["all_by_offer_kind"].most_common()),
        "price_by_offer_kind": {
            key: summarize_prices(values)
            for key, values in sorted(market["price_by_offer_kind"].items())
        },
        "market_intelligence_limits": [
            "Use accepted/import-candidate evidence for market slices; raw saved volume is scraper coverage, not market supply.",
            "Pending/missing QA dominates several sources; do not infer supply share from raw source counts.",
            "Long-term rent stale review needs stricter thresholds than sale. Short-term rent needs calendar/slot evidence.",
        ],
    }
    return {"totals": dict(totals), "sources": sources, "market": market_out}


def summarize_prices(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "min": None, "median": None, "max": None, "avg": None}
    values = sorted(values)
    mid = len(values) // 2
    median = values[mid] if len(values) % 2 else (values[mid - 1] + values[mid]) / 2
    return {
        "count": len(values),
        "min": round(values[0], 2),
        "median": round(median, 2),
        "max": round(values[-1], 2),
        "avg": round(sum(values) / len(values), 2),
    }


def source_risk_level(stats: dict[str, Any]) -> str:
    rows = max(int(stats["rows"]), 1)
    blocked_pct = stats["blocked_default_import"] / rows
    missing_qa = sum(stats["qa_state"].get(key, 0) for key in ("MISSING", "PENDING_QA", "UNKNOWN")) / rows
    media_gap = (stats["rows_partial_gallery"] + stats["rows_one_photo"]) / rows
    if blocked_pct > 0.9 or missing_qa > 0.8:
        return "critical"
    if blocked_pct > 0.5 or media_gap > 0.25:
        return "high"
    if blocked_pct > 0.2:
        return "medium"
    return "watch"


def default_source_repair(stats: dict[str, Any]) -> dict[str, str]:
    return {
        "wrong": "Source has saved rows but no source-specific repair template yet.",
        "likely_reason": "Legacy or small-sample parser path needs QA field normalization.",
        "inspect": "Parser output envelope, QA writer, price/location/media/contact extraction.",
        "fixture": f"Use sample {stats.get('sample_file') or 'one saved listing'} plus one edge case per top bad rule.",
        "acceptance": "All accepted rows have QA, source URL, price/status, area, media, contact provenance, and source-publication type.",
        "blocked": "Missing QA, LOST, grouped/development, inactive, zero-price, missing location/area, and media-gap rows.",
    }


def parse_sql_tables() -> dict[str, list[str]]:
    schema = (REPO / "sql/schema.sql").read_text(encoding="utf-8")
    tables: dict[str, list[str]] = {}
    for match in re.finditer(r"create table if not exists\s+([a-zA-Z0-9_]+)\s*\((.*?)\n\);", schema, re.S | re.I):
        table = match.group(1)
        body = match.group(2)
        cols: list[str] = []
        for raw_line in body.splitlines():
            line = raw_line.strip().rstrip(",")
            if not line or line.lower().startswith(("constraint ", "unique(", "foreign key", "primary key")):
                continue
            col = line.split()[0]
            if col not in {"create", "select"}:
                cols.append(col)
        tables[table] = cols
    for match in re.finditer(r"alter table\s+([a-zA-Z0-9_]+)\s+add column if not exists\s+([a-zA-Z0-9_]+)", schema, re.I):
        tables.setdefault(match.group(1), []).append(match.group(2))
    return {table: sorted(set(cols)) for table, cols in tables.items()}


def db_review() -> dict[str, Any]:
    tables = parse_sql_tables()
    existing_tables = set(tables)
    concept_rows = []
    for item in REQUIRED_DB_CONCEPTS:
        existing = [table for table in item["existing"] if table in existing_tables or "." in table]
        concept_rows.append(
            {
                **item,
                "existing_found": existing,
                "found": bool(existing),
            }
        )

    canonical_cols = set(tables.get("canonical_listing", []))
    source_listing_cols = set(tables.get("source_listing", []))
    source_snapshot_cols = set(tables.get("source_listing_snapshot", []))
    property_offer_cols = set(tables.get("property_offer", []))
    media_cols = set(tables.get("media_asset", [])) | set(tables.get("listing_media", [])) | set(tables.get("property_media", []))
    contact_cols = set(tables.get("contact_entity", [])) | set(tables.get("person_contact", [])) | set(tables.get("contact_method", []))

    field_mapping = {
        "qa_state": "first_class_pending_db_proof: source_publication_qa_review.qa_state",
        "qa_reviewer": "first_class_pending_db_proof: source_publication_qa_review.reviewer",
        "qa_reviewed_at": "first_class_pending_db_proof: source_publication_qa_review.reviewed_at",
        "source_publication_type": "crawl_provenance_only",
        "source_publication_status": "partial: source_listing.status",
        "listing_status": "crawl_provenance_only",
        "listing_status_history": "first_class_pending_db_proof: status_history",
        "price_status": "crawl_provenance_only",
        "price_currency": "first_class: canonical_listing.currency/property_offer.currency",
        "price_period": "missing",
        "price_provenance": "crawl_provenance_only",
        "offer_kind": "partial: listing_intent/property_offer.intent",
        "use_class": "partial: property_category + bucket_key JSON",
        "property_type": "first_class: property_category/entity_type",
        "building_or_development_flag": "crawl_provenance_only",
        "canonical_property_id": "first_class: property_entity.property_id",
        "canonical_listing_offer_id": "first_class: property_offer.offer_id",
        "source_publication_id": "partial: source_listing.source_listing_id",
        "duplicate_cluster_id": "candidate_layer_pending_db_proof: entity_resolution_candidate.candidate_id",
        "entity_resolution_confidence": "candidate_layer_pending_db_proof: entity_resolution_candidate.confidence_score",
        "photo_count_from_source": "crawl_provenance_only",
        "local_image_count": "crawl_provenance_only",
        "local_image_storage_keys": "crawl_provenance_only",
        "image_hash": "partial: media_asset.sha256/listing_media.content_hash",
        "image_perceptual_hash": "first_class: media_asset.perceptual_hash",
        "image_description_coverage": "first_class_pending_action0_and_db_proof: media_description.coverage_state",
        "image_evidence_status": "partial: media_asset.download_status/listing_media.download_status",
        "contact_provenance": "missing_first_class",
        "contact_type": "partial: person_contact.role/contact metadata only",
        "contact_permission_source": "missing",
        "geo_scope": "crawl_provenance_only",
        "bucket_key": "crawl_provenance_only",
        "inactive_expired_sold_rented_stale_markers": "partial: removed_at/listing_event/status JSON",
        "last_seen_at": "first_class: source_listing.last_seen_at/canonical_listing.last_seen",
        "first_seen_at": "first_class: source_listing.first_seen_at/canonical_listing.first_seen",
        "source_observed_at": "partial: raw_capture.fetched_at/source_snapshot.created_at",
        "import_eligibility_reason": "first_class_pending_db_proof: source_publication_qa_review.import_eligibility_reason",
        "blocked_import_reason": "first_class_pending_db_proof: source_publication_qa_review.blocked_import_reason",
    }
    corrections = [
        "Keep import default accepted-only and source-publication-first; property_entity/property_offer promotion requires explicit reviewed flag.",
        "Convert numeric price 0 to null plus price_status provenance before persistence.",
        "Run BD-18 migration and DB smoke import for source_publication_qa_review, status_history, entity_resolution_candidate/review_event, media_description, availability, inquiry, and external_chat_ref tables.",
        "Verify status_history for source_publication, listing_offer, canonical_property transitions with observed_at and provenance.",
        "Refine availability_calendars, availability_slots, and availability_observations before short-term rental publication/search.",
        "Use media_descriptions only after gallery identity/local image completeness is reliable and Action0 is approved; do not mix semantic status with raw gallery capture.",
        "Use entity_resolution_candidate and review events before entity-resolution promotion; keep candidates out of public APIs.",
        "Implement viewing_inquiry_request and external_chat_ref API/read-model policy with chat DB remaining external and refs only.",
    ]
    return {
        "tables": tables,
        "canonical_columns_present": sorted(canonical_cols),
        "source_listing_columns_present": sorted(source_listing_cols | source_snapshot_cols),
        "offer_columns_present": sorted(property_offer_cols),
        "media_columns_present": sorted(media_cols),
        "contact_columns_present": sorted(contact_cols),
        "concepts": concept_rows,
        "field_mapping": {field: field_mapping.get(field, "needs_review") for field in REQUIRED_FIELDS},
        "corrections_required": corrections,
        "db_count_status": "blocked_missing_DATABASE_URL",
        "safe_import_status": "file-backed dry-run only until DATABASE_URL and BD-18 DB smoke tests pass",
    }


def pct(num: int | float, den: int | float) -> str:
    if not den:
        return "0.0%"
    return f"{num / den * 100:.1f}%"


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:,.1f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def write_markdown(payload: dict[str, Any]) -> None:
    scan = payload["corpus_scan"]
    audit = payload["audit"]
    db = payload["database_review"]
    totals = audit.get("totals", {})
    lines: list[str] = [
        "# Data Quality Deep Review",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Role Execution",
        "",
        "| Step | Acting role | Output |",
        "|---|---|---|",
        "| 1 | data_analyst | Reconciled saved corpus, DA-01, quality gate, importer candidates, media evidence, and denominator gaps. |",
        "| 2 | backend_developer | Reviewed BD-18 schema/import safety and patched source-publication-first importer guardrails. |",
        "| 3 | vision_media_agent | Assessed gallery evidence separately from inactive semantic image descriptions. |",
        "| 4 | market_intelligence_analyst | Produced accepted-only market-analysis readiness notes and limits. |",
        "| 5 | user_analytics_agent | Produced dashboard/funnel data requirements without adding third-party analytics. |",
        "",
        "## Verification Summary",
        "",
        f"- FACT: DA-01 audit rows: {fmt(totals.get('rows'))}; Action1 rows: {fmt(totals.get('action1_rows'))}.",
        f"- FACT: Importer default candidates: {fmt(totals.get('db_import_default_candidate_rows'))}; pending/missing QA: {fmt(totals.get('pending_or_missing_qa_rows'))}.",
        f"- FACT: Action1 offline estimate: {fmt(totals.get('action1_estimated_ok'))} accepted candidates, {fmt(totals.get('action1_estimated_lost'))} LOST, {fmt(totals.get('action1_estimated_grouped'))} grouped/development.",
        "- FACT: DB-backed counts remain blocked until `DATABASE_URL` exists and `make verify-db-counts` runs.",
        "- FACT: Image semantic descriptions are not active; gallery capture/media counts are evidence, image-description coverage is not.",
        "- INTERPRETATION: scraper repair can proceed fixture-first, but canonical property/offer promotion remains unsafe without BD-18 DB proof.",
        "- GAP: DA-02 denominator reconciliation and BD-18 DB smoke tests still require verifier acceptance.",
        "",
        "## Blocked From Canonical Import",
        "",
    ]
    blocked = [
        "PENDING_QA, missing-QA, UNKNOWN, and unreviewed rows",
        "LOST or needs_rescrape rows",
        "grouped/development/multi-unit publications without unit-level evidence",
        "inactive, removed, expired, stale-review, sold, or rented rows unless source-confirmed and reviewed",
        "numeric zero-price rows unless converted to null plus explicit price_status",
        "missing price without on_request/undefined provenance",
        "missing source URL/provenance, location, area, or required media evidence",
        "rows with local gallery gaps or image evidence overstated",
        "contact-only or mass-enriched personal data without provenance/permission metadata",
    ]
    lines.extend(f"- {item}" for item in blocked)
    lines.extend(["", "## Source Repair Table", ""])
    lines.append("| Source | Rows | Import candidates | Blocked | Risk | Top bad rules | Required scraper action |")
    lines.append("|---|---:|---:|---:|---|---|---|")
    for key, stats in sorted(scan["sources"].items()):
        top_rules = ", ".join(f"{rule}:{count}" for rule, count in list(stats["bad_rules_top"].items())[:4]) or "none"
        action = stats["repair_plan"]["inspect"]
        lines.append(
            f"| `{key}` | {fmt(stats['rows'])} | {fmt(stats['import_default_candidates'])} | "
            f"{fmt(stats['blocked_default_import'])} | {stats['risk_level']} | {top_rules} | {action} |"
        )
    lines.extend(["", "## Source-by-Source Repair Instructions", ""])
    for key, stats in sorted(scan["sources"].items()):
        repair = stats["repair_plan"]
        lines.extend(
            [
                f"### {key}",
                "",
                f"- FACT: rows={fmt(stats['rows'])}; default import candidates={fmt(stats['import_default_candidates'])}; blocked={fmt(stats['blocked_default_import'])}; risk={stats['risk_level']}.",
                f"- FACT: media rows with full gallery={fmt(stats['rows_full_gallery'])}; partial gallery={fmt(stats['rows_partial_gallery'])}; one-photo suspect={fmt(stats['rows_one_photo'])}.",
                f"- FACT: image semantic rows={fmt(stats['image_description_rows'])}; image report status={json.dumps(stats['image_report_status'], ensure_ascii=False)}.",
                f"- What is wrong: {repair['wrong']}",
                f"- Likely reason: {repair['likely_reason']}",
                f"- Inspect: {repair['inspect']}",
                f"- Fixture/sample: {repair['fixture']}",
                f"- Acceptance condition: {repair['acceptance']}",
                f"- Must remain blocked: {repair['blocked']}",
                f"- Example paths: {json.dumps(dict(list(stats['examples'].items())[:5]), ensure_ascii=False)}",
                "",
            ]
        )
    lines.extend(
        [
            "## Database/BD-18 Review",
            "",
            "| Concept | Status | Existing tables | Gap |",
            "|---|---|---|---|",
        ]
    )
    for concept in db["concepts"]:
        lines.append(
            f"| {concept['concept']} | {concept['status']} | {', '.join(concept['existing_found']) or 'none'} | {concept['gap']} |"
        )
    lines.extend(["", "### Required Corrections", ""])
    lines.extend(f"- {item}" for item in db["corrections_required"])
    lines.extend(["", "### Field Mapping", ""])
    lines.append("| Required field | Current state |")
    lines.append("|---|---|")
    for field, state in db["field_mapping"].items():
        lines.append(f"| {field} | {state} |")
    lines.extend(
        [
            "",
            "## Market Intelligence Readiness",
            "",
            "- FACT: Market analysis must use accepted/import-candidate evidence and clearly label file-backed scope.",
            "- INTERPRETATION: raw saved source volume shows scraper coverage and parser health, not market share.",
            "- GAP: DB-backed dedupe, current availability, and stale/out-of-stock status are not verified.",
            "",
            "### Accepted Offer Mix",
            "",
            "| Offer kind | Accepted rows | Price count | Median price |",
            "|---|---:|---:|---:|",
        ]
    )
    market = scan["market"]
    for offer, count in market["accepted_by_offer_kind"].items():
        prices = market["price_by_offer_kind"].get(offer, {})
        lines.append(f"| {offer} | {fmt(count)} | {fmt(prices.get('count'))} | {fmt(prices.get('median'))} |")
    lines.extend(
        [
            "",
            "## User Analytics Handoff",
            "",
            "- FACT: No live product analytics were queried or added in this run.",
            "- Required future events: listing impression, listing detail open, map result open, filter apply, save, contact intent, inquiry request, chat handoff, admin QA decision, media confidence interaction.",
            "- Payload rule: no raw source URLs, image URLs, phones, emails, names, raw chat text, IP addresses, user agents, or private notes in analytics events.",
            "- Dashboard denominator rule: funnels use first-party events after UI launch; corpus counts use DA/BD read models, not product telemetry.",
            "",
            "## Acceptance Gates Still Missing",
            "",
            "- DA-02 denominator contract must reconcile audit, importer, quality-gate, scrape-status, and operational dashboard semantics.",
            "- BD-18 DB smoke test must prove accepted-only source-publication import, zero-price null/status, grouped import blocking, media idempotency, and no default property_entity promotion.",
            "- INFRA-02 must run DB counts after `DATABASE_URL` is provided.",
            "- VM-02/VM-04 must verify gallery identity/local completeness before semantic image descriptions are trusted.",
            "- DBG gate must verify this dashboard/report and rerun importer dry-run plus parser/backend focused tests.",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_db_review_markdown(payload: dict[str, Any]) -> None:
    db = payload["database_review"]
    lines = [
        "# BD-18 Database Review And Correction Spec",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Result",
        "",
        "- FACT: DB-backed counts are still blocked by missing `DATABASE_URL`.",
        "- FACT: The current schema has partial source/publication, property, offer, media, contact, and CRM structures.",
        "- FACT: BD-18 evidence tables are now defined in schema/migration/ORM for QA reviews, status history, entity-resolution candidates/reviews, media descriptions, availability, inquiry requests, and external chat refs.",
        "- INTERPRETATION: scraper repair can write better source-publication evidence now, but default DB import must not promote to canonical property/offer until BD-18 DB tests pass.",
        "",
        "## Concept Coverage",
        "",
        "| Required concept | Status | Current mapping | Required correction |",
        "|---|---|---|---|",
    ]
    for item in db["concepts"]:
        lines.append(
            f"| {item['concept']} | {item['status']} | {', '.join(item['existing_found']) or 'none'} | {item['gap']} |"
        )
    lines.extend(
        [
            "",
            "## Safe Import Rules",
            "",
            "- Default import is accepted-only and source-publication-first.",
            "- Numeric price `0` is converted to `null` and preserved as `price_status=undefined` unless source evidence says `on_request`.",
            "- `PENDING_QA`, missing-QA, `UNKNOWN`, `LOST`, `needs_rescrape`, grouped/development, inactive, removed, expired, stale-review, sold, and rented rows remain blocked by default.",
            "- Property/entity promotion requires an explicit reviewed path and should not run from the scraped-corpus import default.",
            "- Source publication provenance, bucket, geo scope, QA state, media counts, local image keys, and contact provenance must survive import.",
            "",
            "## Tables To Add Or Refine",
            "",
            "1. `source_publication_qa_review`: migrate and smoke-test QA state, reviewer, reviewed_at, import_eligible, import_eligibility_reason, blocked_import_reason, evidence_jsonb.",
            "2. `status_history`: migrate and verify subject_type, subject_id, from_status, to_status, observed_at, source_observed_at, provenance_jsonb.",
            "3. `entity_resolution_candidate` / `entity_resolution_review_event`: keep reviewable candidate evidence separate from property promotion.",
            "4. `availability_calendar`, `availability_slot`, `availability_observation`: refine long-term viewing/inquiry availability separately from short-term booking calendars.",
            "5. `viewing_inquiry_request`: implement request workflow from platform/company to owner/realtor/company contact.",
            "6. `media_description`: use only after gallery identity/local image completeness is reliable and Action0 is approved.",
            "7. `external_chat_ref`: store thread/request/listing/offer handoff refs only; chat content remains outside listing truth.",
            "",
            "## Field Mapping",
            "",
            "| Field | Current state |",
            "|---|---|",
        ]
    )
    for field, state in db["field_mapping"].items():
        lines.append(f"| {field} | {state} |")
    DB_REVIEW_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def stat_card(label: str, value: Any, insight: str, details: str, action: str) -> str:
    return f"""
    <details class="stat" open>
      <summary><span class="label">{escape(label)}</span><span class="value">{escape(fmt(value))}</span></summary>
      <p><strong>Insight:</strong> {escape(insight)}</p>
      <p><strong>Details:</strong> {escape(details)}</p>
      <p><strong>Action:</strong> {escape(action)}</p>
    </details>
    """


def bar(value: int, max_value: int, cls: str = "") -> str:
    width = 0 if not max_value else max(2, min(100, round(value / max_value * 100)))
    return f'<span class="bar {cls}"><span style="width:{width}%"></span></span>'


def link_path(path: str) -> str:
    return "../../" + path


def write_dashboard(payload: dict[str, Any]) -> None:
    scan = payload["corpus_scan"]
    audit_totals = payload["audit"].get("totals", {})
    gate = payload["quality_gate"].get("quality_rollup", {})
    sources = scan["sources"]
    max_rows = max((stats["rows"] for stats in sources.values()), default=1)
    source_rows = []
    detail_sections = []
    for key, stats in sorted(sources.items()):
        top_rules = ", ".join(f"{rule} {count}" for rule, count in list(stats["bad_rules_top"].items())[:3]) or "none"
        source_rows.append(
            "<tr>"
            f"<td><a href=\"#{escape(key)}\">{escape(key)}</a></td>"
            f"<td>{fmt(stats['rows'])}{bar(stats['rows'], max_rows)}</td>"
            f"<td>{fmt(stats['import_default_candidates'])}</td>"
            f"<td>{fmt(stats['blocked_default_import'])}</td>"
            f"<td>{escape(stats['risk_level'])}</td>"
            f"<td>{fmt(stats['rows_full_gallery'])}/{fmt(stats['rows'])}</td>"
            f"<td>{fmt(stats['image_description_rows'])}</td>"
            f"<td>{escape(top_rules)}</td>"
            "</tr>"
        )
        examples = "".join(
            f"<li><code>{escape(rule)}</code>: <a href=\"{escape(link_path(path))}\">{escape(path)}</a></li>"
            for rule, path in list(stats["examples"].items())[:8]
        ) or "<li>No example captured.</li>"
        detail_sections.append(
            f"""
            <details class="source" id="{escape(key)}">
              <summary><span>{escape(key)}</span><strong>{fmt(stats['rows'])} rows</strong></summary>
              <div class="source-grid">
                {stat_card("Import candidates", stats["import_default_candidates"], "Accepted-only default import candidates.", "Rows still need DB-backed BD-18 proof before release claims.", "Use as internal QA/import fixture scope only.")}
                {stat_card("Blocked rows", stats["blocked_default_import"], "Blocked rows remain source publications or repair queues.", "Includes missing QA, LOST, grouped/development, inactive/stale, missing evidence, and media/contact issues.", "Scraper must repair or quarantine by rule.")}
                {stat_card("Gallery full rows", stats["rows_full_gallery"], "Local gallery evidence is separate from semantic image descriptions.", f"Partial={stats['rows_partial_gallery']}, one-photo suspect={stats['rows_one_photo']}, local exceeds remote={stats['rows_local_exceeds_remote']}.", "Do not start image descriptions until gallery identity is reliable.")}
                {stat_card("Semantic image rows", stats["image_description_rows"], "Image semantic descriptions are not active.", f"Report statuses: {stats['image_report_status']}", "Vision/media agent must verify Action0 before treating descriptions as evidence.")}
              </div>
              <h3>Repair Pattern</h3>
              <p><strong>Wrong:</strong> {escape(stats["repair_plan"]["wrong"])}</p>
              <p><strong>Likely reason:</strong> {escape(stats["repair_plan"]["likely_reason"])}</p>
              <p><strong>Inspect:</strong> {escape(stats["repair_plan"]["inspect"])}</p>
              <p><strong>Fixture/sample:</strong> {escape(stats["repair_plan"]["fixture"])}</p>
              <p><strong>Acceptance:</strong> {escape(stats["repair_plan"]["acceptance"])}</p>
              <p><strong>Blocked:</strong> {escape(stats["repair_plan"]["blocked"])}</p>
              <h3>Top Rules</h3>
              <table><tbody>{''.join(f'<tr><td>{escape(rule)}</td><td>{fmt(count)}</td></tr>' for rule, count in stats["bad_rules_top"].items())}</tbody></table>
              <h3>Examples</h3>
              <ul>{examples}</ul>
            </details>
            """
        )
    market_rows = "".join(
        f"<tr><td>{escape(kind)}</td><td>{fmt(count)}</td><td>{fmt(scan['market']['price_by_offer_kind'].get(kind, {}).get('median'))}</td></tr>"
        for kind, count in scan["market"]["accepted_by_offer_kind"].items()
    )
    city_rows = "".join(
        f"<tr><td>{escape(city)}</td><td>{fmt(count)}</td></tr>"
        for city, count in scan["market"]["accepted_by_city"].items()
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Data Quality Deep Review | Bulgaria Real Estate Ops</title>
  <style>
    :root {{ --bg:#f6f8fb; --panel:#fff; --ink:#152033; --muted:#637083; --line:#d9e2ec; --good:#047857; --warn:#b45309; --bad:#b91c1c; --info:#1d4ed8; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--bg); color:var(--ink); font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height:1.45; }}
    header {{ background:#fff; border-bottom:1px solid var(--line); padding:28px min(5vw,56px) 20px; }}
    main {{ padding:24px min(5vw,56px) 56px; }}
    h1 {{ margin:0 0 6px; font-size:clamp(28px,4vw,44px); letter-spacing:0; }}
    h2 {{ margin:30px 0 12px; font-size:22px; letter-spacing:0; }}
    h3 {{ margin:18px 0 8px; font-size:16px; letter-spacing:0; }}
    nav {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:18px; }}
    nav a {{ border:1px solid var(--line); border-radius:6px; padding:8px 10px; background:#f8fafc; color:var(--ink); text-decoration:none; font-size:14px; }}
    a {{ color:var(--info); text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    .muted {{ color:var(--muted); }}
    .grid,.source-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:12px; }}
    .wide {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(330px,1fr)); gap:12px; }}
    .panel, details.stat, details.source {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:14px; }}
    details.stat summary, details.source summary {{ cursor:pointer; list-style:none; }}
    details.stat summary::-webkit-details-marker, details.source summary::-webkit-details-marker {{ display:none; }}
    details.source summary {{ display:flex; justify-content:space-between; gap:12px; font-size:18px; }}
    .label {{ display:block; color:var(--muted); font-size:13px; }}
    .value {{ display:block; font-size:28px; font-weight:760; line-height:1.15; }}
    table {{ width:100%; border-collapse:collapse; background:#fff; border:1px solid var(--line); border-radius:8px; overflow:hidden; }}
    th,td {{ padding:9px 10px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; font-size:14px; }}
    th {{ background:#eef3f8; color:#435166; font-size:12px; text-transform:uppercase; letter-spacing:.02em; }}
    .bar {{ display:block; height:6px; background:#e5eaf1; border-radius:999px; margin-top:6px; overflow:hidden; }}
    .bar span {{ display:block; height:100%; background:var(--info); }}
    code {{ background:#eef3f8; padding:2px 5px; border-radius:4px; }}
    footer {{ color:var(--muted); padding:0 min(5vw,56px) 32px; font-size:13px; }}
  </style>
</head>
<body>
<header>
  <p class="muted">Generated {escape(payload['generated_at'])}. File-backed only; no live scraping or DB count claim.</p>
  <h1>Data Quality Deep Review</h1>
  <p class="muted">Scrape/database QA, BD-18 blockers, source repair patterns, media evidence, market-intelligence limits, and analytics handoff.</p>
  <nav>
    <a href="index.html">Hub</a>
    <a href="properties-database.html">Properties Database</a>
    <a href="data-quality-dashboard.html">Deep Data Quality</a>
    <a href="scrape-status.html">Source Matrix</a>
    <a href="../exports/data-quality-deep-review-{REPORT_DATE}.md">Report</a>
    <a href="../exports/bd18-database-review-and-correction-spec-{REPORT_DATE}.md">BD-18 Spec</a>
  </nav>
</header>
<main>
  <section class="grid">
    {stat_card("Audit rows", audit_totals.get("rows"), "DA-01 file-backed corpus size.", "This is saved corpus evidence, not DB-backed count.", "Keep DB claims blocked until DATABASE_URL and INFRA-02.")}
    {stat_card("Action1 rows", audit_totals.get("action1_rows"), "Controlled A1 source/bucket scope.", "Seven Action1 sources across buy/rent personal/commercial buckets.", "Repair A1 before widening Action2.")}
    {stat_card("Importer candidates", audit_totals.get("db_import_default_candidate_rows"), "Default import remains accepted-only.", "Importer now avoids default property_entity promotion.", "Use dry-run until BD-18 DB proof.")}
    {stat_card("Pending/missing QA", audit_totals.get("pending_or_missing_qa_rows"), "Largest repair queue.", "Rows without QA state cannot enter public views.", "Scraper and DA-02 must classify or quarantine.")}
    {stat_card("Gate good rows", gate.get("good_single_unit"), "Offline single-unit estimate.", "Needs denominator reconciliation with importer/dashboard.", "Do not call this market coverage.")}
    {stat_card("Gate LOST", gate.get("bad_lost"), "Repair/quarantine queue.", "LOST rows are not canonical properties.", "Scraper consumes LOST fixtures source by source.")}
    {stat_card("Gate grouped", gate.get("grouped_publication"), "Source publications, not units.", "Development/project pages need unit-level evidence before split.", "Keep out of canonical import.")}
    {stat_card("Zero price rows", scan["totals"].get("numeric_zero_price", 0), "Numeric zero is invalid as real price.", "Importer coerces zero to null plus price_status provenance.", "Parser must write price_status explicitly.")}
  </section>
  <h2>Source Overview</h2>
  <table>
    <thead><tr><th>Source</th><th>Rows</th><th>Import candidates</th><th>Blocked</th><th>Risk</th><th>Full gallery</th><th>Image descriptions</th><th>Top rules</th></tr></thead>
    <tbody>{''.join(source_rows)}</tbody>
  </table>
  <h2>Source Drilldown</h2>
  <section class="wide">{''.join(detail_sections)}</section>
  <h2>Market Intelligence Readiness</h2>
  <section class="wide">
    <div class="panel">
      <h3>Accepted Offer Mix</h3>
      <table><thead><tr><th>Offer kind</th><th>Accepted rows</th><th>Median price</th></tr></thead><tbody>{market_rows}</tbody></table>
    </div>
    <div class="panel">
      <h3>Accepted Cities</h3>
      <table><thead><tr><th>City</th><th>Accepted rows</th></tr></thead><tbody>{city_rows}</tbody></table>
    </div>
  </section>
  <h2>Analytics Handoff</h2>
  <div class="panel">
    <p><strong>FACT:</strong> No product telemetry was read or added. Current analysis is corpus/file-backed.</p>
    <p><strong>INTERPRETATION:</strong> Future funnels must separate product events from data-quality counts.</p>
    <p><strong>GAP:</strong> UA-02/BD-20/UA-03 remain needed before live analytics dashboards.</p>
  </div>
</main>
<footer>Unsafe canonical import remains blocked. Semantic image descriptions remain unverified.</footer>
</body>
</html>
"""
    DASHBOARD_HTML.write_text(html, encoding="utf-8")


def main() -> int:
    EXPORTS.mkdir(parents=True, exist_ok=True)
    DASHBOARD.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    audit = read_json(EXPORTS / "scrape-database-quality-audit-2026-05-13.json", {})
    quality_gate = compact_quality_gate(read_json(EXPORTS / "action1-dataset-quality-gate.json", {}))
    scrape_status = compact_scrape_status(read_json(EXPORTS / "scrape-status-dashboard.json", {}))
    payload = {
        "generated_at": generated_at,
        "skills_used": [
            "hugging-face:huggingface-datasets (local read-only pagination/statistics pattern; no HF network call)",
            "data-analytics-insight",
            "data-architecture-pipelines",
            "backend-api-architecture",
            "dashboard-visual-ops",
        ],
        "audit": audit,
        "quality_gate": quality_gate,
        "scrape_status": scrape_status,
        "source_registry_count": len(load_registry()),
        "corpus_scan": scan_corpus(),
        "database_review": db_review(),
        "acceptance_gates": {
            "unsafe_import_blocked_by_default": True,
            "zero_price_to_null_status_required": True,
            "grouped_development_noncanonical_by_default": True,
            "db_counts_verified": False,
            "db_counts_blocker": "DATABASE_URL missing",
            "image_semantic_descriptions_verified": False,
            "image_semantic_description_note": "Inactive until gallery identity/local completeness is reliable.",
        },
    }
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(payload)
    write_db_review_markdown(payload)
    write_dashboard(payload)
    print(f"Wrote {REPORT_JSON.relative_to(REPO)}")
    print(f"Wrote {REPORT_MD.relative_to(REPO)}")
    print(f"Wrote {DB_REVIEW_MD.relative_to(REPO)}")
    print(f"Wrote {DASHBOARD_HTML.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
