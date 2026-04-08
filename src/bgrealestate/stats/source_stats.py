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
            sum(case when description is not null and length(trim(description)) > 0 then 1 else 0 end)::int as with_description
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
                has_legal_rule=bool(r["has_legal_rule"]),
                has_endpoint=bool(r["has_endpoint"]),
            )
        )
    return out
