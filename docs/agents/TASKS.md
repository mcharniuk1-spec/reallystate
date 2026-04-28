# Agent Task Queue

Single source of truth for **what to do next** per specialist agent.

**Rules** (see `docs/agents/README.md` for the full protocol):

- One active slice per agent at a time.
- When done, set status to `DONE_AWAITING_VERIFY` and wait for the verifier.
- When verified, verifier sets status to `VERIFIED`.
- If blocked, record the blocker (points to another slice ID) and propose an alternative.
- Append a journal entry to `docs/agents/<agent>/JOURNEY.md` after every slice (done or blocked).

**Statuses**: `TODO` → `IN_PROGRESS` → `DONE_AWAITING_VERIFY` → `VERIFIED` / `BLOCKED`

**Goal**: Working website at `https://bgrealestate.vercel.app` (frontend) + `https://bgrealestate-api.up.railway.app` (backend) with live scrapers, unified database, map, shop view, user profiles, and admin dashboard.

**Hosting stack**: Railway (PostgreSQL+PostGIS, Python backend, scraper workers) + Vercel (Next.js frontend) + GitLab CI/CD.

## Session backlog context digest (2026-04-08)

This digest captures the full operator intent and execution context from the latest orchestration chat so no agent loses strategic direction between activations.

### A) Locked scope and product intent

- Build a LUN-style, buyer-oriented marketplace with map + feed + AI chat.
- Owners are the primary posters; agency participants are represented as owner representatives.
- MVP **3D / building-data** focus may remain Varna-first (BD-08 / UX-07); **map + listings browse UX (`UX-04`)** is **nationwide Bulgaria** (all regions/cities), not Varna-only.
- Scraping/output must feed a continuously updated database with canonical unification and exports.

### B) Agent governance and runtime behavior

- Parallel lanes are required; dependencies are enforced at slice level.
- Tier ownership is strict:
  - `scraper_1`: tier-1/2
  - `scraper_t3`: tier-3
  - `scraper_sm`: tier-4
- No slice is complete before verifier promotion to `VERIFIED`.
- Non-stop continuation is mandatory for every agent:
  - continue to next unblocked slice after each completion
  - stop only on `END`, no unblocked slices, or real blocker
  - when idle, ask: `Which <agent_name> task should I execute next?`

### C) Session deliverables already completed

- Business/model outputs completed:
  - `docs/business/unit-economics-market-analysis.md`
  - `docs/business/product-ux-structure.md`
  - `docs/business/varna-3d-osm-integration.md`
  - `output/pdf/investor-presentation-2026-04-08.pdf`
- Backlog enriched with new backend/frontend/scraper/debugger/lead slices for deployment-ready execution.
- Dashboard reliability issue fixed (embedded payload support for local `file://` opens) and dashboard regenerated.

### D) Immediate execution priorities (2026-04-09 — operator lock-in)

**Single focus lane until the volume gate is met:** `scraper_1` tier-1/2 live harvesting. Other specialists **do not start new non-blocking slices** except the narrow backend prerequisite below and recurring `CONST-*` hygiene.

1. **`scraper_1` — non-stop until volume gate (see `S1-18`)**  
   Implement/complete live HTTP + discovery + detail ingest (`S1-15`), then **continue running harvests without pausing for “slice done”** until **at least 5 distinct tier-1 or tier-2 sources** each have **≥100** persisted listing rows (see `S1-18` for counting rules).

2. **`backend_developer` — prerequisite only until `S1-18` is met**  
   **`BD-11` is the mandatory prerequisite** so live scrapes can land in `canonical_listing` (and related tables) for auditable counts. **Do not** treat `BD-12`–`BD-16` as in-scope for the same sprint wave as `S1-18` unless they unblock ingest. After `S1-18` is `VERIFIED`, resume the backend chain: `BD-12` → `BD-13` → `BD-14` → `BD-15` → …

3. **`debugger` — planned after backend chain catches up**  
   - **`DBG-06`**: batch-verify all `DONE_AWAITING_VERIFY` slices **after** `S1-18` is `VERIFIED` and **`BD-11` ingest is proven** on live rows (or operator explicitly waives DB counts — document in JOURNEY).  
   - **`DBG-05`**: stage-1 quality gate (fixtures + product types per `docs/exports/stage1-product-type-coverage.md`) **after** live volume evidence exists or is explicitly deferred.

4. **Parked (do not expand until `S1-18` VERIFIED):** new `scraper_t3` / `scraper_sm` live work, LUN-style UX expansion (`UX-04`–`UX-12`), and deployment slices — unless they fix a blocker for tier-1/2 ingest.

5. **Recurring:** `CONST-01` / `CONST-02`, `LEAD-05` dashboard refresh after any TASKS/JOURNEY change.

**Fixture / stage-1 analysis (no live DB):** `docs/exports/stage1-product-type-coverage.md` — all required product types (`sale`, `long_term_rent`, `short_term_rent`, `land`, `new_build`) are covered by tier-1/2 fixtures; this is **parser readiness**, not production volume.

---

## Constant recurring slices (all agents)

### CONST-01: Activation sync + dashboard refresh
- **Status**: `TODO` (recurring)
- **Read first**: `docs/agents/TASKS.md`, all `docs/agents/*/JOURNEY.md`, `docs/dashboard/index.html`
- **Do**: on each activation, review progress deltas, update task dependencies/notes, and regenerate dashboard/exports after doc/task changes
- **Acceptance gate**: latest run updates `TASKS.md` + dashboard JSON/HTML timestamps
- **Output**: refreshed `docs/exports/progress-dashboard.json`, `docs/dashboard/index.html`, `docs/exports/parallel-execution-timeline.md`, `docs/exports/scraper-activity-snapshot.md`, and updated task notes
- **Verifier**: debugger
- **Depends on**: —

### CONST-02: Cross-agent note propagation
- **Status**: `TODO` (recurring)
- **Read first**: latest entries in all `JOURNEY.md` files
- **Do**: convert blockers/findings from one agent into explicit follow-up tasks for impacted agents, and preserve recurring scraper evidence rules in the affected task notes
- **Standing scraper memory**:
  - for each property item, try to identify the full gallery on the detail page
  - download all reachable item photos, not only the lead thumbnail or first image
  - check whether the downloaded photos are readable or decodable, and record partial-gallery failures
  - treat full item capture as the default target: description, attributes, contacts, and the full reachable media set
  - store image binaries as local files under `data/media/<reference_id>/...`; keep remote image URLs only as traceability metadata, not as the primary image storage
  - only call a source `Patterned` when one saved sample item proves local image-file capture for the full reachable gallery and also lands the core item fields (`price` plus `city` or `address`) and at least two structured fields such as `area`, `rooms`, `floor`, or `phones`
  - for each website, find the reusable parsing pattern for every property/service route and save that pattern as code before calling the source `Patterned`
  - keep a website-level status split between item-pattern readiness and count-method readiness; do not mark a source fully ready if live counts are still estimate-only
  - the recurring scraper_1 operating loop is incremental: every 15 minutes append new listings, refresh changed listings, and mark disappeared listings inactive instead of silently dropping them
  - after every scrape run, refresh source metrics with explicit counts for:
    - saved items started out of latest saved website-total count
    - fully parsed/full-gallery items out of saved items
    - description coverage out of saved items
    - local/remote image capture totals plus average images per item
    - image-description coverage out of saved local images
  - dashboard metrics must use source-total counts for operator views; threshold-only counters such as `100` belong only in dedicated control-plane views
- **Acceptance gate**: each blocker has at least one mapped follow-up slice with dependency, and scraper-facing follow-ups keep the full-item/full-gallery requirement visible
- **Output**: updated `TASKS.md` dependencies and notes
- **Verifier**: lead agent + debugger
- **Depends on**: —

---

## ═══════════════════════════════════════════════════════
## BACKEND_DEVELOPER (data engineer + infrastructure)
## ═══════════════════════════════════════════════════════

**Mission**: Create the full backend (DB, APIs, scraper orchestration, auth, user profiles, deployment) that powers the website. Every endpoint must work end-to-end from database to frontend.

**2026-04-09 wave:** Until **`S1-18`** is `VERIFIED`, treat **`BD-11`** (live ingest → `canonical_listing`) as the **only** must-ship backend slice. Defer **`BD-12`–`BD-16`** unless they unblock ingest or the operator reprioritizes.

### BD-01: DB sync + control plane bootstrap
- **Status**: `VERIFIED` — hardened 2026-04-08 session 2 (stats query registry-aware, admin dashboard extended, tests added)
- **Read first**: `docs/development-setup.md`, `src/bgrealestate/db_sync.py`, `src/bgrealestate/connectors/legal.py`, `sql/schema.sql`
- **Do**: run Compose + migrations, sync registry into Postgres (`source_registry`, `source_legal_rule`, `source_endpoint`)
- **Acceptance gate**: `GET /api/v1/ready` returns 200; `GET /admin/source-stats` returns JSON with all registry sources (tier, legal_mode, has_legal_rule, has_endpoint); `make export-source-stats` writes XLSX
- **Output**: `docs/exports/source-stats.xlsx` via `scripts/export_source_stats_xlsx.py`; `tests/test_control_plane.py`
- **Verifier**: debugger
- **Depends on**: —

### BD-02: Listings, CRM, Crawl APIs + DB dependencies
- **Status**: `VERIFIED`
- **Read first**: `src/bgrealestate/api/`, `src/bgrealestate/db/repositories.py`, `PLAN.md` §7
- **Do**: `GET /listings`, `GET /listings/{id}`, `GET /crm/threads`, `GET /crm/threads/{id}/messages`, `POST .../messages` (manual notes only), `GET /crawl-jobs`; shared `get_engine`/`get_db` deps
- **Acceptance gate**: `make test` passes; API returns 503 cleanly when `DATABASE_URL` unset; with DB, returns JSON lists
- **Output**: API routes registered in FastAPI; repository methods for list/get
- **Verifier**: debugger + scraper_1 (API contracts match what connectors write)
- **Depends on**: BD-01

### BD-03: Stats v2 (coverage breakdown)
- **Status**: `VERIFIED` (2026-04-08; debugger acceptance gate pass)
- **Read first**: `src/bgrealestate/api/routers/`, `src/bgrealestate/db/repositories.py`
- **Do**: extend stats to include photo coverage and intent/category breakdown from `canonical_listing`
- **Acceptance gate**: `/admin` dashboard shows coverage bars; XLSX export includes new columns
- **Output**: updated `/admin` dashboard + XLSX export
- **Verifier**: debugger
- **Depends on**: BD-02
- **Resolution**: updated `tests/test_control_plane.py` for expanded `SourceStatRow`; `make validate` passes.

### BD-04: Auth / RBAC on CRM and listings routes
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08)
- **Read first**: `sql/schema.sql` (app_user, api_key, permission_grant), `PLAN.md` §7
- **Do**: API key or session auth middleware; protect CRM write + listings write + admin routes
- **Acceptance gate**: unauthenticated requests return 401/403; `make test` passes with auth fixtures
- **Output**: auth middleware + test fixtures
- **Resolution**: implemented API-key scope checks (`listings:read`, `crm:read`, `crm:write`, `crawl:read`, `admin:read`) with route protection and auth tests.
- **Verifier**: debugger (Bugbot priority: auth/RBAC)
- **Depends on**: BD-02

### BD-05: Temporal workflow wiring
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08: Temporal worker/scheduler runtime scaffold implemented)
- **Read first**: `src/bgrealestate/dev_worker.py`, `src/bgrealestate/dev_scheduler.py`, `agent-skills/workflow-runtime/SKILL.md`
- **Do**: replace dev stubs with real Temporal worker + scheduler; implement `SourceDiscoveryWorkflow` and `ListingDetailWorkflow`
- **Acceptance gate**: jobs survive worker restart; cursors persist; `make test` passes
- **Output**: Temporal workflows, workers, scheduler config
- **Verifier**: debugger (idempotency + restart survival)
- **Depends on**: BD-01, BD-02
- **Verifier note**: run live check with Temporal service (`ENABLE_TEMPORAL_RUNTIME=1`) to confirm restart survival and persistent cursor behavior.

