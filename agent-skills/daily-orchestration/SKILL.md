---
name: daily-orchestration
description: Use for daily project review, roadmap alignment, policy/guardrail enforcement, and slicing work into agent-ready tasks with acceptance gates.
---

# daily-orchestration

Use this skill once per day (or at the start of each session) to keep the project strategically aligned and execution-ready across agents.

## Read First

- `AGENTS.md`
- `PLAN.md`
- `docs/project-status-roadmap.md`
- `data/source_registry.json`
- `.cursor/rules/00-project.mdc`

## Daily Review Checklist (15–25 min)

1. **Confirm current stage** in `docs/project-status-roadmap.md` and update the “Updated:” date if anything shipped.
2. **Validate guardrails**:
   - no live-network dependency added to tests
   - no high-risk/private-messaging scraping paths were introduced
   - legal gates remain fail-closed (`legal_mode`, `risk_mode`, `access_mode`)
3. **Run quick verification** (pick what applies):
   - `make test`
   - `make lint` (if deps installed)
4. **Diff vs roadmap**:
   - list what moved forward since yesterday (files + tests)
   - identify the single highest-leverage next slice (one connector, one migration, one repo layer, one API surface)
5. **Create or refine skills**:
   - if a repeated action took >10 minutes or was error-prone, extract it into a new `agent-skills/<name>/SKILL.md`
   - add “Read First”, “Workflow”, and “Acceptance” so other agents can replicate it safely

## Work Slicing Rules

- One slice = one phase unit (e.g., “repository layer for raw captures” OR “Homes.bg discovery parser”), not “build everything”.
- Every slice must have:
  - changed files list
  - runnable command(s)
  - acceptance gate(s) and how to verify

## Acceptance

- `docs/project-status-roadmap.md` reflects reality (no “done” without tests).
- Next slice is clearly defined and assignable to an agent with minimal ambiguity.
