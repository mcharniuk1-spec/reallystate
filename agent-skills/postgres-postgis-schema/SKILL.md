---
name: postgres-postgis-schema
description: Use for PostgreSQL/PostGIS schema, Alembic migrations, indexes, partition-ready tables, repositories, and database tests.
---

# postgres-postgis-schema

Use this skill for database schema, migrations, indexes, and repositories.

## Read First
- `sql/schema.sql`
- `PLAN.md`
- `platform-mvp-plan.md`

## Workflow
1. Use PostgreSQL/PostGIS as the operational source of truth.
2. Store raw binaries and media in S3/MinIO; store only keys and metadata in PostgreSQL.
3. Add GiST indexes for geometry, GIN indexes for JSONB/full-text, and B-tree indexes for source/status/time fields.
4. Treat `raw_capture`, `source_listing_snapshot`, `listing_event`, `lead_message`, and `webhook_event` as partition-ready.
5. Pair schema changes with repository and migration tests.

## Acceptance
- Migrations apply cleanly.
- PostGIS queries and required indexes exist.
- User/chat/publishing tables preserve auditability and tenant boundaries.
