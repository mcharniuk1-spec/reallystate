#!/usr/bin/env bash
# Notify OpenClaw (Telegram) with Action1 RUNNING metrics + explicit continue instructions for the 7-source harvest.
# Requires: `openclaw` on PATH; network permission for send.
#
# Usage:
#   ./scripts/action1_openclaw_continue.sh
#   OPENCLAW_PROFILE=codex OPENCLAW_TARGET=181488201 ./scripts/action1_openclaw_continue.sh
#
# Dry-run (no send):
#   DRY_RUN=1 ./scripts/action1_openclaw_continue.sh

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PROFILE="${OPENCLAW_PROFILE:-codex}"
TARGET="${OPENCLAW_TARGET:-181488201}"
DRY="${DRY_RUN:-}"

REPORT="$(python3 "$ROOT/scripts/action1_full_telegram_report.py" --running-line)"
# Update snapshot after printing so the *next* report has deltas (optional; comment out if you only want manual snapshots)
python3 "$ROOT/scripts/action1_full_telegram_report.py" --running-line --write-snapshot >/dev/null

HANDOFF="$(cat <<'EOFM'

---
**OpenClaw / Gemma4 — Action1 reporting contract (read this)**

1. **Do not** invent or estimate per-source or total listing counts in Telegram.  
2. **Do** run on the host repo and paste **verbatim** the output of:  
   `python3 scripts/action1_full_telegram_report.py --running-line`  
   (or `make action1-running-report`). **Per-website %** = saved JSON files ÷ `website_total` in `docs/exports/website-inventory-analysis.json` (see each line *vs portal inventory total*).  
3. **Exact layout** is defined in `docs/openclaw/action1-running-report-template.md` — same bullets, same order (checkpoint → snapshot → deal type → segments → categories → words → images → **By source** with registry URLs).  
4. **Codex → continue scrape:** explicit `--sources` no longer drops portals when pattern-status lags. Re-run:

```bash
cd REPROOT
export SCRAPER_CONCURRENCY_A1=4   # bounded parallel detail fetches per A1 source (override as needed)
make action1-scrape-full-uncapped
```

   Per-source metrics (bucket A1/A12/other, workers used, timings) append to `data/runs/scrape_metrics.jsonl`; latest line mirrored in `data/runs/scrape_metrics_latest.json`.

5. **5-minute Telegram pulse (optional, parallel terminal):** `make action1-telegram-watch` — runs `action1_full_telegram_report.py --running-line` + OpenClaw send every `ACTION1_TG_INTERVAL_SEC` (default 300).

6. **Read:** `docs/openclaw/ACTION1_AGENT_BOOTSTRAP.md`, `docs/openclaw/scrape-taxonomy-a1-a12.md` (Action1 = A1; A12 = Patterned non-A1 / Action2), `docs/exports/taskforgema.md` (`Action1 ACCEPT`).

EOFM
)"
HANDOFF="${HANDOFF//REPROOT/$ROOT}"

MSG="${REPORT}${HANDOFF}"
if [ -n "$DRY" ]; then
  echo "$MSG"
  exit 0
fi

if command -v timeout >/dev/null 2>&1; then
  exec timeout 180 openclaw --profile "$PROFILE" message send --channel telegram --target "$TARGET" --message "$MSG"
fi
exec openclaw --profile "$PROFILE" message send --channel telegram --target "$TARGET" --message "$MSG"
