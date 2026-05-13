#!/usr/bin/env bash
# Reliable Action1 ops rehydration to Telegram via OpenClaw **message send** (not `agent --deliver`,
# which can hang on long prompts).
#
# Sends two messages:
#   1) Short rules (always small; resets model context).
#   2) Compact metrics (`--compact`) with a Python-side timeout — full `--running-line` can take
#      many minutes on a large corpus and can stall Telegram delivery.
#
# Usage:
#   ./scripts/action1_telegram_ops_rehydrate.sh
#   OPENCLAW_PROFILE=codex OPENCLAW_TARGET=181488201 ./scripts/action1_telegram_ops_rehydrate.sh
#
# Dry-run:
#   DRY_RUN=1 ./scripts/action1_telegram_ops_rehydrate.sh
#
# Prepend compact host/task context to message 2 (set ACTION1_REHYDRATE_PREFLIGHT=0 to disable):
#   ACTION1_REHYDRATE_PREFLIGHT=0 ./scripts/action1_telegram_ops_rehydrate.sh

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PROFILE="${OPENCLAW_PROFILE:-codex}"
TARGET="${OPENCLAW_TARGET:-181488201}"
DRY="${DRY_RUN:-}"
REPORT_TIMEOUT_SEC="${ACTION1_REHYDRATE_REPORT_TIMEOUT_SEC:-300}"
TELEGRAM_SAFE_CHARS="${ACTION1_REHYDRATE_MAX_CHARS:-3800}"

RULES="$(cat <<'EOF'
Action1 ops — REHYDRATE (follow; do not ask for GO / confirmation / standing by).

• Inbound Telegram → agent id **action1_gemma**; model: **ollama/qwen3-coder:30b** (see ~/.openclaw-codex/openclaw.json).
• Scraper is Python on host: **make action1-scrape-full-uncapped** or **make action1-scrape-full-uncapped-detached**.
• **Every 5 min** the host posts the full RUNNING layout via **make action1-telegram-watch-detached** (verbatim `--running-line`). That is the canonical pulse — not manual narration.
• Parser fixes imply **rescrape** via the same Make targets; **bad** rows are visible in reports (thin / $0 / multi / gallery_gap).
• If operator says "start action1": reply **already running** or give the two Make commands above — never block on approval.

Next message: compact metrics snapshot (or timeout note).
EOF
)"

compact_report_block() {
  python3 - "$ROOT" "$REPORT_TIMEOUT_SEC" "$TELEGRAM_SAFE_CHARS" <<'PY'
import json
import os
import signal
import subprocess
import sys
from pathlib import Path

root, timeout_s, max_chars = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
root_path = Path(root)


def run_timeboxed(cmd, timeout):
    proc = subprocess.Popen(
        cmd,
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        out, err = proc.communicate()
        return 124, out, err
    return proc.returncode, out, err


def inline_pulse() -> str:
    sources = [
        ("address_bg", "Address.bg"),
        ("bulgarianproperties", "BulgarianPr"),
        ("homes_bg", "Homes.bg"),
        ("imot_bg", "imot.bg"),
        ("luximmo", "LUXIMMO"),
        ("property_bg", "property.bg"),
        ("suprimmo", "SUPRIMMO"),
    ]
    total = 0
    parts = []
    for sk, label in sources:
        d = root_path / "data" / "scraped" / sk / "listings"
        n = 0
        try:
            with os.scandir(d) as it:
                for e in it:
                    if e.is_file() and e.name.endswith(".json"):
                        n += 1
        except FileNotFoundError:
            pass
        total += n
        parts.append(f"{label}:{n}")
    snap = {}
    try:
        snap = json.loads((root_path / "data" / "runs" / "action1_last_running_snapshot.json").read_text(encoding="utf-8"))
    except Exception:
        pass
    return (
        f"⚡ Action1 compact fallback. Total JSON files={total}; "
        f"last full snapshot={snap.get('updated_at', 'n/a')}\n"
        "• by source: " + " | ".join(parts)
    )

cmd = [
        sys.executable,
        str(root_path / "scripts" / "action1_full_telegram_report.py"),
        "--compact",
        "--skip-top-tokens",
    ]
code, out, err = run_timeboxed(cmd, timeout_s)
if code != 0:
    print(inline_pulse())
    sys.exit(0)
out = (out or "").strip()
if len(out) > max_chars:
    out = out[: max_chars - 80] + "\n\n…(truncated for Telegram; full via 5-min watcher or host `--running-line`.)"
print(out)
PY
}

send() {
  local body="$1"
  if [ -n "$DRY" ]; then
    printf '%s\n' "$body"
    return 0
  fi
  openclaw --profile "$PROFILE" message send --channel telegram --target "$TARGET" --message "$body" --json
}

# Rules first (fast path for the operator), then generate metrics — full corpus can take minutes.
send "$RULES"
REPORT_BLOCK="$(compact_report_block)"
PREFLIGHT_BLOCK=""
if [[ "${ACTION1_REHYDRATE_PREFLIGHT:-1}" != "0" ]]; then
  PREFLIGHT_BLOCK="$(bash "$ROOT/scripts/openclaw_context_preflight.sh" --compact 2>/dev/null || true)"
fi
if [[ -n "$PREFLIGHT_BLOCK" ]]; then
  send "$(printf '%s\n\n📌 Context preflight (repo + TASKS grep + logs):\n%s\n\n%s' '📎 Action1 compact snapshot (file-backed):' "$PREFLIGHT_BLOCK" "$REPORT_BLOCK")"
else
  send "$(printf '%s\n\n%s' '📎 Action1 compact snapshot (file-backed):' "$REPORT_BLOCK")"
fi
