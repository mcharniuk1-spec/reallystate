# OpenClaw / Action1 agent reset review — 2026-05-05

## FACT — what exists

- OpenClaw Action1/A1 scope is documented as seven sources: `Address.bg`, `BulgarianProperties`, `Homes.bg`, `imot.bg`, `LUXIMMO`, `property.bg`, `SUPRIMMO`.
- The scraper implementation is Python/Make-driven; OpenClaw is an operator/monitor/reporting layer that can trigger approved Make targets.
- A1 quality gates already exist:
  - `scripts/action1_dataset_quality_gate.py`
  - `scripts/action1_full_telegram_report.py`
  - `scripts/import_scraped_listings.py`
  - `scripts/generate_frontend_scraped_listings.py`
- Prior A1 defects were already partly hardened: route/bucket context, source-publication status, grouped/development quarantine, `LOST` quarantine, inactive import/export blocking, and QA-eligible pattern proof.
- The uncapped A1 runner already sets `SCRAPER_PAGE_ORDER=oldest_first`.

## INTERPRETATION — current consistency gaps

- Agent ownership was too fragmented: tier-3 and social were separate while Action1 still needed data-quality and reporting control.
- There was no explicit data analyst owner for corpus truth, so dashboard/report wording could mix accepted properties with `LOST`, grouped/development, inactive, or partial-media rows.
- OpenClaw had strong bootstrap instructions but needed an explicit S&M role boundary so monitoring/intelligence work does not widen A1 marketplace scope.
- "Oldest to newest" is currently implemented as oldest-first within each paginated scan window, then wider waves. This is practical and reproducible but not a perfect native chronological cursor for every website.

## HYPOTHESIS — remaining scraper risks

- Some portals may not expose stable chronological pagination; exact old-to-new backfill will require source-specific cursor logic by date/id/list position.
- Full-corpus QA can be slow on the large local file tree; bounded smoke QA is necessary for OpenClaw/debugger responsiveness.
- File-backed totals and DB-backed totals can drift until `make import-scraped` runs with `DATABASE_URL` and the import excludes bad/grouped/inactive rows.

## GAP — needs next execution

- Data analyst must run DA-01 to produce the seven-source × four-bucket accepted/LOST/grouped/inactive/media/description/parser-gap report.
- Debugger must verify PLAN-01, SM-00, and OpenClaw reporting consistency.
- If exact chronological continuation is required per source, scraper_1/Qwen must implement source-native cursor support after DA-01 identifies which sources still need it.

## Changes made in this reset

- Added planner and data analyst lanes.
- Converted `scraper_sm` into S&M, owning tier-3 plus tier-4 intelligence overlays.
- Marked `scraper_t3` as historical only; new tier-3 work goes to S&M.
- Added `docs/openclaw/OPENCLAW_S_AND_M_AGENT.md`.
- Hardened OpenClaw bootstrap, reporter skill, reporter instructions, and model-routing docs.
- Added completion rule: Action1 is not complete until data analyst/debugger separate accepted-good, `LOST`, grouped/development, inactive, media gaps, description gaps, and parser gaps.

## Next required actions

1. `data_analyst` runs `DA-01`.
2. `debugger` verifies `PLAN-01`, `SM-00`, and `DBG-08` readiness.
3. `scraper_1` continues A1 only through the approved runner:

```bash
SCRAPER_PAGE_ORDER=oldest_first make action1-scrape-full-uncapped
```

4. OpenClaw reporter uses:

```bash
make action1-telegram-watch-detached
make action1-matrix-snapshot
python3 scripts/action1_dataset_quality_gate.py --limit-per-source 20 --output docs/exports/action1-dataset-quality-gate-dryrun.json
```
