from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone
from pathlib import Path

from .source_registry import SourceRegistry


def main() -> int:
    parser = argparse.ArgumentParser(description="Development scheduler placeholder for source crawl scheduling.")
    parser.add_argument("--registry", default="data/source_registry.json")
    parser.add_argument("--once", action="store_true", help="Print one schedule summary and exit.")
    args = parser.parse_args()

    registry = SourceRegistry.from_file(Path(args.registry))
    print("dev scheduler started")
    print("note: this is a lightweight placeholder; implement durable Temporal scheduling in Stage 3.")
    while True:
        candidates = registry.promotion_candidates()
        print(
            f"dev scheduler heartbeat {datetime.now(timezone.utc).isoformat()} | "
            f"sources={len(registry.all())} | tier1-cadence-candidates={len(candidates)}"
        )
        if args.once:
            return 0
        time.sleep(60)


if __name__ == "__main__":
    raise SystemExit(main())
