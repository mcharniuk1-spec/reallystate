from __future__ import annotations

import argparse
import asyncio
import os
import time
from datetime import datetime, timezone

from .workflows.temporal_runtime import load_temporal_settings, run_temporal_worker_forever, temporal_connectivity_check, temporal_enabled


def main() -> int:
    parser = argparse.ArgumentParser(description="Development worker (placeholder or Temporal runtime).")
    parser.add_argument("--once", action="store_true", help="Print one heartbeat and exit.")
    parser.add_argument(
        "--mode",
        choices=("auto", "placeholder", "temporal"),
        default="auto",
        help="Worker mode. auto uses ENABLE_TEMPORAL_RUNTIME to pick temporal/placeholder.",
    )
    args = parser.parse_args()

    mode = args.mode
    if mode == "auto":
        mode = "temporal" if temporal_enabled() else "placeholder"

    if mode == "temporal":
        settings = load_temporal_settings()
        print(
            f"dev worker started (temporal mode) | address={settings.address} "
            f"namespace={settings.namespace} task_queue={settings.task_queue}"
        )
        if args.once:
            try:
                out = asyncio.run(temporal_connectivity_check())
                print(f"temporal connectivity: {out}")
                return 0
            except Exception as exc:  # noqa: BLE001
                if os.getenv("ALLOW_TEMPORAL_FALLBACK", "1").strip().lower() in {"1", "true", "yes", "on"}:
                    print(f"temporal connectivity failed, fallback to placeholder: {exc}")
                else:
                    raise
        else:
            asyncio.run(run_temporal_worker_forever())
            return 0

    print("dev worker started")
    print("note: placeholder mode active. Set ENABLE_TEMPORAL_RUNTIME=1 for real Temporal worker.")
    while True:
        print(f"dev worker heartbeat {datetime.now(timezone.utc).isoformat()}")
        if args.once:
            return 0
        time.sleep(30)


if __name__ == "__main__":
    raise SystemExit(main())
