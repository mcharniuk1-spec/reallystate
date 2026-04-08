# Agent Task Queue

Single source of truth for **what to do next** per specialist agent.

**Rules** (see `docs/agents/README.md` for the full protocol):

- One active slice per agent at a time.
- When done, set status to `DONE_AWAITING_VERIFY` and wait for the verifier.
- When verified, verifier sets status to `VERIFIED`.
- If blocked, record the blocker (points to another slice ID) and propose an alternative.
- Append a journal entry to `docs/agents/<agent>/JOURNEY.md` after every slice (done or blocked).

**Statuses**: `TODO` → `IN_PROGRESS` → `DONE_AWAITING_VERIFY` → `VERIFIED` / `BLOCKED`

---

## Constant recurring slices (all agents)

### CONST-01: Activation sync + dashboard refresh
- **Status**: `TODO` (recurring)
- **Read first**: `docs/agents/TASKS.md`, all `docs/agents/*/JOURNEY.md`, `docs/dashboard/index.html`
- **Do**: on each activation, review progress deltas, update task dependencies/notes, and regenerate dashboard/exports after doc/task changes
- **Acceptance gate**: latest run updates `TASKS.md` + dashboard JSON/HTML timestamps
- **Output**: refreshed `docs/exports/progress-dashboard.json`, `docs/dashboard/index.html`, and updated task notes
- **Verifier**: debugger
- **Depends on**: —

### CONST-02: Cross-agent note propagation
- **Status**: `TODO` (recurring)
- **Read first**: latest entries in all `JOURNEY.md` files
- **Do**: convert blockers/findings from one agent into explicit follow-up tasks for impacted agents
- **Acceptance gate**: each blocker has at least one mapped follow-up slice with dependency
- **Output**: updated `TASKS.md` dependencies and notes
- **Verifier**: lead agent + debugger
- **Depends on**: —

---

## Backend_developer (data engineer)

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
- **Status**: `TODO`
- **Read first**: `src/bgrealestate/dev_worker.py`, `src/bgrealestate/dev_scheduler.py`, `agent-skills/workflow-runtime/SKILL.md`
- **Do**: replace dev stubs with real Temporal worker + scheduler; implement `SourceDiscoveryWorkflow` and `ListingDetailWorkflow`
- **Acceptance gate**: jobs survive worker restart; cursors persist; `make test` passes
- **Output**: Temporal workflows, workers, scheduler config
- **Verifier**: debugger (idempotency + restart survival)
- **Depends on**: BD-01, BD-02

### BD-06: Varna-only MVP map/search + chat context APIs
- **Status**: `TODO`
- **Read first**: `PLAN.md` §8, `src/bgrealestate/api/routers/listings.py`, `src/bgrealestate/api/routers/chat.py`, `sql/schema.sql`
- **Do**: enforce MVP geo scope to Varna city + Varna region for `/listings` + `/map` contracts; expose chat context payload so AI chat can always view current property + map filter state
- **Acceptance gate**: API contract test proves Varna-only scope when MVP flag is on; chat context endpoint returns selected property + active filters
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

---

## Scraper_1 (marketplace websites)

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

---

## Debugger

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
- **Do**: for each awaiting slice, run its acceptance gate commands; record PASS/FAIL in own JOURNEY.md; update TASKS.md status
- **Acceptance gate**: every verified slice has a matching JOURNEY.md entry
- **Output**: verification entries in JOURNEY.md + status updates here
- **Verifier**: lead agent (spot checks)
- **Depends on**: —

### DBG-03: Cross-agent safety audit
- **Status**: `VERIFIED` (2026-04-08)
- **Read first**: `.cursor/BUGBOT.md`, `data/source_registry.json`, all `tests/test_*.py`
- **Do**: check all connectors for legal gate enforcement; check all tests for live network calls; check fixtures for secrets/PII; check media storage for Postgres binaries
- **Acceptance gate**: zero violations found, or violations documented as blockers on the responsible agent
- **Output**: audit entry in JOURNEY.md; blockers filed in TASKS.md if needed
- **Verifier**: lead agent
- **Depends on**: S1-01 through S1-10 (need connectors to audit)

### DBG-04: CI pipeline verification
- **Status**: `VERIFIED` (2026-04-08)
- **Read first**: `.gitlab-ci.yml` (when created), `Makefile`, `Dockerfile`
- **Do**: verify CI runs `make test`, `make lint`, `make validate`, `make golden-path` (with DB service container)
- **Acceptance gate**: pipeline green on fixture-only tests; golden-path job passes with service containers
- **Output**: verification entry in JOURNEY.md
- **Verifier**: self
- **Depends on**: BD-05 (needs real worker/scheduler before full CI is meaningful)

### DBG-05: Verify stage-1 scraping is perfect before Varna 3D map MVP
- **Status**: `TODO`
- **Read first**: `docs/exports/stage1-product-type-coverage.md` (from S1-13), `scripts/golden_path_check.py`, `/admin/source-stats`
- **Do**: verify stage-1 scrape quality and product-type completeness; block map/search scope expansion until coverage and ingestion quality pass
- **Acceptance gate**: verifier note confirms all required product types are covered and golden path passes
- **Output**: verification entry in `docs/agents/debugger/JOURNEY.md` + status update in TASKS
- **Verifier**: lead agent
- **Depends on**: S1-13, BD-01

