# Continuous Development Roadmap

Date: 2026-05-13

## Phase 0 - Current State

FACT: The repo has FastAPI, Next.js, SQL schema/Alembic, Docker Compose docs, source registry, scraper scripts, dashboard artifacts, OpenClaw handoffs, and multi-agent task logs.

FACT: Action1/A1 quality gates show accepted, LOST, grouped/development, inactive, media, and description classes.

GAP: Remote server, SSH access, and live database counts are not available in this session.

## Phase 1 - Safe Git And Architecture Baseline

Owner: `ops_release_manager` plus `planner`.

Outputs:

- `.gitignore` hygiene for secrets, runtime logs, DB dumps, raw scrape captures.
- Agent architecture docs.
- Role docs for each agent.
- Skill map and MCP setup docs.
- Safe commit/push after staged secret scan.

Gate:

- No `.env`, DB dumps, raw HTML, OpenClaw runtime state, or secret-bearing diff is staged.

## Phase 2 - Server And DB Migration

Owner: `infra_db_operator`.

Outputs:

- Server selected and SSH working.
- Docker/runtime baseline installed.
- Postgres/PostGIS, Redis, MinIO, Temporal reachable privately.
- Local DB dump transferred and restored.
- Key table count comparison report.

Gate:

- Dump checksum matches.
- `make verify-db-counts` runs locally and remotely.
- App connects to remote DB with private credentials.

## Phase 3 - Action1 QA And Import Reliability

Owners: `scraper_1`, `data_analyst`, `backend_developer`, `debugger`.

Outputs:

- A1 seven-source x four-bucket counts.
- Accepted/grouped/LOST/inactive/media/description classification.
- Rescrape queues.
- DB import dry-run and live import report after migration.

Gate:

- Debugger verifies no LOST/grouped/inactive rows enter public/frontend or canonical DB by default.

## Phase 4 - Media And Vision Evidence

Owners: `vision_media_agent`, `data_analyst`, `debugger`.

Outputs:

- Full-gallery backfill queue.
- Image readability and local-file report.
- Room/style/condition/equipment reports with uncertainty.

Gate:

- Image reports are evidence only and do not overwrite source facts.

## Phase 5 - Entity Resolution And Map Truth

Owners: `entity_resolution_agent`, `backend_developer`, `ux_ui_designer`, `debugger`.

Outputs:

- Match candidate queue.
- Property/source publication relationship.
- Conservative confidence thresholds.
- Map/listing UI that labels grouped, uncertain, and verified states correctly.

Gate:

- No grouped/development page is shown as a single canonical property.
- 3D building claims require verified building footprints and match confidence.

## Phase 6 - Market And Product Intelligence

Owners: `market_intelligence_analyst`, `user_analytics_agent`, `planner`, `ux_ui_designer`.

Outputs:

- Weekly rival/source report.
- Price/supply movement notes.
- UX event taxonomy and funnel dashboards.
- Product task recommendations for filters, profiles, buttons, map modes, and saved/search flows.

Gate:

- Product changes cite market, user behavior, or operator evidence.

## Phase 7 - Launch Readiness

Owners: all, verified by `debugger` and released by `ops_release_manager`.

Outputs:

- CI/deploy pipeline.
- Production env template.
- Runbooks.
- Monitoring.
- Compliance gates.
- Public UI smoke tests.

Gate:

- No public launch until ingestion, CRM, compliance, and operator review foundations are verified.
