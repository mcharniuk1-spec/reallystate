## OpenClaw operator pack (Codex + Gemma4 + Claude)

This folder documents how to run this repo using **OpenClaw** with:

- **Codex**: implementation agent (edits repo, runs commands, fixes tests).
- **Gemma4 via Ollama**: local/offline assistant for *data QA, summarization, extraction, report generation*, and other tasks where you prefer a local model.
- **Claude**: later planning/refactor agent (long-context design review, architecture).

This pack is designed to preserve project guardrails in `AGENTS.md` and the execution queue in `docs/agents/TASKS.md`.

### What to read first

- `AGENTS.md` (guardrails and stop conditions)
- `docs/agents/TASKS.md` (what to do next)
- `docs/docker-and-database.md` (Docker/Postgres/MinIO/Temporal + media)
- `docs/openclaw/gemma4-agent.md` (Gemma4 role, constraints, prompts)
- `docs/exports/reporting-and-instruction-index.md` (current DOCX/reporting pack)
- `docs/exports/taskforgema.md` (current Gemma4 scrape/image-description task)

### Baseline local runtime (host machine)

OpenClaw agents can run project commands, but the host must provide prerequisites:

- Docker Desktop (macOS/Windows) or Docker Engine (Linux)
- Python 3.12+ (or use `make test-docker`)
- Node.js for Next.js UI (if running the frontend)

Standard dependency start:

```bash
make dev-up
make dev-ready
export DATABASE_URL='postgresql+psycopg://bgrealestate:bgrealestate@localhost:5432/bgrealestate'
make db-init
```

### OpenClaw + Ollama preflight (required for Gemma4)

Before running Action0/1/2 via OpenClaw, verify all of these:

```bash
openclaw --profile codex gateway probe
openclaw --profile codex channels status
ollama list | grep -i gemma4
```

If agent turns stall or return “couldn’t generate a response”, it is usually an Ollama timeout. Fix by increasing the provider timeout and restarting the gateway:

```bash
openclaw --profile codex config set models.providers.ollama.timeoutSeconds 3600
openclaw --profile codex gateway restart
openclaw --profile codex gateway probe
```

### Recommended division of labor

- **Codex**:
  - Connectors, parsers, DB importers, Temporal workers, Makefile targets.
  - Any changes that require code edits, tests, or refactors.

- **Gemma4 (Ollama)**:
  - Purely local tasks: summarizing scrape logs, validating extracted JSON, generating SQL queries, generating Markdown/JSON “image report” drafts *from already-local inputs*.
  - Must not do risky compliance decisions; must defer to `data/source_registry.json` + `AGENTS.md`.
  - Current action order (**operator gate 2026-04-30**):
    - Always **read** Action0+1+2 together from `docs/exports/taskforgema.md` so the agent never asks for ad-hoc URLs/patterns.
    - **Execute Action1 first** only after the operator sends **`Action1 ACCEPT`**. While Action1 runs, send Telegram every **+100** net new saves with a **7×4** matrix (`make action1-matrix-snapshot`).
    1. **Action1 / S1-22B**: seven-source all-Bulgaria scrape/backfill for `Address.bg`, `BulgarianProperties`, `Homes.bg`, `imot.bg`, `LUXIMMO`, `property.bg`, and `SUPRIMMO` across the four buckets.
    2. **Action0 / S1-22A**: image-description and property-QA reports from `docs/exports/s1-21-gemma-action0-eligible.json`; no live scrape — only after **`Action0 now`** (unless waiver in `JOURNEY.md`).
    3. **Action2 / S1-22C**: remaining legal tier-1/2 sources — only after **`Action2 now`** + Action1 QA.
  - For every apartment/property item, describe images one by one and produce a grouped property QA report with style, visual condition, layout/planning evidence, visible tools/equipment, colors, requirements, source links, and uncertainty flags.

- **Claude** (later):
  - Planning documents, larger refactor proposals, multi-file architecture reasoning.

### Action0 / Action1 / Action2 (operator entry points)

The authoritative contract for all three actions is `docs/exports/taskforgema.md`. The task slices and acceptance gates also exist inside `docs/agents/TASKS.md` under `S1-22A` / `S1-22B` / `S1-22C`.

- **Action0**: `S1-22A` — local gallery reports only (no live scraping); operator **`Action0 now`**
- **Action1**: `S1-22B` — live all-Bulgaria scrape/backfill for 7 sources × 4 buckets; operator **`Action1 ACCEPT`**
- **Action2**: `S1-22C` — expand to remaining legal tier-1/2 sources; operator **`Action2 now`** after Action1 QA

When you want OpenClaw to post progress updates to Telegram, use chat id `181488201` and the CLI delivery pattern:

```bash
openclaw --profile codex message send --channel telegram --target 181488201 --message "update text" --json
```
