#!/usr/bin/env python3
"""
Notify Telegram when Action1 saved listing JSON count grows by N (default 100).

Counts `data/scraped/<source>/listings/*.json` for the seven Action1 sources.
Persists last notified total in `data/runs/action1_listing_json_total.txt`.

No network except optional `openclaw message send` when --send is used.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    "address_bg",
    "bulgarianproperties",
    "homes_bg",
    "imot_bg",
    "luximmo",
    "property_bg",
    "suprimmo",
]
CKPT = ROOT / "data" / "runs" / "action1_listing_json_total.txt"


def count_listing_json() -> int:
    n = 0
    for sk in SOURCES:
        d = ROOT / "data" / "scraped" / sk / "listings"
        if not d.is_dir():
            continue
        n += sum(1 for _ in d.glob("*.json"))
    return n


def read_last() -> int:
    if not CKPT.exists():
        return 0
    try:
        return int(CKPT.read_text(encoding="utf-8").strip() or "0")
    except (OSError, ValueError):
        return 0


def write_last(v: int) -> None:
    CKPT.parent.mkdir(parents=True, exist_ok=True)
    CKPT.write_text(str(v), encoding="utf-8")


def build_report() -> str:
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "action1_full_telegram_report.py"), "--compact"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    return r.stdout


def send_telegram(message: str, *, profile: str, target: str, dry_run: bool) -> int:
    cmd = [
        "openclaw",
        "--profile",
        profile,
        "message",
        "send",
        "--channel",
        "telegram",
        "--target",
        target,
        "--message",
        message,
    ]
    if dry_run:
        cmd.append("--dry-run")
    return subprocess.call(cmd)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--threshold", type=int, default=100, help="Min net-new JSON files before notify")
    ap.add_argument("--send", action="store_true", help="Send via openclaw telegram when threshold met")
    ap.add_argument("--dry-run", action="store_true", help="Pass --dry-run to openclaw (no real send)")
    ap.add_argument("--force", action="store_true", help="Notify regardless of threshold")
    ap.add_argument("--profile", default="codex", help="OpenClaw profile")
    ap.add_argument("--target", default="181488201", help="Telegram chat id")
    args = ap.parse_args()

    total = count_listing_json()
    last = read_last()
    delta = total - last

    print(f"action1 listing JSON total={total} last_notified={last} delta={delta} threshold={args.threshold}")

    if not args.force and delta < args.threshold:
        print("skip: below threshold")
        return 0

    body = build_report()
    prefix = f"**Action1 +{delta} saves** (checkpoint)\n\n"
    msg = prefix + body
    if len(msg) > 3900:
        msg = msg[:3850] + "\n\n…(truncated)"

    if args.send:
        rc = send_telegram(msg, profile=args.profile, target=args.target, dry_run=args.dry_run)
        if rc != 0:
            print("openclaw send failed", file=sys.stderr)
            return rc
        if not args.dry_run:
            write_last(total)
            print(f"updated checkpoint -> {total}")
    else:
        print("--- would send (use --send) ---")
        print(msg)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
