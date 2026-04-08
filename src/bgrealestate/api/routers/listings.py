from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...db.repositories import CanonicalListingRepository
from ..auth import AuthPrincipal, require_scope
from ..deps import get_db

router = APIRouter(tags=["listings"])


def _iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt is not None else None


def _num(v: Decimal | float | None) -> float | None:
    if v is None:
        return None
    return float(v)


def _serialize_listing(m: Any) -> dict[str, Any]:
    return {
        "reference_id": m.reference_id,
        "source_name": m.source_name,
        "owner_group": m.owner_group,
        "listing_url": m.listing_url,
        "external_id": m.external_id,
        "listing_intent": m.listing_intent,
        "property_category": m.property_category,
        "city": m.city,
        "district": m.district,
        "resort": m.resort,
        "region": m.region,
        "address_text": m.address_text,
        "latitude": m.latitude,
        "longitude": m.longitude,
        "area_sqm": m.area_sqm,
        "rooms": m.rooms,
        "price": _num(m.price),
        "currency": m.currency,
        "description": m.description,
        "image_urls": list(m.image_urls or []),
        "first_seen": _iso(m.first_seen),
        "last_seen": _iso(m.last_seen),
        "last_changed_at": _iso(m.last_changed_at),
        "removed_at": _iso(m.removed_at),
        "parser_version": m.parser_version,
        "crawl_provenance": dict(m.crawl_provenance or {}),
    }


@router.get("/listings")
def list_listings(
    _principal: Annotated[AuthPrincipal, Depends(require_scope("listings:read"))],
    session: Annotated[Session, Depends(get_db)],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    source_name: str | None = None,
    include_removed: bool = False,
) -> dict[str, Any]:
    repo = CanonicalListingRepository(session)
    rows = repo.list_recent(
        limit=limit,
        offset=offset,
        source_name=source_name,
        include_removed=include_removed,
    )
    return {"count": len(rows), "items": [_serialize_listing(m) for m in rows]}


@router.get("/listings/{reference_id}")
def get_listing(
    reference_id: str,
    _principal: Annotated[AuthPrincipal, Depends(require_scope("listings:read"))],
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    repo = CanonicalListingRepository(session)
    m = repo.get(reference_id)
    if m is None:
        raise HTTPException(status_code=404, detail="listing_not_found")
    return {"item": _serialize_listing(m)}
