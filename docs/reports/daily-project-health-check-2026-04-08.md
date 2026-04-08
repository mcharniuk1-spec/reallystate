# Daily Project Health Check Report

Date: 2026-04-08
Generated at: 2026-04-08T11:42:29.065273+00:00
Workspace: `/Users/getapple/Documents/Real Estate Bulg`

## Scope

This report audits the repository state, local executable environment, fixture-backed parser coverage, export artifacts, and dependency/runtime drift.
It does not guess missing telemetry. Where the repo or environment does not provide evidence, the report explicitly says `no data available`.

## 1. Execution Monitoring (Scraping Layer)

- Scheduled scraping job telemetry: no data available
- Crawl success rate: no data available
- Failed endpoints: no data available
- Time anomalies vs baseline: no data available
- Dev worker placeholder: OK
- Dev scheduler placeholder: OK
- Tier-1 fixture coverage: 10/10 sources have fixture directories
- Offline parser regression result: passed (45 tests, 6 skipped)

Evidence:
- `PYTHONPATH=src python3 -m bgrealestate.dev_worker --once` -> 0 in 97 ms
- `PYTHONPATH=src python3 -m bgrealestate.dev_scheduler --once` -> 0 in 103 ms
- There are no scrape logs, retry logs, or persisted crawl rows available in this shell-backed run.

Registry summary:
- Tier 1: 10
- Tier 2: 17
- Tier 3: 10
- Tier 4: 7

Fixture sources:
- address_bg
- alo_bg
- bulgarianproperties
- homes_bg
- imot_bg
- imoti_net
- luximmo
- olx_bg
- property_bg
- suprimmo

## 2. Data Validation (Database Layer)

- Database validation availability: no data available
- Missing values by column: no data available
- Duplicate row checks: no data available
- Price/category anomalies: no data available
- Freshness window: no data available
- Schema consistency: blueprint and migration scaffold present; migration tests passed offline.

Reason: DATABASE_URL not set
- `DATABASE_URL` is not configured in this shell, and SQLAlchemy is not installed locally.
- The optional DB roundtrip test was skipped for the same reason.

## 3. Backend Integrity

- FastAPI runtime package: missing
- SQLAlchemy runtime package: missing
- Uvicorn runtime package: missing
- Endpoint availability/status codes/response times: no live data available
- Data flow scraper -> DB -> API: no live data available
- Static route inventory present: 13 routes defined in `src/bgrealestate/api/routers`

Defined backend routes:
- `/`
- `/admin`
- `/admin/source-stats`
- `/api/v1/chat`
- `/api/v1/ready`
- `/crawl-jobs`
- `/crm/threads`
- `/crm/threads/{thread_id}/messages`
- `/health`
- `/listings`
- `/listings/{reference_id}`
- `/sources`
- `/status`

Runtime evidence:
- Overall unit test suite: passed
- FastAPI route tests were skipped in this shell because the `fastapi` package is not installed locally.
- test_chat_stub (test_api_fastapi.TestFastAPIApp) ... skipped 'fastapi not installed in this environment'
- test_crm_threads_returns_503_without_database_url (test_api_fastapi.TestFastAPIApp) ... skipped 'fastapi not installed in this environment'
- test_health (test_api_fastapi.TestFastAPIApp) ... skipped 'fastapi not installed in this environment'
- test_listings_returns_503_without_database_url (test_api_fastapi.TestFastAPIApp) ... skipped 'fastapi not installed in this environment'
- test_ready_without_deps (test_api_fastapi.TestFastAPIApp) ... skipped 'fastapi not installed in this environment'
- This is intentionally optional: ... skipped 'DATABASE_URL not set'
- DB-backed APIs are coded to return 503 when `DATABASE_URL` is not configured.

## 4. Frontend Consistency

- Node runtime: zsh:1: command not found: node
- npm runtime: zsh:1: command not found: npm
- Frontend smoke tests: no data available
- Playwright tests: none found in the repository

Required route files:
- `app/(main)/listings/page.tsx`: present
- `app/(main)/properties/[id]/page.tsx`: present
- `app/(main)/map/page.tsx`: present
- `app/(main)/chat/page.tsx`: present
- `app/(main)/settings/page.tsx`: present
- `app/(main)/admin/page.tsx`: present

Observed UI behavior from code inspection:
- `/listings` fetches `/sources` and currently renders source-registry cards, not listing search results.
- `/chat` renders a proxy-backed assistant playground and a placeholder threads pane.
- `/map`, `/settings`, `/admin`, and `/properties/[id]` are layout shells awaiting stable APIs.
- Because Node/npm are absent, lint, typecheck, build, and browser smoke tests could not be executed.