### BD-06: Map/search + chat context APIs (geo scope configurable)
- **Status**: `TODO`
- **Read first**: `PLAN.md` §8, `src/bgrealestate/api/routers/listings.py`, `src/bgrealestate/api/routers/chat.py`, `sql/schema.sql`
- **Do**: expose **configurable** geo scope for `/listings` + map-related contracts: **default = all Bulgaria** (no forced Varna filter). Support optional query params or feature flags for **Varna preset** (city/region bbox) for demos and 3D pilot. Expose chat context payload so AI chat can always view current property + active map filter state.
- **Acceptance gate**: API contract tests prove (a) default/nationwide listing queries return Bulgaria-wide results when data exists, (b) optional Varna scope filter works when requested, (c) chat context returns selected property + active filters
- **Coordination**: **`UX-04`** is **nationwide**; do not ship APIs that hard-lock clients to Varna-only unless behind an explicit opt-in flag.
- **Output**: API contract docs + tests + route updates
- **Verifier**: debugger + ux_ui_designer
- **Depends on**: BD-02, BD-03, DBG-05

### BD-07: AI chat API bridge for property-aware search assistant
- **Status**: `TODO`
- **Read first**: `src/bgrealestate/api/routers/chat.py`, `PLAN.md` §8, UX-05 task
- **Do**: create backend chat bridge endpoint to selected AI chat API with retrieval context from current property item + active listing/map filters
- **Acceptance gate**: chat endpoint returns responses that include referenced property IDs and active filter echo; tests cover fallback/error states
- **Output**: chat bridge contract + tests + provider adapter
- **Verifier**: debugger + ux_ui_designer
- **Depends on**: BD-06

### BD-08: Varna OSM 3D building data pipeline
- **Status**: `TODO`
- **Read first**: `docs/business/varna-3d-osm-integration.md`, `sql/schema.sql` (building_entity)
- **Do**: download GeoFabrik Bulgaria extract, clip to Varna bbox, extract buildings with height/levels, import into PostGIS `building_entity`, generate PMTiles for MapLibre 3D extrusion
- **2026-04-28 product note**: homepage now uses OSM raster base map with at most 20 aggregated city/district points. Do not treat synthetic marker clusters as building-level geospatial objects. This slice must provide real address/coordinate → OSM/PostGIS building footprint matches before the UI can highlight actual buildings.
- **Acceptance gate**: `scripts/import_osm_buildings_varna.py` runs on fixture/sample data; PostGIS query returns building footprints; PMTiles file generated
- **Output**: `scripts/import_osm_buildings_varna.py`, `data/tiles/varna-buildings.pmtiles`, migration for building_entity enrichment, tests
- **Verifier**: debugger + ux_ui_designer
- **Depends on**: BD-01

### BD-09: Property analytics views + duplicate detection
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08: SQL views + API endpoints implemented)
- **Read first**: `sql/schema.sql`, `src/bgrealestate/db/repositories.py`
- **Do**: create SQL views `v_property_analytics` (aggregation by type/district/price/source) and `v_duplicate_candidates` (same address + similar price + similar area); create endpoint `GET /analytics/summary`
- **Acceptance gate**: views return expected shapes on seeded data; API endpoint works; `make test` passes
- **Output**: `sql/views.sql`, `src/bgrealestate/api/routers/analytics.py`, tests in `test_api_fastapi.py` + `test_unification.py`
- **Resolution**: created materialized views in `sql/views.sql`; `GET /analytics/summary` (scope `listings:read`) and `GET /analytics/duplicates` (scope `admin:read`) with inline SQL queries; auth-gated; 503 without DB; tests pass on `make validate`.
- **Verifier**: debugger
- **Depends on**: BD-02

### BD-10: Photo classification pipeline stub
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08: classifier stub + model columns + 14 tests)
- **Read first**: `sql/schema.sql` (media_asset), `src/bgrealestate/models.py`
- **Do**: add columns to `media_asset` (room_type, quality_score, is_exterior, is_floorplan); create stub classifier `src/bgrealestate/analytics/photo_classifier.py` that accepts an image path and returns classification dict; fixture-backed tests
- **Acceptance gate**: migration applies; classifier stub returns expected dict on test image; `make test` passes
- **Output**: `src/bgrealestate/analytics/photo_classifier.py`, updated `sql/schema.sql` + `db/models.py`, `tests/test_photo_classifier.py` (14 tests)
- **Resolution**: Added 4 columns to `media_asset` (room_type, quality_score, is_exterior, is_floorplan). Heuristic classifier detects room types (kitchen, bathroom, bedroom, living_room, balcony, entrance, garage, garden, pool), exterior/facade images, and floorplans from filename/URL + metadata captions. Supports Bulgarian labels. Quality score estimates based on image dimensions. Batch API included. All 14 tests pass.
- **Verifier**: debugger
- **Depends on**: BD-01

### BD-11: Unified listing database — merge scraper outputs into canonical store
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08: unification service + /properties endpoints + pipeline wiring implemented)
- **Priority**: **CRITICAL** — core pipeline for the website; **execution order:** verify/promote **`BD-11` immediately after `S1-15` live path exists** so `S1-18` volume counts use PostgreSQL. Remaining backend slices (`BD-12`+) wait until **`S1-18` VERIFIED** unless they unblock ingest.
- **Read first**: `src/bgrealestate/connectors/ingest.py`, `src/bgrealestate/pipeline.py`, `sql/schema.sql` (source_listing → parsed_listing → canonical_listing → property_entity), `src/bgrealestate/db/models.py`
- **Do**:
  1. Create `src/bgrealestate/services/unification.py` — takes raw scraper output from any tier-1/2/3 connector and writes into `source_listing` → `parsed_listing` → `canonical_listing` pipeline
  2. Implement deduplication: match by address + similar price + similar area within same city/district → link to single `property_entity`
  3. Create `property_entity` records that aggregate all source listings for the same physical property
  4. Merge best data: take highest-quality photos, most complete description, latest price from all sources
  5. Compute `confidence_score` per property based on number of cross-source matches
  6. Create `GET /properties` endpoint (distinct from `/listings`) that returns deduplicated property entities with all source listings attached
  7. Create `GET /properties/{id}` endpoint with full property detail including source breakdown
  8. Wire scraper outputs to unification service via Temporal workflow or cron job
- **Acceptance gate**: given 3 fixture listings for the same apartment from different sources, unification produces 1 `property_entity` with 3 linked `canonical_listing` records; `/properties` endpoint returns deduplicated list; `make test` passes
- **Output**: `src/bgrealestate/services/unification.py`, `src/bgrealestate/api/routers/properties.py`, `PropertyEntityRepository` in `repositories.py`, `tests/test_unification.py`, updated `connectors/ingest.py`
- **Resolution**: Created unification service with dedupe-key matching (city+normalized_address+area_sqm bucket), property_entity creation, property_offer linkage, confidence scoring (0.2/0.5/0.8+ based on distinct source count), best-data merge (longest description, most photos). Wired into `ingest_listing_detail_html` via `unify=True` flag. `GET /properties` and `GET /properties/{id}` endpoints (scope `listings:read`) with full source breakdown. Tests pass on `make validate` (121 tests, 25 skipped for Python 3.9). Full live acceptance gate (3 listings → 1 property_entity) requires DB + Python 3.10+.
- **Verifier**: debugger + scraper_1
- **Depends on**: BD-01, BD-02, S1-13

### BD-12: Shop-style filter API for property feed
- **Status**: `TODO`
- **Priority**: **CRITICAL** — this powers the main listing/shop view (**blocked until `S1-18` VERIFIED** unless operator waives)
- **Read first**: `docs/business/product-ux-structure.md` (§3.1 Homepage), `src/bgrealestate/api/routers/listings.py`, UX-08
- **Do**:
  1. Extend `GET /properties` with full filter parameters: `intent` (buy/rent/str/auction), `category` (apartment/house/villa/studio/land/commercial), `price_min`, `price_max`, `area_min`, `area_max`, `rooms_min`, `rooms_max`, `city`, `district`, `bbox` (map viewport), `sort_by` (price_asc, price_desc, newest, area), `page`, `limit`
  2. Add `GET /properties/facets` — returns available filter options with counts (how many apartments, how many houses, price range, etc.)
  3. Add PostGIS spatial query: filter by map bounding box (`bbox=lat1,lon1,lat2,lon2`) and polygon draw (`polygon=...`)
  4. Add `GET /properties/map-clusters` — return clustered pins for low zoom levels, individual pins for high zoom
  5. Ensure all filters compose correctly (AND logic)
  6. Add sort + pagination with cursor-based pagination for infinite scroll
- **Acceptance gate**: API returns correct filtered results with seeded data; facets reflect filter state; bbox query works; cluster endpoint returns GeoJSON; `make test` passes
- **Output**: updated API routes, PostGIS queries, facet aggregation, tests
- **Verifier**: debugger + ux_ui_designer
- **Depends on**: BD-11, BD-06

### BD-13: User profile + auth system (buyer/renter/seller modes)
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08: registration, login, profile, saved properties, dashboard implemented)
- **Priority**: **HIGH** — users need accounts to save properties, post listings, and switch modes
- **Read first**: `sql/schema.sql` (app_user, organization_account), `docs/business/product-ux-structure.md` (§3.7 Post Listing), `src/bgrealestate/api/auth.py`
- **Do**:
  1. Implement user registration: `POST /auth/register` (email + password + name)
  2. Implement login: `POST /auth/login` → returns JWT token
  3. Implement user profile: `GET /users/me`, `PATCH /users/me`
  4. Add `user_mode` field to `app_user`: enum `buyer` | `renter` | `seller` | `agent` — user can switch freely
  5. Mode-specific features:
     - **Buyer/Renter mode**: saved properties (`POST /users/me/saved`), saved searches, alert preferences, contact history
     - **Seller mode**: my listings (`GET /users/me/listings`), post new listing (`POST /listings`), edit listing, deactivate listing
     - **Agent mode**: managed properties (on behalf of owner), lead inbox from CRM
  6. `GET /users/me/dashboard` — returns mode-appropriate dashboard data (saved count, listing count, leads count)
  7. Photo upload for listings: `POST /media/upload` → S3/MinIO → returns media_asset reference
  8. Listing submission: `POST /listings` with validation (requires photos, price, location, category)
- **Acceptance gate**: registration + login flow works end-to-end; mode switch updates user record; saved properties persist; listing submission creates `canonical_listing` + `property_entity`; `make test` passes
- **Output**: `src/bgrealestate/services/user_auth.py`, `src/bgrealestate/api/routers/user_auth.py`, `src/bgrealestate/api/routers/users.py`, `src/bgrealestate/api/user_deps.py`, `tests/test_user_auth.py`
- **Resolution**: Implemented items 1–6: registration with PBKDF2 password hashing, JWT login, user profile with mode switching, saved properties CRUD, mode-appropriate dashboard. Listing submission (items 7–8) deferred to follow-up slice as it requires media upload pipeline (S3/MinIO). 14 tests pass (pure auth + endpoint registration).
- **Verifier**: debugger + ux_ui_designer
- **Depends on**: BD-04, BD-11

### BD-14: Railway deployment — backend + DB + scraper worker
- **Status**: `TODO`
- **Priority**: **CRITICAL** — nothing works publicly without deployment
- **Read first**: `Dockerfile`, `docker-compose.yml`, `Makefile`, `pyproject.toml`
- **Do**:
  1. Create `railway.toml` configuration for 3 services:
     - **api**: FastAPI backend (`make run-api`), port 8000, `DATABASE_URL` from Railway PostgreSQL plugin
     - **worker**: Temporal/cron scraper worker (`make run-worker`), connects to same DB
     - **scheduler**: Cron scheduler for periodic scrapes (`make run-scheduler`)
  2. Add Railway PostgreSQL plugin with PostGIS extension
  3. Add Railway Redis plugin
  4. Create `scripts/railway_deploy.sh` — automates initial deploy: migrate → sync-registry → seed initial data
  5. Set environment variables: `DATABASE_URL`, `REDIS_URL`, `API_KEYS_JSON`, `OPENAI_API_KEY`, `CORS_ORIGINS`
  6. Configure health check at `GET /api/v1/ready`
  7. Set up auto-deploy from `main` branch via Railway GitHub/GitLab integration
  8. Document deployment in `docs/deployment.md`
