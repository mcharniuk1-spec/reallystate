# Skill: OpenClaw Ollama Gemma4 (orchestrated QA + gated live scrape narration)

## When to use

Use this skill when the operator runs **OpenClaw** with **Gemma4 via Ollama** for:

- **Offline/local**: QA, summarization, SQL drafting, image-report drafting from **local files only** (`data/media/`, `docs/exports/`).
- **Gated live scrape narration**: Action1 (`S1-22B`) after the operator posts **`Action1 ACCEPT`**, with **Telegram progress** on a fixed cadence.
- **Triad (three local models)**: role split is **text-only** in `docs/openclaw/action1-multi-agent.md` — Gemma/Gamma = orchestration / description / management; **Qwen 3 Coder 30B = primary coding and automation model**; DeepSeek = reasoning / heavy logic. No repo image file defines roles. **Telegram peer routes to agent id `action1_gemma`;** the **actual Ollama model** for that id is set in `~/.openclaw-codex/openclaw.json` (this deployment uses **`ollama/qwen3-coder:30b`** for ops chat). Escalate per `docs/openclaw/OLLAMA_MODEL_ESCALATION.md`.

## Hard constraints (non-negotiable)

- Follow `AGENTS.md` guardrails.
- Treat `data/source_registry.json` as authoritative for `legal_mode`, `risk_mode`, and `access_mode`.
- Do **not** add live-network dependencies to tests.
- Do **not** propose private social/messenger scraping.
- Do **not** handle secrets beyond “set env var locally”.
- **Never** ask the operator for new “target URLs / CSS patterns” for the seven Action1 sources — patterns live in `scripts/live_scraper.py`, `src/bgrealestate/scraping/`, and exports; read `docs/exports/taskforgema.md` and `docs/openclaw/scrape-taxonomy-a1-a12.md` (Action1 = A1 keys; do not mix A12 sources into Action1 without operator scope change).
- **OpenClaw `main` workspace**: must be the repo root `/Users/getapple/Documents/Real Estate Bulg` (see `docs/openclaw/ACTION1_AGENT_BOOTSTRAP.md`). If `main` uses `~/.openclaw/workspace-codex`, the model cannot read project files and may falsely claim Action1 docs are missing.
- **S&M scope**: if acting as S&M, also read `docs/openclaw/OPENCLAW_S_AND_M_AGENT.md`. S&M owns tier-3/tier-4 intelligence overlays and Action1 monitoring support; it does not own A1 source expansion.

## Operator acceptance gate (2026-04-30)

1. **Always load** Action0 + Action1 + Action2 from `docs/exports/taskforgema.md` in the prompt context.
2. **Do not execute** shell/Make steps that mutate `data/scraped/` or `data/media/` until **`Action1 ACCEPT`**.
3. **After `Action1 ACCEPT`**: run Action1 per `docs/agents/TASKS.md` (`make scrape-all-full`, prefer detached/`nohup` on hosts that SIGTERM interactive runners). **Live scrape scope = seven A1 portals only** — not Patterned A12 sources (alo.bg, Bazar.bg, …) until **`Action2 now`** (`docs/openclaw/scrape-taxonomy-a1-a12.md`).
4. **Telegram**: after every **+100 net new** listing JSON saves across the seven Action1 sources, send **one** Telegram message with a **7 sources × 4 buckets** matrix (counts + full-gallery % + avg description chars when available) and top errors. Host shortcut: `make action1-matrix-snapshot`.
5. **Quality gate**: after every Action1 batch, run `python3 scripts/action1_dataset_quality_gate.py --output docs/exports/action1-dataset-quality-gate-dryrun.json` when full local QA is practical, or add `--limit-per-source 20` for smoke checks. Treat `LOST`, grouped/development, and inactive rows as blocked from import/frontend exposure unless explicitly investigating.
6. **Backfill order**: Action1 continuation uses `SCRAPER_PAGE_ORDER=oldest_first make action1-scrape-full-uncapped`. This is oldest-first within each scanned pagination window, then wider repeated waves; if exact source-native chronological cursors exist, implement them as source-specific Qwen tasks before claiming perfect old-to-new completion.
7. **Action0**: only after operator **`Action0 now`** (no Action0 file writes before then unless `docs/agents/scraper_1/JOURNEY.md` documents a waiver).
8. **Action2**: only after operator **`Action2 now`** + Action1 QA.

## Session continuity and explicit step logging

The model **does not** persist tasks between turns unless they live in **files**. Treat chat as volatile.

**At the start of a substantive reply (especially after reconnect / rehydrate):**

1. State **repo root** (`/Users/getapple/Documents/Real Estate Bulg`) and confirm OpenClaw **`main` workspace** matches it (`docs/openclaw/ACTION1_AGENT_BOOTSTRAP.md`).
2. **Read** `docs/agents/TASKS.md` for the current slice; **read** the owning `docs/agents/<agent>/JOURNEY.md` tail for what was last done.
3. For metrics or progress claims, **do not improvise** — use host output of `python3 scripts/action1_full_telegram_report.py --running-line` or `--pulse` if timeboxed (`docs/openclaw/action1-running-report-template.md`).

**Log format when narrating steps (include in reply or JOURNEY):**

- `STEP` — what you did (e.g. “read TASKS”, “ran matrix snapshot”).
- `ARTIFACT` — path or command.
- `RESULT` — one line outcome (ok / timeout / blocked).

**Problem-shaped verification (do not skip when the user’s issue matches):**

| User symptom | Check |
|----------------|--------|
| Wrong URLs / “missing Action1 doc” | Workspace path + `docs/openclaw/ACTION1_AGENT_BOOTSTRAP.md` |
| Empty or missing stats | Report timeout / corpus size — `--pulse`, logs under `data/runs/action1_telegram_watch_detached_*.log` |
| Task confusion | `docs/agents/TASKS.md` + relevant `JOURNEY.md` |
| Illegal extra sources | `data/source_registry.json`, Action1 = A1 only until Action2 gate |
| S&M confusion | `docs/openclaw/OPENCLAW_S_AND_M_AGENT.md`; tier-3/tier-4 intelligence is not A1 marketplace scraping |

Operator shortcut for a host snapshot: `make openclaw-preflight` (full log in `data/runs/openclaw_preflight.log`). Telegram rehydrate (`make action1-telegram-ops-rehydrate`) prepends a **compact** preflight block unless `ACTION1_REHYDRATE_PREFLIGHT=0`.

**5-minute scheduled reporting:** assign the **`reporter`** skill — `agent-skills/reporter/SKILL.md` and `docs/openclaw/reporter-agent-instructions.md` (defaults: `ACTION1_TG_INTERVAL_SEC=300`, watcher `make action1-telegram-watch-detached`).

## Standard workflows

### A) Offline scrape-status summary (Markdown)

Must include: artifact timestamp, top sources by count, low full-gallery warnings, next `make` command from existing targets only.

### B) SQL validation bundle

Read-only queries for `canonical_listing` by source and media completion — only when DB access is in scope.

### C) Image report draft (Action0)

Only local images. Include `single_property_ok`, `single_property_comment`, `mismatch_notes` per `docs/exports/taskforgema.md`.

### D) Ollama timeouts

If the model idles out: `openclaw --profile codex config set models.providers.ollama.timeoutSeconds 3600` then restart gateway (see `docs/openclaw/README.md`).
