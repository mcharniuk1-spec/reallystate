---
name: postgres-analysis
description: PostgreSQL read-focused analysis skill for schema inspection, query planning, index checks, and data-quality diagnostics. Use for DB health checks, reporting queries, and performance triage.
---

# Postgres Analysis

## Use When

- Auditing schema and migration alignment.
- Diagnosing slow queries or missing indexes.
- Building aggregate/reporting SQL safely.

## Workflow

1. Confirm target schema and table ownership.
2. Inspect query shape and index coverage.
3. Validate cardinality assumptions.
4. Propose safe, incremental query improvements.
5. Add tests for query outputs when possible.

## Query Review Checklist

- Uses selective predicates early.
- Avoids unbounded scans where avoidable.
- Uses appropriate indexes (`btree`, `gin`, `gist`, trigram).
- Keeps aggregation/reporting queries deterministic.

## Output

```text
Objective:
Current query/risk:
Proposed query/index changes:
Expected impact:
Validation method:
```