- **Acceptance gate**: `https://bgrealestate-api.up.railway.app/api/v1/ready` returns 200; `/admin/source-stats` returns JSON; listings endpoint works from Vercel frontend
- **Output**: `railway.toml`, deploy scripts, deployment docs, environment setup guide
- **Verifier**: debugger
- **Depends on**: BD-01, BD-04

### BD-15: Scraper orchestration — continuous crawl loop
- **Status**: `TODO`
- **Priority**: **CRITICAL** — the database must be populated with real data
- **Read first**: `src/bgrealestate/connectors/factory.py`, `src/bgrealestate/connectors/ingest.py`, `src/bgrealestate/dev_scheduler.py`, BD-05 output
- **Do**:
  1. Implement production scraper loop in `src/bgrealestate/services/scraper_runner.py`:
     - On startup: load all tier-1 sources from `source_registry`
     - For each source: discover listing URLs → fetch detail → parse → unify → store
     - Respect `freshness_target` per source (10min for OLX/Homes, hourly for agencies)
     - Implement crawl cursor persistence (resume from last position)
     - Rate limiting per source (configurable, default 1 req/sec)
     - Error handling: log failures to `crawl_attempt` table, skip and continue
     - Metrics: update `crawl_job` records with success/fail counts
  2. Wire to Temporal workflows OR implement as asyncio cron (simpler for MVP)
  3. Create `make run-scraper` command
  4. Add health endpoint: `GET /api/v1/scraper-status` — returns last crawl time per source, queue depth, error rate
- **Acceptance gate**: scraper runs continuously on Railway; new listings appear in database within freshness_target; `/scraper-status` shows healthy state; no live-network dependency in test suite (tests use fixtures)
- **Output**: `src/bgrealestate/services/scraper_runner.py`, updated Makefile, health endpoint, Railway worker config
- **Verifier**: debugger + scraper_1
- **Depends on**: BD-05, BD-11, BD-14

### BD-16: WebSocket/SSE for real-time listing updates
- **Status**: `TODO`
- **Priority**: MEDIUM — nice-to-have for live feed updates
- **Read first**: `src/bgrealestate/api/main.py`, BD-15 output
- **Do**: add Server-Sent Events endpoint `GET /listings/stream` that pushes new listings as they're ingested; frontend can subscribe for live feed updates
- **Acceptance gate**: SSE endpoint sends events when new listings are inserted; frontend receives and displays them; `make test` passes
- **Output**: SSE endpoint, event publisher in unification service, tests
- **Verifier**: debugger
- **Depends on**: BD-15, BD-12

---

## ═══════════════════════════════════════════════════════
## SCRAPER_1 (tier-1 and tier-2 marketplace connectors)
## ═══════════════════════════════════════════════════════

**Mission**: Get a full, constantly-updating database of ALL properties from tier-1 and tier-2 Bulgarian real estate portals. Every connector must work end-to-end: discover URLs → fetch pages → parse to canonical format → feed into unification pipeline.

**Current operator mandate (2026-04-09):** Do **not** stop for end-of-session idle after `S1-15` code lands — keep executing harvest + ingest iterations until **`S1-18` volume gate** is satisfied (≥100 listings × ≥5 sources), except for real blockers (legal gate, site outage, CAPTCHA) documented in `JOURNEY.md`.

### S1-01: Homes.bg connector + fixtures
- **Status**: `VERIFIED`
- **Read first**: `src/bgrealestate/connectors/homes_bg.py`, `tests/fixtures/homes_bg/*`
- **Do**: connector interface + discovery/detail parser + fixtures + tests
- **Acceptance gate**: `make test` passes; no live network in tests
- **Output**: connector, fixtures, tests
- **Verifier**: debugger
- **Depends on**: —

### S1-02: OLX.bg API connector + JSON fixtures
- **Status**: `VERIFIED`
- **Read first**: `src/bgrealestate/connectors/olx_bg.py`, `tests/fixtures/olx_bg/*`
- **Do**: dedicated API parser for OLX JSON structure; 3 fixture cases
- **Acceptance gate**: `make test` passes; parser handles blocked/missing-price cases
- **Output**: connector, fixtures, tests
- **Verifier**: debugger
- **Depends on**: —

### S1-03 through S1-09: Remaining tier-1 HTML connectors
- **Status**: `VERIFIED`
- **Sources**: alo.bg, imot.bg, BulgarianProperties, Address.bg, SUPRIMMO, LUXIMMO, property.bg
- **Acceptance gate**: `make test` — 44 tests pass, 0 failures
- **Verifier**: debugger
- **Depends on**: —

### S1-10: imoti.net stub (legal-gated)
- **Status**: `VERIFIED`
- **Do**: fixture parsing only; live HTTP blocked by `legal_mode=legal_review_required`
- **Acceptance gate**: `TestImotiNetLegalGate` passes; live fetch raises `LegalGateError`
- **Verifier**: debugger (Bugbot priority: legal gates)
- **Depends on**: —

### S1-11: Live-safe ingestion runner (small)
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08; CLI + tests added, golden-path command executed in skip-mode without DATABASE_URL)
- **Read first**: `src/bgrealestate/connectors/ingest.py`, `src/bgrealestate/connectors/factory.py`
- **Do**: CLI command that ingests 1 fixture into DB using `ingest.py`
- **Acceptance gate**: stats endpoints reflect the inserted record; `make golden-path` still passes
- **Output**: CLI command + test
- **Verifier**: debugger + backend_developer (DB round-trip)
- **Depends on**: BD-01, S1-01

### S1-12: Tier-2 connector stubs (fixture-only)
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08; Bazar.bg/Domaza/Yavlena/Home2U stubs + fixtures + tests)
- **Read first**: `data/source_registry.json` (tier-2 sources), `src/bgrealestate/connectors/scaffold.py`
- **Do**: stub connectors + 1 fixture each for Bazar.bg, Domaza, Yavlena, Home2U (highest-value tier-2)
- **Acceptance gate**: `make test` passes; legal gates enforced for `licensing_required` sources
- **Output**: connectors, fixtures, tests
- **Verifier**: debugger
- **Depends on**: S1-03 (tier-1 pattern established)

### S1-13: Stage-1 scraping completion check (all product types)
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08; coverage matrix + assertions added)
- **Read first**: `data/source_registry.json`, `tests/fixtures/`, `src/bgrealestate/models.py`
- **Do**: ensure stage-1 scraping for tier-1/2 covers property intents/types used by MVP (`sale`, `long_term_rent`, `short_term_rent`, `land`, `new_build`) with fixture + ingest coverage matrix
- **Acceptance gate**: matrix report exists and `make test` passes with product-type coverage assertions
- **Output**: `docs/exports/stage1-product-type-coverage.md`, coverage tests
- **Verifier**: debugger + backend_developer
- **Depends on**: S1-12

### S1-14: Discovery pagination for ALL tier-1 sources
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08; discovery parsers + fixtures + tests added for all tier-1 sources)
- **Priority**: **CRITICAL** — scrapers can't run without discovery
- **Read first**: `src/bgrealestate/connectors/homes_bg.py` (has `parse_discovery_html`), all other tier-1 connectors in `src/bgrealestate/connectors/`
- **Do**:
  1. Implement `parse_discovery_html()` / `parse_discovery_json()` for every tier-1 source that doesn't already have it:
     - OLX.bg: paginate API search results (page parameter in API URL)
     - alo.bg: HTML pagination with next-page link
     - imot.bg: HTML pagination
     - BulgarianProperties: HTML pagination
     - Address.bg: HTML pagination
     - SUPRIMMO: HTML pagination
     - LUXIMMO: HTML pagination
     - property.bg: HTML pagination
  2. Each discovery parser returns list of `{url, external_id, preview_price, preview_intent}` per page
  3. Add discovery fixtures: `tests/fixtures/<source>/discovery_page/raw.html` + `expected.json` for each source
  4. Test: discovery returns correct count, handles last page, handles empty results
- **Acceptance gate**: every tier-1 source has working discovery; `make test` passes; fixtures exist for each
- **Output**: updated connector files, discovery fixtures, tests
- **Verifier**: debugger
- **Depends on**: S1-01 through S1-10

### S1-15: Live HTTP integration for tier-1 connectors
- **Status**: `IN_PROGRESS` (2026-04-21; strict pattern repairs promoted `Address.bg`, `BulgarianProperties`, `LUXIMMO`, `OLX.bg`, `property.bg`, `SUPRIMMO`, `Bazar.bg`, and `Yavlena` to `Patterned` from saved item evidence; DB proof is still blocked because no PostgreSQL server is running locally and Docker daemon/compose are unavailable in this environment; `alo.bg`/`Domaza`/`Home2U` still remain low-yield or zero-sample)
- **Priority**: **CRITICAL** — must actually hit real websites to populate database; **feeds `S1-18` volume gate**
- **Read first**: `src/bgrealestate/connectors/scaffold.py`, `src/bgrealestate/connectors/legal.py`, `src/bgrealestate/connectors/protocol.py`
- **Do**:
  1. Implement `httpx`-based live fetch in `HtmlPortalConnector.fetch_url()` with:
     - User-Agent rotation (realistic browser UAs)
     - Rate limiting (configurable per source, default 1 req/2sec)
     - Retry with exponential backoff (3 retries)
     - Proxy support (optional, configured via env var `HTTP_PROXY`)
     - Response caching in `raw_capture` table (raw HTML stored in S3/local, metadata in DB)
     - Legal gate check before every request (`assert_live_http_allowed`)
  2. Implement live discovery + detail fetch flow:
     - `discover_listing_urls(source, page)` → returns URL list from live site
     - `fetch_listing_detail(url)` → returns raw HTML → parse → canonical listing
  3. Integration test (separate from unit tests): `tests/test_live_integration.py` — skipped by default, runs only with `ENABLE_LIVE_TESTS=1`
  4. **Tests must remain fixture-only by default** — live tests are opt-in only
- **Acceptance gate**: `make test` still passes (no live network); with `ENABLE_LIVE_TESTS=1`, fetches 1 page from each tier-1 source and parses successfully; legal gates block restricted sources
- **Output**: updated connector base class, live fetch implementation, integration tests
- **Verifier**: debugger (legal gate enforcement) + backend_developer (DB storage)
- **Depends on**: S1-14, BD-01

**Continuation checklist (operator pause 2026-04-08 — resume here)**  
Bulk live harvesting was started outside the formal S1-15 acceptance gate; do **not** assume it is complete.

1. **Stabilize `scripts/live_scraper.py`**: fix remaining discovery URLs (alo.bg, address.bg, property.bg, home2u, SUPRIMMO/LUXIMMO home-only patterns); prefer each site’s real listing URL regex after a one-page probe; cap `--max-listings` per run to avoid hour-long jobs.
2. **Normalize media URLs everywhere**: protocol-relative `//cdn...` must become `https:` before `download_image` (partially done in live scraper; align with `ingest` / listing API if URLs are stored raw).
3. **Homes.bg volume**: use `/api/offers` with validated `city` / `offerType` params; confirm pagination until empty `result`; merge with connector `HomesBgConnector` so one code path owns discovery.
4. **Wire harvest → DB**: either extend `ingest_listing_detail_html` + crawl job runner or a dedicated “bulk import JSON” path so `data/scraped/*/listings/*.json` round-trips to `canonical_listing` + `listing_media` (not only on disk).
5. **Regenerate exports**: after a successful harvest, run `make scraping-inventory` and extend `scripts/generate_scraping_inventory.py` to ingest **live** counts from `data/scraped/**/scrape_stats.json` + `scrape_summary.json` (separate columns from fixture stats).
6. **Agent report MD + DOCX + PDF**: add `docs/exports/scraper-1-tier12-status.md` and a small script (or Makefile target) to render DOCX/PDF from that markdown (reuse `reportlab` / `python-docx` patterns from inventory script).
7. **Opt-in live tests**: keep `make test` fixture-only; add `ENABLE_LIVE_TESTS=1` smoke that hits **one** URL per source (as in original S1-15 spec).
8. **Then**: mark `S1-15` `DONE_AWAITING_VERIFY` only when live fetch + parse + **persistence path** (via `BD-11`) works; immediately continue **`S1-18`** until volume gate met → then `S1-16` tier-2 expansion → `S1-17` Playwright for JS-heavy portals.

