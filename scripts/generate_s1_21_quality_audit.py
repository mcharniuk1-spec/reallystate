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
    areas: int = 0
    city_or_address: int = 0
    remote_photos: int = 0
    local_photo_refs: int = 0
    valid_local_files: int = 0
    missing_local_files: int = 0
    full_gallery_items: int = 0
    complete_local_gallery_items: int = 0
    action0_eligible_items: int = 0
    same_location_items: int = 0
    same_location_groups: int = 0
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
    deal = "rent" if intent in {"rent", "short_term_rental"} else "buy"
    space = "commercial" if category in {"office", "shop", "land", "garage"} else "residential"
    return f"{deal}_{space}"


def row_gaps(row: dict[str, Any], valid_files: int) -> list[str]:
    gaps: list[str] = []
    desc = row.get("description") or ""
    if not desc:
        gaps.append("missing_description")
    elif len(desc) < 160:
        gaps.append("thin_description")
    if row.get("price") is None:
        gaps.append("missing_price")
    if row.get("area_sqm") is None:
        gaps.append("missing_area")
    if not (row.get("city") or row.get("address_text")):
        gaps.append("missing_city_or_address")
    if remote_count(row) and valid_files < remote_count(row):
        gaps.append("partial_or_missing_local_gallery")
    if not row.get("image_report_status") or row.get("image_report_status") == "missing":
        gaps.append("missing_image_report")
    if not location_group_key(row):
        gaps.append("no_strong_location_group_key")
    return gaps


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
            if row.get("area_sqm") is not None:
                source.areas += 1
            if row.get("city") or row.get("address_text"):
                source.city_or_address += 1
            remote = remote_count(row)
            local_ref_count = expected_local_count(row)
            valid_files = sum(1 for item in local_files(row) if file_valid(item))
            source.remote_photos += remote
            source.local_photo_refs += local_ref_count
            source.valid_local_files += valid_files
            source.missing_local_files += max(0, local_ref_count - valid_files)
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
        "| Source | Items | Desc | Thin desc | Price | Area | City/address | Remote photos | Valid local files | Full galleries | Complete local galleries | Action0 eligible | Same-location items | Top gaps |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for source in data["sources"]:
        top_gaps = ", ".join(f"{key}:{value}" for key, value in (source.get("top_gaps") or {}).items())
        row = {**source, "top_gaps_text": top_gaps}
        lines.append(
            "| {source_name} | {saved_items} | {descriptions} | {thin_descriptions} | {prices} | {areas} | {city_or_address} | {remote_photos} | {valid_local_files} | {full_gallery_items} | {complete_local_gallery_items} | {action0_eligible_items} | {same_location_items} | {top_gaps_text} |".format(
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
