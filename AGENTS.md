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