### S1-18: Tier-1/2 live volume gate (≥100 listings × ≥5 sources) — NON-STOP
- **Status**: `TODO`
- **Priority**: **CRITICAL** — primary success metric for the current execution wave
- **Read first**: `S1-15`, `BD-11`, `data/source_registry.json` (tier 1–2 rows), `docs/exports/stage1-product-type-coverage.md`
- **Do**:
  1. After live HTTP + ingest work (`S1-15` + `BD-11`), run **repeated** discovery → detail → persist cycles for tier-1 and tier-2 sources allowed by `legal_mode` / `access_mode`.
  2. **Stop condition:** at least **5** distinct `source_name` values (from the registry, tier 1 or 2) each have **≥100** rows in **`canonical_listing`** (count distinct `reference_id` or equivalent unique key per source). If Postgres is temporarily unavailable, document **interim** counts from an agreed export under `data/scraped/` in `docs/exports/tier12-live-volume-report.md` and still treat the gate as **not met** until DB counts match.
  3. **Non-stop rule:** do not mark this slice `DONE_AWAITING_VERIFY` until the numeric gate is hit or **`BLOCKED`** with a concrete reason (e.g. `LegalGateError`, sustained HTTP 403, missing partner contract). Rotate sources if one is blocked; prefer Homes.bg, OLX.bg, imot.bg, alo.bg, property.bg as the default “first five” unless the registry forbids live fetch.
  4. Update **`docs/exports/tier12-live-volume-report.md`** after each major run: timestamp, per-source counts, sample `reference_id`s, and command lines used.
- **Current analysis artifact (2026-04-20)**: `docs/dashboard/scrape-status.html` is the operator dashboard for per-source service/property coverage, field capture, image/text readiness, and next steps across all tier-1/2 sources.
- **Website inventory artifact (2026-04-20)**: `docs/exports/website-inventory-analysis.json` and `docs/exports/website-inventory-analysis.md` now persist website-side totals, category-level count evidence, count method, count gaps, and estimate conflicts for each tier-1/2 source; `scrape-status.html` renders those inside each website block and should be extended after every live counting pass.
- **Interim evidence (2026-04-09)**: `data/scraped/` already contains ≥100 parsed listings for **5** sources (`Bazar.bg`, `BulgarianProperties`, `imot.bg`, `OLX.bg`, `Yavlena`), and the continuation wave added live on-disk corpus for `Address.bg` (43), `LUXIMMO` (15), `property.bg` (15), and `SUPRIMMO` (12). The gate is still **not met** until those rows land in PostgreSQL `canonical_listing`.
- **Gemma/OpenClaw analysis note (2026-04-27)**: `docs/exports/gemma4-openclaw-run-analysis-2026-04-27.md` shows 1,549 file-backed tier-1/2 items, 18,707 remote photo references, 5,376 local photos, and no completed apartment image-description reports. Treat this as the handoff baseline for `S1-21` and `S1-22`.
- **Pattern audit note (2026-04-21)**:
  1. Current strict `Patterned` set from saved sample evidence is `Address.bg`, `BulgarianProperties`, `Homes.bg`, `imot.bg`, `LUXIMMO`, `OLX.bg`, `property.bg`, `SUPRIMMO`, `Bazar.bg`, `Yavlena`.
  2. Current remaining non-patterned tier-1/2 sources split into:
     - no saved sample proof yet: `alo.bg`, `ApartmentsBulgaria.com`, `Domaza`, `Holding Group Real Estate`, `Home2U`, `Indomio.bg`, `Lions Group`, `Pochivka.bg`, `realestates.bg`, `Realistimo`, `Rentica.bg`, `Svobodni-kvartiri.com`, `Unique Estates`, `Vila.bg`
     - legal/authorization review required: `imoti.net`, `Imoteka.bg`, `Imoti.info`
  3. DB persistence proof is currently blocked by environment runtime, not parser code: `psql` and Python DB deps are present, but `localhost:5432` is not running and Docker daemon/socket are unavailable here.
- **Follow-up planning note (2026-04-14)**:
  1. Use `docs/exports/tier12-source-analysis.md` and `docs/exports/tier12-source-analysis.xlsx` as the source-by-source runbook for the next tier-1/2 continuation wave.
  2. Recover the zero-yield or weak-yield set first: `alo.bg`, `Domaza`, `Home2U`, then deepen `Homes.bg` apartment coverage and re-run `imot.bg` media downloads.
  3. After that, promote remaining tier-2 implementation in this order: `Rentica.bg`, `Svobodni-kvartiri.com`, `Holding Group Real Estate`, `Unique Estates`, `Realistimo`.
  4. Apply the new local skills when relevant:
     - `agent-skills/browser-scrape-ops/SKILL.md`
     - `agent-skills/image-media-pipeline/SKILL.md`
     - `agent-skills/postgres-ops-psql/SKILL.md`
- **Research and setup note (2026-04-20)**:
  1. Use `docs/exports/scraping-tools-market-radar-2026-04-20.md` as the dated tool-market reference before expanding new complex-source strategies.
  2. Use `docs/exports/universal-agent-scrape-setup-2026-04-20.md` to keep Codex and Claude-agent runs on the same runtime, env-var, and escalation policy.
  3. Apply the newer local skills when a source becomes expensive or brittle:
     - `agent-skills/hybrid-scrape-stack/SKILL.md`
     - `agent-skills/managed-scrape-platforms/SKILL.md`
     - `agent-skills/universal-agent-scrape-setup/SKILL.md`
  4. For each property item, treat media completeness as part of completeness:
     - identify the whole gallery on the detail page where possible
     - download all reachable listing photos, not only the first image
     - record readability/decode success for the full set and note partial or broken galleries
  5. Use `docs/exports/tier12-source-metrics-deep-dive.md` and `docs/exports/tier12-source-metrics-deep-dive.xlsx` as the per-source metric baseline:
     - declared site offering
     - estimated site scale
     - confirmed landed corpus
     - intent/category splits
     - progress percentages
     - method and automation recommendations
- **Acceptance gate**: report shows ≥5 sources × ≥100 listings in `canonical_listing`; `make test` still passes (fixture-only); rate limits and legal gates respected
- **Output**: `docs/exports/tier12-live-volume-report.md`, crawl/job logs as needed, JOURNEY entries per run batch
- **Verifier**: debugger
- **Depends on**: `S1-15`, `BD-11`

### S1-21: Codex tier-1/2 scrape quality audit + pattern repair prep
- **Status**: `TODO`
- **Priority**: **CRITICAL** — next operator-requested tier-1/2 run before Gemma resumes
- **Read first**: `docs/exports/gemma4-openclaw-run-analysis-2026-04-27.md`, `docs/exports/source-item-photo-coverage.json`, `docs/exports/tier12-pattern-status.md`, `docs/dashboard/scrape-status.html`, `scripts/live_scraper.py`, `data/scraped/*/listings/*.json`
- **Do**:
  1. Audit every tier-1/2 source with saved rows for: item count, `photo_count_remote`, `photo_count_local`, `full_gallery_downloaded`, local file existence/decodability, description length, price, area, city, property type, rooms/floor/phones.
  2. Produce per-source and per-property failure tables: missing images, partial galleries, thin descriptions, missing price/area/city/type, suspicious one-photo galleries, and missing image-description reports.
  3. Improve source-specific parsing patterns in code, not only generated JSON. Current priority repairs: `imot_bg` price/area extraction, `yavlena` description extraction, `address_bg` city extraction, and media backfill patterns for `bulgarianproperties`, `property_bg`, `suprimmo`, `homes_bg`.
  4. Regenerate all affected listing JSON, photo coverage exports, pattern-status exports, `docs/dashboard/scrape-status.html`, and frontend scraped-listing seed data.
  5. Keep legal gates intact and keep tests fixture-only.
- **Acceptance gate**: parser regression tests pass; dashboards show source-by-source and item-by-item media/field completeness; every source gap is mapped to either fixed, legal/runtime blocked, or queued for Gemma image reporting.
- **Output**: updated parser code/tests, refreshed dashboards/exports, `docs/exports/tier12-quality-audit-2026-04-27.md`, updated `docs/agents/scraper_1/JOURNEY.md`
- **Verifier**: debugger
- **Depends on**: S1-18 file-backed corpus evidence, S1-20 all-Bulgaria runner

### S1-22: Gemma/OpenClaw apartment image-report generation handoff
- **Status**: `TODO`
- **Priority**: **HIGH** — starts after `S1-21` repairs media/field completeness
- **Read first**: `docs/exports/taskforgema.md`, `docs/exports/property-quality-and-building-contract.md`, `docs/exports/gemma4-openclaw-run-analysis-2026-04-27.md`, `docs/exports/source-item-photo-coverage.json`, `data/scraped/*/listings/*.json`, `data/media/`
- **Do**:
  1. Run only after Codex confirms which apartment listings have complete local galleries.
  2. Generate one Markdown and one JSON visual report per apartment under `docs/exports/apartment-image-reports/<source_key>/`.
  3. Describe every local image in order with scene type, style, layout clues, visible objects/equipment/tools, colors/materials, condition, defects/risks, confidence, and uncertainty.
  4. Run or replicate `GET /api/property-quality/<encoded reference_id>` for every processed listing and include photo completeness, description-context match, price/size plausibility, source-link evidence, and building-match status in the report.
  5. Write global `index.md` and `index.json` with per-source counts: apartments eligible, reports created, images described, skipped rows, skip reasons, QA warnings, and building-match-pending rows.
  6. Do not invent unseen rooms or unavailable media; use `unclear` and confidence values.
- **Acceptance gate**: every apartment with `full_gallery_downloaded=true` has report paths or a documented skip reason; every completed report includes property QA checks; dashboard/export artifacts include image-report status.
- **Output**: `docs/exports/apartment-image-reports/`, refreshed dashboards, updated `docs/agents/scraper_1/JOURNEY.md`
- **Verifier**: debugger
- **Depends on**: S1-21

### S1-20: Stage 1 controlled production prep — Varna-only region-first control plane (no live crawl)
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-23; control-plane widened to all tier-1/2 sources, per-source/segment readiness matrix, threshold summary, queue status, manual control worker, pause/unpause command, and manual activation runbook; operator must still run migrations locally and decide when to enqueue)
- **Priority**: **HIGH** — prerequisite for passive background scraping and per-segment “100 valid listings” gates without auto-starting crawls
- **Read first**: `migrations/versions/20260423_0003_stage1_scrape_control_plane.py`, `docs/stage1-controlled-production-architecture.md`, `data/scrape_patterns/regions/varna/sections.json`, `src/bgrealestate/scraping/*`
- **Do**:
  1. Keep **only** `region_key = varna` in schema, manifests, and CHECK constraints; do not add other regions in implementation until an explicit schema/policy change.
  2. Persist layered patterns per **source → section → list_page → detail_page → media_gallery** in `source_section` + `source_section_pattern`; segment keys must include `buy_personal`, `buy_commercial`, `rent_personal`, `rent_commercial` where applicable.
  3. Wire operator commands: `make scrape-validate-manifest`, `make scrape-sync-sections-dry`, `make scrape-sync-sections` (needs `DATABASE_URL`), `make scrape-threshold-summary`, `make scrape-queue-status`, `make scrape-control-worker-once`, `make scrape-runner-unpause`, and `make scrape-runner-once` (enqueue only after manual unpause).
  4. Provide a manual control-worker path that can process queued `discover` and `threshold_check` tasks without auto-starting HTTP scraping; keep fetch/detail/media execution operator-controlled in this stage.
  5. **Do not** start live HTTP collection as part of this slice; Stage 2 activates “100 valid listings per Varna source/segment bucket” after operator approval.