## 5. Reporting Layer

- Existing report/export artifacts were structurally validated in this run.
- Aggregation correctness against raw ingested data: no data available
- PDF visual rendering validation: no data available (`pdftoppm` is not installed in this shell)

Export artifact checks:
- `docs/exports/bulgaria-real-estate-source-links.xlsx`: ok
- `docs/exports/bulgaria-real-estate-source-report.docx`: ok
- `docs/exports/project-status-roadmap.docx`: ok
- `docs/exports/project-architecture-execution-guide.pdf`: ok

## 6. Dependency & SDK Drift Detection

### 6.1 Detect Current State

- `.python-version`: `3.12`
- `pyproject.toml` requires Python: `>=3.12`
- CI Python target: `3.12`
- CI Node target: `22`
- Dockerfile base image: `python:3.12-slim`
- Docker Compose images: `postgis/postgis:17-3.5`, `redis:7-alpine`, `minio/minio:RELEASE.2025-04-22T22-12-26Z`, `temporalio/auto-setup:1.27`, `temporalio/ui:2.34.0`
- Local `python3`: `Python 3.9.6`
- Local `python3.12`: `zsh:1: command not found: python3.12`
- Local `node`: `zsh:1: command not found: node`
- Local `npm`: `zsh:1: command not found: npm`
- Local `docker`: `zsh:1: command not found: docker`

### 6.2 Compare with Target State

- Python target is explicitly defined by `.python-version`, CI, Dockerfile, and `pyproject.toml`.
- Node target is partially defined by CI (`22`) plus the committed Next.js manifest.
- Exact resolved dependency targets are not defined because there are no committed lockfiles.

### 6.3 Drift Types

- Version mismatch: local Python is 3.9.6 while repo targets 3.12.
- SDK/runtime mismatch: Node/npm are missing locally, so the Next.js app cannot be validated here.
- Reproducibility drift: no Python or Node lockfile is committed.
- Deprecated package status: no data available (offline, no package audit tooling installed).
- Security vulnerability status: no data available (offline, no lockfile, no audit output).

### 6.4 Drift Analysis