---

## UX_UI_designer (frontend)

### UX-01: Operator dashboard UI plan
- **Status**: `VERIFIED` (2026-04-08; debugger contract check)
- **Read first**: `PLAN.md` §8 (`/admin` row), `src/bgrealestate/api/routers/`, BD-02 API outputs
- **Do**: define `/admin` UX layout and data model (source list, filters, coverage bars, error queues)
- **Acceptance gate**: markdown spec + component breakdown reviewed by debugger for API contract alignment
- **Output**: `docs/agents/ux_ui_designer/admin-ui-spec.md`
- **Verifier**: debugger (API contract alignment)
- **Depends on**: BD-02 (needs API routes to design against)

### UX-02: Beta main page — map + listings + category picker
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08)
- **Read first**: `PLAN.md` §8 (`/listings` + `/map` rows), `src/bgrealestate/api/routers/listings.py`
- **Do**: Build split-view main page with MapLibre map (left) + scrollable listing feed (right) + intent toggle (Buy/Rent/Short-term/Auction) + category picker (Apartment/House/Studio/Villa/...) + search + source badges. Uses 12 mock listings matching `canonical_listing` API schema. Map pins highlight on card hover and vice-versa.
- **Acceptance gate**: page loads with mock/seeded data; category/intent filters work; map renders with pins; responsive mobile stacking
- **Output**: `app/(main)/page.tsx`, `components/listings/ListingFeed.tsx`, `components/listings/ListingCard.tsx`, `components/listings/CategoryPicker.tsx`, `components/map/MapCanvas.tsx`, `components/map/FullScreenMap.tsx`, `lib/types/listing.ts`, `lib/mock/listings.ts`
- **Verifier**: debugger
- **Depends on**: UX-01

### UX-03: Wire listings feed to live `/listings` API
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08)
- **Read first**: `src/bgrealestate/api/routers/listings.py`, `lib/server/fetch-backend.ts`
- **Do**: Replace mock data with TanStack Query fetch from `/api/backend/listings`; add infinite scroll pagination; remove mock module when live data is seeded
- **Acceptance gate**: page fetches from FastAPI; pagination works; fallback to mock if API unreachable
- **Output**: updated `ListingFeed.tsx`, new `lib/hooks/useListings.ts`
- **Verifier**: debugger
- **Depends on**: UX-02, BD-02, BD-03

### UX-04: Varna-only LUN-style map + listings experience
- **Status**: `TODO`
- **Read first**: `PLAN.md` §8, `docs/agents/ux_ui_designer/operator-dashboard-spec.md`, LUN-style reference notes
- **Do**: shape homepage UX to LUN-like split flow (map + feed + filters), scoped to Varna city/region for MVP
- **Acceptance gate**: prototype shows Varna-only boundaries, map filters, listing cards, and synchronized selection
- **Output**: UX spec/update doc + component task breakdown
- **Verifier**: debugger + backend_developer
- **Depends on**: UX-03, BD-06, DBG-05

### UX-05: AI chat panel with property/map-aware context
- **Status**: `TODO`
- **Read first**: `app/(main)/page.tsx`, chat API contracts, `PLAN.md` chat sections
- **Do**: define and implement persistent chat panel connected to AI chat API, always aware of selected property and active map filters
- **Acceptance gate**: chat can reference current property card + filtered map state and propose next search/refinement actions
- **Output**: frontend chat-panel implementation plan and integration tasks
- **Verifier**: debugger
- **Depends on**: UX-04, BD-06

---

## Scraper_T3 (vendor/partner/official routes)

### T3-01: Tier-3 ingestion policy and integration contracts
- **Status**: `VERIFIED` (2026-04-08; debugger policy + fixture contract review)
- **Read first**: `data/source_registry.json` (tier-3 sources), `AGENTS.md` (guardrails), `deep-research-report.md` (per-source legal/extraction notes)
- **Do**: define what's allowed per source and the integration pattern for each:
  - Airbnb: partner feed only (`legal_mode=official_partner_or_vendor_only`, `risk=prohibited_without_contract`)
  - Booking.com: partner feed only (`legal_mode=official_partner_or_vendor_only`, `risk=prohibited_without_contract`)
  - Vrbo: partner feed only (`legal_mode=official_partner_or_vendor_only`, `risk=high`)
  - Flat Manager: partner feed (`legal_mode=official_partner_or_vendor_only`, `risk=medium`)
  - Menada Bulgaria: partner feed (`legal_mode=official_partner_or_vendor_only`, `risk=medium`)
  - AirDNA: licensed data subscription (`legal_mode=official_partner_or_vendor_only`, `risk=low`)
  - Airbtics: licensed data API (`legal_mode=official_partner_or_vendor_only`, `risk=low`)
  - BCPEA property auctions: public crawl with review (`legal_mode=public_crawl_with_review`, `risk=medium`)
  - Property Register: manual/consent only (`legal_mode=consent_or_manual_only`, `risk=high`)
  - KAIS Cadastre: manual/consent only (`legal_mode=consent_or_manual_only`, `risk=high`)
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
- **Alternative while blocked**: keep Tier-3 outputs stable and wait for debugger verification pass; resume immediately after dependency statuses move to `VERIFIED`.