- **Acceptance gate**: `make test` passes; `alembic upgrade head` applies `20260423_0003` on Postgres; manifest validates; architecture doc + operator checklist exist; `scrape_runner_state.global_pause` remains default **true** until operator clears it; queue status + control-worker preview commands stay read-only unless `--apply` is passed
- **Output**: migration, ORM models, `src/bgrealestate/scraping/`, manifest generator, threshold planner, queue status + control worker, Makefile/CLI targets, `docs/stage1-controlled-production-architecture.md`, `docs/exports/varna-controlled-crawl-matrix.{json,md}`, `agent-skills/stage1-scrape-control-plane/SKILL.md`
- **Verifier**: debugger + backend_developer
- **Depends on**: BD-01 (migrations baseline)

### S1-16: Remaining tier-2 connectors (full set)
- **Status**: `TODO`
- **Priority**: HIGH — more sources = more complete database (**start only after `S1-18` is `VERIFIED`** unless operator reprioritizes)
- **Read first**: `data/source_registry.json` (all tier-2 sources), `src/bgrealestate/connectors/tier2_stubs.py`
- **Do**: Implement fixture-backed connectors for remaining tier-2 sources:
  - Imoti.info, realestates.bg, Indomio.bg, Realistimo
  - Holding Group, Rentica, Svobodni-kvartiri
  - Pochivka (vacation focus), Vila (rural/villa focus)
  - ApartmentsBulgaria (English-market)
  - Unique Estates, Lions Group, Imoteka
  - Each: discovery + detail parsing + 2 fixtures (basic + edge case)
- **Acceptance gate**: `make test` passes; each source has working parser + fixtures; legal gates enforced where applicable
- **Output**: expanded tier-2 connectors, fixtures, tests
- **Verifier**: debugger
- **Depends on**: S1-12, S1-14, **S1-18**

### S1-17: Playwright connectors for headless-required sources
- **Status**: `TODO`
- **Priority**: MEDIUM — some sites require JS rendering
- **Read first**: `data/source_registry.json` (sources with `access_mode: "headless"`), `agent-skills/scraper-connector-builder/SKILL.md`
- **Do**: For sources that require browser rendering (imoti.net after legal review, any tier-2 with heavy JS):
  1. Create `src/bgrealestate/connectors/playwright_base.py` — base class using Playwright for JS-rendered pages
  2. Implement headless connector for specific sources
  3. Fixture capture: use Playwright to save rendered HTML as fixture files
  4. Test with saved fixtures (no live browser in CI)
- **Acceptance gate**: headless connector parses rendered HTML fixtures correctly; Playwright only runs in live mode; `make test` passes without Playwright installed
- **Output**: Playwright base connector, source-specific implementations, fixtures, tests
- **Verifier**: debugger
- **Depends on**: S1-15, **S1-18**

---

## ═══════════════════════════════════════════════════════
## SCRAPER_T3 (tier-3: vendor/partner/official routes)
## ═══════════════════════════════════════════════════════

**Mission**: Get data from licensed vendors (AirDNA/Airbtics for STR analytics), official registers (KAIS/Property Register), and partner feeds (Airbnb/Booking when contracts exist). All tier-3 sources are gated by contracts/licenses — implement the importers so they work the moment a contract is signed.

**2026-04-09:** Do **not** expand **live** tier-3 work until **`S1-18`** is `VERIFIED` (or operator explicitly reprioritizes). Fixture slices awaiting **`DBG-06`** stay in queue behind the tier-1/2 volume wave.

### T3-01: Tier-3 ingestion policy and integration contracts
- **Status**: `VERIFIED` (2026-04-08; debugger policy + fixture contract review)
- **Read first**: `data/source_registry.json` (tier-3 sources), `AGENTS.md` (guardrails), `deep-research-report.md`
- **Do**: define what's allowed per source and the integration pattern for each
- **Acceptance gate**: policy doc reviewed by debugger; integration pattern defined per source; fixture format defined
- **Output**: `docs/agents/scraper_t3/tier3-ingestion-policy.md`, fixture templates under `tests/fixtures/`
- **Verifier**: debugger (legal gates + Bugbot priority)
- **Depends on**: —

### T3-02: AirDNA / Airbtics licensed data importer (fixture-first)
- **Status**: `DONE_AWAITING_VERIFY`
- **Read first**: T3-01 policy, `src/bgrealestate/connectors/protocol.py`, vendor API docs
- **Do**: connector that maps licensed STR analytics data → `canonical_listing` or dedicated STR analytics table; fixture-backed tests with sample JSON
- **Acceptance gate**: `make test` passes; no live vendor API calls in tests; fixture contains realistic STR metrics
- **Output**: connector, fixtures, tests, STR data model helpers
- **Verifier**: debugger + backend_developer (DB round-trip)
- **Depends on**: T3-01, BD-01

### T3-03: BCPEA property auctions connector (fixture-first)
- **Status**: `DONE_AWAITING_VERIFY`
- **Read first**: T3-01 policy, `data/source_registry.json` (BCPEA entry), `src/bgrealestate/connectors/scaffold.py`
- **Do**: HTML connector for BCPEA forced-sale auction listings; parse starting price, area, address, court, bailiff, dates; fixture-backed
- **Acceptance gate**: `make test` passes; no live network in tests; legal gates enforced
- **Output**: connector, fixtures, tests
- **Verifier**: debugger
- **Depends on**: T3-01

### T3-04: Partner feed stub connectors (Airbnb/Booking.com/Vrbo)
- **Status**: `DONE_AWAITING_VERIFY`
- **Read first**: T3-01 policy, partner API documentation (when available)
- **Do**: stub connector classes with fixture parsing for partner feed JSON format; actual API integration blocked until partner contracts are signed
- **Acceptance gate**: `make test` passes; connector raises `PartnerContractRequired` on live calls; fixtures demonstrate expected feed structure
- **Output**: stub connectors, fixtures, tests
- **Verifier**: debugger (legal gate enforcement)
- **Depends on**: T3-01

### T3-05: Official register query wrappers (Property Register / KAIS Cadastre)
- **Status**: `DONE_AWAITING_VERIFY`
- **Read first**: T3-01 policy, official e-service documentation
- **Do**: query wrappers for official e-services; manual/consent mode only; fixture-backed for parser tests; live queries require explicit operator authorization
- **Acceptance gate**: `make test` passes; no automated queries without operator consent; fixtures contain redacted sample responses
- **Output**: query wrappers, fixtures, tests, consent enforcement
- **Verifier**: debugger + backend_developer
- **Depends on**: T3-01, BD-01

### T3-06: Varna-focused enrichment handoff (post stage-1 gate)
- **Status**: `BLOCKED` (2026-04-08: dependency gates not yet verified)
- **Read first**: DBG-05 verification output, T3-02..T3-05 outputs
- **Do**: define tier-3 enrichment payloads prioritized for Varna region market depth (STR/vendor/official overlays) without unauthorized scraping
- **Acceptance gate**: enrichment handoff spec consumed by backend + UX tasks
- **Output**: `docs/agents/scraper_t3/varna-enrichment-handoff.md`
- **Verifier**: debugger + backend_developer
- **Depends on**: DBG-05, T3-02, T3-05
- **Blocker**: `DBG-05` remains `TODO`, and `T3-02`/`T3-05` are still `DONE_AWAITING_VERIFY` (not `VERIFIED`), so slice cannot start under dependency rules.
- **Mapped follow-up slices**: `DBG-06` (verify T3-02/T3-03/T3-04/T3-05) and `DBG-05` (stage-1 quality gate).

### T3-07: BCPEA live scraper (public auctions are legal to crawl)
- **Status**: `DONE_AWAITING_VERIFY`
- **Priority**: HIGH — BCPEA is public data and can be crawled immediately
- **Read first**: T3-03 output, `src/bgrealestate/connectors/tier3.py`
- **Do**: implement live HTTP fetch for BCPEA auction listings (public_crawl_with_review legal mode); discovery pagination + detail parsing + storage; respect rate limits
- **Acceptance gate**: live scraper fetches real auction listings; stores in DB; `make test` still passes (fixture-only)
- **Output**: live BCPEA connector (`src/bgrealestate/connectors/tier3.py`), CLI command (`scrape-bcpea`), Makefile targets, realistic fixtures, 7 new tests (156 total pass)
- **Verifier**: debugger
- **Depends on**: T3-03, BD-15
- **Completion notes (2026-04-08)**: Parsed real BCPEA HTML structure from sales.bcpea.org; discovery pagination (`?perpage=36&p=N`), detail parsing (property type, area, price, court, bailiff, dates, photos, descriptions, scanned documents), rate limiting (1.5s default). Successfully scraped 180 real auction listings with full detail. CLI: `make scrape-bcpea`.

### T3-08: STR analytics API integration (AirDNA/Airbtics — when licensed)
- **Status**: `TODO`
- **Priority**: MEDIUM — requires license subscription first
- **Read first**: T3-02 output, vendor API documentation
- **Do**: implement actual API client for AirDNA and/or Airbtics; pull Varna STR metrics (occupancy, revenue, ADR by property type/area); store in dedicated analytics table; expose via `GET /analytics/str-metrics`
- **Acceptance gate**: with valid API key, fetches real STR data; without key, returns mock/fixture data; `make test` passes
- **Output**: API client, analytics table migration, API endpoint, tests
- **Verifier**: debugger + backend_developer
- **Depends on**: T3-02, BD-14

---

## ═══════════════════════════════════════════════════════
## SCRAPER_SM (tier-4: social media overlays)
## ═══════════════════════════════════════════════════════

**Mission**: Extract real estate leads from social media channels (Telegram, X, Facebook groups) as intelligence overlays. All data feeds into CRM as leads, not as primary listings. Consent-gated, redaction-enforced.

**2026-04-09:** Pause **new** live social expansion until **`S1-18`** is `VERIFIED` unless it unblocks tier-1/2 ingest or the operator overrides.

### SM-01: Social ingestion contract (policy + fixtures)
- **Status**: `VERIFIED` (2026-04-08; debugger consent + fixture review)
- **Read first**: `data/source_registry.json` (tier-4 sources), `AGENTS.md` (guardrails), `sql/schema.sql` (CRM tables)
- **Do**: define what's allowed per platform
- **Acceptance gate**: policy doc reviewed by debugger; consent checklist complete; fixture format defined
- **Output**: `docs/agents/scraper_sm/social-ingestion-policy.md`, fixture templates, detailed contract
- **Verifier**: debugger (consent checklist + Bugbot priority: legal gates)
- **Depends on**: —

### SM-02: Telegram public channel connector (fixture-first)
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08: acceptance gate passed)
- **Read first**: SM-01 policy, `src/bgrealestate/connectors/protocol.py`, CRM tables
- **Do**: connector that maps Telegram channel messages → `lead_message` + `lead_thread`; NLP extraction
- **Acceptance gate**: `make test` passes; fixtures contain redacted posts; no live Telegram calls
- **Output**: `src/bgrealestate/connectors/telegram_public.py`, tests, NLP extraction
- **Verifier**: debugger + backend_developer
- **Depends on**: SM-01, BD-01

### SM-03: X (Twitter) public monitor connector (fixture-first)
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08: acceptance gate passed)
- **Read first**: SM-01 policy, `data/source_registry.json` (X entry)
- **Do**: connector for X API JSON → lead extraction; fixture-backed
- **Acceptance gate**: `make test` passes; no live API calls
- **Output**: `src/bgrealestate/connectors/x_public.py`, tests, fixtures
- **Verifier**: debugger
- **Depends on**: SM-01

### SM-04: Social lead-to-property mapping for AI chat context
- **Status**: `TODO`
- **Read first**: SM-01 policy, `src/bgrealestate/connectors/social_parser.py`, chat/API contracts
- **Do**: provide social lead mapping format so chat can show related properties and map-filter suggestions from social signals
- **Acceptance gate**: fixture-backed mapping examples pass tests; no live social calls
- **Output**: mapping schema + fixtures + parser update tasks
- **Verifier**: debugger + ux_ui_designer
- **Depends on**: SM-02, UX-05

