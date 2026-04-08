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
- **Status**: `TODO`
- **Read first**: `src/bgrealestate/api/routers/`, `src/bgrealestate/db/repositories.py`
- **Do**: extend stats to include photo coverage and intent/category breakdown from `canonical_listing`
- **Acceptance gate**: `/admin` dashboard shows coverage bars; XLSX export includes new columns
- **Output**: updated `/admin` dashboard + XLSX export
- **Verifier**: debugger
- **Depends on**: BD-02

### BD-04: Auth / RBAC on CRM and listings routes
- **Status**: `TODO`
- **Read first**: `sql/schema.sql` (app_user, api_key, permission_grant), `PLAN.md` §7
- **Do**: API key or session auth middleware; protect CRM write + listings write + admin routes
- **Acceptance gate**: unauthenticated requests return 401/403; `make test` passes with auth fixtures
- **Output**: auth middleware + test fixtures
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
- **Status**: `TODO`
- **Read first**: `src/bgrealestate/connectors/ingest.py`, `src/bgrealestate/connectors/factory.py`
- **Do**: CLI command that ingests 1 fixture into DB using `ingest.py`
- **Acceptance gate**: stats endpoints reflect the inserted record; `make golden-path` still passes
- **Output**: CLI command + test
- **Verifier**: debugger + backend_developer (DB round-trip)
- **Depends on**: BD-01, S1-01

### S1-12: Tier-2 connector stubs (fixture-only)
- **Status**: `TODO`
- **Read first**: `data/source_registry.json` (tier-2 sources), `src/bgrealestate/connectors/scaffold.py`
- **Do**: stub connectors + 1 fixture each for Bazar.bg, Domaza, Yavlena, Home2U (highest-value tier-2)
- **Acceptance gate**: `make test` passes; legal gates enforced for `licensing_required` sources
- **Output**: connectors, fixtures, tests
- **Verifier**: debugger
- **Depends on**: S1-03 (tier-1 pattern established)

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
- **Status**: `TODO` (recurring)
- **Read first**: this file (scan for `DONE_AWAITING_VERIFY` status)
- **Do**: for each awaiting slice, run its acceptance gate commands; record PASS/FAIL in own JOURNEY.md; update TASKS.md status
- **Acceptance gate**: every verified slice has a matching JOURNEY.md entry
- **Output**: verification entries in JOURNEY.md + status updates here
- **Verifier**: lead agent (spot checks)
- **Depends on**: —

### DBG-03: Cross-agent safety audit
- **Status**: `TODO`
- **Read first**: `.cursor/BUGBOT.md`, `data/source_registry.json`, all `tests/test_*.py`
- **Do**: check all connectors for legal gate enforcement; check all tests for live network calls; check fixtures for secrets/PII; check media storage for Postgres binaries
- **Acceptance gate**: zero violations found, or violations documented as blockers on the responsible agent
- **Output**: audit entry in JOURNEY.md; blockers filed in TASKS.md if needed
- **Verifier**: lead agent
- **Depends on**: S1-01 through S1-10 (need connectors to audit)

### DBG-04: CI pipeline verification
- **Status**: `TODO`
- **Read first**: `.gitlab-ci.yml` (when created), `Makefile`, `Dockerfile`
- **Do**: verify CI runs `make test`, `make lint`, `make validate`, `make golden-path` (with DB service container)
- **Acceptance gate**: pipeline green on fixture-only tests; golden-path job passes with service containers
- **Output**: verification entry in JOURNEY.md
- **Verifier**: self
- **Depends on**: BD-05 (needs real worker/scheduler before full CI is meaningful)

---

## UX_UI_designer (frontend)

### UX-01: Operator dashboard UI plan
- **Status**: `TODO`
- **Read first**: `PLAN.md` §8 (`/admin` row), `src/bgrealestate/api/routers/`, BD-02 API outputs
- **Do**: define `/admin` UX layout and data model (source list, filters, coverage bars, error queues)
- **Acceptance gate**: markdown spec + component breakdown reviewed by debugger for API contract alignment
- **Output**: `docs/agents/ux_ui_designer/admin-ui-spec.md`
- **Verifier**: debugger (API contract alignment)
- **Depends on**: BD-02 (needs API routes to design against)

### UX-02: `/listings` page implementation
- **Status**: `TODO`
- **Read first**: `PLAN.md` §8 (`/listings` row), `web/`, API contract from BD-02
- **Do**: Next.js page with infinite scroll, filters, source badges, photo preview
- **Acceptance gate**: page loads with mock/seeded data; Playwright snapshot (when available)
- **Output**: `web/app/listings/` components
- **Verifier**: debugger
- **Depends on**: UX-01, BD-02, BD-03

---

## Scraper_SM (social overlays)

### SM-01: Social ingestion contract (policy + fixtures)
- **Status**: `TODO`
- **Read first**: `data/source_registry.json` (tier-4 sources), `AGENTS.md` (guardrails), `sql/schema.sql` (CRM tables)
- **Do**: define what's allowed per platform:
  - Telegram public channels: official API ingestion (`legal_mode=official_api_allowed`)
  - X public accounts: official API (`legal_mode=official_api_allowed`)
  - Facebook/Instagram/Threads: manual/consent only (`legal_mode=consent_or_manual_only`)
  - Viber/WhatsApp: explicit opt-in only (`legal_mode=consent_or_manual_only` / `official_partner_or_vendor_only`)
- **Acceptance gate**: policy doc reviewed by debugger; consent checklist complete; fixture format defined
- **Output**: `docs/agents/scraper_sm/social-ingestion-policy.md`, fixture templates under `tests/fixtures/social/`
- **Verifier**: debugger (consent checklist + Bugbot priority: legal gates)
- **Depends on**: —

### SM-02: Telegram public channel connector (fixture-first)
- **Status**: `TODO`
- **Read first**: SM-01 policy, `src/bgrealestate/connectors/protocol.py`, CRM tables in `sql/schema.sql`
- **Do**: connector that maps Telegram channel messages → `lead_message` + `lead_thread`; NLP entity extraction for phone/price/area/intent; fixture-backed tests
- **Acceptance gate**: `make test` passes; fixtures contain redacted posts; no live Telegram calls in tests
- **Output**: connector, fixtures, tests, NLP extraction helpers
- **Verifier**: debugger + backend_developer (CRM table round-trip)
- **Depends on**: SM-01, BD-01

### SM-03: X (Twitter) public monitor connector (fixture-first)
- **Status**: `TODO`
- **Read first**: SM-01 policy, `data/source_registry.json` (X entry)
- **Do**: connector for X API JSON → lead extraction; fixture-backed
- **Acceptance gate**: `make test` passes; no live API calls in tests
- **Output**: connector, fixtures, tests
- **Verifier**: debugger
- **Depends on**: SM-01

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
  └──► SM-02 (needs CRM tables)

S1-01..S1-10 ──► S1-12 (tier-2 stubs follow tier-1 pattern)
               ──► DBG-03 (need connectors to audit)

SM-01 ──► SM-02 ──► SM-03
```
