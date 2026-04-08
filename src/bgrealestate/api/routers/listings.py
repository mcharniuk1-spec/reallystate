from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from urllib.parse import quote

from ...db.repositories import CanonicalListingRepository
from ..auth import AuthPrincipal, require_scope
from ..deps import get_db_optional

router = APIRouter(tags=["listings"])


def _iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt is not None else None


def _num(v: Decimal | float | None) -> float | None:
    if v is None:
        return None
    return float(v)


def _proxied_image_url(url: str) -> str:
    """Wrap an external image URL in our proxy endpoint so the frontend can load it."""
    if not url or url.startswith("/"):
        return url
    return f"/media/proxy?url={quote(url, safe='')}"


def _serialize_listing(m: Any, *, media_rows: list | None = None) -> dict[str, Any]:
    raw_urls = list(m.image_urls or [])

    if media_rows is not None:
        served_urls = []
        for mr in media_rows:
            if mr.storage_key:
                served_urls.append(f"/media/{mr.media_id}")
            else:
                served_urls.append(_proxied_image_url(mr.url))
        image_urls = served_urls
    else:
        image_urls = [_proxied_image_url(u) for u in raw_urls]

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
        "image_urls": image_urls,
        "original_image_urls": raw_urls,
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
    session: Annotated[Session | None, Depends(get_db_optional)],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    source_name: str | None = None,
    include_removed: bool = False,
) -> dict[str, Any]:
    if session is None:
        raise HTTPException(status_code=503, detail="database_unavailable")
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
    session: Annotated[Session | None, Depends(get_db_optional)],
) -> dict[str, Any]:
    if session is None:
        raise HTTPException(status_code=503, detail="database_unavailable")
    repo = CanonicalListingRepository(session)
    m = repo.get(reference_id)
    if m is None:
        raise HTTPException(status_code=404, detail="listing_not_found")
    return {"item": _serialize_listing(m)}
