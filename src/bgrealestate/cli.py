from __future__ import annotations

import argparse
from pathlib import Path

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

    return 1

