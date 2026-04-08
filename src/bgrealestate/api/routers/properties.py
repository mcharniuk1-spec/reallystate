from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...db.repositories import PropertyEntityRepository
from ..auth import AuthPrincipal, require_scope
from ..deps import get_db_optional

router = APIRouter(tags=["properties"])


def _iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt is not None else None


def _num(v: Decimal | float | None) -> float | None:
    if v is None:
        return None
    return float(v)


def _serialize_property(m: Any) -> dict[str, Any]:
    return {
        "property_id": m.property_id,
        "dedupe_key": m.dedupe_key,
        "entity_type": m.entity_type,
        "canonical_title": m.canonical_title,
        "canonical_description": m.canonical_description,
        "canonical_address": m.canonical_address,
        "canonical_city": m.canonical_city,
        "canonical_building_name": m.canonical_building_name,
        "latitude": m.latitude,
        "longitude": m.longitude,
        "confidence_score": _num(m.confidence_score),
        "review_status": m.review_status,
    }


def _serialize_offer(o: Any) -> dict[str, Any]:
    return {
        "offer_id": o.offer_id,
        "property_id": o.property_id,
        "listing_reference_id": o.listing_reference_id,
        "intent": o.intent,
        "offer_status": o.offer_status,
        "price_amount": _num(o.price_amount),
        "currency": o.currency,
        "last_changed_at": _iso(o.last_changed_at),
    }


def _serialize_listing_brief(m: Any) -> dict[str, Any]:
    return {
        "reference_id": m.reference_id,
        "source_name": m.source_name,
        "listing_url": m.listing_url,
        "listing_intent": m.listing_intent,
        "property_category": m.property_category,
        "city": m.city,
        "district": m.district,
        "price": _num(m.price),
        "currency": m.currency,
        "area_sqm": m.area_sqm,
        "image_urls": list(m.image_urls or []),
        "first_seen": _iso(m.first_seen),
        "last_seen": _iso(m.last_seen),
    }


@router.get("/properties")
def list_properties(
    _principal: Annotated[AuthPrincipal, Depends(require_scope("listings:read"))],
    session: Annotated[Session | None, Depends(get_db_optional)],
    city: str | None = None,
    min_confidence: float | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    if session is None:
        raise HTTPException(status_code=503, detail="database_unavailable")
    repo = PropertyEntityRepository(session)
    rows = repo.list_properties(
        limit=limit, offset=offset, city=city, min_confidence=min_confidence
    )
    return {"count": len(rows), "items": [_serialize_property(m) for m in rows]}


@router.get("/properties/{property_id}")
def get_property(
    property_id: str,
    _principal: Annotated[AuthPrincipal, Depends(require_scope("listings:read"))],
    session: Annotated[Session | None, Depends(get_db_optional)],
) -> dict[str, Any]:
    if session is None:
        raise HTTPException(status_code=503, detail="database_unavailable")
    repo = PropertyEntityRepository(session)
    prop = repo.get(property_id)
    if prop is None:
        raise HTTPException(status_code=404, detail="property_not_found")

    offers = repo.get_offers(property_id)
    listings = repo.get_linked_listings(property_id)

    return {
        "property": _serialize_property(prop),
        "offers": [_serialize_offer(o) for o in offers],
        "source_listings": [_serialize_listing_brief(listing_item) for listing_item in listings],
    }
