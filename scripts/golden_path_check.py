#!/usr/bin/env python3
"""Golden-path check: migrate → sync → ingest offline fixture → stats → XLSX export.

- Skips with exit 0 when ``DATABASE_URL`` is unset (CI / laptops without Postgres).
- When set, runs against local Postgres only; no live HTTP (fixture HTML only).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
_SRC = REPO / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


def _log(msg: str) -> None:
    print(f"[golden-path] {msg}", flush=True)


def _effective_database_url() -> str | None:
    """Return a non-empty DB URL, or None if unset/blank (whitespace-only counts as unset)."""
    raw = os.getenv("DATABASE_URL", "")
    stripped = raw.strip()
    return stripped or None


def main() -> int:
    db_url = _effective_database_url()
    if not db_url:
        _log("SKIP: DATABASE_URL not set — golden path needs a prepared Postgres (see docs/development-setup.md)")
        return 0

    child_env = {**os.environ, "DATABASE_URL": db_url}

    _log("1/5 alembic upgrade head")
    r = subprocess.run(
        [sys.executable, "-m", "alembic", "-c", str(REPO / "alembic.ini"), "upgrade", "head"],
        cwd=str(REPO),
        env=child_env,
    )
    if r.returncode != 0:
        _log("alembic failed")
        return r.returncode

    from sqlalchemy import create_engine

    from bgrealestate.connectors.fixtures import fixture_dir, read_text
    from bgrealestate.connectors.ingest import ingest_listing_detail_html
    from bgrealestate.db_sync import sync_marketplace_sources_to_db
    from bgrealestate.source_registry import SourceRegistry
    from bgrealestate.stats.source_stats import fetch_source_stats

    engine = create_engine(db_url, pool_pre_ping=True)

    _log("2/5 sync registry + legal rules + endpoints")
    registry = SourceRegistry.from_file(REPO / "data" / "source_registry.json")
    sync_result = sync_marketplace_sources_to_db(engine, registry)
    _log(f"sync: {sync_result}")

    _log("3/5 ingest Homes.bg basic_listing fixture (offline HTML)")
    case = fixture_dir("homes_bg") / "basic_listing"
    html = read_text(case / "raw.html")
    expected = json.loads(read_text(case / "expected.json"))
    url = expected["listing_url"]
    source = registry.by_name("Homes.bg")
    if source is None:
        _log("Homes.bg missing from registry")
        return 1
    ingest_out = ingest_listing_detail_html(
        engine=engine,
        source=source,
        url=url,
        html=html,
        discovered_at=datetime.now(tz=timezone.utc),
    )
    _log(f"ingest: reference_id={ingest_out['reference_id']}")

    _log("4/5 fetch source stats (same query as /admin/source-stats)")
    rows = fetch_source_stats(engine)
    homes = [x for x in rows if x.source_name == "Homes.bg"]
    if not homes or homes[0].canonical_listings < 1:
        _log(f"expected Homes.bg canonical_listings >= 1, got {homes!r}")
        return 1
    _log(f"stats: Homes.bg canonical_listings={homes[0].canonical_listings} raw_captures={homes[0].raw_captures}")

    _log("5/5 export docs/exports/source-stats.xlsx")
    out_xlsx = REPO / "docs" / "exports" / "source-stats.xlsx"
    r = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "export_source_stats_xlsx.py")],
        cwd=str(REPO),
        env={**child_env, "OUT_XLSX": str(out_xlsx), "PYTHONPATH": str(_SRC)},
    )
    if r.returncode != 0:
        _log("export_source_stats_xlsx failed")
        return r.returncode

    _log("OK — golden path complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
