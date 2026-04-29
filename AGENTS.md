# Bulgaria Real Estate MVP Agent Instructions

This repository is the foundation for a Bulgaria real estate ingestion, map, CRM, and publishing MVP. Extend the existing scaffold; do not replace it wholesale.

## Mission

- Build source-first ingestion for Bulgarian portals, agencies, STR/vendor channels, official registers, and lead-intelligence overlays.
- Normalize all listings into one canonical real estate model with photos, descriptions, contacts, geospatial links, and lifecycle events.
- Add a map/search MVP with `/listings`, `/properties/[id]`, `/map`, `/chat`, `/settings`, and `/admin`.
- Add reverse publishing only through official, authorized, partner, vendor, or assisted-manual routes.

## Hard Guardrails

- Use `data/source_registry.json` as the authoritative source matrix.
- Enforce `legal_mode`, `risk_mode`, and `access_mode` before implementing any connector or publishing adapter.
- Treat every saved scraper row as a source publication first. Promote it to a single property item only when the source page clearly represents one unit with its own detail URL and one price, or an explicit `on request` / `undefined` price state preserved in provenance.
- Flag mixed multi-unit pages (`1-2 bedroom`, `apartments (various types)`, whole residential-building/development pages, or price-from pages) as grouped/development publications unless the source exposes unit-level URL, price, area, floor/rooms, and media evidence for each unit.
- Never store numeric `0` as a real property price. Use `null` plus provenance such as `price_status = on_request` or `price_status = undefined` until a first-class field exists.
- Do not add unsafe broad scraping for Airbnb, Booking.com, WhatsApp, Viber, private Facebook groups, or private Telegram groups.
- Do not automate mass account creation, KYC bypass, CAPTCHA bypass, or private-account access.
- Do not add live-network dependencies to tests; crawler tests must use fixtures.
- Do not start public UI work until ingestion, CRM, compliance, and operator review foundations exist.
- **Agent skills are version-controlled deliverables**: any new or updated skill must be saved under `agent-skills/<name>/SKILL.md` and included in the same change set as the code/docs it enables (so other agents can use it when the repo is cloned).
- If a Linear issue key is present in the task or branch context, keep implementation and status notes aligned with that issue.
- If Linear tools are unavailable in the session, use `docs/linear-integration.md` and `docs/exports/linear-import-roadmap.csv` as the fallback project-management source.

## Agent Coordination

Six specialist agents plus the lead agent operate under a structured coordination protocol:

- **Task queue**: `docs/agents/TASKS.md` — single source of truth for what each agent does next.
- **Journey logs**: `docs/agents/<agent>/JOURNEY.md` — append-only execution log per agent.
- **Coordination protocol**: `docs/agents/README.md` — dependency graph, verification rules, handoff format.
- **Cross-verification**: no slice is complete until a verifier agent (usually `debugger`) runs the acceptance gate and logs the result.

Agents: `backend_developer`, `scraper_1`, `scraper_t3`, `scraper_sm`, `ux_ui_designer`, `debugger`.

Before starting work, every agent must read `docs/agents/TASKS.md` to find their current slice.

Current Gemma/OpenClaw handoff (2026-04-29, **operator gate 2026-04-30**):

- **Load in one context**: Action0 + Action1 + Action2 contracts from `docs/exports/taskforgema.md` so Gemma4 never asks for ad-hoc “URLs/patterns”.
- **`S1-22B` / Action1**: scrape/backfill only `Address.bg`, `BulgarianProperties`, `Homes.bg`, `imot.bg`, `LUXIMMO`, `property.bg`, and `SUPRIMMO` for all Bulgaria across `buy_personal`, `buy_commercial`, `rent_personal`, and `rent_commercial` — **first execution after operator `Action1 ACCEPT`**. Telegram every **+100** net new saves: **7×4** matrix (`make action1-matrix-snapshot`).
- **`S1-22A` / Action0**: local-gallery image reports — **only after operator `Action0 now`** following Action1 completion (unless waiver logged in `docs/agents/scraper_1/JOURNEY.md`).
- **`S1-22C` / Action2**: expand to remaining legal tier-1/2 sources — **only after operator `Action2 now`** + Action1 QA.
- Detailed operator prompt and report contract: `docs/exports/taskforgema.md` and `docs/openclaw/gemma4-agent.md`.

## Operator GO Commands

