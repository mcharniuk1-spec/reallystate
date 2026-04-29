# Skill: OpenClaw Ollama Gemma4 (orchestrated QA + gated live scrape narration)

## When to use

Use this skill when the operator runs **OpenClaw** with **Gemma4 via Ollama** for:

- **Offline/local**: QA, summarization, SQL drafting, image-report drafting from **local files only** (`data/media/`, `docs/exports/`).
- **Gated live scrape narration**: Action1 (`S1-22B`) after the operator posts **`Action1 ACCEPT`**, with **Telegram progress** on a fixed cadence.

## Hard constraints (non-negotiable)

- Follow `AGENTS.md` guardrails.
- Treat `data/source_registry.json` as authoritative for `legal_mode`, `risk_mode`, and `access_mode`.
- Do **not** add live-network dependencies to tests.
- Do **not** propose private social/messenger scraping.
- Do **not** handle secrets beyond “set env var locally”.
- **Never** ask the operator for new “target URLs / CSS patterns” for the seven Action1 sources — patterns live in `scripts/live_scraper.py`, `src/bgrealestate/scraping/`, and exports; read `docs/exports/taskforgema.md` instead.

## Operator acceptance gate (2026-04-30)

1. **Always load** Action0 + Action1 + Action2 from `docs/exports/taskforgema.md` in the prompt context.
2. **Do not execute** shell/Make steps that mutate `data/scraped/` or `data/media/` until **`Action1 ACCEPT`**.
3. **After `Action1 ACCEPT`**: run Action1 per `docs/agents/TASKS.md` (`make scrape-all-full`, prefer detached/`nohup` on hosts that SIGTERM interactive runners).
4. **Telegram**: after every **+100 net new** listing JSON saves across the seven Action1 sources, send **one** Telegram message with a **7 sources × 4 buckets** matrix (counts + full-gallery % + avg description chars when available) and top errors. Host shortcut: `make action1-matrix-snapshot`.
5. **Action0**: only after operator **`Action0 now`** (no Action0 file writes before then unless `docs/agents/scraper_1/JOURNEY.md` documents a waiver).
6. **Action2**: only after operator **`Action2 now`** + Action1 QA.

## Standard workflows

### A) Offline scrape-status summary (Markdown)

Must include: artifact timestamp, top sources by count, low full-gallery warnings, next `make` command from existing targets only.

### B) SQL validation bundle

Read-only queries for `canonical_listing` by source and media completion — only when DB access is in scope.

### C) Image report draft (Action0)

Only local images. Include `single_property_ok`, `single_property_comment`, `mismatch_notes` per `docs/exports/taskforgema.md`.

### D) Ollama timeouts

If the model idles out: `openclaw --profile codex config set models.providers.ollama.timeoutSeconds 3600` then restart gateway (see `docs/openclaw/README.md`).
