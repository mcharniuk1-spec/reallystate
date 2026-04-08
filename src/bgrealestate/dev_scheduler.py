from __future__ import annotations

import argparse
import asyncio
import time
from datetime import datetime, timezone
from pathlib import Path

from .source_registry import SourceRegistry
from .workflows.temporal_runtime import load_temporal_settings, run_temporal_scheduler_once, temporal_enabled


def main() -> int:
    parser = argparse.ArgumentParser(description="Development scheduler (placeholder or Temporal starter).")
    parser.add_argument("--registry", default="data/source_registry.json")
    parser.add_argument("--once", action="store_true", help="Print one schedule summary and exit.")
    parser.add_argument(
        "--mode",
        choices=("auto", "placeholder", "temporal"),
        default="auto",
        help="Scheduler mode. auto uses ENABLE_TEMPORAL_RUNTIME to pick temporal/placeholder.",
    )
    args = parser.parse_args()

    mode = args.mode
    if mode == "auto":
        mode = "temporal" if temporal_enabled() else "placeholder"
    if mode == "temporal":
        s = load_temporal_settings()
        print(
            f"dev scheduler started (temporal mode) | address={s.address} "
            f"namespace={s.namespace} task_queue={s.task_queue}"
        )
        if args.once:
            try:
                out = asyncio.run(run_temporal_scheduler_once(registry_path=args.registry))
                print(f"temporal workflow started: {out}")
                return 0
            except Exception as exc:  # noqa: BLE001
                print(f"temporal scheduler once failed, fallback to placeholder: {exc}")
        else:
            # For now, long-running temporal scheduling loops are intentionally not autonomous.
            # Operators should use --once via cron/system scheduler until recurring policies mature.
            print("temporal mode long-running scheduler not enabled yet; use --once from cron.")
            return 0

    registry = SourceRegistry.from_file(Path(args.registry))
    print("dev scheduler started")
    print("note: placeholder mode active. Set ENABLE_TEMPORAL_RUNTIME=1 for Temporal scheduler start.")
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
