#!/usr/bin/env python3
"""Backfill missing local media files for saved `data/scraped` listings.

This is intentionally a file-backed utility: it works on the harvested JSON
corpus and updates each listing's `local_image_files`, storage keys, and gallery
status after downloading missing image orders.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx


REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from bgrealestate.services.media import download_image, ensure_media_root  # noqa: E402


SCRAPED_ROOT = REPO / "data" / "scraped"
EXPORTS = REPO / "docs" / "exports"
DEFAULT_OUTPUT = EXPORTS / "scraped-media-backfill-summary.json"


def safe_ref(reference_id: str) -> str:
    return "".join("_" if c in '/:*?"<>|\\' else c for c in reference_id)


def normalize_image_url(url: str) -> str:
    return f"https:{url}" if url.startswith("//") else url


def iter_listing_paths(source: str | None = None) -> list[Path]:
    roots = [SCRAPED_ROOT / source] if source else [p for p in SCRAPED_ROOT.iterdir() if p.is_dir()]
    paths: list[Path] = []
    for root in roots:
        listing_dir = root / "listings"
        if listing_dir.exists():
            paths.extend(sorted(listing_dir.glob("*.json")))
    return paths


def existing_orderings(media_dir: Path) -> set[int]:
    orders: set[int] = set()
    if not media_dir.exists():
        return orders
    for path in media_dir.iterdir():
        if not path.is_file():
            continue
        match = re.match(r"^(\d{4})_", path.name)
        if match:
            orders.add(int(match.group(1)))
    return orders


def local_refs(media_dir: Path, reference_id: str) -> tuple[list[str], list[str]]:
    if not media_dir.exists():
        return [], []
    files = sorted(path for path in media_dir.iterdir() if path.is_file())
    return (
        [str(path.resolve().relative_to(REPO)) for path in files],
        [f"{safe_ref(reference_id)}/{path.name}" for path in files],
    )


def refresh_payload_media_fields(payload: dict[str, Any], media_dir: Path, reference_id: str) -> None:
    local_files, storage_keys = local_refs(media_dir, reference_id)
    remote_urls = [normalize_image_url(str(url)) for url in payload.get("image_urls") or [] if str(url).strip()]
    payload["image_urls"] = remote_urls
    payload["local_image_files"] = local_files
    payload["local_image_storage_keys"] = storage_keys
    payload["photo_count_remote"] = len(remote_urls)
    payload["photo_count_local"] = len(local_files)
    payload["full_gallery_downloaded"] = bool(remote_urls and len(local_files) >= len(remote_urls))
    if not remote_urls:
        payload["photo_download_status"] = "no_remote_gallery"
    elif not local_files:
        payload["photo_download_status"] = "no_local_files"
    elif len(local_files) >= len(remote_urls):
        payload["photo_download_status"] = "full_gallery"
    else:
        payload["photo_download_status"] = "partial_gallery"


def backfill_listing(
    listing_path: Path,
    *,
    client: httpx.Client,
    dry_run: bool,
    max_images_per_listing: int,
    include_complete: bool,
) -> dict[str, Any]:
    payload = json.loads(listing_path.read_text(encoding="utf-8"))
    reference_id = str(payload.get("reference_id") or listing_path.stem)
    remote_urls = [normalize_image_url(str(url)) for url in payload.get("image_urls") or [] if str(url).strip()]
    media_dir = ensure_media_root()
    if not media_dir.is_absolute():
        media_dir = (REPO / media_dir).resolve()
    media_dir = media_dir / safe_ref(reference_id)

    before_orders = existing_orderings(media_dir)
    missing = [(idx, url) for idx, url in enumerate(remote_urls) if idx not in before_orders]
    if max_images_per_listing > 0:
        missing = missing[:max_images_per_listing]

    row = {
        "listing_path": str(listing_path.resolve()),
        "source_key": listing_path.parent.parent.name,
        "source_name": payload.get("source_name") or listing_path.parent.parent.name,
        "reference_id": reference_id,
        "remote_photos": len(remote_urls),
        "local_photos_before": len(before_orders),
        "missing_before": max(0, len(remote_urls) - len(before_orders)),
        "attempted": 0,
        "downloaded": 0,
        "failed": 0,
        "status": "complete" if remote_urls and len(before_orders) >= len(remote_urls) else "incomplete",
    }
    if row["status"] == "complete" and not include_complete:
        return row
    if dry_run or not missing:
        return row

    for idx, url in missing:
        result = download_image(url, reference_id=safe_ref(reference_id), ordering=idx, client=client)
        row["attempted"] += 1
        if result.status == "downloaded":
            row["downloaded"] += 1
        else:
            row["failed"] += 1

    refresh_payload_media_fields(payload, media_dir, reference_id)
    listing_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    row["local_photos_after"] = payload["photo_count_local"]
    row["missing_after"] = max(0, payload["photo_count_remote"] - payload["photo_count_local"])
    row["status"] = payload["photo_download_status"]
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description="Download missing local photos for saved data/scraped listing JSON files.")
    parser.add_argument("--source", help="Limit to one source directory key, e.g. homes_bg or bazar_bg.")
    parser.add_argument("--limit", type=int, default=0, help="Limit listing files scanned after filtering.")
    parser.add_argument("--max-images-per-listing", type=int, default=0, help="Cap newly downloaded images per listing; 0 means all missing.")
    parser.add_argument("--include-complete", action="store_true", help="Also scan listings already marked complete.")
    parser.add_argument("--dry-run", action="store_true", help="Report missing images without downloading.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Summary JSON output path.")
    args = parser.parse_args()

    paths = iter_listing_paths(args.source)
    if args.limit > 0:
        paths = paths[: args.limit]

    rows: list[dict[str, Any]] = []
    totals: dict[str, dict[str, int]] = defaultdict(lambda: {"listings": 0, "attempted": 0, "downloaded": 0, "failed": 0, "missing_before": 0})
    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        for path in paths:
            row = backfill_listing(
                path,
                client=client,
                dry_run=args.dry_run,
                max_images_per_listing=args.max_images_per_listing,
                include_complete=args.include_complete,
            )
            rows.append(row)
            source = str(row["source_name"])
            totals[source]["listings"] += 1
            totals[source]["attempted"] += int(row["attempted"])
            totals[source]["downloaded"] += int(row["downloaded"])
            totals[source]["failed"] += int(row["failed"])
            totals[source]["missing_before"] += int(row["missing_before"])

    payload = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "dry_run": bool(args.dry_run),
        "source": args.source,
        "limit": args.limit,
        "max_images_per_listing": args.max_images_per_listing,
        "totals": dict(totals),
        "items": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