| Item | Current version (repo/local) | Target version | Status | Evidence |
| --- | --- | --- | --- | --- |
| Python local runtime | Python 3.9.6 | 3.12 | conflicting | `.python-version`, `pyproject.toml`, `ci.yml`, `Dockerfile` |
| Python CI runtime | 3.12 | 3.12 | aligned | `.github/workflows/ci.yml` |
| Python Docker runtime | python:3.12-slim | >=3.12 | aligned | `Dockerfile`, `pyproject.toml` |
| Node local runtime | zsh:1: command not found: node | 22 | conflicting | local shell vs CI |
| Python lockfile | none | no exact repo target defined | unknown | no `requirements*.txt` / `poetry.lock` / lock artifact committed |
| Node lockfile | none | no exact repo target defined | unknown | no `package-lock.json` / `pnpm-lock.yaml` / `yarn.lock` |
| Python dep `alembic` | `alembic>=1.15` | no exact target defined | unknown | `pyproject.toml` only |
| Python dep `asyncpg` | `asyncpg>=0.30` | no exact target defined | unknown | `pyproject.toml` only |
| Python dep `beautifulsoup4` | `beautifulsoup4>=4.13` | no exact target defined | unknown | `pyproject.toml` only |
| Python dep `boto3` | `boto3>=1.37` | no exact target defined | unknown | `pyproject.toml` only |
| Python dep `dateparser` | `dateparser>=1.2` | no exact target defined | unknown | `pyproject.toml` only |
| Python dep `fastapi` | `fastapi>=0.115` | no exact target defined | unknown | `pyproject.toml` only |
| Python dep `httpx` | `httpx>=0.28` | no exact target defined | unknown | `pyproject.toml` only |
| Python dep `imagehash` | `imagehash>=4.3` | no exact target defined | unknown | `pyproject.toml` only |
| Python dep `lxml` | `lxml>=5.3` | no exact target defined | unknown | `pyproject.toml` only |
| Python dep `openpyxl` | `openpyxl>=3.1` | no exact target defined | unknown | `pyproject.toml` only |
| Python dep `phonenumbers` | `phonenumbers>=8.13` | no exact target defined | unknown | `pyproject.toml` only |
| Python dep `pillow` | `pillow>=11.0` | no exact target defined | unknown | `pyproject.toml` only |
| Python dep `price-parser` | `price-parser>=0.5` | no exact target defined | unknown | `pyproject.toml` only |
| Python dep `psycopg[binary]` | `psycopg[binary]>=3.2` | no exact target defined | unknown | `pyproject.toml` only |
| Python dep `pydantic` | `pydantic>=2.11` | no exact target defined | unknown | `pyproject.toml` only |
| Python dep `pyproj` | `pyproj>=3.7` | no exact target defined | unknown | `pyproject.toml` only |
| Python dep `redis` | `redis>=5.2` | no exact target defined | unknown | `pyproject.toml` only |
| Python dep `shapely` | `shapely>=2.0` | no exact target defined | unknown | `pyproject.toml` only |
| Python dep `sqlalchemy` | `sqlalchemy>=2.0` | no exact target defined | unknown | `pyproject.toml` only |
| Python dep `structlog` | `structlog>=25.0` | no exact target defined | unknown | `pyproject.toml` only |
| Python dep `temporalio` | `temporalio>=1.10` | no exact target defined | unknown | `pyproject.toml` only |
| Python dep `tenacity` | `tenacity>=9.0` | no exact target defined | unknown | `pyproject.toml` only |
| Python dep `uvicorn[standard]` | `uvicorn[standard]>=0.34` | no exact target defined | unknown | `pyproject.toml` only |
| Python dev dep `mypy` | `mypy>=1.15` | no exact target defined | unknown | `pyproject.toml` only |
| Python dev dep `pytest` | `pytest>=8.3` | no exact target defined | unknown | `pyproject.toml` only |
| Python dev dep `ruff` | `ruff>=0.11` | no exact target defined | unknown | `pyproject.toml` only |
| Node package `@deck.gl/core` | `^9.1.0` | no exact target defined | unknown | `package.json` only |
| Node package `@deck.gl/layers` | `^9.1.0` | no exact target defined | unknown | `package.json` only |
| Node package `@deck.gl/react` | `^9.1.0` | no exact target defined | unknown | `package.json` only |
| Node package `@tanstack/react-query` | `^5.74.0` | no exact target defined | unknown | `package.json` only |
| Node package `maplibre-gl` | `^5.3.0` | no exact target defined | unknown | `package.json` only |
| Node package `next` | `^15.3.0` | no exact target defined | unknown | `package.json` only |
| Node package `react` | `^19.1.0` | no exact target defined | unknown | `package.json` only |
| Node package `react-dom` | `^19.1.0` | no exact target defined | unknown | `package.json` only |
| Node package `zod` | `^3.24.0` | no exact target defined | unknown | `package.json` only |
| Node package `@playwright/test` | `^1.52.0` | no exact target defined | unknown | `package.json` only |
| Node package `@types/node` | `^22.14.0` | no exact target defined | unknown | `package.json` only |
| Node package `@types/react` | `^19.1.0` | no exact target defined | unknown | `package.json` only |
| Node package `@types/react-dom` | `^19.1.0` | no exact target defined | unknown | `package.json` only |
| Node package `autoprefixer` | `^10.4.21` | no exact target defined | unknown | `package.json` only |
| Node package `eslint` | `^9.25.0` | no exact target defined | unknown | `package.json` only |
| Node package `eslint-config-next` | `^15.3.0` | no exact target defined | unknown | `package.json` only |
| Node package `postcss` | `^8.5.3` | no exact target defined | unknown | `package.json` only |
| Node package `prettier` | `^3.5.0` | no exact target defined | unknown | `package.json` only |
| Node package `tailwindcss` | `^3.4.17` | no exact target defined | unknown | `package.json` only |
| Node package `typescript` | `^5.8.0` | no exact target defined | unknown | `package.json` only |

## 7. Minimal Alignment Plan

Preferred option: Conservative

1. Install the declared runtimes without changing package versions.
2. Re-run the audit on Python 3.12 with FastAPI/SQLAlchemy/Uvicorn installed.
3. Commit lockfiles only after a clean install succeeds and tests pass.
4. Add DB-backed validation once `DATABASE_URL` points to the Compose PostgreSQL service.
5. Add frontend lint/typecheck and at least one Playwright smoke test once Node/npm are present.

Conservative plan (preferred):
- Python: align local shell to 3.12. Risk: low. Impact: unlocks backend validation without changing app code.
- Node: install Node 22 to match CI. Risk: low. Impact: unlocks Next.js lint/typecheck/build validation.
- Lockfiles: commit one Python lock artifact and one Node lockfile. Risk: low-medium. Impact: reproducible installs.
- Database: run Compose services and migrations, then enable DB checks in this audit. Risk: low-medium. Impact: actual scrape/data freshness metrics become available.

