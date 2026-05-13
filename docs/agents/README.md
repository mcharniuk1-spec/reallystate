# Agent Coordination Protocol

This project uses a core execution team plus support agents. Each agent finds work in one place, logs progress in one place, and gets verified by another agent.

## Single source of truth

| What | Where |
|------|-------|
| **What to do next** (per agent) | `docs/agents/TASKS.md` |
| **Execution log** (append-only) | `docs/agents/<agent>/JOURNEY.md` |
| **Self-development architecture** | `docs/agents/SELF_DEVELOPMENT_ARCHITECTURE.md` |
| **Agent cadence and Plan B** | `docs/agents/AGENT_LOOP_AND_CADENCE.md` |
| **Role-specific instructions** | `docs/agents/roles/<agent>.md` |
| **Human operating manual** | `docs/operator/agent-team-operating-manual.md` |
| **Server/DB migration runbook** | `docs/runbooks/server-db-migration.md` |
| **MCP and skills setup** | `docs/integrations/mcp-and-skills-setup.md` |
| **Global guardrails** | `AGENTS.md` (repo root) |
| **Phase gates** | `PLAN.md` §9 + `AGENTS.md` §Phase Gates |
| **Bugbot review priorities** | `.cursor/BUGBOT.md` |
| **Skills (acceptance contracts)** | `agent-skills/<name>/SKILL.md` |

## Current execution wave (2026-04-29, **gate 2026-04-30**)

Read **`docs/agents/TASKS.md`** § *Current Gemma/OpenClaw execution order* for the full rules. Summary:

1. **`scraper_1` / Gemma4 OpenClaw Action1 (`S1-22B`)**: all-Bulgaria scrape/backfill for the seven priority sources across `buy_personal`, `buy_commercial`, `rent_personal`, and `rent_commercial` — **first execution after operator `Action1 ACCEPT`**. Telegram: **+100 net new saves → 7×4 matrix** (`make action1-matrix-snapshot`).
2. **`scraper_1` / Gemma4 OpenClaw Action0 (`S1-22A`)**: generate property image reports from `docs/exports/s1-21-gemma-action0-eligible.json` — **only after operator `Action0 now`** (unless waiver in `JOURNEY.md`). No live scrape.
3. **`scraper_1` / Gemma4 OpenClaw Action2 (`S1-22C`)**: remaining legal tier-1/2 expansion — **only after operator `Action2 now`** + Action1 QA notes.
4. **`debugger`**: verify each action output with `DBG-08`, including report completeness, media counts, source/bucket logs, and refreshed dashboards.
5. **Other agents**: only pick work that unblocks this sequence or fixes website/dashboard regressions.

**Detective / strategy index**: `docs/exports/detective-product-orchestration-2026-04-30.md`.

## Operator GO command protocol

Use one command per activation:

- `GO backend_developer`
- `GO data_analyst`
- `GO scraper_1`
- `GO scraper_sm` (S&M: tier-3 + tier-4 intelligence)
- `GO ux_ui_designer`
- `GO planner`
- `GO debugger`
- `GO all`

When `GO` is issued, each selected agent should run its current slice from `TASKS.md`, update JOURNEY, update TASKS status, and hand off for verification in the same execution window.

Debugger handoff rule:

- Every non-debugger agent run ends with a debugger handoff.
- The producing agent must either mark the slice `DONE_AWAITING_VERIFY` or `BLOCKED`, append its JOURNEY entry, and then queue the corresponding debugger verification task.
- Treat `debugger` as the default final step after every backend, scraper, and UX run unless the operator explicitly suspends verification.

Non-stop execution rule:

- Do not end work after a single slice if another unblocked slice exists for the same agent.
- Continue in sequence until blocked, no unblocked slice remains, or the operator says `END`.
- After each slice: update `TASKS.md` status, append JOURNEY entry, then immediately pick the next unblocked slice for that same agent.
- If there is no unblocked slice left, ask:
  - `Which <agent_name> task should I execute next?`
  - Example: `Which backend_developer task should I execute next?`

## Agents

