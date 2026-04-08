from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine


@dataclass(frozen=True)
class SourceStatRow:
    source_name: str
    tier: int | None
    legal_mode: str | None
    canonical_listings: int
    raw_captures: int
    with_description: int
    with_photos: int
    photo_coverage_pct: float
    intent_sale: int
    intent_rent: int
    intent_str: int
    intent_auction: int
    category_apartment: int
    category_house: int
    category_land: int
    category_commercial: int
    has_legal_rule: bool
    has_endpoint: bool


def fetch_source_stats(engine: Engine) -> list[SourceStatRow]:
    """Per-source health stats that cover both registry metadata and ingestion counts.

    The query LEFT JOINs registry → canon/raw/legal/endpoint so sources that have been
    synced but have zero ingested data still appear (important for the control-plane
    bootstrap verification).

    SQLAlchemy is imported inside this function so ``SourceStatRow`` stays importable in
    stdlib-only / minimal test environments (AGENTS.md: no heavy deps required for unit tests).
    """
    from sqlalchemy import text

    q = text(
        """
        with canon as (
          select
            source_name,
            count(*)::int as canonical_listings,
            sum(case when description is not null and length(trim(description)) > 0 then 1 else 0 end)::int as with_description,
            sum(
              case when image_urls is not null and jsonb_typeof(image_urls) = 'array' and jsonb_array_length(image_urls) > 0
                then 1
                else 0
              end
            )::int as with_photos,
            sum(case when lower(coalesce(listing_intent, '')) = 'sale' then 1 else 0 end)::int as intent_sale,
            sum(case when lower(coalesce(listing_intent, '')) = 'rent' then 1 else 0 end)::int as intent_rent,
            sum(case when lower(coalesce(listing_intent, '')) in ('str', 'short_term_rent') then 1 else 0 end)::int as intent_str,
            sum(case when lower(coalesce(listing_intent, '')) = 'auction' then 1 else 0 end)::int as intent_auction,
            sum(case when lower(coalesce(property_category, '')) = 'apartment' then 1 else 0 end)::int as category_apartment,
            sum(case when lower(coalesce(property_category, '')) = 'house' then 1 else 0 end)::int as category_house,
            sum(case when lower(coalesce(property_category, '')) = 'land' then 1 else 0 end)::int as category_land,
            sum(
              case when lower(coalesce(property_category, '')) in ('commercial', 'office', 'retail', 'warehouse', 'industrial')
                then 1
                else 0
              end
            )::int as category_commercial
          from canonical_listing
          group by source_name
        ),
        raw as (
          select source_name, count(*)::int as raw_captures
          from raw_capture
          group by source_name
        ),
        legal as (
          select source_name, true as has_rule
          from source_legal_rule
          group by source_name
        ),
        ep as (
          select source_name, true as has_ep
          from source_endpoint
          group by source_name
        )
        select
          sr.source_name,
          sr.tier,
          sr.legal_mode,
          coalesce(canon.canonical_listings, 0) as canonical_listings,
          coalesce(raw.raw_captures, 0) as raw_captures,
          coalesce(canon.with_description, 0) as with_description,
          coalesce(canon.with_photos, 0) as with_photos,
          case
            when coalesce(canon.canonical_listings, 0) = 0 then 0
            else round((coalesce(canon.with_photos, 0)::numeric / canon.canonical_listings::numeric) * 100, 2)
          end as photo_coverage_pct,
          coalesce(canon.intent_sale, 0) as intent_sale,
          coalesce(canon.intent_rent, 0) as intent_rent,
          coalesce(canon.intent_str, 0) as intent_str,
          coalesce(canon.intent_auction, 0) as intent_auction,
          coalesce(canon.category_apartment, 0) as category_apartment,
          coalesce(canon.category_house, 0) as category_house,
          coalesce(canon.category_land, 0) as category_land,
          coalesce(canon.category_commercial, 0) as category_commercial,
          coalesce(legal.has_rule, false) as has_legal_rule,
          coalesce(ep.has_ep, false) as has_endpoint
        from source_registry sr
        left join canon using (source_name)
        left join raw using (source_name)
        left join legal using (source_name)
        left join ep using (source_name)
        order by sr.tier asc, canonical_listings desc, sr.source_name asc
        """
    )
    with engine.connect() as conn:
        rows = conn.execute(q).mappings().all()
    out: list[SourceStatRow] = []
    for r in rows:
        out.append(
            SourceStatRow(
                source_name=str(r["source_name"]),
                tier=int(r["tier"]) if r["tier"] is not None else None,
                legal_mode=r["legal_mode"],
                canonical_listings=int(r["canonical_listings"]),
                raw_captures=int(r["raw_captures"]),
                with_description=int(r["with_description"]),
                with_photos=int(r["with_photos"]),
                photo_coverage_pct=float(r["photo_coverage_pct"]),
                intent_sale=int(r["intent_sale"]),
                intent_rent=int(r["intent_rent"]),
                intent_str=int(r["intent_str"]),
                intent_auction=int(r["intent_auction"]),
                category_apartment=int(r["category_apartment"]),
                category_house=int(r["category_house"]),
                category_land=int(r["category_land"]),
                category_commercial=int(r["category_commercial"]),
                has_legal_rule=bool(r["has_legal_rule"]),
                has_endpoint=bool(r["has_endpoint"]),
            )
        )
    return out
