# Action1 — agent bootstrap (read before any OpenClaw reply)

Paste or load this block **verbatim** at the start of every Action1 / Telegram session so the model **never** claims it lacks “target URLs”, “patterns”, or “the Action1 document”.

## Repo root (canonical on this machine)

`/Users/getapple/Documents/Real Estate Bulg`

If tools run from another clone, replace with that clone’s absolute path.

## Read first (in order)

1. `AGENTS.md`
2. `docs/agents/TASKS.md` (slices `S1-22A` / `S1-22B` / `S1-22C`)
3. `docs/exports/taskforgema.md` — **Action0 / Action1 / Action2** contract + operator gate (`Action1 ACCEPT`, `Action0 now`, `Action2 now`)
4. `data/source_registry.json` — `legal_mode`, `risk_mode`, `access_mode`, `primary_url` per source
5. `agent-skills/openclaw-ollama-gemma4/SKILL.md` — OpenClaw + scrape narration rules
6. `agent-skills/reporter/SKILL.md` + `docs/openclaw/reporter-agent-instructions.md` — **reporter** role: 5-minute Telegram cadence (`ACTION1_TG_INTERVAL_SEC=300`), file-backed stats only
7. `docs/openclaw/action1-multi-agent.md` — triad roles (Gemma / Qwen / DeepSeek), **defined only in Markdown** in this repository
8. `docs/openclaw/OLLAMA_MODEL_ESCALATION.md` — **default Gemma4**; when to hand off to **Qwen3** (code) or **DeepSeek** (reasoning)
9. `docs/openclaw/scrape-taxonomy-a1-a12.md` — **Action1 = code bucket A1** (same seven keys); **A12** Patterned non-A1 (Action2 batch); concurrency env + metrics + DB alignment
10. `docs/openclaw/OPENCLAW_S_AND_M_AGENT.md` — S&M monitor/intelligence role; tier-3/tier-4 ownership and Action1 monitor boundaries

**Do not** ask the operator to “re-provide” listing URLs or CSS patterns for the seven Action1 sources. Discovery and parsers live in the codebase (`Makefile` `scrape-all-full`, `src/bgrealestate/`, `scripts/`). Your job is to **read** the files above and **run** the approved Make targets after `Action1 ACCEPT`, not to invent a parallel “deep-scraper”.

## Action1 — seven sources and registry `primary_url`

| # | `source_name` (registry) | `primary_url` | Typical scraped JSON dir |
|---|--------------------------|---------------|---------------------------|
| 1 | Address.bg | https://address.bg/ | `data/scraped/address_bg/listings/` |
| 2 | BulgarianProperties | https://www.bulgarianproperties.bg/ (registry; scraper list/detail routes use **bulgarianproperties.com**) | `data/scraped/bulgarianproperties/listings/` |
| 3 | Homes.bg | https://www.homes.bg/ | `data/scraped/homes_bg/listings/` |
| 4 | imot.bg | https://www.imot.bg/ | `data/scraped/imot_bg/listings/` |
| 5 | LUXIMMO | https://www.luximmo.bg/ | `data/scraped/luximmo/listings/` |
| 6 | property.bg | https://www.property.bg/ | `data/scraped/property_bg/listings/` |
| 7 | SUPRIMMO | https://www.suprimmo.bg/ | `data/scraped/suprimmo/listings/` |

## Four buckets (screen categories)

Every source must be attempted (subject to registry gates) for:

- `buy_personal`
- `buy_commercial`
- `rent_personal`
- `rent_commercial`

## Execution (after operator sends `Action1 ACCEPT`)

