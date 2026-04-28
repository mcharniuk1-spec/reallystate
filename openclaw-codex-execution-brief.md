# OpenClaw Codex Execution Brief

This document is the execution handoff for Codex running in OpenClaw.

It is intended to be:

- the single source of truth for implementation order
- the progress tracker
- the acceptance checklist
- the output contract for every phase

---

## 1. Mission

Build a Bulgaria real estate ingestion platform that:

- ingests sale, long-term rent, short-term rent, new-build, land, and related listing data
- prioritizes the Bulgarian market with strong Black Sea coverage
- supports source-first ingestion and testing before UI work
- adds reverse connectivity and publishing after ingestion is stable
- treats legal mode, access mode, and platform risk as first-class constraints

Execution order:

1. Source-first ingestion and testing
2. Data hardening, dedupe, geospatial enrichment, compliance gating
3. Reverse connectivity and publishing
4. Internal ops UI
5. Public aggregator UI
6. Later building/3D experiences

---

## 2. Guardrails

The agent must follow these rules:

- Do not make Airbnb or Booking.com scraping a core dependency.
- Prefer official APIs, partner feeds, licensed datasets, or explicit authorization whenever available.
- Treat WhatsApp, Viber, and private social groups as opt-in or owned-business only.
- Do not make autonomous mass account creation a dependency.
- Use assisted onboarding where KYC, verification, or CAPTCHA requires human completion.
- Do not start public UI work until ingestion and reverse connectivity gates are passed.
- Preserve and extend the current implementation instead of replacing it wholesale.

---

## 3. Workspace State

Current workspace already contains a foundation implementation:

- [x] Python package scaffold in [src/bgrealestate](/Users/getapple/Documents/Real Estate Bulg/src/bgrealestate)
- [x] Seeded source registry in [data/source_registry.json](/Users/getapple/Documents/Real Estate Bulg/data/source_registry.json)
- [x] Canonical models and enums
- [x] Standard ingestion pipeline skeleton
- [x] Publishing eligibility engine and payload mapper
- [x] SQL schema in [sql/schema.sql](/Users/getapple/Documents/Real Estate Bulg/sql/schema.sql)
- [x] Source matrix artifact in [artifacts/source-matrix.md](/Users/getapple/Documents/Real Estate Bulg/artifacts/source-matrix.md)
- [x] Legal risk artifact in [artifacts/legal-risk-matrix.md](/Users/getapple/Documents/Real Estate Bulg/artifacts/legal-risk-matrix.md)
- [x] Unit tests passing
- [x] Docker Compose stack available (Postgres/PostGIS, Redis, MinIO, Temporal, Temporal UI)
- [x] Alembic migrations wire initial schema from `sql/schema.sql` (`make db-init`)
- [x] Next.js app shell present at repo root (`npm run dev`)
- [x] In-repo operator docs for Docker + DB + media: `docs/docker-and-database.md`

Known current limitation:

- [ ] No live tier-1 source connectors yet
- [ ] Live volume gate not yet proven in PostgreSQL `canonical_listing` (S1-18 proof path)
- [ ] No real fixture corpus yet
- [ ] No geocoder/cadastre integration yet
- [ ] No publishing adapters yet
- [ ] No operator UI yet

---

## 4. Progress Dashboard

Update this table continuously during execution.

| Phase | Status | Owner | Start Date | End Date | Notes |
|---|---|---|---|---|---|
| 0. Foundation scaffold | Done | Codex |  |  | Initial package, registry, schema, tests |
| 1. Persistence and runtime | Not Started |  |  |  |  |
| 2. Tier-1 source connectors | Not Started |  |  |  |  |
| 3. Fixture and parser QA system | Not Started |  |  |  |  |
| 4. Dedupe, geocode, building matching | Not Started |  |  |  |  |
| 5. Compliance and legal gating | Not Started |  |  |  |  |
| 6. Reverse publishing control plane | Not Started |  |  |  |  |
| 7. Internal ops interface | Not Started |  |  |  |  |
| 8. Public aggregator UI | Blocked |  |  |  | Must not start until gates pass |

Status values:

- `Not Started`
- `In Progress`
- `Blocked`
- `In Review`
- `Done`

---

## 5. Required Deliverables

The agent must produce all of the following by the end of execution:

