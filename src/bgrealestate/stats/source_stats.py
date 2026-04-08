from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine


@dataclass(frozen=True)
class SourceStatRow:
    source_name: str
    canonical_listings: int
    raw_captures: int
    with_description: int


def fetch_source_stats(engine: Engine) -> list[SourceStatRow]:
    """
    Minimal per-source health stats for operator dashboards.

    Notes:
    - counts are approximate MVP metrics
    - schema stores image_urls as JSONB; we treat "non-empty array" as photo-present
    """
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
        )
        select
          coalesce(canon.source_name, raw.source_name) as source_name,
          coalesce(canon.canonical_listings, 0) as canonical_listings,
          coalesce(raw.raw_captures, 0) as raw_captures,
          coalesce(canon.with_description, 0) as with_description
        from canon
        full outer join raw using (source_name)
        order by 2 desc, 1 asc
        """
    )
    with engine.connect() as conn:
        rows = conn.execute(q).mappings().all()
    out: list[SourceStatRow] = []
    for r in rows:
        out.append(
            SourceStatRow(
                source_name=str(r["source_name"]),
                canonical_listings=int(r["canonical_listings"]),
                raw_captures=int(r["raw_captures"]),
                with_description=int(r["with_description"]),
            )
        )
    return out

