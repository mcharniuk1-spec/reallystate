#!/usr/bin/env bash
# Control Action1 Telegram reporter lifecycle (enable/disable/status/stop/start).
#
# This is the antidote to “OpenClaw texts me even when off”: the reporter only sends
# when the enabled file exists, and detached processes can be stopped by pidfiles.
#
# Usage:
#   ./scripts/action1_reporter_control.sh status
#   ./scripts/action1_reporter_control.sh enable
#   ./scripts/action1_reporter_control.sh disable
#   ./scripts/action1_reporter_control.sh stop
#   ./scripts/action1_reporter_control.sh start
#
# Env:
#   ACTION1_REPORTER_ENABLED_FILE (default data/runs/action1_reporter_enabled)

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

RUN_DIR="$ROOT/data/runs"
ENABLED_FILE="${ACTION1_REPORTER_ENABLED_FILE:-$RUN_DIR/action1_reporter_enabled}"

cmd="${1:-status}"

_latest_pidfile() {
  python3 -c '
import os, sys
root=sys.argv[1]; prefix=sys.argv[2]; suffix=sys.argv[3]
d=os.path.join(root,"data","runs")
best=None; best_t=-1.0
try:
  with os.scandir(d) as it:
    for e in it:
      if not e.is_file(follow_symlinks=False): continue
      n=e.name
      if not (n.startswith(prefix) and n.endswith(suffix)): continue
      try: t=e.stat().st_mtime
      except OSError: continue
      if t>best_t: best_t=t; best=e.path
except FileNotFoundError:
  pass
print(best or "")
' "$ROOT" "$1" "$2"
}

_kill_pidfile() {
  local pidfile="$1"
  [ -f "$pidfile" ] || return 0
  local pid
  pid="$(cat "$pidfile" 2>/dev/null || true)"
  if [[ "$pid" =~ ^[0-9]+$ ]]; then
    kill "$pid" 2>/dev/null || true
  fi
}

status() {
  echo "ROOT=$ROOT"
  if [ -f "$ENABLED_FILE" ]; then
    echo "reporter_enabled=yes ($ENABLED_FILE)"
  else
    echo "reporter_enabled=no ($ENABLED_FILE missing)"
  fi
  echo "watcher_latest_log=$RUN_DIR/action1_telegram_watch_detached_LATEST.log"
  echo "scrape_latest_log=$RUN_DIR/action1_scrape_uncapped_detached_LATEST.log"
  local wp
  wp="$(_latest_pidfile "action1_telegram_watch_detached_" ".pid")"
  echo "watcher_pidfile=${wp:-"(none)"}"
  if [ -n "${wp:-}" ] && [ -f "$wp" ]; then
    echo "watcher_pid=$(cat "$wp" 2>/dev/null || true)"
  fi
}

enable() {
  mkdir -p "$RUN_DIR"
  : >"$ENABLED_FILE"
  echo "enabled reporter ($ENABLED_FILE)"
}

disable() {
  rm -f "$ENABLED_FILE"
  echo "disabled reporter (removed $ENABLED_FILE)"
}

stop() {
  local wp
  wp="$(_latest_pidfile "action1_telegram_watch_detached_" ".pid")"
  if [ -n "${wp:-}" ]; then
    _kill_pidfile "$wp"
    echo "stopped watcher via $wp"
  else
    echo "no watcher pidfile found"
  fi
}

start() {
  enable
  "$ROOT/scripts/action1_telegram_watch_detached.sh"
}

case "$cmd" in
  status) status ;;
  enable) enable ;;
  disable) disable ;;
  stop) stop ;;
  start) start ;;
  *) echo "unknown command: $cmd" >&2; exit 2 ;;
esac

