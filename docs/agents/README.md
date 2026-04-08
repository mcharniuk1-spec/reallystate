# Agent Coordination Protocol

This project uses **5 specialist agents** plus a lead agent. Each agent finds work in one place, logs progress in one place, and gets verified by another agent.

## Single source of truth

| What | Where |
|------|-------|
| **What to do next** (per agent) | `docs/agents/TASKS.md` |
| **Execution log** (append-only) | `docs/agents/<agent>/JOURNEY.md` |
| **Global guardrails** | `AGENTS.md` (repo root) |
| **Phase gates** | `PLAN.md` §9 + `AGENTS.md` §Phase Gates |
| **Bugbot review priorities** | `.cursor/BUGBOT.md` |
| **Skills (acceptance contracts)** | `agent-skills/<name>/SKILL.md` |

## Agents

| Agent | Role | Primary area |
|-------|------|--------------|
| `backend_developer` | Data engineer / backend structure | DB, APIs, persistence, orchestration |
| `scraper_1` | Marketplace website connectors | Tier-1/2 portal/classifieds/agency parsers |
| `scraper_sm` | Social/messenger overlays | Tier-4 Telegram/FB/IG/X; consent-gated |
| `ux_ui_designer` | Frontend, operator-first | `/admin`, `/listings`, `/map`, `/chat`, `/settings` |
| `debugger` | Cross-agent verification | Golden path, fixture regression, integration smoke |

## Dependency graph (who feeds whom)

```
backend_developer ──► debugger (verifies DB + API contracts)
       │
       ▼
scraper_1 ──────────► debugger (verifies fixtures + legal gates)
       │
       ▼
scraper_sm ─────────► debugger (verifies consent gates + redaction)
       │
       ▼
ux_ui_designer ─────► debugger (verifies UI against API contracts)
```

Concrete dependency chains:

1. **backend_developer** delivers DB migrations + API routes → **debugger** runs `make golden-path` + API smoke tests → passes or blocks.
2. **scraper_1** delivers connector + fixtures → **debugger** runs `make test` + checks legal gate enforcement → passes or blocks.
3. **scraper_sm** delivers social ingestion contract + fixtures → **debugger** verifies consent checklist + fixture redaction → passes or blocks.
4. **ux_ui_designer** delivers UI spec or component → **debugger** verifies API contract alignment + Playwright snapshot (when available) → passes or blocks.
5. **backend_developer** unblocks **scraper_1** (needs DB + ingest path ready before connectors persist).
6. **scraper_1** + **backend_developer** unblock **ux_ui_designer** (needs API data before UI pages).

## Lifecycle of a task slice

```
┌─────────────────────────────────────────────────────────┐
│  1. Lead agent writes slice in TASKS.md                 │
│     (agent, inputs, acceptance gate, outputs, verifier) │
├─────────────────────────────────────────────────────────┤
│  2. Assigned agent reads TASKS.md, picks their slice    │
├─────────────────────────────────────────────────────────┤
│  3. Agent implements; appends entry to own JOURNEY.md   │
│     (changed files, commands, tests, review comments)   │
├─────────────────────────────────────────────────────────┤
│  4. Agent marks slice "DONE — awaiting verification"    │
│     in TASKS.md                                         │
├─────────────────────────────────────────────────────────┤
│  5. Verifier agent (usually debugger) runs the          │
│     acceptance gate commands                            │
├─────────────────────────────────────────────────────────┤
│  6a. PASS → verifier appends entry to own JOURNEY.md    │
│     with "VERIFIED: <slice>" + updates TASKS.md status  │
│                                                         │
│  6b. FAIL → verifier appends JOURNEY.md with failure    │
│     details + blocker; original agent picks up fix      │
└─────────────────────────────────────────────────────────┘
```

## TASKS.md format (per slice)

Every slice in `docs/agents/TASKS.md` must have:

| Field | Required | Description |
|-------|----------|-------------|
| **Agent** | yes | Which specialist owns the slice |
| **Slice name** | yes | Short name for the work unit |
| **Status** | yes | `TODO` / `IN_PROGRESS` / `DONE_AWAITING_VERIFY` / `VERIFIED` / `BLOCKED` |
| **Read first** | yes | Files the agent must read before starting |
| **Do** | yes | What to implement/change |
| **Acceptance gate** | yes | Commands/tests that must pass |
| **Output** | yes | Artifacts produced (files, DB rows, exports) |
| **Verifier** | yes | Which agent runs the acceptance gate |
| **Depends on** | if any | Slice IDs that must be `VERIFIED` first |

## JOURNEY.md format (per entry)

Every entry appended to `docs/agents/<agent>/JOURNEY.md`:

```markdown
### YYYY-MM-DD — <slice name>

- **Action**: what was done
- **Changed files**: list
- **Commands run**: list
- **Tests run**: results summary
- **Status**: DONE / DONE_AWAITING_VERIFY / BLOCKED (reason)
- **Review comments**: what to improve, edge cases found, warnings for next agent
```

For **verification entries** (debugger or other verifier):

```markdown
### YYYY-MM-DD — VERIFY: <slice name> (agent: <original agent>)

- **Gate commands run**: list with results
- **Result**: PASS / FAIL
- **Failure details**: (if FAIL) what broke, suggested fix
- **Review comments**: observations for the original agent
```

## Cross-agent review rules

1. **No slice is complete until verified.** The `VERIFIED` status requires a verifier entry in both TASKS.md and the verifier's JOURNEY.md.
2. **Debugger is the default verifier** for all agents. Another agent may verify if explicitly assigned.
3. **Backend_developer verifies scraper_1** on DB persistence correctness (does the ingested record round-trip cleanly?).
4. **Scraper_1 verifies backend_developer** on API contract correctness (does the API return what connectors wrote?).
5. **Debugger verifies everyone** on safety gates: no live network in tests, legal mode enforcement, consent checklist for social, no secrets in fixtures.
6. **Blocked slices** must record the blocker in TASKS.md and the agent's JOURNEY.md. The blocker points to another agent's unfinished slice.
7. **Bugbot priorities** (`.cursor/BUGBOT.md`) apply to all verification: legal gates, SQL injection, auth/RBAC, idempotency, privacy leaks, media in Postgres, live-network tests.

## Quick reference for each agent

### backend_developer
- **Find tasks**: `docs/agents/TASKS.md` → section "Backend_developer"
- **Log work**: `docs/agents/backend_developer/JOURNEY.md`
- **Verified by**: debugger (golden path + API smoke), scraper_1 (API contracts)

### scraper_1
- **Find tasks**: `docs/agents/TASKS.md` → section "Scraper_1"
- **Log work**: `docs/agents/scraper_1/JOURNEY.md`
- **Verified by**: debugger (fixtures + legal gates), backend_developer (DB persistence)

### scraper_sm
- **Find tasks**: `docs/agents/TASKS.md` → section "Scraper_SM"
- **Log work**: `docs/agents/scraper_sm/JOURNEY.md`
- **Verified by**: debugger (consent checklist + redaction + fixture format)

### ux_ui_designer
- **Find tasks**: `docs/agents/TASKS.md` → section "UX_UI_designer"
- **Log work**: `docs/agents/ux_ui_designer/JOURNEY.md`
- **Verified by**: debugger (API contract alignment + component spec completeness)

### debugger
- **Find tasks**: `docs/agents/TASKS.md` → section "Debugger" + all `DONE_AWAITING_VERIFY` slices
- **Log work**: `docs/agents/debugger/JOURNEY.md`
- **Verified by**: lead agent (spot checks) or self-verify via `make validate` + `make golden-path`
