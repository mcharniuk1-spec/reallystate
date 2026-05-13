# Plan 13.05 - Git sync, database migration, and agent architecture rebuild

Date: 2026-05-13
Project: Bulgaria Real Estate MVP

## 1. Current facts

FACT: The authoritative source matrix is `data/source_registry.json`.

FACT: Current branch is `reallystate`; remote is `origin git@github.com:mcharniuk1-spec/reallystate.git`.

FACT: Unsafe/non-code files are mixed into the current git state, including `.env`, `.env.local`, `.openclaw` state, raw scrape captures, logs, and large scraped corpus changes.

FACT: The project already has FastAPI, SQLAlchemy/Alembic, PostgreSQL/PostGIS, Redis, MinIO, Temporal, Next.js, scraper scripts, OpenClaw handoff docs, and multi-agent coordination docs.

FACT: Tier ownership must remain strict:

- `scraper_1`: tier 1-2 website connectors.
- `scraper_t3`: tier 3 vendor, partner, and official routes.
- `scraper_sm`: tier 4 public/consent-gated social overlays only.

GAP: Live database size, exact table counts, and remote VM credentials are not yet known.

GAP: Final server provider requires user purchase/API access.

## 2. Git push plan

Goal: reliably push relevant project files to GitHub, excluding database, secrets, raw captures, and local runtime state.

### 2.1 Hygiene first

Update `.gitignore` before staging:

```gitignore
.env
.env.*
!.env.example
.openclaw/
.cursor/*.log
data/runs/*.log
data/runs/*.pid
data/runs/*.lock
*.dump
*.backup
*.sqlite
*.sqlite3
*.zip
data/scraped/**/raw/
```

### 2.2 Unstage unsafe files

Run targeted unstaging, not `git reset --hard`:

```bash
git restore --staged .env .env.local .openclaw/workspace-state.json || true
git restore --staged 'data/scraped/**/raw/**' || true
git restore --staged 'data/runs/**' || true
git restore --staged '*.dump' '*.backup' '*.sqlite' '*.sqlite3' '*.zip' || true
```

### 2.3 Stage only relevant project files

Stage code, docs, configs, migrations, agent docs, skills, frontend/backend files, and source registry.

Do not stage:

- Database dumps.
- PostgreSQL volumes.
- `.env` or `.env.local`.
- OpenClaw runtime state.
- Raw HTML captures.
- PID, lock, and log files.
- Large archive files.

### 2.4 Secret and corpus check

Before commit:

```bash
git diff --cached --name-only
git diff --cached -- . ':!data/scraped/**/raw/**' | rg -n 'SECRET|PASSWORD|TOKEN|API_KEY|PRIVATE|DATABASE_URL|BEGIN .*PRIVATE KEY' || true
```

If secrets appear, stop and remove them from staging.

### 2.5 Commit and push

Recommended commit:

```bash
git commit -m "Sync project architecture, Action1 orchestration, and product surfaces"
git push origin reallystate
```

If push is rejected, fetch and inspect. Do not force-push without explicit approval.

## 3. Database migration plan

Goal: migrate full DB structure and all scraped property data from Mac to a remote server/VM without putting the DB into git.

Recommended method: logical PostgreSQL custom dump with `pg_dump -Fc`, then `pg_restore`.

### 3.1 User execution

**User must choose/order the server and provide SSH access.**

Recommended primary target: Hetzner dedicated EX44/AX42-class server.

Reasoning:

- Strong price/performance.
- Dedicated CPU/RAM/disk avoids noisy-neighbor DB issues.
- Good fit for PostgreSQL/PostGIS, scrapers, OpenClaw, Codex, Ollama CPU inference, and background workers.

Fallback:

- OVH VPS-5/VPS-6 for lower setup friction.
- DigitalOcean if API friendliness is more important than price.
- RunPod GPU only for burst image-processing batches, not primary database hosting.

### 3.2 Remote server baseline

Install:

- Ubuntu 24.04 LTS.
- Docker + Docker Compose plugin.
- Git.
- Tailscale or SSH key-only access.
- Firewall: expose only SSH, HTTP, HTTPS. Keep PostgreSQL private.
- Reverse proxy with TLS.

### 3.3 Mac dump

**User or agent runs on Mac after confirming local DB URL:**

```bash
pg_dump -Fc --no-owner --no-acl "$DATABASE_URL" -f /tmp/bgrealestate_full_20260513.dump
shasum -a 256 /tmp/bgrealestate_full_20260513.dump > /tmp/bgrealestate_full_20260513.dump.sha256
```

