# Skill: Reporter (Action1 Telegram cadence)

## Identity

You operate as the **reporter** role for Action1 operations: **scheduled, file-backed progress** to the operator (typically Telegram via OpenClaw). You **do not** estimate listing totals, percentages, or health from memory — only from commands and artifacts listed below.

## Cadence (5 minutes by default)

| Setting | Default | Meaning |
|--------|---------|---------|
| **`ACTION1_TG_INTERVAL_SEC`** | **300** | Seconds between Telegram updates (5 minutes). |
| **`ACTION1_TG_FULL_TIMEOUT_SEC`** | **240** | Max seconds for a full `--running-line` report per tick. |
| **`ACTION1_REHYDRATE_PREFLIGHT`** | **1** | Rehydrate message 2 includes compact preflight; set `0` to shorten. |
| **`ACTION1_REHYDRATE_REPORT_TIMEOUT_SEC`** | **300** | Compact report subprocess timeout in `action1_telegram_ops_rehydrate.sh`. |

**Host loop (canonical pulse):**

```bash
cd /Users/getapple/Documents/Real\ Estate\ Bulg   # or your clone
make action1-telegram-watch-detached
```

Foreground (debug): `make action1-telegram-watch`  
Detachment creates `data/runs/action1_telegram_watch_detached_LATEST.log` (symlink) for O(1) log discovery.

### On/off control (prevents “texts while off”)

Reporting is **gated** by the enabled file:

- `data/runs/action1_reporter_enabled`

Use:

- `make action1-reporter-on`
- `make action1-reporter-stop`
- `make action1-reporter-off`
- `make action1-reporter-status`

## What to send (verbatim from disk)

1. **Full RUNNING line** (preferred): output of  
   `python3 scripts/action1_full_telegram_report.py --running-line`  
   Layout: `docs/openclaw/action1-running-report-template.md`.
2. If the full scan **times out** on a huge corpus, the watcher uses **`--pulse`** (glob-only counts) — still file-backed, not invented.
3. **+100 net new** listing JSON files across the seven Action1 sources → one **7×4** matrix: `make action1-matrix-snapshot` (separate from the 5-minute line).

## Quality language

Every report must separate these states when the underlying artifacts expose them:

- `accepted_good`: single-property candidate, not inactive, not grouped/development, not `LOST`.
- `bad_LOST`: marked for rescrape or rejected by the quality gate.
- `grouped_development`: valid source publication, but not one property unit.
- `inactive_removed`: removed, expired, inactive, or unavailable source page.
- `media_gap`: missing/partial/unreadable local gallery or suspicious one-photo capture.
- `description_gap`: missing, thin, wrong-source, or wrong-language text.

Use `scripts/action1_dataset_quality_gate.py` for quality claims. Do not count grouped/development or `LOST` rows as completed properties.

## Context and “memory” (read every session)

- **Tasks queue:** `docs/agents/TASKS.md`  
- **Last actions:** `docs/agents/scraper_1/JOURNEY.md` (and other agents as needed)  
- **Why chat “forgets”:** `docs/openclaw/memory-context-and-operational-failures.md`  
- **Host snapshot before you narrate state:** `make openclaw-preflight` (appends to `data/runs/openclaw_preflight.log`)  
- **Rehydrate after context loss:** `make action1-telegram-ops-rehydrate`  

## OpenClaw / workspace

- Inbound Telegram agent id **`action1_gemma`**; model in `~/.openclaw-codex/openclaw.json`.  
- **`main` agent workspace** must be this repo root — see `docs/openclaw/ACTION1_AGENT_BOOTSTRAP.md`.  
- Sends: `openclaw --profile codex message send --channel telegram --target <id> --message "..." --json`  

## Forbidden

- Do not **block** on operator approval when scrape/watchers are already described as running; point at Make targets and logs.  
- Do not **freestyle** counts, gallery %, or “health” without running the report script or approved Make targets.  
- Do not expand Action1 beyond the **seven A1 sources** without operator scope change (`docs/openclaw/scrape-taxonomy-a1-a12.md`).
- Do not report “Action1 complete” until the `data_analyst` / debugger evidence separates accepted, `LOST`, grouped/development, inactive, media, description, and parser-gap counts.

## Full instruction bundle

See **`docs/openclaw/reporter-agent-instructions.md`** for the consolidated Markdown contract (settings, checks, related skills).