Progressive plan (suggestion):
- After lockfiles exist, review patch/minor upgrades for FastAPI, SQLAlchemy, Next.js, React, and TypeScript. Risk: medium. Impact: modernized stack with broader test surface.
- Add package audit tooling and a CI dependency drift job. Risk: medium. Impact: real vulnerability/deprecation visibility.

## 8. Final Report

### 8.1 System Status Summary

- Scraping: Issues
- Data: Issues
- Backend: Issues
- Frontend: Issues

### 8.2 Key Issues

1. Local runtime does not satisfy the repo contract: Python 3.12 is required, but only Python 3.9.6 is available; Node/npm/docker are missing.
2. There is no live ingestion telemetry or database dataset in this environment, so scrape success rate, freshness, duplicate counts, and anomaly checks are unavailable.
3. Backend route files exist, but FastAPI/SQLAlchemy/Uvicorn are not installed locally, so endpoint execution is not validated in this shell.
4. The Next.js route scaffold exists, but frontend build/smoke validation is blocked by the missing Node toolchain and the absence of Playwright specs.
5. Dependency resolution is not reproducible yet because there are no committed Python or Node lockfiles.

### 8.3 Drift Summary

- Python runtime mismatch: local 3.9.6 vs target 3.12.
- Node runtime mismatch: local missing vs CI target 22.
- No committed lockfile for Python.
- No committed lockfile for Node.
- Exact vulnerability/deprecation state cannot be determined from this offline shell.

### 8.4 Recommended Actions

1. Install Python 3.12 locally and run the backend stack with committed dev dependencies.
2. Install Node 22/npm, then run `npm install`, `npm run lint`, and `npm run typecheck`.
3. Start Compose services and set `DATABASE_URL` so this report can compute live scrape/data metrics.
4. Commit dependency lockfiles after a clean green run on Python 3.12 and Node 22.
5. Add one frontend smoke test and one DB-backed golden-path validation script to close the current observability gaps.

### 8.5 Logs Appendix

Tooling errors:
- `python3.12 --version`: zsh:1: command not found: python3.12
- `node --version`: zsh:1: command not found: node
- `npm --version`: zsh:1: command not found: npm
- `docker --version`: zsh:1: command not found: docker
- `pdftoppm -v`: zsh:1: command not found: pdftoppm