### 3.4 Transfer

```bash
rsync -avP /tmp/bgrealestate_full_20260513.dump user@server:/srv/bgrealestate/backups/
rsync -avP /tmp/bgrealestate_full_20260513.dump.sha256 user@server:/srv/bgrealestate/backups/
```

If media files are outside PostgreSQL, transfer media separately:

```bash
rsync -avP data/media/ user@server:/srv/bgrealestate/data/media/
```

### 3.5 Restore on server

```bash
git clone git@github.com:mcharniuk1-spec/reallystate.git /srv/bgrealestate/app
cd /srv/bgrealestate/app
git checkout reallystate
docker compose up -d postgres redis minio temporal temporal-ui
pg_restore --clean --if-exists --no-owner --no-acl -d "$REMOTE_DATABASE_URL" /srv/bgrealestate/backups/bgrealestate_full_20260513.dump
```

### 3.6 Verify

Compare key local vs remote counts:

- `source_registry`
- `source_endpoint`
- `crawl_run`
- `crawl_item`
- `canonical_listing`
- `property_entity`
- `property_offer`
- media tables
- CRM/user/chat tables

Do not continue to production scraping until counts match or differences are explained.

## 4. Rebuilt agent architecture

Goal: keep current structure but make lanes stricter, automatable, and easier to run on a remote server.

## 4.1 Lead/control agents

### `planner_lead`

Owns:

- Task graph.
- Agent dependencies.
- Phase gates.
- Source-tier boundaries.
- Weekly plan updates.

Inputs:

- `docs/agents/TASKS.md`
- `docs/agents/*/JOURNEY.md`
- `data/source_registry.json`
- wiki memory/insights.

Outputs:

- Updated task queue.
- Architecture decisions.
- Run priorities.

### `ops_release_manager`

Owns:

- Git hygiene.
- Release branches.
- Secret checks.
- Deployment runbooks.
- CI/CD gates.

Outputs:

- Safe commits.
- Push/release reports.
- Rollback instructions.

### `infra_db_operator`

Owns:

- PostgreSQL/PostGIS.
- Backups/restores.
- Docker Compose.
- Remote server bootstrap.
- DB migrations.
- Observability.

Outputs:

- Backup files.
- Restore reports.
- Count comparisons.
- DB health reports.

## 4.2 Scraping agents

### `scraper_tier12`

Owns:

- Tier 1-2 website connectors.
- Action1 core sources.
- Action2 remaining legal tier 1-2 sources.
- Fixture tests.
- Legal/access gates.

Rules:

- Start from category/city entrypoints.
- Keep source publications separate from canonical properties.
- Never store numeric `0` as real price.
- No live-network tests.

Main automation:

```bash
make scrape-tier12
make action1-matrix-snapshot
make import-scraped
```

### `scraper_tier3`

Owns:

- Tier 3 vendor/partner/official sources.
- Airbnb, Booking.com, Vrbo only through lawful/vendor/partner/manual routes.
- Cadastre/register/auction routes where legally available.
- STR analytics sources such as AirDNA/Airbtics only through API/export/partner routes.

Rules:

- No broad unsafe scraping of Airbnb/Booking/Vrbo.
- No account/KYC/CAPTCHA bypass.
- Preserve provenance and licensing fields.

### `scraper_social_tier4`

Owns:

- Public Facebook groups/pages.
- Public Instagram profiles.
- Public Telegram channels.
- Threads/X public profiles/search where allowed.
- WhatsApp/Viber only via opt-in/manual export/bot/partner route.

Rules:

- Social data enters as `social_publication_candidate` or CRM evidence first.
- No private group/channel automation.
- Redact personal data where needed.
- Operator review before canonical promotion.

## 4.3 Intelligence/product agents

### `data_analytics_agent`

Owns:

- SQL analysis.
- Data quality.
- Coverage dashboards.
- Price/area anomaly detection.
- Market statistics.

### `vision_media_agent`

Owns:

- Real-estate image review.
- Local cheap vision model pipeline.
- Room/style/condition/equipment extraction.
- Image evidence reports.

Recommended local model:

- `qwen2.5vl:3b` via Ollama for cheapest CPU use.
- `qwen2.5vl:7b` if quality is insufficient and RAM allows.
- RunPod RTX 4090 only for batch acceleration when needed.

