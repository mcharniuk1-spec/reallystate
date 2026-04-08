---
name: fullstack-coding
description: Use for end-to-end coding slices that touch connectors, backend APIs, data models, and UI contracts.
---

# fullstack-coding

Use this skill when a feature crosses scraper/backend/frontend boundaries.

## Read First
- `PLAN.md`
- `src/bgrealestate/api/*`
- `src/bgrealestate/connectors/*`
- `sql/schema.sql`

## Workflow
1. Define data contract first (DB and API response shape).
2. Implement backend and tests before UI wiring.
3. Keep fixtures for parser paths and unit tests for APIs.
4. Update docs and exports (`make docs-refresh`).

## Acceptance
- End-to-end path works from data ingestion to API output.
- Tests pass without live network dependencies.

