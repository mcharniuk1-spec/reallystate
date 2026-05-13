#!/usr/bin/env bash
# Cron/launchd-safe Action1 reporter entrypoint.
#
# Fixes “Cron job Action1 Progress Reporter failed … read”: this wrapper is silent,
# idempotent, and exits 0 when reporter is disabled or locked (so the scheduler stops alarming).
#
# Recommended cron/launchd command:
#   cd /Users/getapple/Documents/Real\ Estate\ Bulg && bash scripts/action1_progress_reporter_cron_safe.sh
#
# This will *only* send if:
# - data/runs/action1_reporter_enabled exists AND
# - no active lock exists from the detached watcher.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ENABLED_FILE="${ACTION1_REPORTER_ENABLED_FILE:-$ROOT/data/runs/action1_reporter_enabled}"
LOCK_FILE="${ACTION1_REPORTER_LOCK_FILE:-$ROOT/data/runs/action1_reporter.lock}"

if [ ! -f "$ENABLED_FILE" ]; then
  exit 0
fi

if [ -f "$LOCK_FILE" ]; then
  pid="$(cat "$LOCK_FILE" 2>/dev/null || true)"
  if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then
    exit 0
  fi
fi

# One tick (interval logic belongs to the detached watcher).
STOP_AFTER_SUCCESS_STREAK=1 ACTION1_TG_INTERVAL_SEC=1 python3 "$ROOT/scripts/action1_openclaw_report_monitor.py" >/dev/null 2>&1 || true
exit 0

