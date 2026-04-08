from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from ..models import CanonicalListing


def fixture_dir(source: str) -> Path:
    return Path(__file__).resolve().parents[3] / "tests" / "fixtures" / source


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path))


def canonical_to_subset(listing: CanonicalListing) -> dict[str, Any]:
    payload = asdict(listing)
    payload["listing_intent"] = str(listing.listing_intent.value) if hasattr(listing.listing_intent, "value") else str(listing.listing_intent)
    payload["property_category"] = (
        str(listing.property_category.value) if hasattr(listing.property_category, "value") else str(listing.property_category)
    )
    # Keep output stable and focused for fixtures.
    keep = {
        "source_name",
        "owner_group",
        "listing_url",
        "external_id",
        "reference_id",
        "listing_intent",
        "property_category",
        "city",
        "district",
        "region",
        "address_text",
        "latitude",
        "longitude",
        "area_sqm",
        "rooms",
        "price",
        "currency",
        "phones",
        "image_urls",
        "parser_version",
    }
    return {k: payload.get(k) for k in sorted(keep)}