- working source registry and source-specific connector layer
- persistence layer and migration-ready schema usage
- queue/scheduler orchestration for recurring crawls
- fixtures for representative pages per active source
- parser regression tests
- dedupe scoring and merge workflow
- geocoding/building matching pipeline
- compliance flagging and publish eligibility gating
- reverse publishing control plane
- operator-facing review and sync tooling
- updated matrices and execution report

Required final outputs in the repo:

- `README.md` updated with real run instructions
- source connector modules for active sources
- persistence/runtime config
- artifact exports
- test fixtures
- test coverage for ingestion and publishing flows
- execution report with what works, what is partial, and what is blocked

---

## 6. Acceptance Gates

The agent must not advance phases without meeting the gate for the current phase.

### Gate A: Before moving from Phase 1 to Phase 2

- database-backed persistence is working
- source registry can be loaded and queried by runtime code
- scheduler/runner can create crawl jobs
- tests still pass

### Gate B: Before moving from Phase 2 to Phase 3

- at least 3 tier-1 source connectors implemented end-to-end
- connector outputs normalize into canonical listings
- raw capture storage works
- at least one tier-1 source supports incremental crawling

### Gate C: Before moving from Phase 3 to Phase 4

- fixtures exist for every implemented source
- parser regressions run in CI/local test command
- encoding-sensitive cases are covered
- failure cases are captured

### Gate D: Before moving from Phase 4 to Phase 5

- dedupe scoring can compare listings from different sources
- geocoding fallback exists
- building matching produces confidence values
- duplicate evaluation set exists

### Gate E: Before moving from Phase 5 to Phase 6

- every active source has explicit legal/access mode
- prohibited sources are blocked from unsafe flows
- publish eligibility can be blocked by compliance flags

### Gate F: Before moving from Phase 6 to Phase 7

- publication control plane exists
- at least one partner-style channel adapter is implemented as a real interface
- listing-to-channel mapping and sync state are persisted
- dry-run publish flow is testable

### Gate G: Before moving from Phase 7 to Phase 8

- operator review queue is functional
- sync status and audit trail are visible
- ingestion is stable
- reverse connectivity is stable
- external mapping IDs reconcile correctly

---

## 7. Detailed Task Tree

The agent should execute the following tasks in order.

---

## Phase 1. Persistence and Runtime

### Objective

Turn the current framework into a runnable ingestion system with persistent storage and scheduled jobs.

### Operator fast-path (current repo)

This repository already includes a local Docker Compose runtime and migrations. For OpenClaw runs, treat these as the default:

- Start dependencies: `make dev-up` (requires Docker Desktop / Engine on the host)
- Wait for DB: `make dev-ready`
- Apply schema: `export DATABASE_URL=... && make db-init`
- See docs: `docs/docker-and-database.md`

Do not “recreate persistence from scratch” unless a specific missing dependency is proven.

### Tasks

- [ ] Choose runtime stack shape and keep it lightweight.
- [ ] Add config management for environment-specific settings.
- [ ] Add storage adapter layer for registry, captures, listings, events, and publish jobs.
- [ ] Implement a SQLite or PostgreSQL-compatible repository layer.
- [ ] Wire the current SQL schema into executable initialization code.
- [ ] Add crawl job and crawl cursor persistence.
- [ ] Add queue model for discovery, detail fetch, parse, normalize, enrich, and publish.
- [ ] Add a scheduler entrypoint for hourly cadence.
- [ ] Add a CLI command to initialize storage.
- [ ] Add a CLI command to enqueue source runs.

### Expected Outputs

- runtime configuration module
- storage/repository package
- initialization command
- scheduler command
- persisted crawl job records

### Acceptance Criteria

- [ ] A new environment can initialize storage with one command.
- [ ] Source jobs can be created and persisted.
- [ ] Listings and events can be written and read back.
- [ ] Existing tests still pass.

### Progress Notes

- Date:
- Completed:
- Blockers:
- Next step:

---

## Phase 2. Tier-1 Source Connectors

### Objective

Implement real connectors for the highest-priority sources first.

### Priority Order

1. `OLX.bg`
2. `Homes.bg`
3. `alo.bg`
4. `imot.bg`
5. `BulgarianProperties`
6. `Address.bg`
7. `SUPRIMMO`
8. `LUXIMMO`
9. `property.bg`
10. `imoti.net`