| Agent | Role | Primary area |
|-------|------|--------------|
| `planner` | Plan/control-plane owner | Task queue reset, sequencing, dependencies, OpenClaw handoff clarity |
| `ops_release_manager` | Release and git owner | Safe staging, secret scan, commit/push, CI/deploy gates, rollback notes |
| `infra_db_operator` | Runtime and DB owner | Server bootstrap, PostgreSQL/PostGIS, backups/restores, count verification |
| `knowledge_context_agent` | Memory/docs owner | Wiki capture, insights, docs index, skill inventory |
| `backend_developer` | Backend engineer | DB, APIs, persistence, orchestration |
| `data_analyst` | Data quality analyst | Scraped corpus QA, inconsistency detection, source/bucket metrics, dashboard truth |
| `market_intelligence_analyst` | Market/rival analyst | Competitor/source behavior, pricing/supply signals, strategic recommendations |
| `user_analytics_agent` | Product telemetry analyst | Website event taxonomy, funnels, UX analytics dashboards |
| `scraper_1` | Marketplace website connectors | Tier-1/2 portal/classifieds/agency parsers |
| `scraper_sm` | **S&M scraper/monitor** | Tier-3 vendor/partner/official routes + tier-4 social/messenger overlays; consent/legal gated |
| `vision_media_agent` | Media evidence analyst | Gallery completeness, room/style/condition/equipment reports, image uncertainty |
| `entity_resolution_agent` | Property graph analyst | Duplicate candidates, source-publication to property matching, confidence thresholds |
| `ux_ui_designer` | Frontend, operator-first | `/admin`, `/listings`, `/map`, `/chat`, `/settings` |
| `debugger` | Cross-agent verification | Golden path, fixture regression, integration smoke |

`scraper_t3` is retained only as a historical log folder. New tier-3 work is assigned to `scraper_sm` under the **S&M** mission so there is one intelligence-overlay owner.

Before acting, every agent reads its own role file in `docs/agents/roles/`.

## Dependency graph (who feeds whom)

```
planner ────────────► debugger (verifies task/control consistency)
       │
       ▼
backend_developer ──► debugger (verifies DB + API contracts)
       │
       ▼
data_analyst ───────► debugger (verifies corpus metrics + QA claims)
       │
       ▼
scraper_1 ──────────► debugger (verifies tier-1/2 fixtures + legal gates)
       │
       ▼
scraper_sm ─────────► debugger (verifies tier-3 contracts + tier-4 consent gates)
       │
       ▼
ux_ui_designer ─────► debugger (verifies UI against API contracts)
       │
       ▼
ops_release_manager ─► debugger (verifies release hygiene when requested)
```

Concrete dependency chains:

1. **planner** delivers task/dependency order → **debugger** checks ownership and verifier clarity.
2. **backend_developer** delivers DB migrations + API routes → **debugger** runs `make golden-path` + API smoke tests → passes or blocks.
3. **data_analyst** delivers corpus QA and metric contracts → **debugger** verifies reproducibility and dashboard truth.
4. **scraper_1** delivers tier-1/2 connector + fixtures → **debugger** runs `make test` + checks legal gate enforcement → passes or blocks.
5. **scraper_sm / S&M** delivers tier-3/tier-4 intelligence contracts + fixtures → **debugger** verifies contract/legal/consent gates + redaction → passes or blocks.
6. **ux_ui_designer** delivers UI spec or component → **debugger** verifies API contract alignment + Playwright snapshot (when available) → passes or blocks.
7. **backend_developer** unblocks **scraper_1** and **S&M** where persistence is required.
8. **scraper_1** + **backend_developer** + **data_analyst** unblock **ux_ui_designer** data-truth surfaces.
9. **infra_db_operator** unblocks remote DB-backed imports, count verification, and server runtime.
10. **market_intelligence_analyst** and **user_analytics_agent** feed product/UX decisions through planner, not directly into code.
11. **vision_media_agent** and **entity_resolution_agent** run after accepted source-publication/media evidence exists.

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
│  4b. Agent queues debugger follow-up for the run end    │
│      (or documents why verification is deferred)        │
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
6. **Each non-debugger run must produce a debugger follow-up**: either a completed verification pass or an explicit deferral reason in `docs/agents/debugger/JOURNEY.md`.
7. **Blocked slices** must record the blocker in TASKS.md and the agent's JOURNEY.md. The blocker points to another agent's unfinished slice.
8. **Bugbot priorities** (`.cursor/BUGBOT.md`) apply to all verification: legal gates, SQL injection, auth/RBAC, idempotency, privacy leaks, media in Postgres, live-network tests.

