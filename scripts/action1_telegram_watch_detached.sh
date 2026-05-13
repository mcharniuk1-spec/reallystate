#!/usr/bin/env bash
# Detached Action1 Telegram watcher (avoids interactive SIGTERM).
#
# Starts the 5-minute running-line report sender in the background via nohup and writes:
# - data/runs/action1_telegram_watch_detached_<ts>.log
# - data/runs/action1_telegram_watch_detached_<ts>.pid
#
# Env overrides:
# - ACTION1_TG_INTERVAL_SEC (default 300)
# - OPENCLAW_PROFILE (default codex)
# - OPENCLAW_TARGET (default 181488201)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

TS="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="$ROOT/data/runs"
mkdir -p "$RUN_DIR"

LOG="$RUN_DIR/action1_telegram_watch_detached_${TS}.log"
PIDFILE="$RUN_DIR/action1_telegram_watch_detached_${TS}.pid"
ENABLED_FILE="${ACTION1_REPORTER_ENABLED_FILE:-$RUN_DIR/action1_reporter_enabled}"

echo "Starting detached Action1 Telegram watcher."
echo "  log: $LOG"
echo "  pid: $PIDFILE"

mkdir -p "$RUN_DIR"
: >"$ENABLED_FILE"
echo "  enabled: $ENABLED_FILE"

nohup "$ROOT/scripts/action1_telegram_watch.sh" >"$LOG" 2>&1 &
echo $! >"$PIDFILE"

# O(1) pointer for scripts/openclaw_context_preflight.sh (avoids scanning huge data/runs/).
ln -sfn "$LOG" "$RUN_DIR/action1_telegram_watch_detached_LATEST.log"

echo "Detached Telegram watcher started (pid=$(cat "$PIDFILE"))."