### Tasks

- [ ] Define a base connector interface.
- [ ] Implement discovery-stage and detail-stage methods.
- [ ] Implement per-source URL patterns and pagination handling.
- [ ] Implement summary-field extraction.
- [ ] Implement detail-page parsing hooks.
- [ ] Implement source-specific field mapping into canonical schema.
- [ ] Implement source-specific legal mode enforcement.
- [ ] Implement incremental cursor strategy for each source.
- [ ] Add source-specific unit fixtures.
- [ ] Add connector smoke tests.

### Subtasks per connector

- [ ] Discovery route list
- [ ] Pagination strategy
- [ ] Listing-card parser
- [ ] Detail URL normalization
- [ ] Detail parser
- [ ] Hidden JSON/XHR parser if applicable
- [ ] Media extraction
- [ ] Contact extraction
- [ ] Reference ID normalization
- [ ] Source-specific notes in docs

### Expected Outputs

- connector modules under `src/bgrealestate/connectors/`
- source-specific parser tests
- fixture corpus for list and detail pages
- runnable commands per source

### Acceptance Criteria

- [ ] At least 3 tier-1 sources work end-to-end.
- [ ] Connector output lands in canonical schema.
- [ ] Raw capture and parsed output are persisted.
- [ ] Failures produce actionable logs.

### Progress Notes

- Date:
- Completed:
- Blockers:
- Next step:

---

## Phase 3. Fixture and Parser QA System

### Objective

Make the parser layer stable, testable, and regression-safe.

### Tasks

- [ ] Create fixture directories by source and page type.
- [ ] Save representative list pages and detail pages.
- [ ] Add multilingual and encoding-sensitive fixtures.
- [ ] Add negative fixtures: removed page, malformed page, blocked page.
- [ ] Add regression assertions for canonical fields.
- [ ] Add fixture metadata manifest.
- [ ] Add snapshot-like parser outputs for comparison.

### Fixture Minimums

- [ ] 20 representative pages per tier-1 source
- [ ] 10 representative pages per tier-2 source once implemented
- [ ] at least one blocked/anti-bot case per difficult source

### Expected Outputs

- fixture manifest
- parser regression suite
- parser health report

### Acceptance Criteria

- [ ] Parser tests can run without live network calls.
- [ ] Encoding issues are covered.
- [ ] Changes to parsers visibly break tests if outputs regress.

### Progress Notes

- Date:
- Completed:
- Blockers:
- Next step:

---

## Phase 4. Dedupe, Geocode, and Building Matching

### Objective

Move from source listings to normalized property entities and building-aware matching.

### Tasks

- [ ] Persist `property_entity`, `contact_entity`, and `building_entity`.
- [ ] Expand dedupe scoring beyond the current heuristic scaffold.
- [ ] Add configurable score thresholds.
- [ ] Add manual-review state for ambiguous duplicates.
- [ ] Add geocoding service abstraction.
- [ ] Add fallback geocoding path.
- [ ] Add neighborhood/resort taxonomy mapping.
- [ ] Add building matcher using point proximity first.
- [ ] Add later-ready hook for polygon matching.
- [ ] Add confidence scoring and review flags.

### Matching Inputs

- source reference IDs
- address text
- city/district/resort
- price
- area
- contact overlap
- image similarity or media hash
- building/project names
- geospatial distance

### Expected Outputs

- dedupe scorer implementation
- merge/review workflow
- geocoder abstraction
- building match records
- duplicate-labeled evaluation set

### Acceptance Criteria

- [ ] Cross-source duplicate candidates can be scored.
- [ ] Geocoded listings get confidence values.
- [ ] Building matches can be stored and reviewed.
- [ ] An evaluation set exists for quality checking.

### Progress Notes

- Date:
- Completed:
- Blockers:
- Next step:

---

## Phase 5. Compliance and Legal Gating

### Objective

Make legal mode operational in the runtime, not just documented in the registry.

### Tasks

- [ ] Add enforcement rules by `access_mode` and `risk_mode`.
- [ ] Block prohibited connectors without explicit override/config.
- [ ] Add compliance flag generation during ingestion.
- [ ] Add publish-blocking compliance evaluation.
- [ ] Add source legal summary export.
- [ ] Add audit trail for why a source or publish job was blocked.
- [ ] Add operator-visible review status for compliance exceptions.

