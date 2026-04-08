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

