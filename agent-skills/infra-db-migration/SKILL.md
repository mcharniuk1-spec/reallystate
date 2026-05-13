---
name: infra-db-migration
description: Prepare and execute PostgreSQL/PostGIS backup, transfer, restore, and count verification for server migration.
---

# Infra DB Migration

## Purpose

Use this skill for server bootstrap, database backup/restore, migration readiness, and remote runtime verification.

## Required Inputs

- `docs/runbooks/server-db-migration.md`
- `docs/docker-and-database.md`
- `Makefile`
- `sql/schema.sql`
- `migrations/`
- local and remote database URLs from environment variables

## Workflow

1. Confirm no live scraping is running unless operator explicitly allows it.
2. Verify local `DATABASE_URL`.
3. Create logical dump with `make backup-db`.
4. Verify checksum.
5. Transfer dump and media separately.
6. Restore with `make restore-db`.
7. Compare counts with `make verify-db-counts`.
8. Record any differences and block production scraping until explained.

## Acceptance Gate

- Dump checksum exists.
- Restore exits cleanly.
- PostGIS is available.
- Key table counts match or are explained.
- App can connect to remote DB.

## Safety

Never put DB dumps or credentials in git.