### Required Compliance Examples

- [ ] prohibit unsafe Airbnb scraping paths
- [ ] prohibit unsafe Booking scraping paths
- [ ] mark WhatsApp/Viber ingestion as consent-only
- [ ] distinguish official register enrichment from listing acquisition

### Expected Outputs

- compliance evaluator module
- source legal review report
- block reasons in runtime outputs

### Acceptance Criteria

- [ ] Every active source has enforceable access/legal behavior.
- [ ] Unsafe publish requests can be blocked with clear reason codes.
- [ ] Compliance flags are persisted and test-covered.

### Progress Notes

- Date:
- Completed:
- Blockers:
- Next step:

---

## Phase 6. Reverse Publishing Control Plane

### Objective

Implement the stage that happens after ingestion is stable and before aggregator UI work.

### Scope

The goal is not mass autonomous account creation.

The goal is:

- partner onboarding
- authorized account linking
- assisted manual onboarding
- outbound payload preparation
- sync state tracking
- dry-run and audit support

### Tasks

- [ ] Expand `distribution_profile`, `channel_mapping`, `publish_job`, `publish_result`.
- [ ] Add operator/account model for owned vs managed accounts.
- [ ] Add onboarding state machine.
- [ ] Add `PublishEligibilityEngine` persistence and orchestration.
- [ ] Add channel adapter interfaces.
- [ ] Implement Booking adapter scaffold.
- [ ] Implement Airbnb adapter scaffold.
- [ ] Implement Bulgarian portal adapter interface.
- [ ] Implement agency syndication adapter interface.
- [ ] Add dry-run mode for all adapters.
- [ ] Add reconciliation task to sync external IDs and channel state back.

### Subtasks

#### 6.1 Booking

- [ ] property payload mapper
- [ ] content/photo/rate/availability payload contracts
- [ ] certification/test-mode workflow
- [ ] external listing mapping persistence

#### 6.2 Airbnb

- [ ] software-connected listing payload mapper
- [ ] listing/status/pricing sync contracts
- [ ] onboarding mode validation
- [ ] external mapping persistence

#### 6.3 Bulgarian portals and agencies

- [ ] upload/feed capability matrix
- [ ] portal-specific capability flags
- [ ] assisted workflow if no safe API/feed exists

### Expected Outputs

- publishing service package
- channel adapter interfaces
- dry-run publish command
- reconciliation job
- onboarding/checklist documentation

### Acceptance Criteria

- [ ] Publish eligibility is enforceable and persisted.
- [ ] At least one partner-style channel dry-run works.
- [ ] Channel state transitions are recorded.
- [ ] Unsupported channels fail safely.

### Progress Notes

- Date:
- Completed:
- Blockers:
- Next step:

---

## Phase 7. Internal Ops Interface

### Objective

Build internal operator tooling before any public aggregator interface.

### Tasks

- [ ] Add source-health dashboard view
- [ ] Add parser failure queue
- [ ] Add duplicate review queue
- [ ] Add compliance review queue
- [ ] Add publish review queue
- [ ] Add channel sync status view
- [ ] Add audit trail view
- [ ] Add search for canonical listings and property entities

### Minimum UI Modules

- [ ] source status
- [ ] job runs
- [ ] listing detail
- [ ] duplicate review
- [ ] compliance flags
- [ ] publish queue
- [ ] channel mappings
- [ ] sync history

### Expected Outputs

- internal web UI or terminal dashboard
- operator workflows for review and approvals

### Acceptance Criteria

- [ ] Operators can review and approve listings for publish.
- [ ] Operators can inspect why a source or publish was blocked.
- [ ] Operators can see sync state per property/channel.

### Progress Notes

- Date:
- Completed:
- Blockers:
- Next step:

---

## Phase 8. Public Aggregator UI

### Objective

Start only after all previous gates are passed.

### Tasks

- [ ] public search API
- [ ] listing search UI
- [ ] map/search integration
- [ ] filters and facets
- [ ] public building summary layer
- [ ] later 3D/building interaction layer

### Hard Block