Use a single GO command to start an agent slice without extra back-and-forth inside the same activation.

- `GO backend_developer`
- `GO scraper_1`
- `GO scraper_t3`
- `GO scraper_sm`
- `GO ux_ui_designer`
- `GO debugger`
- `GO all` (parallel start; one active slice per agent)

Execution rule:

- When the operator gives `GO <agent>` or `GO all`, agents proceed through their current `TODO`/`IN_PROGRESS` slice and acceptance gate, then write JOURNEY updates and TASKS status updates in the same run.
- If the environment requires elevated runtime approval (OS/sandbox prompt), that platform prompt still applies; otherwise no extra human confirmation is required inside that GO run.

Continuation rule (non-stop execution):

- Agents must not stop after one slice if another unblocked slice exists for the same agent in `docs/agents/TASKS.md`.
- Continue sequentially: complete current slice -> update TASKS/JOURNEY -> start next unblocked slice.
- Stop only when one of these is true:
  1. Operator explicitly says `END`, or
  2. No unblocked slice remains, or
  3. A real blocker prevents progress.
- When stopping because no unblocked slice remains, ask using this format:
  - `Which <agent_name> task should I execute next?`
  - Example: `Which backend_developer task should I execute next?`

## Activation Checklist (every run)

On each activation, the lead agent must:

1. Read `docs/agents/TASKS.md` and all `docs/agents/*/JOURNEY.md`.
2. Analyze current progress, blockers, and dependency drift across all agents.
3. Add follow-up notes/actions into the relevant agent slices in `docs/agents/TASKS.md`.
4. Ensure tier ownership remains strict:
   - `scraper_1`: tier-1 and tier-2 website connectors (HTTP first, Playwright where needed)
   - `scraper_t3`: tier-3 vendor/partner/official routes only
   - `scraper_sm`: tier-4 social overlays and consent-gated channels only
5. Refresh dashboard artifacts whenever changes are detected: run `make dashboard-doc`.

## Skill Packs And Model Policy

Agents should use project-local skills from `agent-skills/` first, including:

- `software-architecture`
- `subagent-driven-development`
- `claude-opus-planner`
- `deep-research-workflow`
- `postgres-analysis`
- `wordpress-development`
- `web-frontend-nextjs`
- `dashboard-visual-ops`
- `web-performance-accessibility`
- `investor-pitch-yc`
- `presentation-pdf-reportlab`
- `presentation-powerpoint-pptx`
- `google-slides-handoff`
- `project-progress-dashboard-web`
- `context-engineering`
- `prompt-engineering`
- `multi-agent-patterns`
- `test-generator`
- `security-audit`
- `vercel-nextjs-deploy`
- `railway-deploy`
- `ci-cd-pipeline`

Model policy for planning:

- When Claude is used for planning/architecture decisions, prefer Opus-level reasoning when available.
- Hand implementation slices to faster agents/models after the plan is stable.

External skill marketplace policy:

- Marketplace-discovered skills (e.g. from `claudeskills.info`) must be mirrored as version-controlled local skills under `agent-skills/<name>/SKILL.md` before becoming part of normal agent execution.

## Files To Read First

- `docs/agents/TASKS.md` (your current task)
- `docs/agents/README.md` (coordination protocol)
- `PLAN.md`
- `platform-mvp-plan.md` if present
- `deep-research-report.md`
- `data/source_registry.json`
- `sql/schema.sql`
- `README.md`
- `docs/linear-integration.md`
- `docs/skills/marketplace-adoption.md`
- `src/bgrealestate/*`
- `tests/*`

## Required Step Output

Every Cursor/Codex/Claude step must end with:

```text
Changed files:
Agent tools used:
Skills used:
Extensions/libraries used:
Commands run:
Tests run:
Outputs produced:
Risks / blockers:
Progress update:
Next step:
```

## Phase Gates

- Phase 1: docs, rules, source registry, and agent skills are present.
- Phase 2: persistence/migrations are working before live connectors.
- Phase 3: one connector is fixture-tested before adding more connectors.
- Phase 4: at least three tier-1 sources work end-to-end before tier-2 expansion.
- Phase 5: dedupe, geospatial confidence, and compliance gates exist before public UI.
- Phase 6: CRM and operator/admin workflows exist before launch.
- Phase 7: reverse publishing uses only official/authorized/vendor/assisted workflows.
