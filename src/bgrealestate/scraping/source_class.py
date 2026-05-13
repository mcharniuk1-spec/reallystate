"""A1 vs A12 classification for live scrape concurrency and metrics.

Operator **Action1** (seven priority portals) matches code bucket **A1** — see
``docs/openclaw/scrape-taxonomy-a1-a12.md``.

- **A1** (Action1): seven priority portals (same seven as OpenClaw Action1).
- **A12**: tier-1/2 sources marked Patterned in ``tier12-pattern-status.json`` excluding A1.
- **other**: everything else (conservative defaults).
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

REPO = Path(__file__).resolve().parents[3]
TIER12_STATUS = REPO / "docs" / "exports" / "tier12-pattern-status.json"

# Registry ``source_name`` → ``live_scraper`` SOURCE_CONFIGS key (must stay aligned with scripts/live_scraper.SOURCE_CONFIGS)
A1_SOURCE_KEYS: frozenset[str] = frozenset(
    {
        "address_bg",
        "bulgarianproperties",
        "homes_bg",
        "imot_bg",
        "luximmo",
        "property_bg",
        "suprimmo",
    }
)

SourceBucket = Literal["A1", "A12", "other"]


@lru_cache(maxsize=1)
def _patterned_source_names() -> frozenset[str]:
    if not TIER12_STATUS.exists():
        return frozenset()
    data = json.loads(TIER12_STATUS.read_text(encoding="utf-8"))
    names: set[str] = set()
    for row in data.get("sources", []):
        if row.get("pattern_status") == "Patterned" and row.get("source_name"):
            names.add(str(row["source_name"]))
    return frozenset(names)


def source_bucket_for_key(source_key: str, *, source_display_name: str) -> SourceBucket:
    if source_key in A1_SOURCE_KEYS:
        return "A1"
    if source_display_name in _patterned_source_names() and source_key not in A1_SOURCE_KEYS:
        return "A12"
    return "other"


def detail_concurrency_for_bucket(bucket: SourceBucket) -> int:
    """Parallel detail-fetch workers (bounded). Env overrides per class."""
    if bucket == "A1":
        return max(1, int(os.environ.get("SCRAPER_CONCURRENCY_A1", "4")))
    if bucket == "A12":
        return max(1, int(os.environ.get("SCRAPER_CONCURRENCY_A12", "3")))
    return max(1, int(os.environ.get("SCRAPER_CONCURRENCY_OTHER", "1")))


def detail_concurrency_for_source(source_key: str, source_display_name: str) -> int:
    return detail_concurrency_for_bucket(source_bucket_for_key(source_key, source_display_name=source_display_name))