## Scraping stage ownership and runtime strategy

### scraper_1 (tier-1 + tier-2)

- Owns all tier-1 and tier-2 web sources.
- Runtime policy: HTTP/API parser first, Playwright only where JS rendering or anti-bot behavior blocks reliable extraction.
- Must keep fixture-first tests and no live-network dependency in tests.
- Website readiness rule:
  - `Patterned` means the repo has a saved code path for discovery + detail parsing on that source and at least one saved sample item proves full detail capture with description, core commercial and location fields, at least two structured fields, and the full reachable gallery saved as local image files.
  - If that proof is incomplete, use an explicit `without ...` status naming the missing capability, for example `without_full_gallery_capture`, `without_live_count_method`, or `without_sample_product_capture`.
- Incremental runtime rule:
  - scraper_1 should prefer a repeating incremental cycle over one-off dumps: append newly seen listings, refresh changed ones, and mark missing listings inactive.
  - The default operator cadence for patterned tier-1/2 sources is every 15 minutes when automation is enabled.
 - Metrics reporting rule:
   - after each scrape action, recount and persist source metrics using the latest saved website-total evidence for that source
   - operator-facing metrics must distinguish:
     - `scraped_started`: saved item rows out of latest saved website-total count
     - `scraped_full`: fully parsed item rows out of saved item rows
     - `description_coverage`: item rows with description out of saved item rows
     - `image_capture`: saved local images out of discovered remote images, plus average local images per item
     - `image_description_coverage`: described/analyzed images out of saved local images
   - do not replace source-total coverage with temporary thresholds such as `100` in operator dashboards unless the view is explicitly a threshold-only control panel

### data_analyst (scraped corpus QA)

- Owns source/bucket metrics truth, accepted-vs-bad classification, file-vs-DB reconciliation, and dashboard denominator correctness.
- Must separate accepted properties from `LOST`, grouped/development, inactive/removed, media-gap, description-gap, and parser-gap rows.
- Does not silently delete rows; uses quality-gate fields, exports, and rescrape queues.

### scraper_sm / S&M (tier-3 + tier-4 intelligence)

- Owns tier-3 partner/vendor/official routes and tier-4 Telegram/X/Facebook/Instagram/Threads/Viber/WhatsApp overlays.
- Must not implement unauthorized scraping for Airbnb/Booking/Vrbo or private social/messenger surfaces.
- Uses contract-required adapters, licensed-data imports, official/manual routes, public/consent-gated APIs, redaction, and legal checks before persistence.
- Tracks lead-intelligence signals separately from canonical marketplace listing ingestion.
- May monitor Action1/OpenClaw state but must not widen A1 marketplace scope.

### scraper_t3 (historical)

- Historical JOURNEY only after the 2026-05-05 reset.
- New tier-3 work belongs to S&M.

## Dashboard refresh rule

Whenever TASKS/JOURNEY/docs change in a run, refresh dashboard outputs before closeout:

- `make dashboard-doc` → writes `docs/dashboard/index.html`, `docs/exports/progress-dashboard.json`, `docs/exports/parallel-execution-timeline.md`, `docs/exports/scraper-activity-snapshot.md`

## Web and architecture skill usage

For architecture and web-delivery work, prefer these local skills:

- `software-architecture`
- `subagent-driven-development`
- `claude-opus-planner`
- `wordpress-development`
- `web-frontend-nextjs`
- `dashboard-visual-ops`
- `web-performance-accessibility`

Data/research support skills:

- `deep-research-workflow`
- `postgres-analysis`

When Claude is the planner path, use Opus-level planning when available, then dispatch implementation slices to specialist agents.

