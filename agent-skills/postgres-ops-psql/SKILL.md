---
name: postgres-ops-psql
description: Use when the project needs practical psql workflows for schema inspection, bulk loads, exports, backups, and ingestion verification.
---

# postgres-ops-psql

Use this skill when working directly with PostgreSQL through `psql`, especially for ingestion verification and bulk operational tasks.

## Read First
- `sql/schema.sql`
- `src/bgrealestate/db_sync.py`
- `agent-skills/postgres-analysis/SKILL.md`
- `agent-skills/db-sync-and-seeding/SKILL.md`

## Workflow
1. Confirm the target database and schema before running commands.
2. Prefer read-only inspection first:
   - `\\dt`, `\\d+`, `\\di`
   - row counts by source
   - latest ingestion timestamps
3. Use explicit, logged commands for:
   - bulk `COPY` / `\\copy`
   - schema inspection
   - export of verification tables
   - backup and restore rehearsal
4. Wrap risky write operations in transactions where possible.
5. For this project, verify source ingestion with stable counts:
   - `canonical_listing` rows by `source_name`
   - distinct `reference_id`
   - media rows by `listing_id`
6. Keep performance in view:
   - inspect indexes before large reconciliations
   - use `EXPLAIN` or `EXPLAIN ANALYZE` only when safe
   - avoid unbounded full-table scans during routine checks

## Output Format

```text
Objective:
Database target:
Inspection commands:
Bulk-load or export commands:
Verification query:
Rollback/backup note:
```

## Acceptance
- Commands are safe, explicit, and reproducible.
- Verification focuses on ingestion truth, not ad hoc impressions.
- Export and bulk-load steps are compatible with project tables and IDs.
