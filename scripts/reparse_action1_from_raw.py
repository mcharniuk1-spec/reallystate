#!/usr/bin/env python3
"""Reparse saved Action1 raw detail pages after parser-pattern repairs.

This is an offline repair pass. It does not fetch live websites. It reads
`data/scraped/<source>/raw/*.html`, reparses the detail page with the current
source-specific parser, preserves stable source identity, refreshes media refs
from local files, and rewrites the matching listing JSON.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "src"))

from bgrealestate.services.media import ensure_media_root  # noqa: E402
from live_scraper import parse_homes_detail, parse_imot_detail, parse_listing_html  # noqa: E402


SCRAPED_ROOT = REPO / "data" / "scraped"
ACTION1_SOURCES = {
    "address_bg": "Address.bg",
    "bulgarianproperties": "BulgarianProperties",
    "homes_bg": "Homes.bg",
    "imot_bg": "imot.bg",
    "luximmo": "LUXIMMO",
    "property_bg": "property.bg",
    "suprimmo": "SUPRIMMO",
}
PRESERVE_FIELDS = {
    "reference_id",
    "external_id",
    "image_report_status",
    "image_report_path",
    "image_report_generated_at",
    "pattern_bucket_label",
    "scrape_session_id",
    "discovered_from_url",
}


def safe_ref(reference_id: str) -> str:
    return "".join("_" if c in '/:*?"<>|\\' else c for c in reference_id)


def normalize_image_url(url: Any) -> str:
    text = str(url or "").strip()
    return f"https:{text}" if text.startswith("//") else text


def parse_raw(source_key: str, source_name: str, html: str, url: str) -> dict[str, Any] | None:
    if source_key == "homes_bg":
        return parse_homes_detail(html, url)
    if source_key == "imot_bg":
        return parse_imot_detail(html, url)
    return parse_listing_html(html, url, source_name)


def local_refs(reference_id: str) -> tuple[list[str], list[str]]:
    media_root = ensure_media_root()
    if not media_root.is_absolute():
        media_root = (REPO / media_root).resolve()
    media_dir = media_root / safe_ref(reference_id)
    files = sorted(path for path in media_dir.iterdir() if path.is_file()) if media_dir.exists() else []
    return (
        [str(path.resolve().relative_to(REPO)) for path in files],
        [f"{safe_ref(reference_id)}/{path.name}" for path in files],
    )


def apply_operator_bucket(row: dict[str, Any]) -> None:
    intent = str(row.get("listing_intent") or "sale").lower()
    category = str(row.get("property_category") or "other").lower()
    deal = "rent" if intent in {"rent", "long_term_rent", "short_term_rent", "short_term_rental"} else "buy"
    commercial = category in {"office", "shop", "land", "garage"}
    row["bucket_key"] = f"{deal}_{'commercial' if commercial else 'personal'}"
    row["segment_key"] = row["bucket_key"]


def refresh_media_fields(row: dict[str, Any], reference_id: str) -> None:
    images = [normalize_image_url(url) for url in row.get("image_urls") or [] if normalize_image_url(url)]
    seen: set[str] = set()
    row["image_urls"] = [url for url in images if not (url in seen or seen.add(url))]
    local_files, storage_keys = local_refs(reference_id)
    row["local_image_files"] = local_files
    row["local_image_storage_keys"] = storage_keys
    row["photo_count_remote"] = len(row["image_urls"])
    row["photo_count_local"] = len(local_files)
    row["full_gallery_downloaded"] = bool(row["photo_count_remote"] and row["photo_count_local"] >= row["photo_count_remote"])
    if row["photo_count_remote"] <= 0:
        row["photo_download_status"] = "no_remote_gallery"
    elif row["photo_count_local"] <= 0:
        row["photo_download_status"] = "no_local_files"
    elif row["photo_count_local"] >= row["photo_count_remote"]:
        row["photo_download_status"] = "full_gallery"
    else:
        row["photo_download_status"] = "partial_gallery"


def meaningful_changes(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    changed: list[str] = []
    for key in (
        "title",
        "description",
        "price",
        "currency",
        "area_sqm",
        "rooms",
        "floor",
        "city",
        "district",
        "address_text",
        "listing_intent",
        "property_category",
        "image_urls",
        "photo_count_remote",
        "photo_count_local",
        "photo_download_status",
        "scrape_warnings",
        "suspected_multi_unit_publication",
    ):
        if before.get(key) != after.get(key):
            changed.append(key)
    return changed


def reparse_listing(source_key: str, source_name: str, listing_path: Path, *, dry_run: bool) -> dict[str, Any]:
    before = json.loads(listing_path.read_text(encoding="utf-8"))
    raw_path = listing_path.parent.parent / "raw" / f"{listing_path.stem}.html"
    row = {
        "source_key": source_key,
        "source_name": source_name,
        "listing_path": str(listing_path.relative_to(REPO)),
        "raw_path": str(raw_path.relative_to(REPO)),
        "reference_id": before.get("reference_id") or listing_path.stem,
        "status": "skipped",
        "changed_fields": [],
    }
    if not raw_path.exists():
        row["status"] = "missing_raw"
        return row
    html = raw_path.read_text(encoding="utf-8", errors="replace")
    url = str(before.get("listing_url") or "")
    parsed = parse_raw(source_key, source_name, html, url)
    if not parsed:
        row["status"] = "parse_failed"
        return row

    after = dict(before)
    after.update(parsed)
    for key in PRESERVE_FIELDS:
        if key in before:
            after[key] = before[key]
    after["source_name"] = source_name
    after["reference_id"] = before.get("reference_id") or parsed.get("reference_id") or f"{source_name}:{listing_path.stem}"
    after["external_id"] = before.get("external_id") or parsed.get("external_id") or listing_path.stem
    after["listing_url"] = parsed.get("listing_url") or before.get("listing_url") or url
    after["last_offline_reparsed_at"] = datetime.now(tz=timezone.utc).isoformat()
    after["scraped_at"] = before.get("scraped_at") or parsed.get("scraped_at")
    refresh_media_fields(after, str(after["reference_id"]))
    apply_operator_bucket(after)
    changes = meaningful_changes(before, after)
    row["changed_fields"] = changes
    row["status"] = "updated" if changes else "unchanged"
    row["remote_before"] = int(before.get("photo_count_remote") or len(before.get("image_urls") or []))
    row["remote_after"] = int(after.get("photo_count_remote") or 0)
    row["local_after"] = int(after.get("photo_count_local") or 0)
    row["description_len_before"] = len(str(before.get("description") or ""))
    row["description_len_after"] = len(str(after.get("description") or ""))
    row["area_before"] = before.get("area_sqm")
    row["area_after"] = after.get("area_sqm")

    if not dry_run and changes:
        listing_path.write_text(json.dumps(after, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline reparse Action1 saved listings from local raw HTML.")
    parser.add_argument("--sources", default=",".join(ACTION1_SOURCES), help="Comma-separated source keys.")
    parser.add_argument("--limit", type=int, default=0, help="Limit listing JSON files per source.")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without rewriting listing JSON.")
    parser.add_argument("--output", type=Path, default=REPO / "docs" / "exports" / "action1-offline-reparse-summary.json")
    args = parser.parse_args()

    selected = [item.strip() for item in args.sources.split(",") if item.strip()]
    rows: list[dict[str, Any]] = []
    for source_key in selected:
        source_name = ACTION1_SOURCES.get(source_key)
        if not source_name:
            rows.append({"source_key": source_key, "status": "unknown_source"})
            continue
        listing_paths = sorted((SCRAPED_ROOT / source_key / "listings").glob("*.json"))
        if args.limit > 0:
            listing_paths = listing_paths[: args.limit]
        for listing_path in listing_paths:
            rows.append(reparse_listing(source_key, source_name, listing_path, dry_run=args.dry_run))

    totals: dict[str, dict[str, int]] = {}
    for row in rows:
        source = str(row.get("source_key") or "unknown")
        totals.setdefault(source, {"scanned": 0, "updated": 0, "unchanged": 0, "missing_raw": 0, "parse_failed": 0})
        status = str(row.get("status") or "unknown")
        totals[source]["scanned"] += 1
        totals[source][status] = totals[source].get(status, 0) + 1

    payload = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "dry_run": bool(args.dry_run),
        "sources": selected,
        "limit": args.limit,
        "totals": totals,
        "items": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    print(json.dumps({"dry_run": args.dry_run, "totals": totals}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
