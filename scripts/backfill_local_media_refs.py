#!/usr/bin/env python3
"""Backfill local media file references into saved listing JSON artifacts."""

from __future__ import annotations

import json
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
SCRAPED_ROOT = REPO / "data" / "scraped"
MEDIA_ROOT = REPO / "data" / "media"


def safe_ref(reference_id: str) -> str:
    return "".join("_" if c in '/:*?"<>|\\' else c for c in reference_id)


def main() -> int:
    updated = 0
    for listing_path in SCRAPED_ROOT.glob("*/listings/*.json"):
        try:
            payload = json.loads(listing_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        reference_id = payload.get("reference_id") or ""
        if not reference_id:
            continue
        media_dir = MEDIA_ROOT / safe_ref(reference_id)
        files = sorted(p for p in media_dir.iterdir() if p.is_file()) if media_dir.exists() else []
        local_image_files = [str(path.relative_to(REPO)) for path in files]
        local_image_storage_keys = [f"{safe_ref(reference_id)}/{path.name}" for path in files]
        if payload.get("local_image_files") == local_image_files and payload.get("local_image_storage_keys") == local_image_storage_keys:
            continue
        payload["local_image_files"] = local_image_files
        payload["local_image_storage_keys"] = local_image_storage_keys
        listing_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        updated += 1
    print(f"Updated {updated} listing JSON files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
