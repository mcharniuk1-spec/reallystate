---
name: db-sync-and-seeding
description: Use when syncing the JSON source registry into PostgreSQL tables (source_registry/source_legal_rule/source_endpoint) and validating the persisted planning fields.
---

# db-sync-and-seeding

Use this skill when you need the database to reflect `data/source_registry.json` (sources + derived legal rules + default endpoints) so connectors can be orchestrated from Postgres.

## Read First

- `data/source_registry.json`
- `sql/schema.sql`
- `src/bgrealestate/db_sync.py`
- `src/bgrealestate/connectors/legal.py`
- `docs/development-setup.md`

## Workflow

1. Start infra: `make dev-up`
2. Apply migrations: `make db-init` (requires `DATABASE_URL`)
3. Sync registry into DB:
   - use the project’s sync entrypoint (`src/bgrealestate/db_sync.py`) to upsert:
     - `source_registry` planning fields (`primary_url`, `related_urls`, `languages`, `listing_types`, etc.)
     - `source_legal_rule` using derived defaults (fail-safe)
     - `source_endpoint` using `primary_url` where present
4. Verify by querying:
   - ensure tier‑1 sources exist
   - ensure high-risk sources have `blocks_live_scrape=true` where required

## Acceptance

- Running sync twice is idempotent (no duplicates, stable rule IDs).
- DB rows match the registry planning fields and default legal rules.
- No tests or scripts require live network access.