Execution traces:
- Unit tests (`174 ms`):
```text
test_chat_stub (test_api_fastapi.TestFastAPIApp) ... skipped 'fastapi not installed in this environment'
test_crm_threads_returns_503_without_database_url (test_api_fastapi.TestFastAPIApp) ... skipped 'fastapi not installed in this environment'
test_health (test_api_fastapi.TestFastAPIApp) ... skipped 'fastapi not installed in this environment'
test_listings_returns_503_without_database_url (test_api_fastapi.TestFastAPIApp) ... skipped 'fastapi not installed in this environment'
test_ready_without_deps (test_api_fastapi.TestFastAPIApp) ... skipped 'fastapi not installed in this environment'
test_fixture_harness_imports_without_optional_runtime (test_connector_fixtures_smoke.TestConnectorFixtureHarness) ... ok
test_alembic_scaffold_exists (test_database_migrations.DatabaseMigrationTests) ... ok
test_initial_migration_is_syntax_valid_without_alembic_installed (test_database_migrations.DatabaseMigrationTests) ... ok
test_initial_migration_reuses_schema_blueprint (test_database_migrations.DatabaseMigrationTests) ... ok
test_make_migrate_points_to_alembic (test_database_migrations.DatabaseMigrationTests) ... ok
test_schema_blueprint_contains_core_mvp_tables (test_database_migrations.DatabaseMigrationTests) ... ok
test_source_registry_includes_planning_columns (test_database_migrations.DatabaseMigrationTests) ... ok
test_db_package_does_not_import_sqlalchemy_on_package_import (test_database_models.DatabaseModelTests) ... ok
test_model_foundation_covers_core_mvp_areas (test_database_models.DatabaseModelTests) ... ok
test_sqlalchemy_model_file_is_syntax_valid_without_dependencies_installed (test_database_models.DatabaseModelTests) ... ok
test_optional_db_roundtrip (test_db_roundtrip_optional.TestDbRoundtripOptional)
This is intentionally optional: ... skipped 'DATABASE_URL not set'
test_skips_without_database_url (test_golden_path_check.TestGoldenPathCheck) ... ok
test_homes_bg_fixtures (test_homes_bg_fixture_parsing.TestHomesBgFixtureParsing) ... ok
test_homes_uses_specialized_class (test_marketplace_connectors.TestConnectorFactory) ... ok
test_other_uses_scaffold (test_marketplace_connectors.TestConnectorFactory) ... ok
test_licensing_blocks_ingestion (test_marketplace_connectors.TestLegalDerivation) ... ok
test_partner_blocks_scrape (test_marketplace_connectors.TestLegalDerivation) ... ok
test_public_crawl_allows_http_gate (test_marketplace_connectors.TestLegalDerivation) ... ok
test_excludes_social_and_messenger (test_marketplace_connectors.TestMarketplaceScope) ... ok
test_is_marketplace_source (test_marketplace_connectors.TestMarketplaceScope) ... ok
test_olx_bg_fixtures (test_olx_bg_fixture_parsing.TestOlxBgFixtureParsing) ... ok
test_dedupe_scorer_prefers_near_duplicate (test_pipeline.PipelineTests) ... ok
test_pipeline_processes_apartment_detail_page (test_pipeline.PipelineTests) ... ok
test_airbnb_payload_contains_sync_flags (test_publishing.PublishingTests) ... ok
test_blocking_compliance_flag_stops_publish (test_publishing.PublishingTests) ... ok
test_booking_listing_is_eligible (test_publishing.PublishingTests) ... ok
test_matrix_exports_include_seeded_sources (test_source_registry.SourceRegistryTests) ... ok
test_registry_contains_key_priority_sources (test_source_registry.SourceRegistryTests) ... ok
test_registry_exposes_agent_planning_fields (test_source_registry.SourceRegistryTests) ... ok
test_registry_filters_legal_review_queue (test_source_registry.SourceRegistryTests) ... ok
test_registry_loads_expected_tiers (test_source_registry.SourceRegistryTests) ... ok
test_imoti_net_blocks_live_http (test_tier1_html_fixture_parsing.TestImotiNetLegalGate) ... ok
test_address_bg (test_tier1_html_fixture_parsing.TestTier1HtmlFixtureParsing) ... ok
test_alo_bg (test_tier1_html_fixture_parsing.TestTier1HtmlFixtureParsing) ... ok
test_bulgarianproperties (test_tier1_html_fixture_parsing.TestTier1HtmlFixtureParsing) ... ok
test_imot_bg (test_tier1_html_fixture_parsing.TestTier1HtmlFixtureParsing) ... ok
test_imoti_net (test_tier1_html_fixture_parsing.TestTier1HtmlFixtureParsing) ... ok
test_luximmo (test_tier1_html_fixture_parsing.TestTier1HtmlFixtureParsing) ... ok
test_property_bg (test_tier1_html_fixture_parsing.TestTier1HtmlFixtureParsing) ... ok
test_suprimmo (test_tier1_html_fixture_parsing.TestTier1HtmlFixtureParsing) ... ok

----------------------------------------------------------------------
Ran 45 tests in 0.057s

OK (skipped=6)
```
- Dev worker (`97 ms`):
```text
dev worker started
note: this is a lightweight placeholder; implement Temporal worker in Stage 3.
dev worker heartbeat 2026-04-08T11:42:29.600230+00:00
```
- Dev scheduler (`103 ms`):
```text
dev scheduler started
note: this is a lightweight placeholder; implement durable Temporal scheduling in Stage 3.
dev scheduler heartbeat 2026-04-08T11:42:29.702817+00:00 | sources=44 | tier1-cadence-candidates=10
```

Repo state notes:
- Dirty worktree entries observed: 44
-  M Dockerfile
-  M Makefile
-  M docs/agent-skills-index.md
-  M docs/agents/README.md
-  M docs/agents/backend_developer/JOURNEY.md
-  M docs/agents/debugger/JOURNEY.md
-  M docs/agents/scraper_1/JOURNEY.md
-  M docs/development-setup.md
-  M docs/exports/platform-mvp-plan.md
-  M docs/exports/project-status-roadmap.docx
-  M docs/exports/project-status-roadmap.md
-  M scripts/validate_project.py
-  M src/bgrealestate/api/main.py
-  M src/bgrealestate/connectors/factory.py
-  M src/bgrealestate/connectors/scaffold.py
-  M src/bgrealestate/db/repositories.py
-  M src/bgrealestate/pipeline.py
-  M tests/fixtures/homes_bg/basic_listing/expected.json
-  M tests/fixtures/homes_bg/missing_geo/expected.json
-  M tests/fixtures/homes_bg/missing_price/expected.json
-  M tests/test_api_fastapi.py
- ?? agent-skills/debugger-golden-path/
- ?? docs/agents/TASKS.md
- ?? docs/reports/daily-project-health-check-2026-04-08.md
- ?? output/