### SM-05: Social collection options research (decision matrix)
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08)
- **Read first**: `docs/agents/scraper_sm/social-ingestion-policy.md`, `data/source_registry.json` (tier-4)
- **Do**: research reliable options for Telegram/X/Facebook/Instagram/Viber/WhatsApp collection; document pros/cons/pricing/legality per platform; present decision matrix for operator
- **Acceptance gate**: decision matrix doc exists with all platforms covered; no code written
- **Output**: `docs/agents/scraper_sm/social-collection-options.md`
- **Verifier**: lead agent
- **Depends on**: SM-01
- **Verification evidence**: decision matrix added with all 7 tier-4 channels, cost bands, legality path, and rollout recommendation.

### SM-06: Telegram live connector (Telegram Bot API or MTProto)
- **Status**: `TODO`
- **Priority**: HIGH — Telegram is the most active social channel for BG real estate
- **Read first**: SM-02 output, SM-05 decision matrix, `src/bgrealestate/connectors/telegram_public.py`
- **Do**:
  1. Implement live Telegram public channel monitoring using official Bot API (or Telethon for MTProto if approved)
  2. Subscribe to 5-10 known Bulgarian real estate Telegram channels (public only)
  3. Parse new messages → extract real estate leads → store as `lead_thread` + `lead_message`
  4. NLP extraction: intent (sell/rent/buy), property type, price, area, city, phone (redacted)
  5. Run as background worker alongside scraper runner
  6. **No private channels, no private messages, no user DMs**
- **Acceptance gate**: live connector receives messages from public channels; leads appear in CRM; `make test` still passes (fixture-only)
- **Output**: live Telegram connector, channel list config, worker integration, tests
- **Verifier**: debugger (consent + legal gate) + backend_developer
- **Depends on**: SM-02, SM-05, BD-14

### SM-07: Facebook public group scraper (consent-gated)
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08: implementation deferred by legal decision)
- **Priority**: MEDIUM — Facebook groups are very active but heavily restricted
- **Read first**: SM-01 policy, SM-05 decision matrix
- **Do**: research and implement if legal: monitor public Facebook real estate groups via Graph API (official) or RSS; only public posts; consent-gated; redaction enforced
- **Acceptance gate**: if implemented, fixture-backed tests pass; no private data accessed; legal review documented
- **Output**: decision doc `docs/agents/scraper_sm/facebook-public-groups-decision.md` (manual/consent path, autonomous scrape deferred)
- **Verifier**: debugger (legal gate)
- **Depends on**: SM-05

---

## ═══════════════════════════════════════════════════════
## UX_UI_DESIGNER (frontend)
## ═══════════════════════════════════════════════════════

**Mission**: Build the complete LUN.ua-style buyer-oriented property marketplace frontend. Map-driven, mobile-responsive, with property shop view, user profiles, and AI chat. Reference: `docs/business/product-ux-structure.md`.

**2026-04-09:** Do **not** start **new** large UX slices (`UX-04`+) until **`S1-18`** is `VERIFIED`; finish **`DBG-06`** promotion for UX-02/03/06 when debugger runs the batch pass.

### UX-01: Operator dashboard UI plan
- **Status**: `VERIFIED` (2026-04-08; debugger contract check)
- **Read first**: `PLAN.md` §8, `src/bgrealestate/api/routers/`, BD-02 API outputs
- **Do**: define `/admin` UX layout and data model
- **Acceptance gate**: markdown spec + component breakdown reviewed by debugger
- **Output**: `docs/agents/ux_ui_designer/admin-ui-spec.md`
- **Verifier**: debugger
- **Depends on**: BD-02

### UX-02: Beta main page — map + listings + category picker
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08)
- **Read first**: `PLAN.md` §8, `src/bgrealestate/api/routers/listings.py`
- **Do**: Build split-view main page with MapLibre map (left) + scrollable listing feed (right) + intent toggle + category picker + search + source badges
- **Acceptance gate**: page loads with mock/seeded data; category/intent filters work; map renders with pins; responsive mobile stacking
- **Output**: `app/(main)/page.tsx`, `components/listings/*`, `components/map/*`, `lib/types/listing.ts`, `lib/mock/listings.ts`
- **Verifier**: debugger
- **Depends on**: UX-01

### UX-03: Wire listings feed to live `/listings` API
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08)
- **Read first**: `src/bgrealestate/api/routers/listings.py`, `lib/server/fetch-backend.ts`
- **Do**: Replace mock data with TanStack Query fetch; add infinite scroll; fallback to mock if API unreachable
- **Acceptance gate**: page fetches from FastAPI; pagination works; fallback to mock if API unreachable
- **Output**: updated `ListingFeed.tsx`, new `lib/hooks/useListings.ts`
- **Verifier**: debugger
- **Depends on**: UX-02, BD-02, BD-03

### UX-04: Nationwide Bulgaria LUN-style map + listings experience
- **Status**: `TODO` (website seed updated 2026-04-28 with grouped map markers, aggregate filter, search-mode toggle, scrollable all-card list, and foldable descriptions; full UX-04 still waits on backend/filter gates)
- **Read first**: `PLAN.md` §8, `docs/agents/ux_ui_designer/operator-dashboard-spec.md`, LUN-style reference notes
- **Do**: shape homepage UX to LUN-like split flow (map + feed + filters) for **all of Bulgaria**: default viewport and filters are **country-wide**; users can narrow by region/city/bbox. Optional **Varna preset** is allowed for demos or 3D pilot (UX-07) but must not be the only mode. Keep the scraped-property evidence fields visible where useful: local/remote photo counts, full-gallery flag, description quality, scrape quality score, and image-report status.
- **2026-04-28 lead note**: homepage seed now has MapLibre + OpenStreetMap raster base, deterministic nationwide coordinates for scraped rows without lat/lon, at most 20 grouped city/district map points, smooth zoom-settled recentering toward the largest nearby aggregate while the visible frame still represents more than 20 properties, synchronized map/list selection, selected-property right panel, selected-card pinning, scrollable full-card list, aggregate duplicate-source filter, region/description search modes, foldable descriptions, and source buttons. Full UX-04 still needs backend filter contracts, viewport-driven clustering, and real geocoding/building entities before verification.
- **2026-04-27 product note**: property detail pages now expose `Marketed by sources` / `Source links` buttons using conservative source-link matching. Current source is always shown; cross-source links are only added when same-property evidence is strong enough and never inferred from neighboring listings on the same source.
- **Acceptance gate**: prototype demonstrates Bulgaria-wide browse (no hard-coded Varna-only lock), map filters + listing cards + synchronized selection; spec calls out optional Varna shortcut vs default nationwide
- **Output**: UX spec/update doc + component task breakdown
- **Verifier**: debugger + backend_developer
- **Depends on**: UX-03, BD-06, DBG-05

### UX-05: AI chat panel with property/map-aware context
- **Status**: `TODO`
- **Read first**: `app/(main)/page.tsx`, chat API contracts, `PLAN.md` chat sections
- **Do**: define and implement persistent chat panel connected to AI chat API, always aware of selected property and active map filters
- **Acceptance gate**: chat can reference current property card + filtered map state
- **Output**: frontend chat-panel implementation
- **Verifier**: debugger
- **Depends on**: UX-04, BD-07

### UX-06: Product UX structure spec (LUN-style buyer marketplace)
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08)
- **Read first**: `docs/business/product-ux-structure.md`, `docs/business/unit-economics-market-analysis.md`
- **Do**: review and refine the product UX structure spec; create wireframe descriptions for each page; define component tree + mobile responsive strategy
- **Acceptance gate**: refined spec exists with component breakdown for all pages
- **Output**: `docs/agents/ux_ui_designer/product-ux-structure-refined.md`
- **Verifier**: debugger + lead agent
- **Depends on**: UX-01

### UX-07: 3D map integration with building layer (MapLibre)
- **Status**: `TODO`
- **Read first**: `docs/business/varna-3d-osm-integration.md`, `components/map/MapCanvas.tsx`
- **Do**: implement MapLibre 3D building extrusion layer using PMTiles from BD-08; building click shows listing drawer; 2D/3D toggle
- **2026-04-28 lead note**: temporary synthetic property/building extrusions were removed from the homepage path. The UI should only claim building-level highlighting after BD-08 provides real PMTiles/OSM/PostGIS building footprints and address-based matches.
- **Acceptance gate**: 3D buildings render in Varna viewport; building click opens drawer; 2D fallback works
- **Output**: updated MapCanvas component + BuildingLayer + BuildingSummaryDrawer
- **Verifier**: debugger + backend_developer
- **Depends on**: UX-04, BD-08

### UX-08: Shop view — full property feed with advanced filters (like LUN.ua)
- **Status**: `TODO`
- **Priority**: **CRITICAL** — this is the main user-facing page
- **Read first**: `docs/business/product-ux-structure.md` (§3.1, §3.2), `components/listings/ListingFeed.tsx`, `components/listings/ListingCard.tsx`, BD-12 API spec
- **Do**:
  1. **Filter sidebar/panel** (collapsible on mobile):
     - Intent toggle: Buy / Rent / Short-term / Auction / Land
     - Category chips: Apartment / House / Villa / Studio / Penthouse / Office / Shop / Land / Garage
     - Price range slider (min–max, €)
     - Area range slider (min–max, m²)
     - Rooms dropdown (1, 2, 3, 4, 5+)
     - Floor range (min–max)
     - Year built (min–max)
     - Construction type checkboxes (brick, panel, EPK, monolith)
     - Amenities checkboxes (parking, balcony, elevator, furnished, sea view)
     - Source filter (show only from: imot.bg, Homes.bg, etc.)
     - Sort: Newest / Price ↑ / Price ↓ / Area ↑
  2. **Listing cards** (per `docs/business/product-ux-structure.md` §3.2):
     - Photo carousel (swipeable, 3–5 photos)
     - Price + price/m² prominently
     - Location (city, district)
     - Key facts: rooms, area, floor/total_floors, year
     - Source badges (which portals list this property)
     - Freshness indicator (updated X hours ago)
     - Save/favorite button (requires login)
     - "Owner representative" label (never "agent")
  3. **Infinite scroll** with cursor-based pagination from BD-12
  4. **Map synchronization**: hover card → highlight pin; click pin → scroll to card; drag map → filter feed to visible area; draw polygon → filter to custom area
  5. **Empty state**: "No properties match your filters" with suggestions
  6. **Loading skeleton**: shimmer cards while fetching
  7. All filters send API params to `GET /properties` (from BD-12)
- **Acceptance gate**: filters work with live API; map sync works; infinite scroll loads next page; mobile responsive; all filter combinations compose correctly
- **Output**: updated ListingFeed, FilterPanel, ListingCard, map sync hooks
- **Verifier**: debugger + backend_developer
- **Depends on**: UX-04, BD-12

### UX-09: Property detail page — LUN.ua style (like lun.ua item page)
- **Status**: `TODO`
- **Priority**: **CRITICAL** — each property needs a rich detail page
- **Read first**: `docs/business/product-ux-structure.md` (§3.3), `app/(main)/properties/[id]/page.tsx`, BD-11 API
- **Do**: Rebuild `/properties/[id]` to match LUN.ua detail page spec:
  1. **Photo gallery**: fullscreen capable, swipeable, zoom, lightbox, photo count badge
  2. **Price box**: price, price/m², price history chart (if available), currency toggle (EUR/BGN)
  3. **Facts grid**: type, rooms, area, floor/total_floors, year, construction type, Act 16 status, amenities
  4. **Description**: expandable, with machine translation toggle (BG ↔ EN)
  5. **Contact panel**: owner/representative name, phone (click-to-call), message button, agency logo if applicable
  6. **Mini map**: property location + nearby properties (3–5 pins)
  7. **Source links panel**: "Listed on: imot.bg, Homes.bg, alo.bg" with links and dates
  8. **Similar properties**: 3–6 cards based on same district + similar price/area
  9. **AI chat context**: "Ask about this property" → opens chat with property pre-loaded
  10. **Breadcrumb**: Home > Varna > Chaika > 2-bed apartment
  11. **Share button**: copy link, share to social
  12. **Save/favorite button** (requires login)
