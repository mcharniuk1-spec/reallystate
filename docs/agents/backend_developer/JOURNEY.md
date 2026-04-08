# Backend developer (data engineer) journey

## Scope
- Backend structure, persistence, ingestion orchestration, data modeling, and APIs.
- Define where/how scraped results are stored (PostgreSQL + object store) and how they flow to stats and UI.

## Task backlog (from scope + `PLAN.md` §6–7)

| ID | Task | Status |
|----|------|--------|
| B-01 | PostgreSQL/PostGIS + Alembic + Docker Compose baseline | done (pre-existing) |
| B-02 | FastAPI app: health, sources, readiness, chat stub / optional OpenAI | done (pre-existing + extended) |
| B-03 | Admin / analytics: per-source stats API + HTML (`/admin`) | done (pre-existing) |
| B-04 | **Listings API**: `GET /listings`, `GET /listings/{reference_id}` backed by `canonical_listing` | **done (2026-04-08)** |
| B-05 | **CRM API**: `GET /crm/threads`, `GET /crm/threads/{id}/messages`, `POST .../messages` (manual operator notes) | **done (2026-04-08)** |
| B-06 | **Crawl API**: `GET /crawl-jobs` (recent jobs) | **done (2026-04-08)** |
| B-07 | Shared DB session dependency for FastAPI (`get_db` / `get_engine`) | **done (2026-04-08)** |
| B-08 | Repository layer: `CanonicalListingRepository.list_recent` / `get`, `CrmRepository`, `CrawlJobRepository` | **done (2026-04-08)** |
| B-09 | Auth / RBAC on CRM and listings routes | not started |
| B-10 | `GET /parser-failures`, `GET /properties/{id}`, map viewport APIs | not started |
| B-11 | Temporal workflow wiring beyond dev worker/scheduler stubs | not started |
| B-12 | **DB sync + control plane bootstrap** (TASKS.md slice) | **done (2026-04-08 session 2)** |
| B-13 | Stats v2: photo coverage + intent/category breakdown | not started |

## Executed tasks (append-only)

### 2026-04-08 — Listings, CRM, crawl APIs + DB dependencies

**Goal:** Close the gap between `PLAN.md` §7 route list and the running FastAPI service so the Next.js `/api/backend/*` proxy and future UI can consume real data from PostgreSQL.

**Rationale:**
- **Persistence is already modeled** (`CanonicalListingModel`, `LeadThreadModel`, `LeadMessageModel`, `CrawlJobModel`) with repositories for ingestion; read APIs were missing for UI/analytics consumers.
- **Dependency injection:** Routes that need Postgres must fail clearly when `DATABASE_URL` is unset (local dev without DB, misconfigured server). A shared `get_engine` / `get_db` avoids duplicating engine creation and returns **503** with a JSON `detail`, which is easy to handle in the BFF.
- **CRM POST** implements only **manual operator notes** (`direction=outbound`, `metadata.kind=manual_note`) to stay within compliance: no simulated channel sync and no fake "inbound" customer messages.
- **Ordering:** Messages ordered by `received_at` / `sent_at` ascending (nulls first) matches inbox chronology for typical rows; threads ordered by `last_message_at` descending.

**Changed files:**
- `src/bgrealestate/api/deps.py` — `get_engine`, `get_db` (503 if no `DATABASE_URL`; session commit/rollback).
- `src/bgrealestate/api/main.py` — register `listings`, `crm`, `crawl_jobs` routers.
- `src/bgrealestate/api/routers/listings.py` — new.
- `src/bgrealestate/api/routers/crm.py` — new.
- `src/bgrealestate/api/routers/crawl_jobs.py` — new.
- `src/bgrealestate/db/repositories.py` — `CrawlJobRepository`, `CrmRepository`, `CanonicalListingRepository.list_recent`, `CanonicalListingRepository.get`; imports for CRM/crawl models; `timezone` for message timestamps.
- `tests/test_api_fastapi.py` — `test_listings_returns_503_without_database_url`, `test_crm_threads_returns_503_without_database_url`; reset `deps._engine` so env changes are respected.

**Verification:**
- `PYTHONPATH=src python3 -m unittest discover -s tests -v` — OK (FastAPI tests skipped if `fastapi` not installed locally; CI installs deps and runs them).
- With `DATABASE_URL` + migrated DB: `GET /listings`, `GET /crm/threads`, `GET /crawl-jobs` return JSON lists; `GET /listings/{id}` returns 404 when missing.

**Example requests (local):**
- `curl -s http://127.0.0.1:8000/listings?limit=10`
- `curl -s http://127.0.0.1:8000/crm/threads`
- `curl -s http://127.0.0.1:8000/crawl-jobs`
- Via Next proxy: `http://localhost:3000/api/backend/listings`

---

### 2026-04-08 session 2 — DB sync + control plane bootstrap (TASKS.md slice)

**Task source:** `docs/agents/TASKS.md` → Backend_developer → "DB sync + control plane bootstrap"

**Goal:** Make `sync_marketplace_sources_to_db` verifiable end-to-end: sync the registry into Postgres (source_registry + source_legal_rule + source_endpoint), verify via `GET /api/v1/ready` and `GET /admin/source-stats`, export `docs/exports/source-stats.xlsx`.

**Rationale and decisions:**

