#!/usr/bin/env python3
"""Generate the Varna controlled-crawl manifest and operator matrix.

Outputs:
- ``data/scrape_patterns/regions/varna/sections.json`` for DB sync / runner use
- ``docs/exports/varna-controlled-crawl-matrix.json`` for agents / operators
- ``docs/exports/varna-controlled-crawl-matrix.md`` as a readable runbook appendix

This script performs no network access and does not touch the database.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

import sys

sys.path.insert(0, str(REPO / "src"))

from bgrealestate.scraping.section_catalog import build_varna_matrix, build_varna_sections  # noqa: E402
from bgrealestate.source_registry import SourceRegistry  # noqa: E402

OUT = REPO / "data" / "scrape_patterns" / "regions" / "varna" / "sections.json"
MATRIX_JSON = REPO / "docs" / "exports" / "varna-controlled-crawl-matrix.json"
MATRIX_MD = REPO / "docs" / "exports" / "varna-controlled-crawl-matrix.md"


def _write_matrix_md(rows: list[dict[str, object]]) -> None:
    lines = [
        "# Varna Controlled Crawl Matrix",
        "",
        "This export is the explicit Stage 2 source/segment readiness layer for tier-1 and tier-2 sources.",
        "",
        "| Source | Segment | Pattern | Support | Active | Verticals | Entry scope | Notes |",
        "|---|---|---|---|---:|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {source_name} | `{segment_key}` | `{pattern_status}` | `{support_status}` | {active} | {verticals} | `{entry_scope}` | {notes} |".format(
                source_name=row["source_name"],
                segment_key=row["segment_key"],
                pattern_status=row["pattern_status"],
                support_status=row["support_status"],
                active="yes" if row["active"] else "no",
                verticals=", ".join(row.get("supported_verticals", [])) or "—",
                entry_scope=row.get("entry_scope") or "—",
                notes=row.get("skip_reason") or "eligible for threshold planning",
            )
        )
    MATRIX_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    registry = SourceRegistry.from_file(REPO / "data" / "source_registry.json")
    sections = build_varna_sections(registry)
    matrix = build_varna_matrix(registry)

    manifest = {"schema_version": 2, "region_key": "varna", "sections": sections}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    MATRIX_JSON.parent.mkdir(parents=True, exist_ok=True)
    MATRIX_JSON.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(tz=timezone.utc).isoformat(),
                "region_key": "varna",
                "bucket_count": len(matrix),
                "active_bucket_count": sum(1 for row in matrix if row["active"]),
                "rows": matrix,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    _write_matrix_md(matrix)

    print(f"Wrote {OUT} ({len(sections)} section buckets)")
    print(f"Wrote {MATRIX_JSON}")
    print(f"Wrote {MATRIX_MD}")


if __name__ == "__main__":
    main()
