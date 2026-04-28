#!/usr/bin/env python3
"""Generate source-by-source item coverage for tier-1/2 scraped listings."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO / "data" / "source_registry.json"
SCRAPED_ROOT = REPO / "data" / "scraped"
MEDIA_ROOT = REPO / "data" / "media"
EXPORTS = REPO / "docs" / "exports"
OUTPUT_JSON = EXPORTS / "source-item-photo-coverage.json"

CORE_FIELDS: tuple[str, ...] = (
    "description",
    "price",
    "area_sqm",
    "rooms",
    "floor",
    "city",
    "district",
    "address_text",
    "phones",
    "amenities",
)


def _safe_ref(reference_id: str) -> str:
    return "".join("_" if c in '/:*?"<>|\\' else c for c in reference_id)


def _load_registry_rows() -> list[dict[str, Any]]:
    payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return [row for row in payload.get("sources", []) if row.get("tier") in (1, 2)]


def _field_present(payload: dict[str, Any], field: str) -> bool:
    value = payload.get(field)
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple, set)):
        return bool(value)
    return True


def _infer_local_files(payload: dict[str, Any], reference_id: str) -> tuple[list[str], str | None]:
    raw_files = [str(item) for item in (payload.get("local_image_files") or []) if str(item).strip()]
    media_dir = MEDIA_ROOT / _safe_ref(reference_id) if reference_id else None
    resolved_dir = str(media_dir.resolve()) if media_dir else None
    if raw_files:
        return raw_files, resolved_dir
    if not media_dir or not media_dir.exists():
        return [], resolved_dir
    files = [
        str(path.relative_to(REPO))
        for path in sorted(media_dir.iterdir())
        if path.is_file()
    ]
    return files, resolved_dir


def _parsed_fields(payload: dict[str, Any], local_count: int, remote_count: int) -> list[str]:
    fields: list[str] = []
    for field in CORE_FIELDS:
        if _field_present(payload, field):
            fields.append(field)
    if payload.get("latitude") is not None and payload.get("longitude") is not None:
        fields.append("geo")
    if payload.get("source_attributes"):
        fields.append("source_attributes")
    if payload.get("structured_extra"):
        fields.append("structured_extra")
    if remote_count:
        fields.append("image_urls")
    if local_count:
        fields.append("local_image_files")
    return fields


def _build_item_row(source_name: str, listing_path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(listing_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    reference_id = str(payload.get("reference_id") or listing_path.stem)
    local_files, media_dir = _infer_local_files(payload, reference_id)
    remote_urls = [str(item) for item in (payload.get("image_urls") or []) if str(item).strip()]
    remote_count = len(remote_urls)
    local_count = len(local_files)
    full_gallery = bool(payload.get("full_gallery_downloaded"))
    if remote_count > 0:
        full_gallery = full_gallery or local_count >= remote_count
    description = str(payload.get("description") or "")
    source_attributes = payload.get("source_attributes") or {}
    structured_extra = payload.get("structured_extra") or {}
    parsed_fields = _parsed_fields(payload, local_count, remote_count)
    missing_core = [field for field in CORE_FIELDS if field not in parsed_fields]

    return {
        "source_name": source_name,
        "source_key": listing_path.parent.parent.name,
        "reference_id": reference_id,
        "listing_json_path": str(listing_path.resolve()),
        "raw_html_path": str((listing_path.parent.parent / "raw" / f"{listing_path.stem}.html").resolve()),
        "media_dir": media_dir,
        "listing_url": str(payload.get("listing_url") or ""),
        "source_section_id": str(payload.get("source_section_id") or ""),
        "region_key": str(payload.get("region_key") or ""),
        "segment_key": str(payload.get("segment_key") or ""),
        "vertical_key": str(payload.get("vertical_key") or ""),
        "listing_intent": str(payload.get("listing_intent") or ""),
        "property_category": str(payload.get("property_category") or ""),
        "title": str(payload.get("title") or ""),
        "description_chars": len(description.strip()),
        "price": payload.get("price"),
        "currency": payload.get("currency"),
        "area_sqm": payload.get("area_sqm"),
        "rooms": payload.get("rooms"),
        "floor": payload.get("floor"),
        "city": payload.get("city"),
        "district": payload.get("district"),
        "address_text": payload.get("address_text"),
        "phones_count": len(payload.get("phones") or []),
        "amenities_count": len(payload.get("amenities") or []),
        "source_attributes_count": len(source_attributes),
        "structured_extra_count": len(structured_extra),
        "has_geo": payload.get("latitude") is not None and payload.get("longitude") is not None,
        "photo_count_remote": remote_count,
        "photo_count_local": local_count,
        "full_gallery_downloaded": full_gallery,
        "photo_download_status": payload.get("photo_download_status") or (
            "full" if full_gallery and remote_count else "none" if local_count == 0 else "partial"
        ),
        "local_image_files": local_files,
        "parsed_fields": parsed_fields,
        "missing_core_fields": missing_core,
        "scraped_at": payload.get("scraped_at"),
    }


def build_payload() -> dict[str, Any]:
    registry_rows = _load_registry_rows()
    ordered_names = [row["source_name"] for row in registry_rows]
    source_items: dict[str, list[dict[str, Any]]] = {name: [] for name in ordered_names}

    for listing_path in SCRAPED_ROOT.glob("*/listings/*.json"):
        source_name = listing_path.parent.parent.name
        try:
            payload = json.loads(listing_path.read_text(encoding="utf-8"))
            source_name = str(payload.get("source_name") or source_name)
        except (OSError, json.JSONDecodeError):
            pass
        if source_name not in source_items:
            continue
        item = _build_item_row(source_name, listing_path)
        if item:
            source_items[source_name].append(item)

    sources: list[dict[str, Any]] = []
    for row in registry_rows:
        source_name = row["source_name"]
        items = sorted(
            source_items[source_name],
            key=lambda item: (
                item.get("listing_intent") or "",
                item.get("property_category") or "",
                -(item.get("photo_count_local") or 0),
                item.get("reference_id") or "",
            ),
        )
        service_counts = Counter(item.get("listing_intent") or "unknown" for item in items)
        category_counts = Counter(item.get("property_category") or "unknown" for item in items)
        field_counts = Counter()
        combo_rows: dict[tuple[str, str], dict[str, Any]] = defaultdict(
            lambda: {
                "count": 0,
                "description": 0,
                "photo_url_items": 0,
                "local_photo_items": 0,
                "full_gallery_items": 0,
                "remote_photos": 0,
                "local_photos": 0,
                "field_counts": Counter(),
            }
        )

        for item in items:
            for field in item["parsed_fields"]:
                field_counts[field] += 1
            combo = combo_rows[(item["listing_intent"] or "unknown", item["property_category"] or "unknown")]
            combo["count"] += 1
            combo["description"] += 1 if item["description_chars"] else 0
            combo["photo_url_items"] += 1 if item["photo_count_remote"] > 0 else 0
            combo["local_photo_items"] += 1 if item["photo_count_local"] > 0 else 0
            combo["full_gallery_items"] += 1 if item["full_gallery_downloaded"] else 0
            combo["remote_photos"] += item["photo_count_remote"]
            combo["local_photos"] += item["photo_count_local"]
            for field in item["parsed_fields"]:
                combo["field_counts"][field] += 1

        combo_payload = []
        for (intent, category), combo in sorted(combo_rows.items(), key=lambda pair: (pair[0][0], pair[0][1])):
            combo_payload.append(
                {
                    "intent": intent,
                    "category": category,
                    "count": combo["count"],
                    "description": combo["description"],
                    "photo_url_items": combo["photo_url_items"],
                    "local_photo_items": combo["local_photo_items"],
                    "full_gallery_items": combo["full_gallery_items"],
                    "remote_photos": combo["remote_photos"],
                    "local_photos": combo["local_photos"],
                    "field_counts": dict(combo["field_counts"]),
                }
            )

        sources.append(
            {
                "tier": row["tier"],
                "source_name": source_name,
                "primary_url": row.get("primary_url", ""),
                "saved_listings": len(items),
                "items_with_remote_photos": sum(1 for item in items if item["photo_count_remote"] > 0),
                "full_gallery_items": sum(1 for item in items if item["full_gallery_downloaded"]),
                "items_with_local_media": sum(1 for item in items if item["photo_count_local"] > 0),
                "items_with_description": sum(1 for item in items if item["description_chars"] > 0),
                "total_remote_photos": sum(item["photo_count_remote"] for item in items),
                "total_local_photos": sum(item["photo_count_local"] for item in items),
                "service_counts": dict(service_counts),
                "category_counts": dict(category_counts),
                "field_counts": dict(field_counts),
                "combo_rows": combo_payload,
                "items": items,
            }
        )

    return {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "sources": sources,
    }


def main() -> None:
    payload = build_payload()
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
