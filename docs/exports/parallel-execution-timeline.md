# Parallel execution timeline

_Generated: 2026-04-28T08:38:23.887343+00:00_

Aligned with `PLAN.md` §9.1 (waves) and `docs/agents/TASKS.md` priority phases.

## Parallel waves (PLAN §9.1)

### Wave A

Docs/rules stability, DB control plane, tier-1/2 fixture connectors, tier-3 policy/contracts, social policy/contracts.

**Typical owners:** backend_developer, scraper_1, scraper_t3, scraper_sm, debugger.

### Wave B

DB-backed ingest runners, stats/admin expansion, auth/RBAC, tier-3 adapter stubs, frontend operator dashboard binding.

**Typical owners:** backend_developer, scraper_1, scraper_t3, ux_ui_designer, debugger.

### Wave C

Dedupe/geo/media, map/listing/chat UI depth, publishing dry-run controls, CI hardening.

**Typical owners:** backend_developer, ux_ui_designer, scraper_1, debugger.

## Operator phases (TASKS — critical path)

### Phase A — Tier-1/2 live volume

*Do first — scraper_1 + minimal backend*

- **Parallel lanes:** scraper_1, backend_developer
- **Task IDs:** S1-14, S1-15, BD-11, S1-18

### Phase B — Backend core

*After S1-18 VERIFIED*

- **Parallel lanes:** backend_developer
- **Task IDs:** BD-12, BD-13, BD-14, BD-15

### Phase C — Debugger consolidation

*Batch verify + quality gate*

- **Parallel lanes:** debugger, lead_agent
- **Task IDs:** DBG-06, DBG-05

### Phase D — Other scrapers

*Parked until S1-18 unless unblocker*

- **Parallel lanes:** scraper_t3, scraper_sm
- **Task IDs:** T3-07, T3-08, SM-06, …

### Phase E — Frontend depth

*ux_ui_designer*

- **Parallel lanes:** ux_ui_designer
- **Task IDs:** UX-13, UX-08, UX-09, UX-10, UX-11

### Phase F — Polish

*Map, 3D, chat, admin, smoke, security*

- **Parallel lanes:** ux_ui_designer, backend_developer, debugger
- **Task IDs:** UX-04, UX-07, BD-08, UX-05, BD-07, UX-12, DBG-07, DBG-08

### Phase G — Growth

*Expansion connectors + realtime + analytics*

- **Parallel lanes:** scraper_1, scraper_sm, scraper_t3, backend_developer
- **Task IDs:** S1-16, S1-17, SM-06, T3-08, BD-16, BD-09, BD-10
