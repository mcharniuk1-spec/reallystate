---
name: backend-data-engineering
description: Use for data pipelines, schema evolution, ingestion persistence, reporting aggregates, and backend reliability.
---

# backend-data-engineering

Use this skill for the backend/data-engineering track.

## Read First
- `sql/schema.sql`
- `migrations/*`
- `src/bgrealestate/db/*`
- `src/bgrealestate/stats/*`

## Workflow
1. Enforce migration-first schema changes.
2. Keep repositories idempotent and traceable (`raw_capture_id`, `snapshot_id`).
3. Expose operational stats for admins and XLSX exports.
4. Validate with optional DB smoke tests plus offline unit tests.

## Acceptance
- Database writes are deterministic and auditable.
- Admin stats and exports reflect ingestion outputs.

