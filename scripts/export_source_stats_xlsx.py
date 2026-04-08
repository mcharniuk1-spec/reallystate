from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine

from bgrealestate.stats.source_stats import fetch_source_stats


def main() -> int:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL not set")

    out_path = Path(os.getenv("OUT_XLSX", "docs/exports/source-stats.xlsx"))
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Lazy import so the script can be present even when deps aren't installed.
    from openpyxl import Workbook  # type: ignore

    engine = create_engine(url, pool_pre_ping=True)
    rows = fetch_source_stats(engine)

    wb = Workbook()
    ws = wb.active
    ws.title = "source_stats"
    ws.append(["source_name", "canonical_listings", "raw_captures", "with_description"])
    for r in rows:
        ws.append([r.source_name, r.canonical_listings, r.raw_captures, r.with_description])
    wb.save(out_path)
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

