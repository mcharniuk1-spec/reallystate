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

### Recommended division of labor

- **Codex**:
  - Connectors, parsers, DB importers, Temporal workers, Makefile targets.
  - Any changes that require code edits, tests, or refactors.

- **Gemma4 (Ollama)**:
  - Purely local tasks: summarizing scrape logs, validating extracted JSON, generating SQL queries, generating Markdown/JSON “image report” drafts *from already-local inputs*.
  - Must not do risky compliance decisions; must defer to `data/source_registry.json` + `AGENTS.md`.
  - Current order is fixed: Action0 property image reports from `docs/exports/s1-21-gemma-action0-eligible.json`, then Action1 seven-source full scrape/backfill, then Action2 remaining legal tier-1/2 sources.
  - For Action1, focus on `Address.bg`, `BulgarianProperties`, `Homes.bg`, `imot.bg`, `LUXIMMO`, `property.bg`, and `SUPRIMMO` across buy residential, buy commercial, rent residential, and rent commercial.
  - For every property item, describe images one by one and produce a grouped property QA report with style, visual condition, layout/planning evidence, visible tools/equipment, colors, requirements, source links, same-location status, and uncertainty flags.

- **Claude** (later):
  - Planning documents, larger refactor proposals, multi-file architecture reasoning.
