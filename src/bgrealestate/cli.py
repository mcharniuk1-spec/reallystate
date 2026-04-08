from __future__ import annotations

import argparse
from pathlib import Path

from .connectors.factory import marketplace_sources
from .exporters import export_matrices
from .source_registry import SourceRegistry


def _default_registry_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "source_registry.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Bulgaria real estate ingestion toolkit")
    parser.add_argument("--registry", type=Path, default=_default_registry_path(), help="Path to the source registry JSON file.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-sources", help="Print seeded sources.")
    export_parser = subparsers.add_parser("export-matrices", help="Export source and legal matrices.")
    export_parser.add_argument("--out-dir", type=Path, default=Path("artifacts"))

    ingest_parser = subparsers.add_parser(
        "ingest-fixture",
        help="Parse a fixture HTML file and insert it into the database (offline, no network).",
    )
    ingest_parser.add_argument("source_name", help="Registry source name (e.g. Homes.bg)")
    ingest_parser.add_argument("fixture_dir", type=Path, help="Path to fixture case dir (must contain raw.html and expected.json)")
    ingest_parser.add_argument("--dry-run", action="store_true", help="Parse and print canonical listing; do not touch the database.")

    sync_parser = subparsers.add_parser(
        "sync-database",
        help="Upsert marketplace sources (excluding social/messenger), legal rules, and primary URLs into PostgreSQL.",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print counts only; do not connect to the database.",
    )

    args = parser.parse_args()
    registry = SourceRegistry.from_file(args.registry)

    if args.command == "list-sources":
        for entry in registry.all():
            print(f"{entry.tier} | {entry.source_name} | {entry.source_family.value} | {entry.access_mode.value}")
        return 0

    if args.command == "ingest-fixture":
        import json
        from datetime import datetime, timezone
        from .connectors.factory import build_connector

        source = registry.by_name(args.source_name)
        if not source:
            print(f"error: source {args.source_name!r} not found in registry")
            return 1
        raw_path = args.fixture_dir / "raw.html"
        if not raw_path.exists():
            raw_path = args.fixture_dir / "raw.json"
        if not raw_path.exists():
            print(f"error: no raw.html or raw.json in {args.fixture_dir}")
            return 1
        html = raw_path.read_text(encoding="utf-8")
        expected_path = args.fixture_dir / "expected.json"
        expected = json.loads(expected_path.read_text(encoding="utf-8")) if expected_path.exists() else {}
        url = expected.get("listing_url", f"https://fixture/{args.source_name}/{args.fixture_dir.name}")
        seed_path = args.fixture_dir / "seed.json"
        seed = json.loads(seed_path.read_text(encoding="utf-8")) if seed_path.exists() else None

        connector = build_connector(args.source_name, registry)
        now = datetime.now(tz=timezone.utc)

        if hasattr(connector, "parse_and_normalize_from_html"):
            out = connector.parse_and_normalize_from_html(url=url, html=html, discovered_at=now, seed=seed)
        elif hasattr(connector, "parse_api_response"):
            out = connector.parse_api_response(url=url, json_text=html, fetched_at=now, seed=seed)
        else:
            print(f"error: connector for {args.source_name} has no parse method")
            return 1

        canonical = out["canonical_listing"]
        if args.dry_run:
            from dataclasses import asdict
            print(json.dumps({k: str(v) if isinstance(v, datetime) else v for k, v in asdict(canonical).items()}, indent=2, ensure_ascii=False, default=str))
            return 0

        from .connectors.ingest import ingest_listing_detail_html
        from .db.session import create_db_engine

        engine = create_db_engine()
        result = ingest_listing_detail_html(engine=engine, source=source, url=url, html=html, discovered_at=now)
        print(f"ingested: {result}")
        return 0

    if args.command == "export-matrices":
        export_matrices(registry.all(), args.out_dir)
        print(f"exported matrices to {args.out_dir}")
        return 0

    if args.command == "sync-database":
        market = marketplace_sources(registry)
        if args.dry_run:
            print(f"would upsert {len(market)} marketplace sources (tier 1–3 + registers/OTAs; social/messenger skipped)")
            print("run alembic upgrade head (or make migrate) before writing if the database is new")
            return 0
        from .db.session import create_db_engine
        from .db_sync import sync_marketplace_sources_to_db

        engine = create_db_engine()
        stats = sync_marketplace_sources_to_db(engine, registry)
        print(f"synced: {stats}")
        return 0

    return 1

