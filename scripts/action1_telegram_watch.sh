#!/usr/bin/env bash
# Every ACTION1_TG_INTERVAL_SEC (default 300 = 5 min): snapshot running-line report + send to Telegram via OpenClaw.
# Reporter skill + defaults: agent-skills/reporter/SKILL.md and docs/openclaw/reporter-agent-instructions.md
# Run in a second terminal while Action1 scrape is in progress (alongside make action1-scrape-full-uncapped).
#
# Usage:
#   ./scripts/action1_telegram_watch.sh
#   ACTION1_TG_INTERVAL_SEC=120 OPENCLAW_TARGET=181488201 ./scripts/action1_telegram_watch.sh
#
# Dry-run (no Telegram send):
#   DRY_RUN=1 ./scripts/action1_telegram_watch.sh

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PROFILE="${OPENCLAW_PROFILE:-codex}"
TARGET="${OPENCLAW_TARGET:-181488201}"
INTERVAL="${ACTION1_TG_INTERVAL_SEC:-300}"
FULL_TIMEOUT="${ACTION1_TG_FULL_TIMEOUT_SEC:-240}"
DRY="${DRY_RUN:-}"
ENABLED_FILE="${ACTION1_REPORTER_ENABLED_FILE:-$ROOT/data/runs/action1_reporter_enabled}"
LOCK_FILE="${ACTION1_REPORTER_LOCK_FILE:-$ROOT/data/runs/action1_reporter.lock}"

echo "action1_telegram_watch: interval=${INTERVAL}s profile=${PROFILE} target=${TARGET} full_timeout=${FULL_TIMEOUT}s"

acquire_lock() {
  mkdir -p "$(dirname "$LOCK_FILE")"
  if [ -f "$LOCK_FILE" ]; then
    local pid
    pid="$(cat "$LOCK_FILE" 2>/dev/null || true)"
    if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then
      echo "action1_telegram_watch: another reporter is running (pid=$pid). Exiting."
      exit 0
    fi
  fi
  echo $$ >"$LOCK_FILE"
  trap 'rm -f "$LOCK_FILE"' EXIT INT TERM
}

build_report() {
  python3 - "$ROOT" "$FULL_TIMEOUT" <<'PY'
import json
import os
import signal
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1])
timeout = float(sys.argv[2])
os.chdir(root)

sources = [
    ("address_bg", "Address.bg"),
    ("bulgarianproperties", "BulgarianPr"),
    ("homes_bg", "Homes.bg"),
    ("imot_bg", "imot.bg"),
    ("luximmo", "LUXIMMO"),
    ("property_bg", "property.bg"),
    ("suprimmo", "SUPRIMMO"),
]


def run_timeboxed(cmd, timeout_s):
    proc = subprocess.Popen(
        cmd,
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        out, err = proc.communicate(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        out, err = proc.communicate()
        return 124, out, err
    return proc.returncode, out, err


def inline_pulse() -> str:
    total = 0
    parts = []
    for sk, label in sources:
        d = root / "data" / "scraped" / sk / "listings"
        n = 0
        try:
            with os.scandir(d) as it:
                for e in it:
                    if e.is_file() and e.name.endswith(".json"):
                        n += 1
        except FileNotFoundError:
            n = 0
        total += n
        parts.append(f"{label}:{n}")

    snap_path = root / "data" / "runs" / "action1_last_running_snapshot.json"
    ckpt_path = root / "data" / "runs" / "action1_listing_json_total.txt"
    cache_path = root / "data" / "runs" / "action1_quality_rollup_latest.json"
    snap = {}
    try:
        snap = json.loads(snap_path.read_text(encoding="utf-8"))
    except Exception:
        pass
    prev = int(snap.get("listing_json_total") or 0)
    ckpt_note = ""
    try:
        ckpt = int((ckpt_path.read_text(encoding="utf-8") or "0").strip())
        ckpt_note = f"; vs ckpt {total - ckpt:+d}"
    except Exception:
        pass

    lines = [
        f"⚡ Action1 PULSE (inline fallback). Total JSON files={total} (Δsnapshot {total - prev:+d}{ckpt_note})",
        "• by source: " + " | ".join(parts),
        f"• last full snapshot `updated_at`: {snap.get('updated_at', 'n/a')}",
    ]
    try:
        qc = json.loads(cache_path.read_text(encoding="utf-8"))
        q = qc.get("quality_rollup") or {}
        lines.insert(
            1,
            "• quality (cached): "
            f"total={int(q.get('total') or 0)} | "
            f"proper(good_single_unit)={int(q.get('good_single_unit') or 0)} | "
            f"bad(bad_lost)={int(q.get('bad_lost') or 0)} | "
            f"rescraped_ok={int(q.get('rescraped_ok') or 0)}",
        )
    except Exception:
        lines.insert(1, "• quality (cached): n/a")
    lines.append(
        "• Full scan timed out; inline pulse avoids orphaned report workers. "
        "Run `ACTION1_REPORT_THREADS=7 python3 scripts/action1_full_telegram_report.py --running-line --write-snapshot` on host for full lines."
    )
    return "\n".join(lines)

cmd = [
    sys.executable,
    str(root / "scripts" / "action1_full_telegram_report.py"),
    "--running-line",
    "--write-snapshot",
]
code, out, err = run_timeboxed(cmd, timeout)
if code == 0 and (out or "").strip():
    sys.stdout.write(out.strip())
    raise SystemExit(0)
# Fallback is in-process, so a second report subprocess cannot hang and leak workers.
sys.stdout.write(inline_pulse())
raise SystemExit(0)
PY
}

acquire_lock

while true; do
  tick_start="$(date +%s)"
  if [ ! -f "$ENABLED_FILE" ]; then
    echo "--- $(date -Iseconds) ---"
    echo "reporter disabled (missing $ENABLED_FILE); skipping send"
    sleep "$INTERVAL"
    continue
  fi
  if ! REPORT="$(build_report)"; then
    REPORT="⚡ Action1: report generation failed (see watcher log)."
  fi
  if [ -n "$DRY" ]; then
    echo "--- $(date -Iseconds) ---"
    echo "$REPORT"
  else
    # Avoid shell quoting pitfalls by sending via python subprocess with the message as an argument.
    export ACTION1_REPORT="$REPORT"
    export OPENCLAW_PROFILE="$PROFILE"
    export OPENCLAW_TARGET="$TARGET"
    python3 -c 'import os, subprocess; msg=os.environ.get("ACTION1_REPORT",""); profile=os.environ.get("OPENCLAW_PROFILE","codex"); target=os.environ.get("OPENCLAW_TARGET","181488201"); subprocess.run(["openclaw","--profile",profile,"message","send","--channel","telegram","--target",target,"--message",msg], check=False)' || true
  fi

  # Fixed cadence: aim to start each tick every INTERVAL seconds (doesn't drift if report is slow).
  tick_end="$(date +%s)"
  elapsed="$((tick_end - tick_start))"
  if [ "$elapsed" -ge "$INTERVAL" ]; then
    continue
  fi
  sleep "$((INTERVAL - elapsed))"
done
