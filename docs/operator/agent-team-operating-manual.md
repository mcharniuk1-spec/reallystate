# Agent Team Operating Manual

This is the human-readable control document for the agent team.

## What To Say

Use one operator prompt per activation:

- `GO planner`
- `GO backend_developer`
- `GO scraper_1`
- `GO data_analyst`
- `GO ux_ui_designer`
- `GO debugger`
- `GO all`
- or a direct task prompt that replaces the current slice for the named agent.

When a direct task prompt arrives, the agent must:

1. Treat the prompt as the current task.
2. Preserve unexecuted prior tasks as next planned work unless the prompt cancels them.
3. Update `TASKS.md` and `JOURNEY.md`.
4. Ask for the next task only when no unblocked slice remains.

## Where To Look

| Need | File |
| --- | --- |
| Current work | `docs/agents/TASKS.md` |
| Team rules | `docs/agents/README.md` |
| Self-development architecture | `docs/agents/SELF_DEVELOPMENT_ARCHITECTURE.md` |
| Agent loop and cadence | `docs/agents/AGENT_LOOP_AND_CADENCE.md` |
| Role-specific instructions | `docs/agents/roles/*.md` |
| Previous actions | `docs/agents/<agent>/JOURNEY.md` |
| Server/DB migration | `docs/runbooks/server-db-migration.md` |
| Skills and MCP setup | `docs/integrations/mcp-and-skills-setup.md` |
| Wiki memory | `/Users/getapple/core/wiki/projects/real-estate-bulgaria/` |

## Execution Contract

Each run must end with:

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

## Reliability Checks

Before work:

- Confirm the agent role file.
- Confirm source-tier ownership.
- Confirm whether the newest prompt supersedes planned work.
- Confirm whether DB, network, or live scraping is forbidden.

After work:

- Write or update files.
- Append the agent journey.
- Update tasks and verifier handoff.
- Run relevant focused checks.
- Refresh dashboard docs if task/journey docs changed.
- Record wiki run and only update memory/insights when reusable.

## Current Operator Warning

Do not touch live scraping DB data until the server/DB migration step is explicitly started. Current work is architecture, docs, git hygiene, runbooks, and task orchestration.
