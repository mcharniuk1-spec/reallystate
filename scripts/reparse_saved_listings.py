#!/usr/bin/env python3
"""Re-parse saved detail HTML into listing JSON artifacts and local media files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

import sys

sys.path.insert(0, str(REPO))

from scripts.live_scraper import (  # noqa: E402
    SCRAPED_ROOT,
    ScrapeStats,
    _save_listing,
    make_client,
    parse_homes_detail,
    parse_imot_detail,
    parse_listing_html,
)


DEFAULT_SOURCE_KEYS = [
    "homes_bg",
    "imot_bg",
    "address_bg",
    "bulgarianproperties",
    "luximmo",
    "olx_bg",
    "property_bg",
    "suprimmo",
    "bazar_bg",
    "yavlena",
]

SOURCE_NAMES = {
    "homes_bg": "Homes.bg",
    "imot_bg": "imot.bg",
    "address_bg": "Address.bg",
    "bulgarianproperties": "BulgarianProperties",
    "luximmo": "LUXIMMO",
    "olx_bg": "OLX.bg",
    "property_bg": "property.bg",
    "suprimmo": "SUPRIMMO",
    "bazar_bg": "Bazar.bg",
    "yavlena": "Yavlena",
}


def iter_listing_files(source_key: str) -> list[Path]:
    listings_dir = SCRAPED_ROOT / source_key / "listings"
    return sorted(listings_dir.glob("*.json")) if listings_dir.exists() else []


def parse_saved_html(source_name: str, html: str, url: str) -> dict | None:
    if source_name == "Homes.bg":
        return parse_homes_detail(html, url)
    if source_name == "imot.bg":
        return parse_imot_detail(html, url)
    return parse_listing_html(html, url, source_name)


def merge_existing_metadata(parsed: dict, existing: dict) -> dict:
    for key in (
        "scraped_at",
        "source_section_id",
        "region_key",
        "segment_key",
        "vertical_key",
        "section_label",
        "pattern_bucket_label",
        "varna_entry_scope",
        "list_page_url",
        "detail_url_canonical",
    ):
        if existing.get(key) and not parsed.get(key):
            parsed[key] = existing[key]
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description="Re-parse saved listing HTML into richer listing JSON artifacts.")
    parser.add_argument("--sources", default=",".join(DEFAULT_SOURCE_KEYS), help="Comma-separated source keys.")
    parser.add_argument("--limit-per-source", type=int, default=0, help="Limit listing count per source (0 = all).")
    parser.add_argument("--download-photos", action="store_true", help="Download photos discovered by the updated parser.")
    args = parser.parse_args()

    source_keys = [item.strip() for item in args.sources.split(",") if item.strip()]
    photo_client = make_client() if args.download_photos else None
    try:
        for source_key in source_keys:
            source_name = SOURCE_NAMES.get(source_key, source_key)
            listing_files = iter_listing_files(source_key)
            if args.limit_per_source > 0:
                listing_files = listing_files[: args.limit_per_source]
            stats = ScrapeStats(source_key=source_key, source_name=source_name)
            for listing_path in listing_files:
                listing = json.loads(listing_path.read_text(encoding="utf-8"))
                raw_dir = listing_path.parent.parent / "raw"
                raw_path = raw_dir / f"{listing_path.stem}.html"
                if not raw_path.exists():
                    continue
                html = raw_path.read_text(encoding="utf-8", errors="ignore")
                url = str(listing.get("listing_url") or "")
                parsed = parse_saved_html(source_name, html, url)
                if not parsed:
                    continue
                parsed = merge_existing_metadata(parsed, listing)
                _save_listing(
                    stats,
                    parsed,
                    html,
                    source_key,
                    download_photos=args.download_photos,
                    photo_client=photo_client,
                )
            print(f"{source_name}: reparsed={stats.listing_pages_parsed} photos={stats.photos_downloaded}/{stats.photos_found}")
    finally:
        if photo_client is not None:
            photo_client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
