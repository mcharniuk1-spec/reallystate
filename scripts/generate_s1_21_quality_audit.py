#!/usr/bin/env python3
"""Generate the S1-21 tier-1/2 quality audit and Gemma action inputs."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRAPED_ROOT = ROOT / "data" / "scraped"
EXPORTS = ROOT / "docs" / "exports"

PRIORITY_SOURCES = {
    "address_bg": "Address.bg",
    "bulgarianproperties": "BulgarianProperties",
    "homes_bg": "Homes.bg",
    "imot_bg": "imot.bg",
    "luximmo": "LUXIMMO",
    "property_bg": "property.bg",
    "suprimmo": "SUPRIMMO",
}


@dataclass
class SourceAudit:
    source_key: str
    source_name: str
    saved_items: int = 0
    descriptions: int = 0
    thin_descriptions: int = 0
    prices: int = 0
    zero_prices: int = 0
    areas: int = 0
    suspicious_area_values: int = 0
    city_or_address: int = 0
    remote_photos: int = 0
    local_photo_refs: int = 0
    valid_local_files: int = 0
    missing_local_files: int = 0
    full_gallery_items: int = 0
    complete_local_gallery_items: int = 0
    one_remote_photo_items: int = 0
    one_local_photo_items: int = 0
    geo_points: int = 0
    outside_bulgaria_coordinates: int = 0
    action0_eligible_items: int = 0
    same_location_items: int = 0
    same_location_groups: int = 0
    suspected_multi_unit_publications: int = 0
    lost_rescrape_required: int = 0
    grouped_publications: int = 0
    accepted_single_entity_candidates: int = 0
    bucket_counts: dict[str, int] | None = None
    category_counts: dict[str, int] | None = None
    top_gaps: dict[str, int] | None = None


def normalize_text(value: Any) -> str:
    return re.sub(r"[^\w]+", " ", str(value or "").lower(), flags=re.UNICODE).strip()


def useful_address(row: dict[str, Any]) -> str:
    address = normalize_text(row.get("address_text"))
    if not address or len(address) < 5:
        return ""
    city = normalize_text(row.get("city") or row.get("region"))
    district = normalize_text(row.get("district") or row.get("resort"))
    weak = {item for item in [city, district, f"{city} {district}".strip(), f"{district} {city}".strip()] if item}
    return "" if address in weak else address


def location_group_key(row: dict[str, Any]) -> str:
    address = useful_address(row)
    if not address:
        return ""
    city = normalize_text(row.get("city") or row.get("region")) or "bg"
    district = normalize_text(row.get("district") or row.get("resort")) or "area"
    return f"{city}::{district}::{address}"


def expected_local_count(row: dict[str, Any]) -> int:
    value = row.get("photo_count_local")
    if isinstance(value, int):
        return value
    return len(row.get("local_image_files") or [])


def remote_count(row: dict[str, Any]) -> int:
    value = row.get("photo_count_remote")
    if isinstance(value, int):
        return value
    return len(row.get("image_urls") or [])


def local_files(row: dict[str, Any]) -> list[str]:
    return [item for item in row.get("local_image_files") or [] if isinstance(item, str)]


def file_valid(path_text: str) -> bool:
    path = Path(path_text)
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists() or path.stat().st_size <= 0:
        return False
    try:
        with path.open("rb") as fh:
            header = fh.read(16)
    except OSError:
        return False
    return header.startswith(b"\xff\xd8") or header.startswith(b"\x89PNG") or header.startswith(b"GIF8") or header.startswith(b"RIFF")


def bucket(row: dict[str, Any]) -> str:
    intent = str(row.get("listing_intent") or "sale").lower()
    category = str(row.get("property_category") or "other").lower()
    deal = "rent" if intent in {"rent", "long_term_rent", "short_term_rent", "short_term_rental"} else "buy"
    space = "commercial" if category in {"office", "shop", "land", "garage"} else "residential"
    return f"{deal}_{space}"


def coordinates_in_bulgaria(row: dict[str, Any]) -> bool:
    try:
        latitude = float(row.get("latitude"))
        longitude = float(row.get("longitude"))
    except (TypeError, ValueError):
        return False
    if not (41.0 <= latitude <= 44.5 and 22.0 <= longitude <= 29.5):
        return False
    polygon = [
        (22.35, 44.22), (22.90, 44.05), (23.80, 44.18), (24.80, 43.95),
        (25.30, 43.70), (26.05, 43.98), (27.30, 44.15), (28.60, 43.75),
        (28.60, 43.25), (28.20, 42.00), (27.50, 41.90), (26.30, 41.75),
        (25.25, 41.25), (24.00, 41.35), (22.90, 41.25), (22.35, 41.60),
    ]
    inside = False
    j = len(polygon) - 1
    for i, (xi, yi) in enumerate(polygon):
        xj, yj = polygon[j]
        if ((yi > latitude) != (yj > latitude)) and (
            longitude < (xj - xi) * (latitude - yi) / ((yj - yi) or 1e-12) + xi
        ):
            inside = not inside
        j = i
    return inside


def row_gaps(row: dict[str, Any], valid_files: int) -> list[str]:
    gaps: list[str] = []
    if row.get("scrape_status") == "LOST" or row.get("needs_rescrape") is True:
        gaps.append("lost_rescrape_required")
    if (
        row.get("source_publication_type") == "multi_unit_or_development"
        or row.get("scrape_acceptance_status") == "not_single_entity"
    ):
        gaps.append("grouped_publication_not_single_entity")
    desc = row.get("description") or ""
    if not desc:
        gaps.append("missing_description")
    elif len(desc) < 160:
        gaps.append("thin_description")
    if row.get("price") is None:
        gaps.append("missing_price")
    elif row.get("price") == 0:
        gaps.append("zero_price_needs_on_request_or_undefined_status")
    if row.get("area_sqm") is None:
        gaps.append("missing_area")
    elif isinstance(row.get("area_sqm"), (int, float)) and 0 < float(row.get("area_sqm")) < 2:
        gaps.append("suspicious_area_decimal_parse")
    if not (row.get("city") or row.get("address_text")):
        gaps.append("missing_city_or_address")
    if remote_count(row) and valid_files < remote_count(row):
        gaps.append("partial_or_missing_local_gallery")
    if remote_count(row) == 1 and row.get("source_name") in {"Address.bg", "BulgarianProperties", "Homes.bg", "imot.bg", "LUXIMMO", "property.bg", "SUPRIMMO"}:
        gaps.append("one_remote_photo_gallery_suspect")
    if row.get("latitude") is not None and row.get("longitude") is not None and not coordinates_in_bulgaria(row):
        gaps.append("outside_bulgaria_coordinates")
    if not row.get("image_report_status") or row.get("image_report_status") == "missing":
        gaps.append("missing_image_report")
    if not location_group_key(row):
        gaps.append("no_strong_location_group_key")
    if suspected_multi_unit_publication(row):
        gaps.append("suspected_multi_unit_publication")
    return gaps


def is_accepted_single_candidate(row: dict[str, Any]) -> bool:
    if row.get("scrape_status") == "LOST" or row.get("needs_rescrape") is True:
        return False
    if (
        row.get("source_publication_type") == "multi_unit_or_development"
        or row.get("scrape_acceptance_status") == "not_single_entity"
    ):
        return False
    return True


MULTI_UNIT_PATTERNS = [
    re.compile(r"\b\d+\s*[-–/]\s*\d+\s*(bedroom|bed|room|спалн|стайн|стаен)\b", re.I),
    re.compile(r"\b(one|two|three|four)\s*[-–/]\s*(two|three|four)\s*(bedroom|bed|room)\b", re.I),
    re.compile(r"(apartments\s*\(various\s*types\)|various_types|different apartments|apartments available|units available|selection of|choice of|цени\s+от|цена\s+от|prices?\s+from|starting\s+from)", re.I),
    re.compile(r"(жилищна сграда|residential building|new residential building|new development|residential complex)", re.I),
]


def suspected_multi_unit_publication(row: dict[str, Any]) -> bool:
    text = "\n".join(str(row.get(key) or "") for key in ("title", "description", "listing_url"))
    return any(pattern.search(text) for pattern in MULTI_UNIT_PATTERNS)


def read_rows(source_key: str) -> list[tuple[Path, dict[str, Any]]]:
    listing_dir = SCRAPED_ROOT / source_key / "listings"
    rows: list[tuple[Path, dict[str, Any]]] = []
    if not listing_dir.exists():
        return rows
    for path in sorted(listing_dir.glob("*.json")):
        try:
            rows.append((path, json.loads(path.read_text(encoding="utf-8"))))
        except Exception:
            continue
    return rows


def audit() -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()
    source_audits: list[SourceAudit] = []
    action0: list[dict[str, Any]] = []
    all_location_groups: dict[str, list[str]] = defaultdict(list)
    item_gaps: list[dict[str, Any]] = []

    loaded: dict[str, list[tuple[Path, dict[str, Any]]]] = {
        source_key: read_rows(source_key) for source_key in PRIORITY_SOURCES
    }
    for rows in loaded.values():
        for _path, row in rows:
            key = location_group_key(row)
            if key:
                all_location_groups[key].append(row.get("reference_id") or "")

    duplicate_location_refs = {
        ref
        for refs in all_location_groups.values()
        if len(set(refs)) > 1
        for ref in refs
        if ref
    }

    for source_key, source_name in PRIORITY_SOURCES.items():
        rows = loaded[source_key]
        gaps = Counter()
        buckets = Counter()
        categories = Counter()
        location_keys = Counter()
        source = SourceAudit(source_key=source_key, source_name=source_name)

        for path, row in rows:
            source.saved_items += 1
            desc = row.get("description") or ""
            if desc:
                source.descriptions += 1
                if len(desc) < 160:
                    source.thin_descriptions += 1
            if row.get("price") is not None:
                source.prices += 1
                if row.get("price") == 0:
                    source.zero_prices += 1
            if row.get("area_sqm") is not None:
                source.areas += 1
                if isinstance(row.get("area_sqm"), (int, float)) and 0 < float(row.get("area_sqm")) < 2:
                    source.suspicious_area_values += 1
            if row.get("city") or row.get("address_text"):
                source.city_or_address += 1
            remote = remote_count(row)
            local_ref_count = expected_local_count(row)
            valid_files = sum(1 for item in local_files(row) if file_valid(item))
            source.remote_photos += remote
            source.local_photo_refs += local_ref_count
            source.valid_local_files += valid_files
            source.missing_local_files += max(0, local_ref_count - valid_files)
            if remote == 1:
                source.one_remote_photo_items += 1
            if local_ref_count == 1:
                source.one_local_photo_items += 1
            if row.get("latitude") is not None and row.get("longitude") is not None:
                source.geo_points += 1
                if not coordinates_in_bulgaria(row):
                    source.outside_bulgaria_coordinates += 1
            if row.get("full_gallery_downloaded"):
                source.full_gallery_items += 1
            if remote > 0 and valid_files >= remote:
                source.complete_local_gallery_items += 1
            key = location_group_key(row)
            if key:
                location_keys[key] += 1
            ref = row.get("reference_id") or path.stem
            if ref in duplicate_location_refs:
                source.same_location_items += 1
            if suspected_multi_unit_publication(row):
                source.suspected_multi_unit_publications += 1
            if row.get("scrape_status") == "LOST" or row.get("needs_rescrape") is True:
                source.lost_rescrape_required += 1
            if (
                row.get("source_publication_type") == "multi_unit_or_development"
                or row.get("scrape_acceptance_status") == "not_single_entity"
            ):
                source.grouped_publications += 1
            if row.get("scrape_acceptance_status") == "accepted_single_entity_candidate":
                source.accepted_single_entity_candidates += 1
            buckets[bucket(row)] += 1
            categories[str(row.get("property_category") or "unknown")] += 1
            row_gap_list = row_gaps(row, valid_files)
            gaps.update(row_gap_list)
            if row_gap_list:
                item_gaps.append(
                    {
                        "source_key": source_key,
                        "source_name": source_name,
                        "reference_id": ref,
                        "listing_json_path": str(path),
                        "listing_url": row.get("listing_url"),
                        "gaps": row_gap_list,
                    }
                )

            if (
                is_accepted_single_candidate(row)
                and
                local_files(row)
                and remote > 0
                and valid_files >= min(remote, len(local_files(row)))
                and desc
                and row.get("price") is not None
                and row.get("area_sqm") is not None
            ):
                source.action0_eligible_items += 1
                action0.append(
                    {
                        "action": "action0_image_by_image_property_description",
                        "source_key": source_key,
                        "source_name": source_name,
                        "reference_id": ref,
                        "listing_json_path": str(path),
                        "listing_url": row.get("listing_url"),
                        "property_category": row.get("property_category"),
                        "listing_intent": row.get("listing_intent"),
                        "title": row.get("title"),
                        "price": row.get("price"),
                        "currency": row.get("currency"),
                        "area_sqm": row.get("area_sqm"),
                        "city": row.get("city"),
                        "district": row.get("district"),
                        "address_text": row.get("address_text"),
                        "photo_count_remote": remote,
                        "photo_count_local_valid": valid_files,
                        "local_image_files": local_files(row),
                        "location_group_key": key,
                        "same_location_group_size": len(all_location_groups.get(key, [])) if key else 0,
                    }
                )

        source.same_location_groups = sum(1 for key, count in location_keys.items() if count > 1 or len(set(all_location_groups.get(key, []))) > 1)
        source.bucket_counts = dict(sorted(buckets.items()))
        source.category_counts = dict(sorted(categories.items()))
        source.top_gaps = dict(gaps.most_common(10))
        source_audits.append(source)

    action0.sort(
        key=lambda row: (
            row["source_key"],
            -int(row.get("photo_count_local_valid") or 0),
            str(row.get("reference_id")),
        )
    )
    return {
        "generated_at": generated_at,
        "scope": "S1-21 offline file-backed audit for seven priority tier-1/2 sources",
        "sources": [asdict(source) for source in source_audits],
        "action0_eligible": action0,
        "same_location_groups": [
            {"location_group_key": key, "count": len(set(refs)), "reference_ids": sorted(set(refs))}
            for key, refs in sorted(all_location_groups.items())
            if len(set(refs)) > 1
        ],
        "item_gaps": item_gaps[:500],
    }


def write_markdown(data: dict[str, Any], path: Path) -> None:
    lines = [
        "# S1-21 Tier-1/2 Scrape Quality Audit",
        "",
        f"Generated: {data['generated_at']}",
        "",
        "FACT: This is an offline file-backed audit. It does not prove new live scraping or PostgreSQL `canonical_listing` counts.",
        "",
        "## Source Summary",
        "",
        "| Source | Items | Accepted single | LOST | Grouped | Desc | Thin desc | Price | Zero price | Area | Area suspect | City/address | Remote photos | Valid local files | One-photo remote | One-photo local | Geo points | Outside-BG geo | Full galleries | Complete local galleries | Action0 eligible | Same-location items | Multi-unit suspects | Top gaps |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for source in data["sources"]:
        top_gaps = ", ".join(f"{key}:{value}" for key, value in (source.get("top_gaps") or {}).items())
        row = {**source, "top_gaps_text": top_gaps}
        lines.append(
            "| {source_name} | {saved_items} | {accepted_single_entity_candidates} | {lost_rescrape_required} | {grouped_publications} | {descriptions} | {thin_descriptions} | {prices} | {zero_prices} | {areas} | {suspicious_area_values} | {city_or_address} | {remote_photos} | {valid_local_files} | {one_remote_photo_items} | {one_local_photo_items} | {geo_points} | {outside_bulgaria_coordinates} | {full_gallery_items} | {complete_local_gallery_items} | {action0_eligible_items} | {same_location_items} | {suspected_multi_unit_publications} | {top_gaps_text} |".format(
                **row,
            )
        )

    lines.extend(
        [
            "",
            "## Action Sequence",
            "",
            "0. **Action0 - image-by-image property report**: use `docs/exports/s1-21-gemma-action0-eligible.json`; describe every local image, then produce one whole-property visual/QA description.",
            "1. **Action1 - full scrape/backfill seven priority sources**: run the all-Bulgaria/full-gallery scrape or backfill for `Address.bg`, `BulgarianProperties`, `Homes.bg`, `imot.bg`, `LUXIMMO`, `property.bg`, and `SUPRIMMO` across buy residential, buy commercial, rent residential, and rent commercial.",
            "2. **Action2 - remaining sources**: after Action1, widen to the rest of the legal tier-1/2 source set and repeat Action0 reporting for newly complete local galleries.",
            "",
            "## Same-Location Grouping",
            "",
            "Same-location grouping is intentionally based on useful `address_text` plus city/district. It excludes city-only or district-only labels, so the website Aggregate filter does not group whole districts as duplicate properties.",
            "",
            "## Property Identity Rules",
            "",
            "- A saved row is one source publication. It becomes one property item only when the source page clearly advertises one unit with its own price or explicit on-request/undefined price state.",
            "- Multi-unit publications such as `1-2 bedroom`, `apartments (various types)`, whole residential buildings, or price-from development pages must be flagged as `suspected_multi_unit_publication` and split into unit rows only when the source exposes unit-level price/area/URL evidence.",
            "- Numeric `0` must not be treated as a real price. Store no numeric price and preserve `price_status = on_request` or `price_status = undefined` in provenance until the schema has a first-class field.",
            "- Suspicious areas below 2 sqm indicate parser decimal mistakes and must not pass publishing QA.",
            "- Any saved coordinate outside Bulgaria bounds (lat 41.0-44.5, lon 22.0-29.5) is a hard geospatial QA failure.",
            "- One-photo rows are only accepted when the source detail page truly exposes one gallery image; otherwise they indicate gallery-pattern or media-backfill failure.",
            "",
            f"- Same-location groups found: {len(data['same_location_groups'])}",
            f"- Action0 eligible rows: {len(data['action0_eligible'])}",
            f"- Item gaps sampled in JSON: {len(data['item_gaps'])}",
            "",
            "## Outputs",
            "",
            "- `docs/exports/s1-21-tier12-quality-audit-2026-04-29.json`",
            "- `docs/exports/s1-21-gemma-action0-eligible.json`",
            "- `docs/exports/s1-21-tier12-quality-audit-2026-04-29.md`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    EXPORTS.mkdir(parents=True, exist_ok=True)
    data = audit()
    json_path = EXPORTS / "s1-21-tier12-quality-audit-2026-04-29.json"
    action0_path = EXPORTS / "s1-21-gemma-action0-eligible.json"
    md_path = EXPORTS / "s1-21-tier12-quality-audit-2026-04-29.md"
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    action0_path.write_text(json.dumps(data["action0_eligible"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(data, md_path)
    print(f"Wrote {json_path}")
    print(f"Wrote {action0_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
