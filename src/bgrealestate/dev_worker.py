from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone


def main() -> int:
    parser = argparse.ArgumentParser(description="Development worker placeholder for the future Temporal worker.")
    parser.add_argument("--once", action="store_true", help="Print one heartbeat and exit.")
    args = parser.parse_args()

    print("dev worker started")
    print("note: this is a lightweight placeholder; implement Temporal worker in Stage 3.")
    while True:
        print(f"dev worker heartbeat {datetime.now(timezone.utc).isoformat()}")
        if args.once:
            return 0
        time.sleep(30)


if __name__ == "__main__":
    raise SystemExit(main())