- **Acceptance gate**: detail page renders with all sections from live API; photo gallery works; contact info displayed; similar properties shown; mobile responsive
- **Output**: rebuilt `properties/[id]/page.tsx`, PhotoGallery, PriceBox, FactsGrid, ContactPanel, SimilarProperties components
- **Verifier**: debugger
- **Depends on**: UX-08, BD-11

### UX-10: User profile cabinet — buyer/renter/seller mode switching
- **Status**: `TODO`
- **Priority**: **HIGH** — all users need account management
- **Read first**: `docs/business/product-ux-structure.md` (§3.7), BD-13 auth API
- **Do**:
  1. **Header mode switcher**: visible toggle in top navigation — "I'm Buying" / "I'm Renting" / "I'm Selling"
     - Switching mode changes: navigation items, dashboard data, available actions
     - Mode persists in user profile (not just frontend state)
  2. **Registration page** `/auth/register`: email, password, name, preferred mode
  3. **Login page** `/auth/login`: email + password → JWT stored in httpOnly cookie
  4. **Settings page** `/settings`:
     - Profile: name, email, phone, avatar, preferred language (BG/EN)
     - Mode preferences: default mode, notification channels
     - Saved searches: list of saved filter combinations with alert toggles
     - Alert preferences: email/push/SMS frequency
  5. **Buyer/Renter dashboard** (when mode = buyer or renter):
     - Saved properties (grid of favorited listings)
     - Recent searches
     - Price alerts ("Property X dropped by 5%")
     - Recommended properties (based on saved search criteria)
  6. **Seller dashboard** (when mode = seller):
     - My listings (with status: active/pending/expired)
     - View count per listing
     - Inquiries/leads received
     - "Post new listing" CTA → `/post` wizard
  7. **Post listing wizard** `/post` (seller mode only):
     - Step 1: Property type + intent (sell/rent)
     - Step 2: Location (address input + pin on map)
     - Step 3: Details (area, rooms, floor, year, amenities — checkboxes)
     - Step 4: Photos (upload 5–20, drag to reorder, crop)
     - Step 5: Price + description (with Bulgarian/English toggle)
     - Step 6: Contact method (phone, chat, email)
     - Step 7: Review + submit
  8. **Auth guard**: protect `/settings`, `/post`, save actions — redirect to login if unauthenticated
- **Acceptance gate**: registration + login works; mode switcher changes navigation; saved properties persist; listing wizard submits to API; mobile responsive
- **Output**: auth pages, settings page, dashboard views, post wizard, mode switcher component
- **Verifier**: debugger + backend_developer (API integration)
- **Depends on**: UX-08, BD-13

### UX-11: Vercel deployment — frontend
- **Status**: `TODO`
- **Priority**: **CRITICAL** — the frontend must be publicly accessible
- **Read first**: `next.config.ts`, `package.json`, `lib/config.ts`, BD-14 Railway output
- **Do**:
  1. Configure Vercel project for Next.js 15 deployment
  2. Set environment variables: `NEXT_PUBLIC_API_URL` pointing to Railway backend (`https://bgrealestate-api.up.railway.app`)
  3. Configure custom domain (optional) or use default `*.vercel.app`
  4. Set up auto-deploy from `main` branch
  5. Configure headers: CORS, security headers, caching for static assets
  6. Verify API proxy route `app/api/backend/[...path]/route.ts` works with Railway backend
  7. Add `vercel.json` if custom config needed
  8. Test: all pages render, API calls work, map loads, images load
- **Acceptance gate**: `https://bgrealestate.vercel.app` loads homepage with map + listings; property detail pages work; API proxy reaches Railway backend
- **Output**: `vercel.json` (if needed), deployment docs, environment variable list
- **Verifier**: debugger
- **Depends on**: UX-08, BD-14

### UX-12: Admin dashboard — live operator panel
- **Status**: `TODO`
- **Priority**: HIGH — operators need to monitor scraper health and data quality
- **Read first**: `docs/agents/ux_ui_designer/admin-ui-spec.md`, `docs/agents/ux_ui_designer/operator-dashboard-spec.md`, `src/bgrealestate/api/routers/admin.py`
- **Do**: Build full admin dashboard at `/admin`:
  1. **Source health table**: all sources with status (active/error/stale), last crawl time, listing count, error rate
  2. **Crawl jobs table**: recent jobs with status, duration, records processed
  3. **Parser failure queue**: failed parses with raw HTML preview + error message + retry button
  4. **Duplicate review queue**: suspected duplicates with side-by-side comparison + merge/dismiss actions
  5. **System metrics**: total listings, total properties, active sources, daily ingestion rate chart
  6. **User management**: list users, roles, API keys
  7. Auth: admin-only access (requires `admin:read` scope)
- **Acceptance gate**: dashboard shows real data from admin API; tables paginate; charts render; admin auth enforced
- **Output**: admin page components, admin hooks, admin types
- **Verifier**: debugger + backend_developer
- **Depends on**: UX-11, BD-03

### UX-13: Design system — colors, typography, spacing tokens
- **Status**: `TODO`
- **Priority**: HIGH — consistent visual identity across all pages
- **Read first**: `docs/business/product-ux-structure.md` (§6 Design System Tokens), `tailwind.config.ts`, `app/globals.css`
- **Do**:
  1. Implement design tokens from product-ux-structure.md §6 in Tailwind config:
     - Colors: primary (#4361ee), accent (#e94560), success (#16c79a), warning (#f9c74f), dark (#1a1a2e), light (#f5f5f5)
     - Typography: Inter/system-ui for body, JetBrains Mono for prices/IDs
     - Spacing: 4px grid
     - Border radius: card (12px), button (8px)
     - Shadows: card elevation
  2. Create reusable component primitives: Button, Badge, Card, Input, Select, Slider, Modal, Drawer, Toast
  3. Apply design system to all existing components
  4. Dark mode support (optional, low priority)
- **Acceptance gate**: all pages use consistent tokens; no hardcoded colors/fonts; components match design spec
- **Output**: updated `tailwind.config.ts`, `app/globals.css`, `components/ui/*` primitives
- **Verifier**: debugger
- **Depends on**: UX-02

---

## ═══════════════════════════════════════════════════════
## DEBUGGER (cross-agent verification + safety)
## ═══════════════════════════════════════════════════════

**Mission**: Verify every slice before it's marked complete. Run acceptance gates, check legal compliance, audit security, ensure tests pass. The quality gatekeeper for the entire project.

**2026-04-09:** Prioritize **`DBG-06`** / **`DBG-05`** **after** **`S1-18`** live volume + **`BD-11`** ingest evidence; you may still **spot-check** `S1-14` promotion if asked.

### DBG-01: Golden path check
- **Status**: `VERIFIED`
- **Read first**: `scripts/golden_path_check.py`, `agent-skills/debugger-golden-path/SKILL.md`
- **Do**: `make golden-path` — migrate → sync → fixture ingest → stats → XLSX
- **Acceptance gate**: `make validate` passes; with DB, golden path ends OK
- **Output**: `scripts/golden_path_check.py`, skill, tests
- **Verifier**: self (via `make validate`)
- **Depends on**: —

### DBG-02: Verify all DONE_AWAITING_VERIFY slices
- **Status**: `VERIFIED` (2026-04-08 run; UX-01 verified)
- **Read first**: this file (scan for `DONE_AWAITING_VERIFY` status)
- **Do**: for each awaiting slice, run its acceptance gate commands; record PASS/FAIL
- **Acceptance gate**: every verified slice has a matching JOURNEY.md entry
- **Output**: verification entries in JOURNEY.md + status updates here
- **Verifier**: lead agent (spot checks)
- **Depends on**: —

### DBG-03: Cross-agent safety audit
- **Status**: `VERIFIED` (2026-04-08)
- **Read first**: `.cursor/BUGBOT.md`, `data/source_registry.json`, all `tests/test_*.py`
- **Do**: check all connectors for legal gate enforcement; check tests for live network; check fixtures for secrets/PII; check media storage
- **Acceptance gate**: zero violations found, or violations documented as blockers
- **Output**: audit entry in JOURNEY.md
- **Verifier**: lead agent
- **Depends on**: S1-01 through S1-10

### DBG-04: CI pipeline verification
- **Status**: `VERIFIED` (2026-04-08)
- **Read first**: `.gitlab-ci.yml`, `Makefile`, `Dockerfile`
- **Do**: verify CI runs `make test`, `make lint`, `make validate`, `make golden-path`
- **Acceptance gate**: pipeline green on fixture-only tests
- **Output**: verification entry in JOURNEY.md
- **Verifier**: self
- **Depends on**: BD-05

### DBG-05: Verify stage-1 scraping before expanding 3D / building-depth geo
- **Status**: `TODO`
- **Read first**: `docs/exports/stage1-product-type-coverage.md`, `docs/exports/tier12-live-volume-report.md` (once exists), `scripts/golden_path_check.py`, `/admin/source-stats`
- **Do**: verify stage-1 **fixture** product-type completeness **and** (when available) **live** volume evidence from `S1-18`; confirm inputs for **Varna 3D / building-mesh pilot** and broader **building-match** rollout. **Note:** nationwide **map + listings browse** (`UX-04`) is not Varna-limited; this gate still matters for data trust before **3D** and **multi-city building** investment.
- **Acceptance gate**: required product types covered per coverage doc; golden path passes; live volume report meets `S1-18` thresholds or waiver is documented
- **Output**: verification entry in `docs/agents/debugger/JOURNEY.md`
- **Verifier**: lead agent
- **Depends on**: S1-13, BD-01, **S1-18** (live portion)

### DBG-08: Verify Codex tier-1/2 quality audit and Gemma readiness
- **Status**: `TODO`
- **Priority**: **CRITICAL** — verifier for the next two operator-requested runs
- **Read first**: `S1-21`, `S1-22`, `docs/exports/gemma4-openclaw-run-analysis-2026-04-27.md`, `docs/dashboard/scrape-status.html`
- **Do**: after the next Codex run, verify source-by-source completeness tables, parser tests, local image file evidence, frontend scraped-listing seed generation, and readiness for Gemma image-report generation.
- **Acceptance gate**: every high-priority source gap has a fix, test, or blocker; Gemma receives a clean eligible-listing set with local galleries and no ambiguous Varna-only instruction.
- **Output**: verification entry in `docs/agents/debugger/JOURNEY.md`, updated TASKS statuses
- **Verifier**: lead agent
- **Depends on**: S1-21

### DBG-06: Verify all pending DONE_AWAITING_VERIFY slices (batch 2)
- **Status**: `TODO`
- **Priority**: **CRITICAL** — many slices await verification (**scheduled after `S1-18` + `BD-11` live ingest proof** per 2026-04-09 wave; early spot-checks allowed if operator requests)
- **Read first**: this file — scan all `DONE_AWAITING_VERIFY` slices
- **Do**: systematically verify each pending slice:
  1. BD-04 (Auth/RBAC): test 401/403 responses, API key scope enforcement
  2. BD-05 (Temporal): verify worker/scheduler stubs, test restart behavior
  3. S1-11 (Ingestion runner): run fixture ingest, check DB round-trip
  4. S1-12 (Tier-2 stubs): verify all 4 tier-2 connectors parse correctly
  5. S1-13 (Stage-1 coverage): verify coverage matrix is complete
  6. T3-02 (AirDNA/Airbtics): verify STR metrics parsing
  7. T3-03 (BCPEA): verify auction parsing
  8. T3-04 (Partner stubs): verify `PartnerContractRequired` enforcement
  9. T3-05 (Official registers): verify consent enforcement
  10. SM-02 (Telegram): verify lead extraction + redaction
  11. SM-03 (X): verify lead extraction + redaction
  12. UX-02 (Beta main page): verify map + listings + filters render
  13. UX-03 (Live API wiring): verify TanStack Query fetch + fallback
  - For each: run `make test`, run specific acceptance gate, record PASS/FAIL
- **Acceptance gate**: all slices either promoted to `VERIFIED` or documented as `BLOCKED` with specific failure reason
- **Output**: batch verification report in `docs/agents/debugger/JOURNEY.md`, updated statuses in TASKS.md
- **Verifier**: lead agent
- **Depends on**: **S1-18**, **BD-11** (live rows or documented waiver)

### DBG-07: End-to-end website smoke test
- **Status**: `TODO`
- **Priority**: **CRITICAL** — must verify the full stack works before launch
- **Read first**: BD-14, UX-11 outputs, all API endpoints
- **Do**: after Railway + Vercel deployment, run full smoke test:
  1. `GET /api/v1/ready` returns 200 (Railway)
  2. Homepage loads with map + listings (Vercel)
  3. Click a listing → property detail page loads
  4. Apply filters → feed updates
  5. Map pan → feed updates to visible area
  6. Register new user → login → save a property → verify saved
  7. Switch to seller mode → post a listing (if implemented)
  8. Admin dashboard loads with real data
  9. Scraper status shows recent crawl times
  10. Mobile responsive check (viewport resize)
- **Acceptance gate**: all 10 smoke tests pass; screenshot evidence in JOURNEY.md
- **Output**: smoke test checklist + results in `docs/agents/debugger/JOURNEY.md`
- **Verifier**: lead agent
- **Depends on**: BD-14, UX-11

### DBG-08: Security audit — auth, injection, XSS, CORS
- **Status**: `TODO`
- **Priority**: HIGH — public website must be secure
- **Read first**: all API routes, auth middleware, frontend forms
- **Do**:
  1. SQL injection audit: verify all queries use parameterized statements
  2. XSS audit: verify all user content is escaped in frontend
  3. Auth audit: verify JWT validation, session handling, password hashing
  4. CORS audit: verify only allowed origins can access API
  5. Rate limiting: verify API has rate limiting on auth endpoints
  6. Secrets audit: no API keys, passwords, or tokens in code or fixtures
  7. HTTPS: verify all traffic is encrypted
- **Acceptance gate**: zero critical vulnerabilities; medium issues documented with fix plan
- **Output**: security audit report in `docs/agents/debugger/JOURNEY.md`
- **Verifier**: lead agent
- **Depends on**: BD-14, BD-13

### DBG-09: End-of-run verification sweep
- **Status**: `TODO`
- **Priority**: HIGH — every non-debugger agent run must end with queued verification
- **Read first**: `docs/agents/README.md`, latest entries in `docs/agents/*/JOURNEY.md`, all `DONE_AWAITING_VERIFY` slices in this file
- **Do**:
  1. After each backend, scraper, or UX run, scan for the latest slice updates and match them to their acceptance gates.
  2. Execute the relevant verification immediately when the gate is runnable, or record an explicit deferred reason in `docs/agents/debugger/JOURNEY.md`.
  3. Keep a short pass/fail queue so no agent run ends without a debugger follow-up.
- **Acceptance gate**: every new non-debugger JOURNEY entry has a corresponding debugger verification note or an explicit deferral reason
- **Output**: rolling handoff log in `docs/agents/debugger/JOURNEY.md`, status updates here when verification completes
- **Verifier**: lead agent
- **Depends on**: —

---

## ═══════════════════════════════════════════════════════
## LEAD AGENT — Business, Strategy & Monitoring
## ═══════════════════════════════════════════════════════

**Mission**: Keep the project on track. Monitor dashboards, update architecture docs, resolve blockers, and ensure all agents are making progress toward the working website goal.

### LEAD-01: Unit economics, TAM/SAM/SOM, market analysis
- **Status**: `VERIFIED` (2026-04-08; created and generated)
- **Output**: `docs/business/unit-economics-market-analysis.md`
- **Verifier**: lead agent (self)
- **Depends on**: —

### LEAD-02: Investor presentation PDF with charts
- **Status**: `VERIFIED` (2026-04-08; generated with matplotlib + reportlab)
- **Output**: `output/pdf/investor-presentation-2026-04-08.pdf` (12 slides, 411 KB)
- **Generator**: `scripts/generate_investor_presentation.py`
- **Verifier**: lead agent (self)
- **Depends on**: LEAD-01

### LEAD-03: Product UX structure plan (LUN-style)
- **Status**: `VERIFIED` (2026-04-08; spec complete)
- **Output**: `docs/business/product-ux-structure.md`
- **Verifier**: lead agent (self)
- **Depends on**: —

### LEAD-04: Varna 3D OSM building integration plan
- **Status**: `VERIFIED` (2026-04-08; plan complete)
- **Output**: `docs/business/varna-3d-osm-integration.md`
- **Verifier**: lead agent (self)
- **Depends on**: —

### LEAD-05: Dashboard monitoring + architecture refresh (recurring)
- **Status**: `TODO` (recurring)
- **Priority**: HIGH — lead agent's primary ongoing responsibility
- **Read first**: `docs/exports/progress-dashboard.json`, all JOURNEY.md files, this file
- **Do**: On each activation:
  1. Read all JOURNEY.md files — identify progress since last check
  2. Update `docs/exports/progress-dashboard.json` with current slice statuses
  3. Run `make dashboard-doc` to regenerate dashboard HTML
  4. Identify blocked agents and propose unblock actions
  5. Update dependency graph if new slices were added
  6. Verify agent slices are being completed in priority order (CRITICAL first)
  7. Report: % complete toward working website, estimated remaining slices, top blockers
- **Acceptance gate**: dashboard is current; no agent has been stuck on same slice for >2 activations without blocker documented
- **Output**: updated dashboard, blocker notes, progress report

### LEAD-07: OpenClaw/Gemma run analysis and next-run preparation
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-27)
- **Priority**: HIGH
- **Read first**: `docs/exports/gemma4-openclaw-run-analysis-2026-04-27.md`, `docs/openclaw/gemma4-agent.md`, `docs/exports/taskforgema.md`
- **Do**: analyze what Gemma/OpenClaw produced, update only relevant agent tasks, prepare the next Codex quality-audit prompt path and the following Gemma image-report path, update website seed data with scraped property evidence, refresh dashboards, and run the website locally.
- **Acceptance gate**: analysis doc exists; `S1-21`, `S1-22`, and `DBG-08` are queued; website can show scraped items with media/quality metadata; dashboards are regenerated.
- **Output**: updated task queue, dashboards, frontend scraped-listing seed, run notes
- **Verifier**: self
- **Depends on**: —