## Quick reference for each agent

### planner
- **Find tasks**: `docs/agents/TASKS.md` → section "PLANNER"
- **Log work**: `docs/agents/planner/JOURNEY.md`
- **Verified by**: debugger (task consistency + dependency clarity)
- **Skills**: `software-architecture`, `subagent-driven-development`, `multi-agent-patterns`, `context-engineering`, `prompt-engineering`

### backend_developer
- **Find tasks**: `docs/agents/TASKS.md` → section "Backend_developer"
- **Log work**: `docs/agents/backend_developer/JOURNEY.md`
- **Verified by**: debugger (golden path + API smoke), scraper_1 (API contracts)
- **Skills**: `postgres-postgis-schema`, `backend-data-engineering`, `workflow-runtime`, `db-sync-and-seeding`, `railway-deploy`, `ci-cd-pipeline`, `test-generator`, `context-engineering`

### data_analyst
- **Find tasks**: `docs/agents/TASKS.md` → section "DATA_ANALYST"
- **Log work**: `docs/agents/data_analyst/JOURNEY.md`
- **Verified by**: debugger (metric reproducibility + QA claims), ux_ui_designer (dashboard interpretation)
- **Skills**: `postgres-analysis`, `dashboard-visual-ops`, `parser-fixture-qa`, `test-generator`, `context-engineering`

### scraper_1
- **Find tasks**: `docs/agents/TASKS.md` → section "Scraper_1"
- **Log work**: `docs/agents/scraper_1/JOURNEY.md`
- **Verified by**: debugger (fixtures + legal gates), backend_developer (DB persistence)
- **Skills**: `scraper-connector-builder`, `parser-fixture-qa`, `real-estate-source-registry`, `runtime-compliance-evaluator`, `test-generator`, `context-engineering`

### scraper_sm / S&M
- **Find tasks**: `docs/agents/TASKS.md` → section "SCRAPER_SM / S&M"
- **Log work**: `docs/agents/scraper_sm/JOURNEY.md`
- **Verified by**: debugger (tier-3 contract gates, consent checklist, redaction, fixture format)
- **Skills**: `scraper-connector-builder`, `parser-fixture-qa`, `real-estate-source-registry`, `runtime-compliance-evaluator`, `deep-research-workflow`, `prompt-engineering`, `context-engineering`

### scraper_t3
- **Find tasks**: historical only
- **Log work**: `docs/agents/scraper_t3/JOURNEY.md`
- **Verified by**: no new assignments; migrate follow-ups to S&M

### ux_ui_designer
- **Find tasks**: `docs/agents/TASKS.md` → section "UX_UI_designer"
- **Log work**: `docs/agents/ux_ui_designer/JOURNEY.md`
- **Verified by**: debugger (API contract alignment + component spec completeness)
- **Skills**: `web-frontend-nextjs`, `frontend-pages`, `dashboard-visual-ops`, `ux-dashboard-design`, `web-performance-accessibility`, `vercel-nextjs-deploy`, `visual-3d-map`, `context-engineering`

### debugger
- **Find tasks**: `docs/agents/TASKS.md` → section "Debugger" + all `DONE_AWAITING_VERIFY` slices
- **Log work**: `docs/agents/debugger/JOURNEY.md`
- **Verified by**: lead agent (spot checks) or self-verify via `make validate` + `make golden-path`
- **Skills**: `debugger-golden-path`, `qa-review-release`, `security-audit`, `test-generator`, `ci-cd-pipeline`, `context-engineering`

### lead_agent
- **Find tasks**: `docs/agents/TASKS.md` → section "Lead Agent"
- **Log work**: orchestration session transcripts
- **Verified by**: self (dashboard + export refresh)
- **Skills**: `claude-opus-planner`, `software-architecture`, `subagent-driven-development`, `multi-agent-patterns`, `daily-orchestration`, `investor-pitch-yc`, `presentation-pdf-reportlab`, `presentation-powerpoint-pptx`, `google-slides-handoff`, `project-progress-dashboard-web`, `prompt-engineering`, `context-engineering`
