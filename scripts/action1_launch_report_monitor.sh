#!/usr/bin/env bash
# Start Action1 Telegram report loop with timeouts + JSON success detection.
#
# **Important:** `openclaw` writes under ~/.openclaw-codex (plugin deps). If you see
# `EPERM: operation not permitted, mkdir .../.openclaw-runtime-deps.lock`, run this from
# **Terminal.app / iTerm** (full OS permissions), not from a restricted Cursor sandbox.
#
# Usage (repo root):
#   chmod +x scripts/action1_launch_report_monitor.sh
#   ./scripts/action1_launch_report_monitor.sh
#
# Background:
#   nohup ./scripts/action1_launch_report_monitor.sh >> data/runs/action1_report_monitor_nohup.out 2>&1 &
#
# Env:
#   STOP_AFTER_SUCCESS_STREAK=5   # exit after N consecutive OK Telegram sends (default 5)
#   ACTION1_TG_INTERVAL_SEC=300   # default 5 minutes
#   OPENCLAW_SEND_TIMEOUT_SEC=220

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export STOP_AFTER_SUCCESS_STREAK="${STOP_AFTER_SUCCESS_STREAK:-5}"
export ACTION1_TG_INTERVAL_SEC="${ACTION1_TG_INTERVAL_SEC:-300}"
export OPENCLAW_SEND_TIMEOUT_SEC="${OPENCLAW_SEND_TIMEOUT_SEC:-220}"
exec python3 "$ROOT/scripts/action1_openclaw_report_monitor.py"
