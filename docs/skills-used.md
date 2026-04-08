# Skills Used In This Project

Updated: 2026-04-08

This document records the skills and agent guidance that are part of the project or were used while shaping the current repository.

## Repo-Local Project Skills

These skills are stored directly in the repository under `agent-skills/`.

- `real-estate-source-registry`
- `scraper-connector-builder`
- `parser-fixture-qa`
- `postgres-postgis-schema`
- `workflow-runtime`
- `dedupe-entity-resolution`
- `geo-map-3d`
- `crm-chat-inbox`
- `publishing-compliance`
- `frontend-pages`
- `docs-export`
- `qa-review-release`
- `daily-orchestration`
- `db-sync-and-seeding`
- `runtime-compliance-evaluator`

## Session Skills Used By Codex

These were used from the Codex environment while working on the repository:

- `github:yeet`
  - used for the Git publish flow and branch/push preparation
- `doc`
  - used when keeping Word-compatible documentation exports aligned
- `pdf`
  - used when creating the architecture and execution PDF artifact

## Agent Workflow Files

These project files act as reusable agent behavior and should be kept in sync with the roadmap:

- `AGENTS.md`
- `.cursor/rules/00-project.mdc`
- `.cursor/rules/backend.mdc`
- `.cursor/rules/database.mdc`
- `.cursor/rules/docs.mdc`
- `.cursor/rules/frontend.mdc`
- `.cursor/rules/scrapers.mdc`
- `.cursor/rules/linear.mdc`
- `docs/cursor-agent-automation.md`
- `docs/linear-integration.md`

## Notes

1. Repo-local skills are the primary portable skill layer for this project.
2. External Codex/Claude/Linear/GitHub skills depend on the active agent environment.
3. If new project-specific skills are added, update this file together with `docs/agent-skills-index.md`.
