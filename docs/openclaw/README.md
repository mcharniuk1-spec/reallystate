## OpenClaw operator pack (Codex + Gemma4 + Claude)

This folder documents how to run this repo using **OpenClaw** with:

- **Codex**: implementation agent (edits repo, runs commands, fixes tests).
- **Gemma4 via Ollama**: local/offline assistant for *data QA, summarization, extraction, report generation*, and other tasks where you prefer a local model.
- **Claude**: later planning/refactor agent (long-context design review, architecture).

This pack is designed to preserve project guardrails in `AGENTS.md` and the execution queue in `docs/agents/TASKS.md`.

### Why “memory” and tasks seem to disappear

OpenClaw and the LLM do **not** automatically retain project state across sessions the way **git** does. Read **`docs/openclaw/memory-context-and-operational-failures.md`** (facts vs interpretations, workspace mistakes, timeouts vs forgetting).

Before debugging “lost context”, run on the host:

```bash
make openclaw-preflight
```

That appends a snapshot to `data/runs/openclaw_preflight.log` (TASKS grep, JOURNEY tails, latest Telegram watcher log, scrape metrics). Use `FOCUS=tasks`, `FOCUS=telegram`, or `PROBE=1` to narrow output.

### Reporter skill (5-minute Telegram cadence)

Use **`agent-skills/reporter/SKILL.md`** for the **reporter** role: default **`ACTION1_TG_INTERVAL_SEC=300`** (5 minutes), file-backed RUNNING lines, no freestyle counts. Full consolidated instructions: **`docs/openclaw/reporter-agent-instructions.md`**.

### What to read first

- `AGENTS.md` (guardrails and stop conditions)
- `docs/agents/TASKS.md` (what to do next)
- `docs/docker-and-database.md` (Docker/Postgres/MinIO/Temporal + media)
- `docs/openclaw/gemma4-agent.md` (Gemma4 role, constraints, prompts)
- `docs/openclaw/action1-multi-agent.md` (Action1: Gemma + Qwen + DeepSeek parallel roles, Telegram triad)
- `docs/openclaw/ACTION1_AGENT_BOOTSTRAP.md` (**mandatory** context: repo path, seven `primary_url`s, four buckets — stops “missing URLs/patterns” hallucinations)
- `docs/openclaw/scrape-taxonomy-a1-a12.md` (**Action1 = A1 keys**, **A12** Patterned non-A1, metrics, DB/file consistency)
- `docs/openclaw/action1-running-report-template.md` (**mandatory** Action1 Telegram/OpenClaw progress layout — must mirror `scripts/action1_full_telegram_report.py --running-line`)
- `docs/openclaw/memory-context-and-operational-failures.md` (why stats/tasks “vanish” — usually disk/workspace/timeout, not magic memory)
- `agent-skills/reporter/SKILL.md` + `docs/openclaw/reporter-agent-instructions.md` (**reporter** role: 5-minute cadence, settings, logs)
- `docs/openclaw/OLLAMA_MODEL_ESCALATION.md` (**Gemma first**, then Qwen for code, DeepSeek for deep logic)
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