---

## Scraper_SM (social overlays)

### SM-01: Social ingestion contract (policy + fixtures)
- **Status**: `VERIFIED` (2026-04-08; debugger consent + fixture review)
- **Read first**: `data/source_registry.json` (tier-4 sources), `AGENTS.md` (guardrails), `sql/schema.sql` (CRM tables)
- **Do**: define what's allowed per platform:
  - Telegram public channels: official API ingestion (`legal_mode=official_api_allowed`)
  - X public accounts: official API (`legal_mode=official_api_allowed`)
  - Facebook/Instagram/Threads: manual/consent only (`legal_mode=consent_or_manual_only`)
  - Viber/WhatsApp: explicit opt-in only (`legal_mode=consent_or_manual_only` / `official_partner_or_vendor_only`)
- **Acceptance gate**: policy doc reviewed by debugger; consent checklist complete; fixture format defined
- **Output**: `docs/agents/scraper_sm/social-ingestion-policy.md`, fixture templates under `tests/fixtures/social/`, plus detailed contract at `docs/agents/scraper_sm/social_ingestion_contract.md`
- **Verifier**: debugger (consent checklist + Bugbot priority: legal gates)
- **Depends on**: —

### SM-02: Telegram public channel connector (fixture-first)
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08: acceptance gate passed)
- **Read first**: SM-01 policy, `src/bgrealestate/connectors/protocol.py`, CRM tables in `sql/schema.sql`
- **Do**: connector that maps Telegram channel messages → `lead_message` + `lead_thread`; NLP entity extraction for phone/price/area/intent; fixture-backed tests
- **Acceptance gate**: `make test` passes; fixtures contain redacted posts; no live Telegram calls in tests
- **Output**: `src/bgrealestate/connectors/telegram_public.py`, `tests/test_telegram_public_connector.py` (4 passing tests), NLP extraction via `connectors/social_parser.py`
- **Verifier**: debugger + backend_developer (CRM table round-trip)
- **Depends on**: SM-01, BD-01
- **Verification evidence**: `make test` → 86 tests OK (11 skipped)

### SM-03: X (Twitter) public monitor connector (fixture-first)
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08: acceptance gate passed)
- **Read first**: SM-01 policy, `data/source_registry.json` (X entry)
- **Do**: connector for X API JSON → lead extraction; fixture-backed
- **Acceptance gate**: `make test` passes; no live API calls in tests
- **Output**: `src/bgrealestate/connectors/x_public.py`, `tests/test_x_public_connector.py`, fixtures under `tests/fixtures/x_public/`
- **Verifier**: debugger
- **Depends on**: SM-01
- **Verification evidence**: `make test` → 86 tests OK (11 skipped)

### SM-04: Social lead-to-property mapping for AI chat context
- **Status**: `TODO`
- **Read first**: SM-01 policy, `src/bgrealestate/connectors/social_parser.py`, chat/API contracts
- **Do**: provide social lead mapping format so chat can show related properties and map-filter suggestions from social signals
- **Acceptance gate**: fixture-backed mapping examples pass tests; no live social calls in tests
- **Output**: mapping schema + fixtures + parser update tasks
- **Verifier**: debugger + ux_ui_designer
- **Depends on**: SM-02, UX-05

---

## Dependency summary (what blocks what)

```
BD-01 ──► BD-02 ──► BD-03
  │         │         │
  │         │         ▼
  │         │       UX-02
  │         │
  │         ├──► BD-04
  │         ├──► BD-05
  │         └──► UX-01
  │
  ├──► S1-11 (needs DB for ingest)
  ├──► T3-02 (needs DB for STR data)
  ├──► T3-05 (needs DB for register data)
  └──► SM-02 (needs CRM tables)

S1-01..S1-10 ──► S1-12 (tier-2 stubs follow tier-1 pattern)
               ──► S1-13 (product-type completion check)
               ──► DBG-03 (need connectors to audit)

S1-13 ──► DBG-05 (stage-1 scrape quality verification)
       ──► BD-06 (Varna-only API scope gate)
       ──► UX-04 (Varna map/feed UX gate)

T3-01 ──► T3-02 (licensed data)
      ──► T3-03 (BCPEA auctions)
      ──► T3-04 (partner feed stubs)
      ──► T3-05 (official registers)
      ──► T3-06 (Varna enrichment handoff)

SM-01 ──► SM-02 ──► SM-03
                 └──► SM-04 (social lead-to-property chat context)

BD-06 ──► BD-07 ──► UX-05
      └──► UX-04 ──► UX-05
DBG-05 ──► BD-06 / UX-04 / T3-06
```