1. **`source_stats.py` upgraded from ingestion-only to registry-aware.**
   The original query only joined `canonical_listing` and `raw_capture`, so an empty DB after `sync_marketplace_sources_to_db` would return zero rows even though the control plane (registry + legal rules + endpoints) was populated. The query now LEFT JOINs from `source_registry` outward to `canonical_listing`, `raw_capture`, `source_legal_rule`, and `source_endpoint`. This means:
   - After `make sync-registry`, the stats show all 37 marketplace sources with `has_legal_rule=true` and `has_endpoint=true/false`, even before any crawl has produced data.
   - The `tier` and `legal_mode` columns are included in the API response and XLSX so operators can see the control plane status at a glance.

2. **`/admin/source-stats` now uses the shared `deps.get_engine`** instead of creating a throwaway engine per request. This means:
   - Returns 503 consistently when `DATABASE_URL` is missing (same behavior as `/listings`, `/crm/threads`).
   - Removed unused `os` and `create_engine` imports.

3. **`export_source_stats_xlsx.py` upgraded** with the new columns (`tier`, `legal_mode`, `has_legal_rule`, `has_endpoint`), styled header row, and auto-column-width.

4. **Makefile targets added:**
   - `make sync-registry` — runs `python -m bgrealestate sync-database` (upserts sources, legal rules, primary endpoints).
   - `make export-source-stats` — runs `scripts/export_source_stats_xlsx.py`.

5. **Admin HTML dashboard extended** with Tier, Legal mode, Legal rule (Y/N), and Endpoint (Y/N) columns.

6. **New test file `tests/test_control_plane.py`:**
   - `TestDbSyncImport` — syntax-valid `db_sync.py`; CLI `sync-database --dry-run` returns 0; `marketplace_sources` excludes social/messenger families.
   - `TestExportScriptSyntax` — syntax-valid `export_source_stats_xlsx.py`.
   - `TestSourceStatsModel` — `SourceStatRow` dataclass has the new `tier`, `has_legal_rule`, `has_endpoint` fields (skipped without SQLAlchemy).
   - `TestReadinessEndpoint` — `GET /api/v1/ready` returns 200/ok when env vars are unset; `GET /admin/source-stats` returns 503 when `DATABASE_URL` is unset (skipped without FastAPI).

**Changed files:**
- `src/bgrealestate/stats/source_stats.py` — `SourceStatRow` extended with `tier`, `legal_mode`, `has_legal_rule`, `has_endpoint`; query now LEFT JOINs from `source_registry`.
- `src/bgrealestate/api/routers/admin.py` — uses `deps.get_engine`; serializer includes new fields; HTML table extended; removed unused imports.
- `scripts/export_source_stats_xlsx.py` — new columns, styled header, auto-width.
- `Makefile` — `sync-registry`, `export-source-stats` targets.
- `tests/test_control_plane.py` — new (7 tests, 3 guard-skipped without optional deps).

**Verification:**
```
PYTHONPATH=src python3 -m unittest discover -s tests -v
# 56 tests, 0 failures, 9 skipped (missing deps / no DB)
# Key new tests:
#   test_cli_sync_database_dry_run ... ok
#   test_marketplace_sources_excludes_social ... ok
#   test_db_sync_is_syntax_valid ... ok
#   test_export_source_stats_xlsx_is_syntax_valid ... ok
```

**End-to-end sequence (with Postgres):**
```bash
make dev-up
export DATABASE_URL=postgresql+psycopg://bgrealestate:bgrealestate@localhost:5432/bgrealestate
make db-init           # alembic upgrade head
make sync-registry     # upserts 37 marketplace sources + legal rules + endpoints
curl -s http://127.0.0.1:8000/api/v1/ready   # {"status":"ok","checks":[{"name":"postgres","ok":true,...},...]}
curl -s http://127.0.0.1:8000/admin/source-stats | python3 -m json.tool
make export-source-stats  # writes docs/exports/source-stats.xlsx
```

## Review comments (after each task)

### After 2026-04-08 slice
- **Auth:** All new routes are unauthenticated; next backend slice should add API keys or session auth aligned with `app_user` / `api_key` tables before any production exposure.
- **Pagination:** List endpoints use limit/offset only; consider cursor-based pagination for large `canonical_listing` volumes.
- **CRM:** `POST /crm/threads/{id}/messages` only appends operator text; channel webhooks and assignment events remain future work.
- **Errors:** DB connection failures surface as 500; optional middleware could map `OperationalError` to 503 for clearer ops behavior.
- **Tests:** Integration tests against a disposable Postgres (e.g. CI service container) would validate serializers and FK constraints end-to-end.

### After 2026-04-08 session 2 — control plane bootstrap
- **XLSX output only when DB is live:** `make export-source-stats` fails fast if `DATABASE_URL` is not set. This is intentional — the XLSX is a snapshot of actual DB state, not a stub. The `make golden-path` script also covers this path (see debugger agent JOURNEY).
- **Stats v2 (next slice in `TASKS.md`):** Photo coverage (`image_urls != '[]'`) and intent/category breakdown from `canonical_listing` are not yet in the stats query. The query structure now makes it easy to add extra CTEs.
- **Admin HTML is server-rendered JS:** For now the `/admin` page is a single inline `<script>` that calls `/admin/source-stats`. Once the Next.js frontend is mature, the admin page should move there.
- **Engine-per-request risk for readiness:** `/api/v1/ready` still creates a fresh engine inside `_check_postgres()` (not via `deps.get_engine`), because readiness must work even when `get_engine` itself would throw 503. This is the one intentional exception.
- **Blocker:** Docker was unavailable in this session's sandbox, so the Python 3.12 full-dep Docker test (`make test-docker`) was not run. CI (GitHub Actions) covers this.
