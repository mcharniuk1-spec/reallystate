# Server And DB Migration Instructions

## Current status
- `INFRA-01` is `DONE_AWAITING_VERIFY` (migration runbook and command paths are prepared).
- `INFRA-02` is `BLOCKED` waiting on live credentials and `BD-18` import/schema verification.
- No live DB dump, no DB scrape, and no production server mutation should run until prerequisites are met.

## Missing inputs checklist (input gate)
- [ ] `DATABASE_URL` (local libpq URL)
- [ ] `REMOTE_DATABASE_URL` (remote libpq URL)
- [ ] `DB_DUMP` path on local and remote
- [ ] SSH access tuple: `user@host`, key, and port
- [ ] Remote deploy path and service control method
- [ ] Media/media-object storage destination confirmation
- [ ] `BD-18` and `BD-19` verifier evidence artifacts
- [ ] Confirmation that live workers/scrapers are paused during migration

## Mandatory execution sequence
1. Confirm sequence with dry run:
   - `make -n backup-db restore-db verify-db-counts`
2. Export all required env values (`DATABASE_URL`, `REMOTE_DATABASE_URL`, `DB_DUMP`).
3. Run local backup and checksum:
   - `make backup-db`
4. Transfer dump/checksum and media path/asset store sync:
   - `ssh ... 'mkdir -p /srv/bgrealestate/backups /srv/bgrealestate/data/media'`
   - `rsync -avP /tmp/bgrealestate-backups/bgrealestate_full_*.dump <server>:/srv/bgrealestate/backups/`
   - `rsync -avP /tmp/bgrealestate-backups/bgrealestate_full_*.dump.sha256 <server>:/srv/bgrealestate/backups/`
5. Remote restore:
   - `make restore-db` (with `REMOTE_DATABASE_URL` and `DB_DUMP`)
6. Run count parity:
   - local `make verify-db-counts`
   - remote `make verify-db-counts`
   - `diff -u` the outputs
7. Debugger/backend approve before unblocking live scraping.

## Authoritative references
- [TASKS](</Users/getapple/Documents/Real Estate Bulg/docs/agents/TASKS.md>)
- [Runbook](</Users/getapple/Documents/Real Estate Bulg/docs/runbooks/server-db-migration.md>)
- [Role: infra_db_operator](</Users/getapple/Documents/Real Estate Bulg/docs/agents/roles/infra_db_operator.md>)
- [Makefile](</Users/getapple/Documents/Real Estate Bulg/Makefile>)
- [BD-18 spec](</Users/getapple/Documents/Real Estate Bulg/docs/exports/bd18-database-review-and-correction-spec-2026-05-13.md>)
- [Journey](</Users/getapple/Documents/Real Estate Bulg/docs/agents/infra_db_operator/JOURNEY.md>)

## Required command snippet
```bash
export DATABASE_URL='postgresql://...'
export REMOTE_DATABASE_URL='postgresql://...'
export DB_DUMP='/srv/bgrealestate/backups/bgrealestate_full_<timestamp>.dump'

make -n backup-db restore-db verify-db-counts
# then execute in this order:
make backup-db
# transfer
make restore-db
# counts
make verify-db-counts
```
