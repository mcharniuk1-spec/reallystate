#!/usr/bin/env bash
# Detached Action1 runner (avoids interactive SIGTERM).
#
# Starts Action1 scrape in the background via nohup and writes:
# - data/runs/action1_scrape_uncapped_detached_<ts>.log
# - data/runs/action1_scrape_uncapped_detached_<ts>.pid
#
# This is still the same Action1 scope as `scripts/action1_scrape_full_uncapped.sh`.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

TS="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="$ROOT/data/runs"
mkdir -p "$RUN_DIR"

LOG="$RUN_DIR/action1_scrape_uncapped_detached_${TS}.log"
PIDFILE="$RUN_DIR/action1_scrape_uncapped_detached_${TS}.pid"

echo "Starting detached Action1 scrape."
echo "  log: $LOG"
echo "  pid: $PIDFILE"

nohup "$ROOT/scripts/action1_scrape_full_uncapped.sh" >"$LOG" 2>&1 &
echo $! >"$PIDFILE"

ln -sf "$LOG" "$RUN_DIR/action1_scrape_uncapped_detached_LATEST.log"

echo "Detached Action1 scrape started (pid=$(cat "$PIDFILE"))."
