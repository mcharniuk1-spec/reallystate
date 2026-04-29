#!/usr/bin/env python3
"""Print Action1 (7 sources × 4 buckets) scrape matrix from file-backed JSON.

Use for Telegram pings or logs. Does not hit the network.

Example:
  PYTHONPATH=src python3 scripts/action1_scrape_matrix_snapshot.py
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

SOURCES = [
    "address_bg",
    "bulgarianproperties",
    "homes_bg",
    "imot_bg",
    "luximmo",
    "property_bg",
    "suprimmo",
]
BUCKETS = ["buy_personal", "buy_commercial", "rent_personal", "rent_commercial"]


def main() -> None:
    root = Path("data/scraped")
    matrix: dict[str, dict[str, list[object]]] = {s: {b: [] for b in BUCKETS} for s in SOURCES}
    extras: dict[str, defaultdict[str, int]] = {s: defaultdict(int) for s in SOURCES}

    total = 0
    full = 0
    for sk in SOURCES:
        d = root / sk / "listings"
        if not d.is_dir():
            continue
        for p in d.glob("*.json"):
            try:
                row = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            total += 1
            if row.get("full_gallery_downloaded"):
                full += 1
            bk = (row.get("bucket_key") or row.get("segment_key") or "").strip()
            if bk in BUCKETS:
                matrix[sk][bk].append(row)
            else:
                extras[sk][bk or "(empty)"] += 1

    lines: list[str] = []
    lines.append(f"Action1 snapshot — total_listings={total} full_gallery={full} ({full / total * 100:.1f}%)" if total else "Action1 snapshot — no rows")
    lines.append("Matrix (saved items per source × bucket):")
    header = "| source | " + " | ".join(BUCKETS) + " |"
    sep = "|---|" + "---|" * len(BUCKETS)
    lines.append(header)
    lines.append(sep)
    for sk in SOURCES:
        cells = [str(len(matrix[sk][b])) for b in BUCKETS]
        lines.append(f"| `{sk}` | " + " | ".join(cells) + " |")
    unk = [(sk, dict(extras[sk])) for sk in SOURCES if extras[sk]]
    if unk:
        lines.append("Unbucketed / legacy keys (fix classifiers or backfill):")
        for sk, mp in unk:
            lines.append(f"- `{sk}`: {mp}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
