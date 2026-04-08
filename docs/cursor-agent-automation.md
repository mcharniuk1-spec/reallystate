# Cursor/Codex/Claude Agent Automation Setup

Use this document when preparing Cursor, Codex, or Claude agents to implement the Bulgaria real estate MVP.

## 1. Cursor Setup

1. Open the repository root as the Cursor workspace.
2. Let Cursor index `src`, `tests`, `data`, `sql`, `docs`, `agent-skills`, `.cursor`, and all plan documents.
3. Read `AGENTS.md` and `.cursor/rules/00-project.mdc` before any agent run.
4. Use `.cursor/mcp.json` for docs/browser/schema helpers. Keep database access read-only unless a human explicitly approves migration execution.
5. Use Background Agents only for bounded tasks: one connector, one migration slice, one frontend page, one review queue, or one doc export task.

## 2. Cursor Background Agent Guardrails

Good background tasks:
- "Implement the Homes.bg fixture parser only."
- "Add the `/listings` page using existing APIs and mock data."
- "Create Alembic migration for CRM tables and repository tests."
- "Generate source/legal matrix docs from `data/source_registry.json`."

Bad background tasks:
- "Build the whole platform."
- "Scrape Airbnb/Booking/WhatsApp automatically."
- "Create accounts on all platforms."
- "Use credentials or private channel access."
- "Run live crawler tests."

## 3. Codex Usage

Use Codex for focused patches:
- review unsafe connector behavior
- implement one repository or migration
- add a fixture regression test
- update source registry and matrices
- check publishing compliance blockers

## 4. Claude Usage

Use Claude Code for long-context synthesis:
- reconcile plan and implementation
- extract or update agent skills
- review whether every research source appears in the registry
- produce DOCX/PDF-ready documentation drafts

## 5. Required Agent Closeout

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
