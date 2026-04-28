#!/usr/bin/env python3
"""Generate a small website data slice from saved scraper output."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRAPED_ROOT = ROOT / "data" / "scraped"
OUT = ROOT / "lib" / "mock" / "scraped-listings.ts"
PUBLIC_OUT = ROOT / "public" / "data" / "scraped-listings.json"
MAX_TOTAL = 24
MAX_PER_SOURCE = 3


SOURCE_NAMES = {
    "address_bg": "Address.bg",
    "bazar_bg": "Bazar.bg",
    "bulgarianproperties": "BulgarianProperties",
    "homes_bg": "Homes.bg",
    "imot_bg": "imot.bg",
    "luximmo": "LUXIMMO",
    "olx_bg": "OLX.bg",
    "property_bg": "property.bg",
    "suprimmo": "SUPRIMMO",
    "yavlena": "Yavlena",
}


def safe_number(value: Any) -> float | int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        cleaned = value.replace(" ", "").replace(",", ".")
        try:
            parsed = float(cleaned)
        except ValueError:
            return None
        return int(parsed) if parsed.is_integer() else parsed
    return None


def category(value: Any) -> str:
    raw = str(value or "other").lower()
    if raw in {"apartment", "house", "studio", "villa", "office", "shop", "land", "garage", "penthouse"}:
        return raw
    if "къщ" in raw or "house" in raw:
        return "house"
    if "парцел" in raw or "зем" in raw or "land" in raw:
        return "land"
    if "офис" in raw or "office" in raw:
        return "office"
    if "гараж" in raw or "garage" in raw:
        return "garage"
    return "apartment" if "ап" in raw or "flat" in raw else "other"


def intent(value: Any) -> str:
    raw = str(value or "sale").lower()
    if raw in {"sale", "rent", "short_term_rental", "auction"}:
        return raw
    if "rent" in raw or "наем" in raw:
        return "rent"
    return "sale"


def quality(desc_len: int) -> str:
    if desc_len <= 0:
        return "missing"
    if desc_len < 160:
        return "thin"
    if desc_len < 700:
        return "ok"
    return "rich"


def media_url(local_path: str) -> str:
    prefix = "data/media/"
    key = local_path.split(prefix, 1)[-1] if prefix in local_path else local_path
    return "/api/local-media/" + "/".join(part for part in key.split("/") if part)


def score(row: dict[str, Any]) -> float:
    desc_len = len(row.get("description") or "")
    remote = int(row.get("photo_count_remote") or len(row.get("image_urls") or []))
    local = int(row.get("photo_count_local") or len(row.get("local_image_files") or []))
    points = 0
    points += 20 if row.get("price") is not None else 0
    points += 15 if row.get("area_sqm") is not None else 0
    points += 15 if row.get("city") else 0
    points += 15 if row.get("property_category") else 0
    points += 20 if desc_len >= 160 else 8 if desc_len else 0
    points += 15 if local and local >= remote else 8 if local else 0
    return min(100, points)


def convert(source_key: str, path: Path) -> dict[str, Any] | None:
    try:
        row = json.loads(path.read_text())
    except Exception:
        return None

    local_files = [x for x in row.get("local_image_files", []) if isinstance(x, str)]
    remote_images = [x for x in row.get("image_urls", []) if isinstance(x, str)]
    images = [media_url(x) for x in local_files[:4]] or remote_images[:4]
    desc = row.get("description") or ""
    ref = row.get("reference_id") or path.stem
    listing_url = row.get("listing_url") or ""
    external_id = row.get("external_id") or ref
    remote_count = int(row.get("photo_count_remote") or len(remote_images))
    local_count = int(row.get("photo_count_local") or len(local_files))

    return {
        "reference_id": ref,
        "title": row.get("title"),
        "source_name": row.get("source_name") or SOURCE_NAMES.get(source_key, source_key),
        "source_key": source_key,
        "owner_group": None,
        "listing_url": listing_url,
        "external_id": external_id,
        "listing_intent": intent(row.get("listing_intent")),
        "property_category": category(row.get("property_category")),
        "city": row.get("city"),
        "district": row.get("district"),
        "resort": row.get("resort"),
        "region": row.get("region") or row.get("city"),
        "address_text": row.get("address_text"),
        "latitude": safe_number(row.get("latitude")),
        "longitude": safe_number(row.get("longitude")),
        "area_sqm": safe_number(row.get("area_sqm")),
        "rooms": safe_number(row.get("rooms")),
        "floor": safe_number(row.get("floor")),
        "total_floors": safe_number(row.get("total_floors")),
        "year_built": safe_number(row.get("year_built")),
        "construction_type": None,
        "amenities": row.get("amenities") or [],
        "price": safe_number(row.get("price")),
        "currency": row.get("currency") or "EUR",
        "description": desc or None,
        "image_urls": images,
        "local_image_files": local_files[:4],
        "photo_count_remote": remote_count,
        "photo_count_local": local_count,
        "full_gallery_downloaded": bool(row.get("full_gallery_downloaded")),
        "photo_download_status": row.get("photo_download_status"),
        "description_chars": len(desc),
        "description_quality": quality(len(desc)),
        "scrape_quality_score": score(row),
        "image_report_status": "missing",
        "image_report_md": None,
        "image_report_json": None,
        "first_seen": row.get("first_seen") or row.get("scraped_at"),
        "last_seen": row.get("last_seen") or row.get("scraped_at"),
        "last_changed_at": row.get("last_changed_at"),
        "removed_at": row.get("removed_at"),
        "parser_version": row.get("parser_version"),
        "crawl_provenance": {
            "scraped_at": row.get("scraped_at"),
            "photo_download_status": row.get("photo_download_status"),
        },
    }


def main() -> int:
    rows: list[dict[str, Any]] = []
    for src_dir in sorted(SCRAPED_ROOT.iterdir()):
        listings = src_dir / "listings"
        if not listings.exists():
            continue
        converted = [x for x in (convert(src_dir.name, p) for p in listings.glob("*.json")) if x]
        converted.sort(
            key=lambda x: (
                bool(x.get("full_gallery_downloaded")),
                x.get("scrape_quality_score") or 0,
                x.get("photo_count_local") or 0,
                x.get("description_chars") or 0,
            ),
            reverse=True,
        )
        rows.extend(converted[:MAX_PER_SOURCE])

    rows.sort(
        key=lambda x: (
            bool(x.get("full_gallery_downloaded")),
            x.get("scrape_quality_score") or 0,
            x.get("photo_count_local") or 0,
        ),
        reverse=True,
    )
    rows = rows[:MAX_TOTAL]

    public_rows: list[dict[str, Any]] = []
    for src_dir in sorted(SCRAPED_ROOT.iterdir()):
        listings = src_dir / "listings"
        if not listings.exists():
            continue
        for path in sorted(listings.glob("*.json")):
            item = convert(src_dir.name, path)
            if item:
                public_rows.append(item)

    public_rows.sort(
        key=lambda x: (
            bool(x.get("full_gallery_downloaded")),
            x.get("scrape_quality_score") or 0,
            x.get("photo_count_local") or 0,
        ),
        reverse=True,
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "import type { Listing } from \"@/lib/types/listing\";\n\n"
        "export const SCRAPED_LISTINGS: Listing[] = "
        + json.dumps(rows, ensure_ascii=False, indent=2)
        + ";\n",
    )
    PUBLIC_OUT.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_OUT.write_text(json.dumps(public_rows, ensure_ascii=False))
    print(f"Wrote {OUT} with {len(rows)} listings")
    print(f"Wrote {PUBLIC_OUT} with {len(public_rows)} listings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