### LEAD-06: GitLab CI/CD pipeline setup
- **Status**: `TODO`
- **Priority**: HIGH — automated testing and deployment
- **Read first**: `Makefile`, `Dockerfile`, `pyproject.toml`, `package.json`
- **Do**:
  1. Create `.gitlab-ci.yml` with stages: lint → test → build → deploy
  2. Lint stage: `make lint` + `make typecheck`
  3. Test stage: `make test` + `make golden-path` (with PostgreSQL service container)
  4. Build stage: Docker build for backend + Next.js build for frontend
  5. Deploy stage: trigger Railway deploy (backend) + Vercel deploy (frontend) on `main` branch
  6. Add branch protection: require CI pass before merge
- **Acceptance gate**: CI pipeline runs on every push; all stages green; auto-deploy works
- **Output**: `.gitlab-ci.yml`, CI documentation
- **Verifier**: debugger
- **Depends on**: BD-14, UX-11

---

## ═══════════════════════════════════════════════════════
## PRIORITY EXECUTION ORDER (Critical Path to Working Website)
## ═══════════════════════════════════════════════════════

The critical path to a working website, in order (**2026-04-09 operator wave**):

```
Phase A — Tier-1/2 live volume (scraper_1 + minimal backend) — DO FIRST:
  S1-14   →  Discovery pagination (DONE_AWAITING_VERIFY — debugger promotes when ready)
  S1-15   →  Live HTTP integration (httpx, rate limits, legal gates)
  BD-11   →  Unified DB ingest path MUST be live for volume counting
  S1-18   →  NON-STOP until ≥100 listings × ≥5 tier-1/2 sources in canonical_listing

Phase B — Backend core (backend_developer) — AFTER S1-18 VERIFIED:
  BD-12   →  Shop-style filter API
  BD-13   →  User profile + auth system (remaining items)
  BD-14   →  Railway deployment
  BD-15   →  Scraper orchestration loop (production cadence)

Phase C — Debugger consolidation:
  DBG-06  →  Batch-verify all pending DONE_AWAITING_VERIFY slices
  DBG-05  →  Stage-1 + live volume quality gate

Phase D — Other scrapers (parked until S1-18 done unless unblocker):
  T3-07   →  BCPEA live scraper
  (tier-3/tier-4 expansion per TASKS)

Phase E — Frontend (ux_ui_designer):
  UX-13   →  Design system tokens
  UX-08   →  Shop view with filters
  UX-09   →  Property detail page (LUN-style)
  UX-10   →  User profile cabinet + mode switching
  UX-11   →  Vercel deployment

Phase F — Polish (all agents):
  UX-04   →  Nationwide Bulgaria LUN-style map + listings experience
  UX-07   →  3D map with buildings
  BD-08   →  Varna OSM 3D data
  UX-05   →  AI chat panel
  BD-07   →  Chat API bridge
  UX-12   →  Admin dashboard
  DBG-07  →  End-to-end smoke test
  DBG-08  →  Security audit

Phase G — Growth:
  S1-16   →  Remaining tier-2 connectors
  S1-17   →  Playwright connectors
  SM-06   →  Telegram live connector
  T3-08   →  STR analytics API
  BD-16   →  Real-time updates (SSE)
  BD-09   →  Analytics views
  BD-10   →  Photo classification
```

---

## Dependency summary (what blocks what)

```
BD-01 ──► BD-02 ──► BD-03
  │         │         │
  │         │         ▼
  │         │       UX-02 ──► UX-03
  │         │
  │         ├──► BD-04 ──► BD-13 (user auth)
  │         ├──► BD-05 ──► BD-15 (scraper loop)
  │         ├──► BD-08 (Varna OSM buildings)
  │         ├──► BD-09 (property analytics)
  │         ├──► BD-10 (photo classification)
  │         ├──► BD-11 (unified DB) ──► S1-18 (live volume) ──► BD-12 (shop filter API)
  │         │                          ──► UX-08 (shop view)
  │         │                          ──► UX-09 (detail page)
  │         └──► UX-01
  │
  ├──► S1-11 (needs DB for ingest)
  ├──► T3-02 (needs DB for STR data)
  ├──► T3-05 (needs DB for register data)
  ├──► SM-02 (needs CRM tables)
  └──► BD-14 (Railway deploy) ──► UX-11 (Vercel deploy)
                                ──► BD-15 (scraper on Railway)
                                ──► DBG-07 (E2E smoke test)

S1-01..S1-10 ──► S1-14 (discovery pagination)
               ──► S1-15 (live HTTP) ──► BD-11 ──► S1-18 (≥100×5 volume) ──► S1-16 (tier-2 expansion)
               ──► S1-12 (tier-2 stubs)
               ──► S1-13 (product-type check)
               ──► DBG-03 (audit)

S1-18 ──► DBG-06 (batch verify) / DBG-05 (stage-1 + live gate)

S1-13 ──► DBG-05 (stage-1 quality gate)
       ──► BD-06 (map/search APIs, nationwide default)
       ──► UX-04 (Bulgaria map/feed)

BD-06 ──► BD-07 (chat API) ──► UX-05 (chat panel)
      ──► BD-12 (shop filter API)
      └──► UX-04 ──► UX-07 (3D map)
                  └──► UX-05

BD-11 ──► BD-12 ──► UX-08 (shop view)
BD-13 ──► UX-10 (user profiles)
BD-14 ──► UX-11 ──► DBG-07

T3-01 ──► T3-02..T3-05 ──► T3-06 (Varna enrichment)
      ──► T3-07 (BCPEA live)
      ──► T3-08 (STR analytics)

SM-01 ──► SM-02 ──► SM-03
      ──► SM-05 ──► SM-06 (Telegram live)
      ──► SM-07 (Facebook)
                 └──► SM-04 (social-to-property mapping)

UX-13 (design system) ──► UX-08 (shop view)
                       ──► UX-09 (detail page)
                       ──► UX-10 (user profiles)
                       ──► UX-12 (admin dashboard)

LEAD-05 (monitoring) ──► ongoing, no dependencies
LEAD-06 (CI/CD) ──► BD-14, UX-11
```
