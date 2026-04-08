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

    from openpyxl import Workbook  # type: ignore[import-untyped]
    from openpyxl.styles import Font, PatternFill  # type: ignore[import-untyped]

    engine = create_engine(url, pool_pre_ping=True)
    rows = fetch_source_stats(engine)

    wb = Workbook()
    ws = wb.active
    ws.title = "source_stats"

    header = [
        "source_name",
        "tier",
        "legal_mode",
        "canonical_listings",
        "raw_captures",
        "with_description",
        "has_legal_rule",
        "has_endpoint",
    ]
    ws.append(header)
    header_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    header_font = Font(bold=True)
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font

    for r in rows:
        ws.append([
            r.source_name,
            r.tier,
            r.legal_mode,
            r.canonical_listings,
            r.raw_captures,
            r.with_description,
            "Y" if r.has_legal_rule else "N",
            "Y" if r.has_endpoint else "N",
        ])

    for col in ws.columns:
        max_len = 0
        for cell in col:
            val = str(cell.value) if cell.value is not None else ""
            max_len = max(max_len, len(val))
        ws.column_dimensions[col[0].column_letter].width = max(max_len + 2, 10)

    wb.save(out_path)
    print(f"wrote {out_path} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
