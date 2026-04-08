---
name: software-architecture
description: Architecture design and review skill for modular service boundaries, dependency direction, SOLID-oriented refactors, and execution sequencing. Use when defining or reviewing system architecture, service contracts, or major refactors.
---

# Software Architecture

## Use When

- Designing or refactoring platform/service boundaries.
- Reviewing dependency direction and coupling risks.
- Planning scalable ingestion + API + UI integration paths.
- Translating product requirements into implementation slices.

## Read First

- `PLAN.md`
- `docs/project-architecture-execution-guide.md`
- `sql/schema.sql`
- `docs/agents/TASKS.md`

## Workflow

1. Identify domain boundaries (ingest, normalize, serve, operate, publish).
2. Validate dependency direction (data/control should not flow backward).
3. Check safety gates: legal mode, risk mode, access mode.
4. Propose parallelizable slices with explicit handoff gates.
5. Ensure each slice has acceptance criteria and failure rollback.

## Architecture Output Template

```text
Context:
Current constraints:
Proposed architecture change:
Dependency impact:
Parallel execution lanes:
Acceptance gates:
Risks and mitigations:
```

## Guardrails

- Prefer incremental architecture changes over big-bang rewrites.
- Keep tests fixture-first for scrapers.
- Do not suggest unauthorized scraping paths.