- **Live HTML/media harvest** runs on the host via **`make scrape-all-full`** (Python `bgrealestate`, not OpenClaw). OpenClaw/Gemma narrates, reports to Telegram, and can trigger Make — it does not replace the scraper process.
- **Scope:** Action1 is **exactly** the seven portals in the table above — same as code bucket **A1** (`docs/openclaw/scrape-taxonomy-a1-a12.md`). Do **not** add **A12** Patterned sources (alo.bg, Bazar.bg, Domaza, Home2U, OLX.bg, Yavlena) to Action1 unless the operator explicitly redefines scope; those belong to **Action2** after QA.
- **Detective fix (2026-05):** when you pass **`--sources Name1,Name2,...`** to `scrape-all-full`, those portals are **always** scheduled — they are **not** intersected with `tier12-pattern-status.json` “Patterned” rows (previously a lagging pattern file could silently drop a listed source). Use explicit names for Action1’s seven portals.
- **Full seven-source run without an early “already have 100” skip**: `make action1-scrape-full-uncapped` (exports default concurrency env vars; `--parallel-sources 7`; `--target-per-source 0`; still bounded by `--max-pages` / `--max-waves` per source until the runner stalls). Log: `data/runs/action1_scrape_uncapped_*.log`.
- **Backfill direction:** the Action1 uncapped runner exports `SCRAPER_PAGE_ORDER=oldest_first`. This processes older pages first within each scanned window and then widens by waves. Treat this as the current resume/backfill method unless a source-specific chronological cursor is implemented and tested.
- **Completion rule:** do **not** say Action1 is complete only because the runner stopped or a source exceeded 100 files. Completion requires `data_analyst`/debugger evidence: accepted-good vs `LOST` vs grouped/development vs inactive, media/full-gallery, description, source/bucket, and parser-warning counts for all seven sources × four buckets.
- **Smaller smoke / gate runs**: `make scrape-all-full EXTRA_ARGS="--target-per-source 100 ..."` as in `docs/exports/taskforgema.md`.
- **Bounded detail concurrency (A1):** optional overrides `SCRAPER_CONCURRENCY_A1`, `SCRAPER_CONCURRENCY_A12`, `SCRAPER_CONCURRENCY_OTHER` — see `src/bgrealestate/scraping/source_class.py`. Per-source run metrics: **`data/runs/scrape_metrics.jsonl`** + **`data/runs/scrape_metrics_latest.json`**.
- Progress to Telegram: every **+100** net new listing JSON files across those seven dirs — `make action1-checkpoint-notify EXTRA_ARGS='--send --profile codex --target 181488201'` or `make action1-telegram-report` + `openclaw message send`.
- **RUNNING-style snapshot report** (emoji header + property_category + per-source img/word stats): `make action1-running-report` or `python3 scripts/action1_full_telegram_report.py --running-line` (optional `--write-snapshot` to persist deltas in `data/runs/action1_last_running_snapshot.json`).
- **Periodic RUNNING reports while a long scrape runs** (default **300s**): `make action1-telegram-watch` (loop: running-line + OpenClaw Telegram); override interval with **`ACTION1_TG_INTERVAL_SEC`**. Detached watcher uses **`ACTION1_TG_FULL_TIMEOUT_SEC`** (default **240s**) for the full `--running-line` scan; if the corpus is too large it falls back to **`--pulse`** (glob-only counts) so Telegram never goes silent — raise the timeout on the host for full bad/good stats every tick.
- **OpenClaw template (structure + bullets):** `docs/openclaw/action1-running-report-template.md` — Gemma/OpenClaw must mirror this layout when reporting Action1; data comes only from the script above.
- **Ping OpenClaw to continue Action1** after Codex changes: `make action1-openclaw-continue` (Telegram send + continue instructions; use `DRY_RUN=1` to preview).
- **Reliable Telegram rehydration** (when the model loses thread context): `make action1-telegram-ops-rehydrate` — posts hard rules + compact **preflight** (TASKS grep + watcher tail + JOURNEY tail) + compact metrics via `openclaw message send`. Disable preflight with **`ACTION1_REHYDRATE_PREFLIGHT=0`** if the message is too long. **Why “memory” drops:** see `docs/openclaw/memory-context-and-operational-failures.md`. **Host snapshot:** `make openclaw-preflight`. Inbound Telegram agent id remains **`action1_gemma`** in `~/.openclaw-codex/openclaw.json`; the **Ollama model** for that id is configured there (operator currently uses **`ollama/qwen3-coder:30b`** for ops chat).
- **OpenClaw scrape skills:** the same `openclaw.json` entry lists **repo** `agent-skills/` paths (browser/hybrid/managed scrape stack, connector builder, parser QA, media pipeline, registry, OpenClaw pack). Symlinks also exist under `~/.openclaw/agents/gemma4_re_bulg/agent/skills/` for tools that scan that tree.
- **S&M role:** if the operator says OpenClaw should act as S&M, read `docs/openclaw/OPENCLAW_S_AND_M_AGENT.md`. S&M may monitor Action1, prepare reports, and route bounded fixes to Qwen, but it must not widen Action1 beyond A1 or start tier-3/tier-4 live collection without the proper gates.
- **Database:** after scrape milestones, disk remains canonical until **`make import-scraped`** with **`DATABASE_URL`** — do not claim DB totals match file counts without import (see taxonomy doc).
- **Quality gate after every Action1 batch:** run `python3 scripts/action1_dataset_quality_gate.py --output docs/exports/action1-dataset-quality-gate-dryrun.json` for full local QA when time allows. For smoke/debugger checks use `--limit-per-source 20`. Rows marked `LOST`, `GROUPED_PUBLICATION`, `source_publication_type=multi_unit_or_development`, or inactive/removed/expired must not be imported or exposed as accepted properties.
- **Import/export safety:** default `python3 scripts/import_scraped_listings.py --dry-run` and `python3 scripts/generate_frontend_scraped_listings.py` exclude `LOST`, grouped/development, and inactive rows. Use `--include-lost`, `--include-grouped`, or `--include-inactive` only for investigation, not production canonicalization.
- **Pattern proof safety:** `docs/exports/tier12-pattern-status.*` must be regenerated only from QA-eligible samples. Do not call a source `Patterned` from a `LOST`, grouped/development, or inactive sample.

### OpenClaw CLI must write outside the repo

Telegram sends run `openclaw message send`, which writes plugin/runtime locks under **`~/.openclaw-codex/`**. Restricted environments (e.g. Cursor agent sandbox) return **`EPERM`** on `mkdir` there — sends fail with `PluginLoadFailureError`. **Run the report monitor from Terminal.app / iTerm** on the Mac (full permissions), or use **`scripts/action1_launch_report_monitor.sh`** after `openclaw gateway probe` shows reachable.

## Misconfiguration symptom (fixed 2026-04-29)

If OpenClaw **`main`** uses workspace `~/.openclaw/workspace-codex`, it **cannot** see this repo and may hallucinate “missing Action1 docs”. **`main` must use this repo as `workspace`** in `~/.openclaw-codex/openclaw.json`.

## Triad roles (text-only)

Same channel, three models — see **`docs/openclaw/action1-multi-agent.md`**: Gemma = orchestration / description / management; Qwen = coding / automation; DeepSeek = reasoning / heavy logic. No external image file is required or referenced by the repo for these roles.
