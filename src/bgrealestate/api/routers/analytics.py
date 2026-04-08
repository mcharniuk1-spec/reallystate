from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.engine import Engine

from ..auth import AuthPrincipal, require_scope
from ..deps import get_engine

router = APIRouter(tags=["analytics"])

_SUMMARY_SQL = text("""
SELECT
    cl.city,
    cl.district,
    cl.listing_intent,
    cl.property_category,
    cl.source_name,
    count(*)                                     AS listing_count,
    count(*) FILTER (WHERE cl.removed_at IS NULL) AS active_count,
    round(avg(cl.price)::numeric, 2)             AS avg_price,
    round(min(cl.price)::numeric, 2)             AS min_price,
    round(max(cl.price)::numeric, 2)             AS max_price,
    round(avg(cl.price_per_sqm)::numeric, 2)     AS avg_price_per_sqm,
    round(avg(cl.area_sqm)::numeric, 1)          AS avg_area_sqm,
    round(avg(cl.rooms)::numeric, 1)             AS avg_rooms,
    count(*) FILTER (WHERE cl.image_urls != '[]'::jsonb) AS with_photos,
    count(*) FILTER (WHERE cl.description IS NOT NULL AND cl.description != '') AS with_description
FROM canonical_listing cl
WHERE (:city IS NULL OR cl.city = :city)
  AND (:intent IS NULL OR cl.listing_intent = :intent)
  AND (:category IS NULL OR cl.property_category = :category)
GROUP BY cl.city, cl.district, cl.listing_intent, cl.property_category, cl.source_name
ORDER BY listing_count DESC
LIMIT :lim OFFSET :off
""")

_DUPLICATES_SQL = text("""
SELECT
    a.reference_id  AS ref_a,
    b.reference_id  AS ref_b,
    a.source_name   AS source_a,
    b.source_name   AS source_b,
    a.city,
    a.address_text  AS address_a,
    b.address_text  AS address_b,
    a.price         AS price_a,
    b.price         AS price_b,
    a.area_sqm      AS area_a,
    b.area_sqm      AS area_b,
    CASE WHEN a.price > 0 AND b.price > 0
         THEN round(abs(a.price - b.price) / greatest(a.price, b.price) * 100, 1)
         ELSE NULL END AS price_diff_pct,
    CASE WHEN a.area_sqm > 0 AND b.area_sqm > 0
         THEN round(abs(a.area_sqm - b.area_sqm) / greatest(a.area_sqm, b.area_sqm) * 100, 1)
         ELSE NULL END AS area_diff_pct
FROM canonical_listing a
JOIN canonical_listing b
  ON a.city IS NOT NULL
 AND a.city = b.city
 AND a.reference_id < b.reference_id
 AND a.removed_at IS NULL
 AND b.removed_at IS NULL
 AND a.address_text IS NOT NULL
 AND b.address_text IS NOT NULL
 AND lower(trim(a.address_text)) = lower(trim(b.address_text))
WHERE
    (:city IS NULL OR a.city = :city)
AND (a.price IS NULL OR b.price IS NULL
     OR abs(a.price - b.price) / greatest(a.price, b.price, 1) < 0.15)
AND (a.area_sqm IS NULL OR b.area_sqm IS NULL
     OR abs(a.area_sqm - b.area_sqm) / greatest(a.area_sqm, b.area_sqm, 1) < 0.15)
ORDER BY a.city, a.address_text
LIMIT :lim OFFSET :off
""")


def _row_to_dict(row: Any, keys: list[str]) -> dict[str, Any]:
    return {k: (float(v) if hasattr(v, "as_integer_ratio") else v) for k, v in zip(keys, row)}


@router.get("/analytics/summary")
def analytics_summary(
    _principal: Annotated[AuthPrincipal, Depends(require_scope("listings:read"))],
    engine: Annotated[Engine, Depends(get_engine)],
    city: str | None = None,
    intent: str | None = None,
    category: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    keys = [
        "city", "district", "listing_intent", "property_category", "source_name",
        "listing_count", "active_count", "avg_price", "min_price", "max_price",
        "avg_price_per_sqm", "avg_area_sqm", "avg_rooms", "with_photos", "with_description",
    ]
    with engine.connect() as conn:
        rows = conn.execute(
            _SUMMARY_SQL,
            {"city": city, "intent": intent, "category": category, "lim": limit, "off": offset},
        ).fetchall()
    items = [_row_to_dict(r, keys) for r in rows]
    return {"count": len(items), "items": items}


@router.get("/analytics/duplicates")
def analytics_duplicates(
    _principal: Annotated[AuthPrincipal, Depends(require_scope("admin:read"))],
    engine: Annotated[Engine, Depends(get_engine)],
    city: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    keys = [
        "ref_a", "ref_b", "source_a", "source_b", "city",
        "address_a", "address_b", "price_a", "price_b",
        "area_a", "area_b", "price_diff_pct", "area_diff_pct",
    ]
    with engine.connect() as conn:
        rows = conn.execute(
            _DUPLICATES_SQL,
            {"city": city, "lim": limit, "off": offset},
        ).fetchall()
    items = [_row_to_dict(r, keys) for r in rows]
    return {"count": len(items), "items": items}