Outputs:

- `image_report`
- room labels
- condition scores
- repair/equipment observations
- uncertainty fields

### `entity_resolution_agent`

Owns:

- Matching same properties across sources.
- Duplicate candidates.
- Property/source publication relationship.
- Conservative confidence scoring.

Rules:

- Prefer source provenance over loose same-complex inference.
- Do not merge grouped/development publications as single units.
- Require evidence: URL, price, area, floor, rooms, geospatial, media, phone/agency, text similarity.

### `fullstack_product_agent`

Owns:

- FastAPI endpoints.
- Next.js pages.
- Admin/operator review UI.
- CRM/chat/settings/product flows.
- Map/search/listing UX.

Rules:

- Public UI waits for ingestion/CRM/compliance foundations.
- Keep mock UI usable, but separate mock from production data paths.

### `knowledge_context_agent`

Owns:

- Wiki memory.
- Project insights.
- Cursor/Claude/OpenClaw knowledge capture.
- Reusable skills under `agent-skills/`.
- Cross-project knowledge mapping.

Sources:

- `/Users/getapple/core/wiki/projects/real-estate-bulgaria/`
- repo `agent-skills/`
- `.cursor/`
- `.claude/`
- `.openclaw/`
- home-level Cursor/Claude/OpenClaw knowledge when explicitly approved.

### `debugger_security_agent`

Owns:

- Acceptance gates.
- Fixture-only test policy.
- Secret scan.
- Legal/access-mode checks.
- Regression review.

## 5. Database/schema additions to plan

Likely new tables:

- `agent_run`
- `agent_task_event`
- `social_publication_candidate`
- `image_report`
- `property_match_candidate`
- `source_publication_review`
- `knowledge_artifact`

Likely new Make targets:

```make
backup-db
restore-db
verify-db-counts
scrape-tier12
scrape-tier3
scrape-tier4
vision-enrich
match-properties
agent-dashboard
```

## 6. Implementation sequence

### Phase A - safe git push

1. Update `.gitignore`.
2. Unstage unsafe files.
3. Selectively stage relevant files.
4. Secret scan staged diff.
5. Commit.
6. Push `reallystate`.

### Phase B - remote infrastructure

1. **User orders server and provides SSH.**
2. Bootstrap Ubuntu, Docker, firewall, repo, env.
3. Start base services.
4. Restore DB dump.
5. Verify counts.

### Phase C - architecture docs and task board

1. Update `docs/agents/README.md`.
2. Update `docs/agents/TASKS.md`.
3. Add ops runbooks.
4. Add or update `agent-skills/` for DB migration, tiered scraping, vision media, entity resolution, and OpenClaw remote ops.

### Phase D - automation

1. Add Make targets.
2. Add scraper schedule wrappers.
3. Add OpenClaw/Codex agent boot commands.
4. Add report cadence and failure alerts.

### Phase E - intelligence pipelines

1. Image report schema and worker.
2. Property match candidate schema and worker.
3. Social candidate ingestion and review queue.
4. Analytics dashboards.

## 7. Acceptance gates

Git:

- No `.env`.
- No DB dumps.
- No raw scrape HTML.
- No OpenClaw runtime state.
- No secrets in staged diff.
- Push succeeds.

DB migration:

- Dump checksum verified.
- Restore completes.
- Key table counts match.
- PostGIS extension works.
- App connects to remote DB.

Scraping:

- Tier 1-2, tier 3, and tier 4 run separately.
- Legal/access gates enforced.
- Social/private channels handled only by consent/manual/official routes.

Vision:

- Local model runs on sample listing images.
- Reports include uncertainty.
- Outputs remain evidence, not final facts.

Entity matching:

- Conservative match candidates.
- No auto-merge without sufficient evidence.
- Grouped/development publications stay separate.

## 8. Risks and blockers

FACT: `.env` and `.env.local` were observed in git state during planning and must not be committed.

FACT: Raw scrape captures and large scraped corpus changes can make git unusable if pushed indiscriminately.

INTERPRETATION: The safest git approach is two-stage: push code/docs/config first, migrate database separately.

HYPOTHESIS: Hetzner dedicated server is the best primary deployment target for price/performance and reliability.

GAP: Final infrastructure choice depends on payment, account availability, and whether direct API access is needed immediately.

## 9. Immediate next step

Execute Phase A first: git hygiene, safe commit, and push.

Then execute Phase B after the server is purchased and SSH access exists.