- [ ] Do not start this phase until Phases 1-7 are accepted.

### Progress Notes

- Date:
- Completed:
- Blockers:
- Next step:

---

## 8. Source-Specific Execution Priorities

These are the first real sources the agent should implement.

### Tier-1 First Batch

- [ ] `OLX.bg`
- [ ] `Homes.bg`
- [ ] `alo.bg`

### Tier-1 Second Batch

- [ ] `imot.bg`
- [ ] `BulgarianProperties`
- [ ] `Address.bg`

### Tier-1 Third Batch

- [ ] `SUPRIMMO`
- [ ] `LUXIMMO`
- [ ] `property.bg`
- [ ] `imoti.net`

### Tier-2 Deferred Until Tier-1 Stabilizes

- [ ] `Bazar.bg`
- [ ] `Domaza`
- [ ] `Realistimo`
- [ ] `Home2U`
- [ ] `Yavlena`
- [ ] `Holding Group Real Estate`
- [ ] `Rentica.bg`
- [ ] `Svobodni-kvartiri.com`
- [ ] `Pochivka.bg`
- [ ] `Vila.bg`
- [ ] `ApartmentsBulgaria.com`
- [ ] `Indomio.bg`
- [ ] `Unique Estates`
- [ ] `Lions Group`

### Tier-3 and Tier-4 Handling

- [ ] `Airbnb` via official/authorized partner path only
- [ ] `Booking.com` via connectivity/content integration only
- [ ] `AirDNA` / `Airbtics` as enrichment
- [ ] `Property Register` and `KAIS Cadastre` as verification/enrichment only
- [ ] `Telegram public channels` as lead overlay
- [ ] `X public search/accounts` as low-priority overlay
- [ ] `Facebook public groups/pages` only where legally accessible
- [ ] `Instagram public profiles` only with safe/authorized strategy
- [ ] `Viber` / `WhatsApp` opt-in only

---

## 9. Outputs by Phase

This section defines what the agent must leave behind after each phase.

### Phase 1 Outputs

- code
- runtime setup
- initialization commands
- persisted job model
- updated README

### Phase 2 Outputs

- connector modules
- source fixtures
- source parser docs
- normalized listing outputs

### Phase 3 Outputs

- fixture corpus
- regression tests
- parser report

### Phase 4 Outputs

- dedupe report
- geocode report
- building-match report

### Phase 5 Outputs

- compliance report
- source risk report
- blocked-flow examples

### Phase 6 Outputs

- publish dry-run report
- channel capability matrix
- onboarding checklist docs
- reconciliation report

### Phase 7 Outputs

- internal ops interface
- review workflow docs
- screenshots or demo notes

### Phase 8 Outputs

- public search interface
- API docs
- deployment notes

---

## 10. Execution Log Template

Append entries here during execution.

### Log Entry Template

- Date:
- Phase:
- Status:
- Files changed:
- Commands run:
- Tests run:
- Outputs produced:
- Issues found:
- Decisions made:
- Next action:

### Execution Log

- Date:
  Phase:
  Status:
  Files changed:
  Commands run:
  Tests run:
  Outputs produced:
  Issues found:
  Decisions made:
  Next action:

---

## 11. Final Completion Checklist

Mark this only when the implementation is fully ready for handoff.

- [ ] source registry operational
- [ ] persistence operational
- [ ] scheduler operational
- [ ] tier-1 connectors operational
- [ ] parser fixtures and tests operational
- [ ] dedupe operational
- [ ] geocoding/building matching operational
- [ ] compliance gating operational
- [ ] reverse publishing control plane operational
- [ ] internal ops interface operational
- [ ] public UI either completed or explicitly deferred by gate
- [ ] README updated
- [ ] artifacts regenerated
- [ ] final execution report written

---

## 12. Immediate Next Command for the Agent

The next concrete implementation target should be:

1. Phase 1 persistence/runtime
2. Then Phase 2 first-batch connectors: `OLX.bg`, `Homes.bg`, `alo.bg`

If the agent needs a smaller first milestone, use this:

- [ ] add repository/storage layer
- [ ] add `init-db` CLI
- [ ] add `run-source` CLI
- [ ] implement first live connector for `Homes.bg`
- [ ] add fixture-backed parser tests for `Homes.bg`

