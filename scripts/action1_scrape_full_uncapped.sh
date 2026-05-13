#!/usr/bin/env bash
# Action1 (S1-22B): seven priority sources, uncapped per-source threshold (--target-per-source 0).
# Live harvest is Python (make scrape-all-full), not OpenClaw. OpenClaw/Gemma = ops narration + Telegram.
#
# Bounded per-source detail concurrency (A1) defaults: export SCRAPER_CONCURRENCY_A1=4 (override as needed).
# Orchestrator parallel sources: --parallel-sources 7 matches the seven A1 portals.
# Metrics: each source run appends a line to data/runs/scrape_metrics.jsonl and overwrites
#   data/runs/scrape_metrics_latest.json for the last completed source in-process.
#
# Logs: data/runs/action1_scrape_uncapped_<timestamp>.log

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export SCRAPER_CONCURRENCY_A1="${SCRAPER_CONCURRENCY_A1:-4}"
export SCRAPER_CONCURRENCY_A12="${SCRAPER_CONCURRENCY_A12:-3}"
export SCRAPER_CONCURRENCY_OTHER="${SCRAPER_CONCURRENCY_OTHER:-1}"
# Crucial backfill behavior: within each scanned window, paginate bottom-to-top (older → newer).
# This reduces starvation of older inventory during long harvests.
export SCRAPER_PAGE_ORDER="${SCRAPER_PAGE_ORDER:-oldest_first}"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="$ROOT/data/runs/action1_scrape_uncapped_${TS}.log"
mkdir -p "$ROOT/data/runs"

{
  echo "=== Action1 uncapped scrape start ${TS} pid=$$ ==="
  echo "LOG=$LOG"
  echo "SCRAPER_CONCURRENCY_A1=$SCRAPER_CONCURRENCY_A1 SCRAPER_CONCURRENCY_A12=$SCRAPER_CONCURRENCY_A12"
  make scrape-all-full EXTRA_ARGS="\
--parallel-sources 7 \
--max-pages 24 \
--max-waves 12 \
--target-per-source 0 \
--refresh-dashboard \
--download-photos \
--sources Address.bg,BulgarianProperties,Homes.bg,imot.bg,LUXIMMO,property.bg,SUPRIMMO"
  echo "=== Action1 uncapped scrape end $(date -Iseconds) ==="
} 2>&1 | tee -a "$LOG"
