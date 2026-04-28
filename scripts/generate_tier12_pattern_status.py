#!/usr/bin/env python3
"""Generate tier-1/2 pattern status, sample capture evidence, and count readiness."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO / "data" / "source_registry.json"
SCRAPED_ROOT = REPO / "data" / "scraped"
MEDIA_ROOT = REPO / "data" / "media"
EXPORTS = REPO / "docs" / "exports"
WEBSITE_INVENTORY_JSON = EXPORTS / "website-inventory-analysis.json"
SCRAPE_STATUS_JSON = EXPORTS / "scrape-status-dashboard.json"
OUTPUT_JSON = EXPORTS / "tier12-pattern-status.json"
OUTPUT_MD = EXPORTS / "tier12-pattern-status.md"


PATTERN_METHODS = {
    "Homes.bg": {
        "code_paths": ["scripts/live_scraper.py::_scrape_homes_bg", "scripts/live_scraper.py::parse_homes_detail"],
        "method": "Homes JSON discovery API + detail-page `__PRELOADED_STATE__` extraction with full gallery download.",
    },
    "imot.bg": {
        "code_paths": ["scripts/live_scraper.py::_scrape_imot_bg", "scripts/live_scraper.py::parse_imot_detail"],
        "method": "Server-rendered search pagination + filtered `obiava-*` detail URLs + structured detail-page blocks for params, text, phones, and full gallery.",
    },
}


@dataclass
class SampleEvidence:
    source_key: str
    listing_root: str
    raw_root: str
    listing_path: str
    raw_path: str
    media_dir: str
    reference_id: str
    listing_url: str
    title: str
    description_chars: int
    remote_photo_count: int
    local_photo_count: int
    local_photo_coverage_pct: float
    has_full_gallery: bool
    has_description: bool
    has_price: bool
    has_area: bool
    has_rooms: bool
    has_floor: bool
    has_phones: bool
    has_city: bool
    has_district: bool
    has_address: bool
    has_local_image_files: bool
    local_image_files_count: int
    local_image_files_preview: list[str]
    structured_fields_count: int
    source_attributes_count: int


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_ref(reference_id: str) -> str:
    return "".join("_" if c in '/:*?"<>|\\' else c for c in reference_id)


def load_registry_rows() -> list[dict]:
    rows = load_json(REGISTRY_PATH)["sources"]
    return [row for row in rows if row.get("tier") in (1, 2)]


def load_inventory() -> dict[str, dict]:
    payload = load_json(WEBSITE_INVENTORY_JSON) if WEBSITE_INVENTORY_JSON.exists() else {"sources": []}
    return {row["source_name"]: row for row in payload.get("sources", [])}


def load_scrape_status() -> dict[str, dict]:
    payload = load_json(SCRAPE_STATUS_JSON) if SCRAPE_STATUS_JSON.exists() else {"sources": []}
    return {row["source_name"]: row for row in payload.get("sources", [])}


def build_source_key_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for listing_path in SCRAPED_ROOT.glob("*/listings/*.json"):
        try:
            payload = json.loads(listing_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        source_name = payload.get("source_name")
        if source_name and source_name not in mapping:
            mapping[source_name] = listing_path.parent.parent.name
    return mapping


def sample_score(payload: dict[str, Any], local_photo_count: int, listing_path: Path) -> tuple[int, ...]:
    remote = len(payload.get("image_urls") or [])
    structured_fields = sum(
        1 for key in ("area_sqm", "rooms", "floor")
        if payload.get(key) is not None
    ) + (1 if payload.get("phones") else 0)
    return (
        1 if remote and local_photo_count >= remote else 0,
        1 if local_photo_count > 0 else 0,
        1 if payload.get("description") else 0,
        1 if payload.get("price") is not None else 0,
        1 if payload.get("address_text") else 0,
        1 if payload.get("city") else 0,
        structured_fields,
        1 if payload.get("area_sqm") is not None else 0,
        1 if payload.get("rooms") is not None else 0,
        1 if payload.get("floor") is not None else 0,
        1 if payload.get("phones") else 0,
        len(payload.get("source_attributes") or {}),
        min(local_photo_count, remote),
        remote,
        listing_path.stat().st_mtime,
    )


def find_best_sample(source_key: str, source_name: str) -> SampleEvidence | None:
    listing_dir = SCRAPED_ROOT / source_key / "listings"
    raw_dir = SCRAPED_ROOT / source_key / "raw"
    if not listing_dir.exists():
        return None

    best: tuple[tuple[int, int, int, int], SampleEvidence] | None = None
    for listing_path in listing_dir.glob("*.json"):
        try:
            payload = json.loads(listing_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if (payload.get("source_name") or source_name) != source_name:
            continue
        listing_url = str(payload.get("listing_url") or "").lower()
        title = str(payload.get("title") or "").lower()
        if any(skip in listing_url for skip in ("zhilishten-kompleks", "zhilishtna-sgrada")):
            continue
        if any(skip in title for skip in ("жилищен комплекс", "жилищна сграда")):
            continue
        reference_id = payload.get("reference_id") or ""
        media_dir = MEDIA_ROOT / safe_ref(reference_id)
        local_photo_count = sum(1 for p in media_dir.iterdir()) if media_dir.exists() else 0
        remote_photo_count = len(payload.get("image_urls") or [])
        coverage = (local_photo_count / remote_photo_count * 100.0) if remote_photo_count else 0.0
        local_image_files = payload.get("local_image_files") or []
        if not local_image_files and media_dir.exists():
            local_image_files = [str(path.relative_to(REPO)) for path in sorted(p for p in media_dir.iterdir() if p.is_file())]
        structured_fields_count = sum(bool(payload.get(key) is not None) for key in ("area_sqm", "rooms", "floor")) + (1 if payload.get("phones") else 0)
        sample = SampleEvidence(
            source_key=source_key,
            listing_root=str(listing_dir.resolve()),
            raw_root=str(raw_dir.resolve()),
            listing_path=str(listing_path.resolve()),
            raw_path=str((raw_dir / listing_path.with_suffix(".html").name).resolve()),
            media_dir=str(media_dir.resolve()),
            reference_id=reference_id,
            listing_url=str(payload.get("listing_url") or ""),
            title=str(payload.get("title") or ""),
            description_chars=len(str(payload.get("description") or "")),
            remote_photo_count=remote_photo_count,
            local_photo_count=local_photo_count,
            local_photo_coverage_pct=coverage,
            has_full_gallery=remote_photo_count > 0 and local_photo_count >= remote_photo_count,
            has_description=bool(payload.get("description")),
            has_price=payload.get("price") is not None,
            has_area=payload.get("area_sqm") is not None,
            has_rooms=payload.get("rooms") is not None,
            has_floor=payload.get("floor") is not None,
            has_phones=bool(payload.get("phones")),
            has_city=bool(payload.get("city")),
            has_district=bool(payload.get("district")),
            has_address=bool(payload.get("address_text")),
            has_local_image_files=bool(local_image_files),
            local_image_files_count=len(local_image_files),
            local_image_files_preview=local_image_files[:5],
            structured_fields_count=structured_fields_count,
            source_attributes_count=len(payload.get("source_attributes") or {}),
        )
        score = sample_score(payload, local_photo_count, listing_path)
        if best is None or score > best[0]:
            best = (score, sample)
    return best[1] if best else None


def pattern_status_for(row: dict, sample: SampleEvidence | None, scrape_row: dict) -> tuple[str, str]:
    legal_mode = row.get("legal_mode")
    saved = scrape_row.get("saved_listings", 0)
    if legal_mode == "licensing_required":
        return "without_authorized_pattern", "Source is licensing-gated; no public scraping pattern should be marked complete."
    if legal_mode == "legal_review_required":
        return "without_authorized_pattern", "Source needs legal review before a live pattern can be promoted."
    if saved <= 0 or not sample:
        return "without_sample_product_capture", "No saved full product sample exists yet for this source."
    if not sample.has_local_image_files:
        return "without_local_image_files", "Images are not yet persisted as local files for the best saved sample."
    if not sample.has_full_gallery:
        return "without_full_gallery_capture", "Detail capture works, but the saved sample does not yet prove full gallery completeness."
    if not sample.has_description:
        return "without_full_item_capture", "A saved sample exists, but it still misses the main description/body text."
    if not sample.has_price or not (sample.has_city or sample.has_address):
        return "without_core_fields_capture", "The saved sample still misses core commercial or location fields such as price and address/city."
    if sample.structured_fields_count < 2:
        return "without_structured_fields_capture", "The saved sample still misses too many structured fields from the detail page (area, rooms, floor, phones)."
    return "Patterned", "Code pattern exists and the best saved sample proves full local image-file capture plus core and structured detail-page fields."


def count_status_for(website_total: dict) -> str:
    kind = website_total.get("kind")
    if kind in {"exact", "lower_bound"}:
        return "recounted_live"
    if kind == "estimate":
        return "without_live_count_method"
    return "without_live_count_method"


def recency_status_for(source_name: str) -> str:
    return "without_recent_count_method"


def varna_status_for(source_name: str) -> str:
    return "without_varna_count_method"


def build_rows() -> list[dict]:
    registry_rows = load_registry_rows()
    inventory = load_inventory()
    scrape_status = load_scrape_status()
    source_key_map = build_source_key_map()
    rows: list[dict] = []

    for row in sorted(registry_rows, key=lambda item: (item["tier"], item["source_name"].lower())):
        source_name = row["source_name"]
        source_key = source_key_map.get(source_name)
        if not source_key:
            slug = source_name.lower().replace(".", "").replace(" ", "_")
            source_key = slug

        sample = find_best_sample(source_key, source_name)
        inventory_row = inventory.get(source_name, {})
        scrape_row = scrape_status.get(source_name, {})
        website_total = inventory_row.get("website_total") or {}
        pattern_status, pattern_issue = pattern_status_for(row, sample, scrape_row)
        count_status = count_status_for(website_total)

        method_info = PATTERN_METHODS.get(source_name, {
            "code_paths": ["scripts/live_scraper.py::generic"],
            "method": scrape_row.get("best_extraction_method") or inventory_row.get("best_extraction_method") or "Generic category-page discovery plus detail-page parsing.",
        })
        rows.append({
            "tier": row["tier"],
            "source_name": source_name,
            "primary_url": row.get("primary_url", ""),
            "pattern_status": pattern_status,
            "pattern_issue": pattern_issue,
            "count_status": count_status,
            "recent_status": recency_status_for(source_name),
            "varna_status": varna_status_for(source_name),
            "website_total_active": website_total,
            "recent_under_2m": {
                "value": None,
                "kind": "unavailable",
                "basis": "not_recomputed",
                "notes": "This source does not yet have a trustworthy whole-site posted-within-2-months counter saved in the repo.",
            },
            "varna_split": {
                "city": None,
                "region": None,
                "text": "n/a+n/a",
                "kind": "unavailable",
                "basis": "not_recomputed",
                "notes": "This source does not yet have a trustworthy whole-site Varna city vs Varna region counter saved in the repo.",
            },
            "method": method_info["method"],
            "code_paths": method_info["code_paths"],
            "db_status": "without_database_target",
            "db_notes": "DATABASE_URL is unset in this environment, so full PostgreSQL persistence could not be re-proved in this run.",
            "sample": sample.__dict__ if sample else None,
        })
    return rows


def render_md(rows: list[dict]) -> str:
    generated_at = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Tier 1-2 Pattern Status",
        "",
        f"Generated: {generated_at}",
        "",
        "Media storage mode: image binaries are stored as local files under `data/media/<reference_id>/...`; remote `image_urls` remain only as source traceability, while listing JSON artifacts now also store `local_image_files` and `local_image_storage_keys`.",
        "",
        "This report separates four questions for each source:",
        "- Can we count the live active site inventory?",
        "- Can we count posted-within-2-months inventory?",
        "- Can we split Varna city vs Varna region at website level?",
        "- Do we have a saved code pattern that lands one full product item with full gallery evidence and local image files?",
        "",
    ]
    strict_patterned = [row["source_name"] for row in rows if row["pattern_status"] == "Patterned"]
    lines.extend([
        f"Strict patterned sources: {', '.join(strict_patterned) if strict_patterned else 'none'}",
        "",
    ])
    for row in rows:
        lines.extend([
            f"## {row['source_name']} (Tier {row['tier']})",
            "",
            f"- Pattern status: `{row['pattern_status']}`",
            f"- Pattern issue: {row['pattern_issue']}",
            f"- Count status: `{row['count_status']}`",
            f"- Recent status: `{row['recent_status']}`",
            f"- Varna status: `{row['varna_status']}`",
            f"- Website total active: {row['website_total_active'].get('value', 'n/a')} ({row['website_total_active'].get('kind', 'unavailable')})",
            f"- Recent under 2 months: {row['recent_under_2m']['value'] if row['recent_under_2m']['value'] is not None else 'n/a'}",
            f"- Varna split: {row['varna_split']['text']}",
            f"- Code method: {row['method']}",
            f"- Code paths: {', '.join(row['code_paths'])}",
            f"- DB status: `{row['db_status']}`",
        ])
        sample = row.get("sample")
        if sample:
            lines.extend([
                f"- Source listing root: {sample['listing_root']}",
                f"- Source raw root: {sample['raw_root']}",
                f"- Sample listing JSON: {sample['listing_path']}",
                f"- Sample raw HTML: {sample['raw_path']}",
                f"- Sample media dir: {sample['media_dir']}",
                f"- Sample listing URL: {sample['listing_url']}",
                f"- Sample title: {sample['title']}",
                f"- Sample gallery: {sample['local_photo_count']}/{sample['remote_photo_count']} saved locally ({sample['local_photo_coverage_pct']:.1f}%)",
                f"- Local image files saved: {sample['local_image_files_count']}",
                f"- Local image file preview: {', '.join(sample['local_image_files_preview']) if sample['local_image_files_preview'] else 'none'}",
                f"- Sample completeness: description={sample['has_description']}, price={sample['has_price']}, area={sample['has_area']}, rooms={sample['has_rooms']}, floor={sample['has_floor']}, phones={sample['has_phones']}, city={sample['has_city']}, address={sample['has_address']}",
                f"- Structured fields count: {sample['structured_fields_count']}",
                f"- Source attributes count: {sample['source_attributes_count']}",
            ])
        else:
            lines.append("- Sample evidence: none saved yet")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    rows = build_rows()
    payload = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "sources": rows,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_MD.write_text(render_md(rows), encoding="utf-8")
    print(f"Wrote {OUTPUT_JSON}")
    print(f"Wrote {OUTPUT_MD}")


if __name__ == "__main__":
    main()
