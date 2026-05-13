# Server And Database Migration Runbook

Date: 2026-05-13

This runbook prepares the next step. Do not run live scraping during migration.

## Required Inputs

- Server provider and OS: recommended Ubuntu 24.04 LTS.
- SSH host, user, and key.
- Remote directory, recommended `/srv/bgrealestate`.
- Local `DATABASE_URL`.
- Remote `REMOTE_DATABASE_URL`.
- Decision on media storage path or object storage bucket.

## Recommended Server

Primary: Hetzner dedicated EX/AX class server.

Fallbacks:

- OVH VPS if setup friction matters more than dedicated resources.
- DigitalOcean if API-friendly provisioning matters more than price.
- RunPod only for burst GPU image processing, not the primary DB.

## Baseline Server Setup

Install:

- Docker Engine and Docker Compose plugin.
- Git.
- `postgresql-client`.
- Tailscale or SSH key-only access.
- Firewall allowing SSH, HTTP, HTTPS only.
- Reverse proxy with TLS.

Keep PostgreSQL private. Do not expose DB publicly.

## Local Backup

Use:

```bash
export DATABASE_URL='postgresql://...'
make backup-db
```

Optional fixed output:

```bash
export DB_DUMP=/tmp/bgrealestate-backups/bgrealestate_full_20260513.dump
make backup-db
```

Expected outputs:

- `/tmp/bgrealestate-backups/*.dump`
- `/tmp/bgrealestate-backups/*.dump.sha256`

## Transfer

```bash
ssh user@server 'mkdir -p /srv/bgrealestate/backups /srv/bgrealestate/data/media'
rsync -avP /tmp/bgrealestate-backups/bgrealestate_full_20260513.dump user@server:/srv/bgrealestate/backups/
rsync -avP /tmp/bgrealestate-backups/bgrealestate_full_20260513.dump.sha256 user@server:/srv/bgrealestate/backups/
rsync -avP data/media/ user@server:/srv/bgrealestate/data/media/
```

Do not transfer `.env`, `.env.local`, raw capture dirs, or local OpenClaw state.

## Remote Restore

```bash
git clone git@github.com:mcharniuk1-spec/reallystate.git /srv/bgrealestate/app
cd /srv/bgrealestate/app
git checkout reallystate
docker compose up -d postgres redis minio temporal temporal-ui
export REMOTE_DATABASE_URL='postgresql://...'
export DB_DUMP=/srv/bgrealestate/backups/bgrealestate_full_20260513.dump
make restore-db
```

## Verify Counts

Local:

```bash
export DATABASE_URL='postgresql://local...'
make verify-db-counts > /tmp/bgrealestate-local-counts.txt
```

Remote:

```bash
export DATABASE_URL='postgresql://remote...'
make verify-db-counts > /tmp/bgrealestate-remote-counts.txt
```

Compare:

```bash
diff -u /tmp/bgrealestate-local-counts.txt /tmp/bgrealestate-remote-counts.txt
```

Key tables:

- `source_registry`
- `source_endpoint`
- `crawl_run`
- `crawl_item`
- `canonical_listing`
- `property_entity`
- `property_offer`
- `media_asset`
- user/CRM/chat tables

## Acceptance Gate

- Checksum matches.
- Restore completes without owner/ACL errors.
- PostGIS extension is available.
- App connects to remote DB.
- Key counts match or every difference is explained.
- No live scraping resumes until `debugger` signs off.

## Rollback

If restore fails:

1. Stop workers and scrapers.
2. Keep dump and checksum.
3. Drop only the failed remote DB, not local DB.
4. Recreate remote DB and retry `make restore-db`.
5. Record failure in `docs/agents/infra_db_operator/JOURNEY.md`.
