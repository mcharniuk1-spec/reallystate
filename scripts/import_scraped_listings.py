#!/usr/bin/env python3
"""Import previously harvested `data/scraped/**` listings into the DB pipeline.

This bridges the existing live scraper output into:
raw_capture -> source_listing -> source_listing_snapshot -> canonical_listing
and, when enabled, property unification + listing_media rows.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent

import sys

sys.path.insert(0, str(REPO / "src"))

from bgrealestate.connectors.ingest import persist_listing_bundle
from bgrealestate.db.session import create_db_engine
from bgrealestate.enums import ListingIntent, PropertyCategory
from bgrealestate.models import CanonicalListing, ParsedListing, RawCapture
from bgrealestate.source_registry import SourceRegistry

SCRAPED_ROOT = REPO / "data" / "scraped"
REGISTRY_PATH = REPO / "data" / "source_registry.json"


def _as_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and value:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return datetime.now(tz=timezone.utc)


def _as_float(value: Any) -> float | None:
    if value in (None, "", False):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_int(value: Any) -> int | None:
    if value in (None, "", False):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _normalize_image_urls(urls: list[Any]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for raw in urls:
        if not isinstance(raw, str) or not raw:
            continue
        url = f"https:{raw}" if raw.startswith("//") else raw
        if url in seen:
            continue
        seen.add(url)
        out.append(url)
    return out


def _coerce_intent(value: Any) -> ListingIntent:
    try:
        return ListingIntent(str(value))
    except ValueError:
        return ListingIntent.MIXED


def _coerce_category(value: Any) -> PropertyCategory:
    try:
        return PropertyCategory(str(value))
    except ValueError:
        return PropertyCategory.UNKNOWN


def _build_models(
    *,
    source_name: str,
    owner_group: str,
    listing: dict[str, Any],
    raw_body: str,
    raw_suffix: str,
    listing_file: Path,
) -> tuple[RawCapture, ParsedListing, CanonicalListing]:
    fetched_at = _as_datetime(listing.get("scraped_at"))
    listing_url = str(listing.get("listing_url") or "")
    external_id = str(listing.get("external_id") or listing.get("reference_id") or listing_file.stem)
    reference_id = str(listing.get("reference_id") or f"{source_name}:{external_id}")
    parser_version = str(listing.get("parser_version") or "live_scraper_import_v1")
    intent = _coerce_intent(listing.get("listing_intent"))
    category = _coerce_category(listing.get("property_category"))
    image_urls = _normalize_image_urls(listing.get("image_urls") or [])
    price = _as_float(listing.get("price"))
    area_sqm = _as_float(listing.get("area_sqm"))
    price_per_sqm = round(price / area_sqm, 2) if price is not None and area_sqm else None

    raw_capture = RawCapture(
        source_name=source_name,
        url=listing_url,
        content_type="text/html" if raw_suffix == ".html" else "application/json",
        body=raw_body,
        fetched_at=fetched_at,
        parser_version=parser_version,
        metadata={
            "import_mode": "data_scraped",
            "listing_file": str(listing_file.relative_to(REPO)),
        },
    )
    parsed = ParsedListing(
        source_name=source_name,
        url=listing_url,
        external_id=external_id,
        title=listing.get("title"),
        listing_intent=intent,
        property_category=category,
        city=listing.get("city") or None,
        district=listing.get("district") or None,
        resort=listing.get("resort") or None,
        region=listing.get("region") or None,
        address_text=listing.get("address_text") or None,
        latitude=_as_float(listing.get("latitude")),
        longitude=_as_float(listing.get("longitude")),
        area_sqm=area_sqm,
        rooms=_as_float(listing.get("rooms")),
        floor=_as_int(listing.get("floor")),
        total_floors=_as_int(listing.get("total_floors")),
        construction_type=listing.get("construction_type") or None,
        construction_year=_as_int(listing.get("construction_year")),
        stage=listing.get("stage") or None,
        act16_present=listing.get("act16_present"),
        price=price,
        currency=listing.get("currency") or "EUR",
        fees=_as_float(listing.get("fees")),
        agency_name=listing.get("agency_name") or None,
        owner_name=listing.get("owner_name") or None,
        developer_name=listing.get("developer_name") or None,
        broker_name=listing.get("broker_name") or None,
        phones=list(listing.get("phones") or []),
        messenger_handles=list(listing.get("messenger_handles") or []),
        outbound_channel_hints=list(listing.get("outbound_channel_hints") or []),
        description=listing.get("description") or None,
        amenities=list(listing.get("amenities") or []),
        image_urls=image_urls,
        raw_payload={
            "import_mode": "data_scraped",
            "scraped_at": fetched_at.isoformat(),
        },
    )
    canonical = CanonicalListing(
        source_name=source_name,
        owner_group=owner_group,
        listing_url=listing_url,
        external_id=external_id,
        reference_id=reference_id,
        listing_intent=intent,
        property_category=category,
        city=listing.get("city") or None,
        district=listing.get("district") or None,
        resort=listing.get("resort") or None,
        region=listing.get("region") or None,
        address_text=listing.get("address_text") or None,
        latitude=_as_float(listing.get("latitude")),
        longitude=_as_float(listing.get("longitude")),
        geocode_confidence=_as_float(listing.get("geocode_confidence")),
        building_name=listing.get("building_name") or None,
        area_sqm=area_sqm,
        rooms=_as_float(listing.get("rooms")),
        floor=_as_int(listing.get("floor")),
        total_floors=_as_int(listing.get("total_floors")),
        construction_type=listing.get("construction_type") or None,
        construction_year=_as_int(listing.get("construction_year")),
        stage=listing.get("stage") or None,
        act16_present=listing.get("act16_present"),
        price=price,
        currency=listing.get("currency") or "EUR",
        fees=_as_float(listing.get("fees")),
        price_per_sqm=price_per_sqm,
        broker_name=listing.get("broker_name") or None,
        agency_name=listing.get("agency_name") or None,
        owner_name=listing.get("owner_name") or None,
        developer_name=listing.get("developer_name") or None,
        phones=list(listing.get("phones") or []),
        messenger_handles=list(listing.get("messenger_handles") or []),
        outbound_channel_hints=list(listing.get("outbound_channel_hints") or []),
        description=listing.get("description") or None,
        amenities=list(listing.get("amenities") or []),
        image_urls=image_urls,
        first_seen=fetched_at,
        last_seen=fetched_at,
        last_changed_at=fetched_at,
        removed_at=None,
        parser_version=parser_version,
        crawl_provenance={
            "import_mode": "data_scraped",
            "scraped_at": fetched_at.isoformat(),
            "listing_file": str(listing_file.relative_to(REPO)),
        },
    )
    return raw_capture, parsed, canonical


def _iter_listing_files(root: Path, source_filter: str | None) -> list[Path]:
    listing_files: list[Path] = []
    for source_dir in sorted(root.iterdir()):
        if not source_dir.is_dir():
            continue
        if source_filter and source_filter not in {source_dir.name.lower(), source_dir.name}:
            continue
        listings_dir = source_dir / "listings"
        if not listings_dir.exists():
            continue
        listing_files.extend(sorted(listings_dir.glob("*.json")))
    return listing_files


def main() -> int:
    parser = argparse.ArgumentParser(description="Import data/scraped listings into the DB pipeline.")
    parser.add_argument("--source", help="Limit to one scraped source dir (e.g. bazar_bg, yavlena).")
    parser.add_argument("--limit", type=int, default=0, help="Max listings to import (0 = no limit).")
    parser.add_argument("--dry-run", action="store_true", help="Only count and print candidate imports.")
    parser.add_argument("--download-images", action="store_true", help="Download images during import.")
    args = parser.parse_args()

    registry = SourceRegistry.from_file(REGISTRY_PATH)
    listing_files = _iter_listing_files(SCRAPED_ROOT, args.source.lower() if args.source else None)
    if args.limit > 0:
        listing_files = listing_files[: args.limit]

    if args.dry_run:
        counts: dict[str, int] = {}
        for listing_file in listing_files:
            data = json.loads(listing_file.read_text(encoding="utf-8"))
            src = str(data.get("source_name") or listing_file.parent.parent.name)
            counts[src] = counts.get(src, 0) + 1
        print(f"candidate_files={len(listing_files)}")
        for source_name, count in sorted(counts.items()):
            print(f"{source_name}: {count}")
        return 0

    engine = create_db_engine()
    imported = 0
    per_source: dict[str, int] = {}

    for idx, listing_file in enumerate(listing_files, start=1):
        listing = json.loads(listing_file.read_text(encoding="utf-8"))
        source_name = str(listing.get("source_name") or "").strip()
        source = registry.by_name(source_name)
        if source is None:
            raise RuntimeError(f"source {source_name!r} from {listing_file} is missing in source_registry.json")

        raw_dir = listing_file.parent.parent / "raw"
        raw_html = raw_dir / f"{listing_file.stem}.html"
        raw_json = raw_dir / f"{listing_file.stem}.json"
        if raw_html.exists():
            raw_path = raw_html
        elif raw_json.exists():
            raw_path = raw_json
        else:
            raw_path = listing_file
        raw_body = raw_path.read_text(encoding="utf-8")

        raw_capture, parsed, canonical = _build_models(
            source_name=source.source_name,
            owner_group=source.owner_group,
            listing=listing,
            raw_body=raw_body,
            raw_suffix=raw_path.suffix.lower(),
            listing_file=listing_file,
        )
        persist_listing_bundle(
            engine=engine,
            source=source,
            raw_capture=raw_capture,
            parsed=parsed,
            canonical=canonical,
            unify=True,
            download_images=args.download_images,
            source_payload={
                "import_mode": "data_scraped",
                "listing_file": str(listing_file.relative_to(REPO)),
            },
        )
        imported += 1
        per_source[source.source_name] = per_source.get(source.source_name, 0) + 1
        if idx % 50 == 0:
            print(f"imported={imported}")

    print(f"imported_total={imported}")
    for source_name, count in sorted(per_source.items()):
        print(f"{source_name}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
