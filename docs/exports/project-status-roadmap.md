# Bulgaria Real Estate Platform Project Status Roadmap

Updated: 2026-04-08

## Current Stage

The project is at **Stage 2: Database And Persistence - In Progress**.

Stage 1 development environment setup is complete.

An early **Stage 4 parser-first connector slice** is also present for `Homes.bg`, but it is fixture-backed only and does not change the recommendation to continue Stage 2 next.

This means the repository has moved beyond planning into local development scaffolding and has started the database persistence layer. It is still **not yet a live real estate scraper**, **not yet a fully runnable PostgreSQL/PostGIS application**, and **not yet a frontend MVP**.

The current repo can load and classify sources, run a generic parser pipeline test, export source/legal matrices, generate a source-link workbook/report, and guide Cursor/Codex/Claude agents through the next phases. It cannot yet continuously scrape real sites every 10 minutes or serve the map/listing/chat UI.

## What Works Now

- Source registry with 44 market sources.
- Source links, access mode, legal mode, risk mode, extraction method, and MVP phase.
- Generated source-link workbook and detailed debug report.
- Generated source/legal matrices.
- Python package scaffold under `src/bgrealestate`.
- Dataclass domain models for sources, listings, contacts, buildings, publishing, and compliance.
- Generic HTML/JSON-LD parser for sample listing pages.
- Canonical listing normalizer.
- Basic dedupe scorer.
- Basic nearby-building matcher.
- Publishing eligibility skeleton for official/authorized/assisted modes.
- Cursor/Codex/Claude agent rules, skills, and automation guidance.
- SQL blueprint for source, crawl, property, media, map, user, CRM, and publishing tables.
- Python 3.12 project pin via `.python-version` and Dockerfile.
- Docker Compose scaffold for PostgreSQL/PostGIS, Redis, MinIO, Temporal, and Temporal UI.
- Backend dependency metadata in `pyproject.toml`.
- Frontend dependency metadata in `package.json`.
- Development setup guide in `docs/development-setup.md`.
- Lightweight development run targets for API, worker, scheduler, and frontend shell.
- Local `make validate` command for JSON, Office package, and unit-test validation.
- One-shot development worker and scheduler smoke checks inside `make validate`.
- Alembic migration scaffold with an initial schema revision entrypoint.
- `make migrate` now points to Alembic for environments with installed dependencies and a configured `DATABASE_URL`.
- SQLAlchemy model foundation for the core source, crawl, listing, property, media, geo, user, CRM, and publishing areas.
- Repository layer foundation for source registry, raw captures, source listings, snapshots, and canonical listings.
- Offline `Homes.bg` fixture corpus under `tests/fixtures/homes_bg/`.
- Fixture-backed `Homes.bg` detail parsing tests for normal, missing-field, blocked-page, and removed-listing cases.
- Generic ingestion helper that persists raw capture, source listing, snapshot, and canonical listing records together.
- Marketplace connector factory for all non-social registry sources (37 portals/classifieds/agencies/OTAs/registers): shared `HtmlPortalConnector`, legal-rule derivation, optional `sync-database` CLI to upsert `source_registry` planning fields, `source_legal_rule`, and `source_endpoint` rows.
- Alembic revision `20260408_0002` plus `sql/schema.sql` updates for `primary_url`, `related_urls`, `languages`, and `listing_types` on `source_registry`.
- Unit tests for current scaffold.

## What Does Not Work Yet

- No real tier-1 live connector for `OLX.bg`, `alo.bg`, `imot.bg`, or other portals beyond the shared HTML scaffold (Homes.bg remains the only fixture-tuned parser).
- No PostgreSQL/PostGIS migration runtime yet.
- No Temporal workers or scheduler yet.
- No Redis rate-limit state yet.
- No S3/MinIO object storage adapter yet.
- No media/photo download pipeline yet.
- No production dedupe/entity graph persistence yet.
- No geocoder/cadastre/building-footprint integration yet.
- No FastAPI API server yet.
- No Next.js frontend yet.
- The current `run-api`, `run-worker`, `run-scheduler`, and `run-frontend` targets are development placeholders, not production services.
- Stage 2 database work is partially implemented: SQLAlchemy model coverage and some repositories now exist, but tenant/account boundaries, broader repository coverage, and real migration execution against PostgreSQL are still pending.
- Source registry persistence now stores `primary_url`, `related_urls`, `languages`, and `listing_types` when `sync-database` is run against PostgreSQL.
- Docker is not available in the current local shell, so Compose services have not been started or validated here.
- `Homes.bg` discovery is still a placeholder and there is no live crawl execution path validated against a running database.
- No `/listings`, `/properties/[id]`, `/map`, `/chat`, `/settings`, or `/admin` pages yet.
- No real CRM messaging integration yet.
- No real reverse publishing adapters yet.
- No production deployment, monitoring, or security hardening yet.

## Completed Work

- [x] 1. Read and incorporated the local research material, including `deep-research-report.md`.
- [x] 2. Created the main MVP technical plan in `PLAN.md`.
- [x] 3. Created portable plan entrypoint `platform-mvp-plan.md`.
- [x] 4. Created cross-agent instructions in `AGENTS.md`.
- [x] 5. Added Cursor project rules under `.cursor/rules/`.
- [x] 6. Added Cursor MCP configuration in `.cursor/mcp.json`.
- [x] 7. Added Cursor Background Agent config in `.cursor/environment.json`.
- [x] 8. Added Cursor Bugbot review instructions in `.cursor/BUGBOT.md`.
- [x] 9. Created 12 repo-local agent skills under `agent-skills/`.
- [x] 10. Added Claude skill mirror guidance under `.claude/skills/`.
- [x] 11. Expanded `data/source_registry.json` to 44 sources.
- [x] 12. Added `primary_url` and `related_urls` to registry entries.
- [x] 13. Added `legal_mode` and `mvp_phase` to source registry entries.
- [x] 14. Added missing sources from the prior plans: `Flat Manager`, `Menada Bulgaria`, `Imoti.info`, `realestates.bg`, `Imoteka.bg`, and `Threads public profiles`.
- [x] 15. Generated `artifacts/source-matrix.md`.
- [x] 16. Generated `artifacts/legal-risk-matrix.md`.
- [x] 17. Generated source-link workbook `docs/exports/bulgaria-real-estate-source-links.xlsx`.
- [x] 18. Generated source-link CSV `docs/exports/bulgaria-real-estate-source-links.csv`.
- [x] 19. Generated detailed debug report `docs/exports/bulgaria-real-estate-source-report.md`.
- [x] 20. Generated Word-compatible debug report `docs/exports/bulgaria-real-estate-source-report.docx`.
- [x] 21. Added reproducible report generator `scripts/generate_source_report.py`.
- [x] 22. Added Mermaid architecture source `docs/diagrams/platform-architecture.mmd`.
- [x] 23. Added Makefile commands for tests, matrix export, report generation, and future lifecycle targets.
- [x] 24. Added `.env.example` with planned infrastructure variables.
- [x] 25. Expanded the SQL blueprint in `sql/schema.sql` for source/crawl/listing/property/media/geo/user/CRM/publishing tables.
- [x] 26. Extended Python source registry models to include planning fields and URLs.
- [x] 27. Updated matrix exporters to include URL and legal planning fields.
- [x] 28. Updated tests for registry planning fields and key sources.
- [x] 29. Verified JSON validity for source registry and Cursor configs.
- [x] 30. Verified generated `.xlsx` and `.docx` as valid Office ZIP packages.
- [x] 31. Verified current test suite with `make test`: 21 tests passing, with 1 optional DB smoke test skipped when `DATABASE_URL` is unset.

## Execution Plan To Final MVP

### Stage 1: Development Environment

- [x] 32. Pin local/project Python to 3.12+ through Docker, pyenv, or uv.
- [x] 33. Add full `docker-compose.yml` for PostgreSQL/PostGIS, Redis, MinIO, Temporal, and local app services.
- [x] 34. Replace placeholder Make targets with working `make run-api`, `make run-worker`, `make run-scheduler`, and `make run-frontend`.
- [x] 35. Add dependency management for backend packages: FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, Temporal SDK, Redis, httpx, parser libraries, geo libraries.
- [x] 36. Add dependency management for frontend packages: Next.js, TypeScript, TanStack Query, MapLibre GL JS, deck.gl, chosen UI/CSS system.
- [x] 37. Add CI/local validation commands for lint, typecheck, unit tests, integration tests, and docs/report export.

### Stage 2: Database And Persistence

- [x] 38. Convert `sql/schema.sql` blueprint into Alembic migrations.
- [x] 38a. Start SQLAlchemy model coverage for source, crawl, listing, property, media, geo, users, CRM, and publishing areas.
- [x] 38b. Start repository layer implementation for source registry, raw captures, listings, snapshots, and canonical listings.
- [x] 38c. Add migration tests and an optional DB roundtrip smoke scaffold.
- [ ] 39. Create SQLAlchemy models for source, crawl, listing, property, media, geo, users, CRM, and publishing tables.
- [ ] 40. Implement repository layer for source registry, crawl jobs, raw captures, listings, properties, media, CRM, and publishing.
- [ ] 41. Add tenant/account boundaries to all user, CRM, settings, and publishing tables.
- [ ] 42. Add migration tests and repository tests.
- [ ] 43. Add PostGIS geometry index checks and sample viewport query tests.
- [ ] 44. Decide retention policy for raw HTML body vs object-storage-only payloads.

### Stage 3: Runtime And Compliance

- [ ] 45. Implement runtime compliance evaluator for `legal_mode`, `risk_mode`, `access_mode`, and `publish_capable`.
- [ ] 46. Block unsafe live scrape attempts before connector execution.
- [ ] 47. Block unsafe publish attempts before payload creation.
- [ ] 48. Add Temporal workflow skeletons for discovery, detail fetch, enrichment, media processing, CRM sync, publishing, and docs export.
- [ ] 49. Add durable job IDs and idempotency keys.
- [ ] 50. Add crawl cursors and retry attempts.
- [ ] 51. Add Redis-backed per-source rate limits and locks.
- [ ] 52. Add dead-letter/review queues for parser, connector, geocode, and publishing failures.

### Stage 4: Tier-1 Source Connectors

- [x] 53. Create fixture folder and expected-output format for connector tests.
- [x] 54. Capture or manually save offline fixtures for `Homes.bg` detail/removed/blocked cases.
- [ ] 55. Implement `Homes.bg` discovery parser.
- [x] 56. Implement `Homes.bg` detail parser.
- [ ] 57. Persist `Homes.bg` raw captures and canonical listing snapshots.
- [x] 58. Add `Homes.bg` parser regression tests with no live network dependency.
- [ ] 59. Add OLX API connector only after credentials/config are available.
- [ ] 60. Add `alo.bg` fixture parser and connector.
- [ ] 61. Add `imot.bg` fixture parser and connector.
- [ ] 62. Add `BulgarianProperties` fixture parser and connector.
- [ ] 63. Add `Address.bg`, `SUPRIMMO`, `LUXIMMO`, `property.bg`, and `imoti.net` in separate gated slices.
- [ ] 64. Require at least 3 tier-1 sources end-to-end before tier-2 expansion.

### Stage 5: Tier-2, Tier-3, And Social Overlays

- [ ] 65. Add tier-2 connectors only after tier-1 parser success rate is stable.
- [ ] 66. Add partnership/licensing-first handling for `Imoti.info`.
- [ ] 67. Add headless/partner-review handling for `Imoteka.bg`, `Indomio.bg`, and `Realistimo`.
- [ ] 68. Add STR/vendor integration stubs for `AirDNA`, `Airbtics`, `Flat Manager`, and `Menada Bulgaria`.
- [ ] 69. Add official-service enrichment adapters for `KAIS Cadastre`, `Property Register`, and `BCPEA property auctions` only where permitted.
- [ ] 70. Add Telegram public-channel ingestion as a lead overlay with NLP extraction.
- [ ] 71. Keep Facebook, Instagram, Threads, Viber, and WhatsApp consent-gated or manual-assist until official/authorized access is confirmed.

### Stage 6: Media, Dedupe, And Entity Graph

- [ ] 72. Implement S3/MinIO object storage adapter.
- [ ] 73. Implement image URL retention without immediate binary download for low-priority sources.
- [ ] 74. Implement media download queue for approved sources.
- [ ] 75. Implement image hashing and perceptual duplicate detection.
- [ ] 76. Implement property entity creation from canonical listings.
- [ ] 77. Implement property offer records for sale, long-term rent, short-term rent, and auctions.
- [ ] 78. Implement contact and organization normalization.
- [ ] 79. Implement cross-source duplicate scoring with address, area, price, contacts, image hashes, project name, and coordinates.
- [ ] 80. Add duplicate review queue and merge audit trail.
- [ ] 81. Measure duplicate precision against a labeled Bulgarian sample.

### Stage 7: Geospatial And Building Matching

- [ ] 82. Implement address normalization and geocoder abstraction.
- [ ] 83. Add city/resort/neighborhood taxonomy for Sofia, Varna, Burgas, Sunny Beach/Nessebar, Bansko, Plovdiv, and national expansion.
- [ ] 84. Import or connect permitted building footprints.
- [ ] 85. Implement PostGIS building match scoring.
- [ ] 86. Persist building match confidence and review status.
- [ ] 87. Add 2D fallback when geometry confidence is weak.
- [ ] 88. Add map viewport queries and building summary queries.

### Stage 8: Backend APIs

- [ ] 89. Add FastAPI application skeleton.
- [ ] 90. Add `/sources`, `/crawl-jobs`, and `/parser-failures` APIs.
- [ ] 91. Add `/listings`, `/listings/{id}`, `/properties/{id}`, `/properties/{id}/history`, and `/properties/{id}/media` APIs.
- [ ] 92. Add `/map/viewport`, `/map/buildings/{id}`, and optional MVT tile APIs.
- [ ] 93. Add `/crm/threads`, `/crm/threads/{id}/messages`, reminders, templates, and assignment APIs.
- [ ] 94. Add `/me`, `/settings/team`, `/settings/api-keys`, and `/settings/channel-accounts` APIs.
- [ ] 95. Add `/publishing/capabilities`, `/publishing/profiles`, `/publishing/jobs`, and `/publishing/channel-mappings` APIs.
- [ ] 96. Add auth/RBAC middleware and audit logging.

### Stage 9: Frontend MVP

- [ ] 97. Create Next.js frontend app under `web/`.
- [ ] 98. Implement shared typed API client.
- [ ] 99. Implement `/listings` infinite scrolling page with filters, sorting, source badges, and create-lead action.
- [ ] 100. Implement `/properties/[id]` detail page with gallery, source links, facts, price history, map mini-panel, and lead action.
- [ ] 101. Implement `/map` with MapLibre GL JS, deck.gl, 2D/3D toggle, clusters, pins, building drawer, and confidence badges.
- [ ] 102. Implement `/chat` CRM inbox with thread list, conversation pane, linked properties, assignment, reminders, templates, and audit timeline.
- [ ] 103. Implement `/settings` for profile, team, API keys, connected channels, crawler settings, and publishing settings.
- [ ] 104. Implement `/admin` source health, parser failure, dedupe review, geocode review, compliance review, publish queue, and sync status pages.
- [ ] 105. Add responsive mobile navigation for Map, Listings, Chat, and Profile.

### Stage 10: Reverse Publishing

- [ ] 106. Implement channel capability matrix.
- [ ] 107. Implement distribution profile review and approval.
- [ ] 108. Implement publish eligibility engine backed by compliance flags.
- [ ] 109. Implement dry-run publishing adapters.
- [ ] 110. Implement Booking.com official connectivity interface only after credentials/partner status.
- [ ] 111. Implement Airbnb authorized software-connected route only after credentials/partner status.
- [ ] 112. Implement Bulgarian portal feed/upload capability matrix.
- [ ] 113. Implement assisted-manual workflow for browser-only destinations.
- [ ] 114. Implement external listing ID reconciliation and sync state.

### Stage 11: QA, Monitoring, And Launch

- [ ] 115. Add full integration tests for crawl-to-canonical-listing flow.
- [ ] 116. Add fixture tests for every active connector.
- [ ] 117. Add frontend Playwright tests for all MVP pages.
- [ ] 118. Add observability with structured logs, metrics, Sentry, and dashboard placeholders.
- [ ] 119. Add performance tests for search and map viewport APIs.
- [ ] 120. Add privacy/security review for contacts, messages, API keys, raw captures, and audit logs.
- [ ] 121. Run pilot ingestion on a small approved source set.
- [ ] 122. Promote only stable tier-1 sources from hourly to 10-minute cadence.
- [ ] 123. Complete operator readiness checklist.
- [ ] 124. Complete public MVP launch checklist.
- [ ] 125. Generate final Markdown, DOCX, PDF, XLSX, and execution report artifacts.

## Immediate Next Recommended Step

The next implementation slice should be:

1. Treat Stage 1 as complete and continue from the current Stage 2 baseline.
2. Run Alembic against a real PostgreSQL/PostGIS instance with `DATABASE_URL` configured.
3. Add repository-focused tests for the repositories already present.
4. Add tenant/account boundaries to user, CRM, settings, and publishing tables.
5. After those checks, complete `Homes.bg` discovery and full persistence wiring.

## Progress Log

- 2026-04-07: Completed Stage 0 foundation and generated source-link/debug report artifacts.
- 2026-04-07: Started Stage 1 development environment setup. Added `.python-version`, `Dockerfile`, `docker-compose.yml`, backend dependencies in `pyproject.toml`, frontend dependencies in `package.json`, and `docs/development-setup.md`. Local validation targets exist, but full CI/integration validation is still pending.
- 2026-04-07: Completed Stage 1 local scaffolding. Added lightweight dev entrypoints for API, worker, scheduler, and frontend shell, plus `make validate`. Stage 2 database migrations/repositories are now the next implementation focus.
- 2026-04-07: Validated Stage 1 locally. `make validate` now checks JSON configs, Office package integrity, one-shot worker/scheduler startup, and the current unit test suite.
- 2026-04-07: Started Stage 2 database persistence. Added Alembic scaffold, initial schema revision that applies `sql/schema.sql`, migration docs, `make migrate`, and migration scaffold tests.
- 2026-04-07: Added the first SQLAlchemy model foundation for core MVP areas. Item 39 remains open until all schema tables and repository tests are covered.
- 2026-04-07: Added initial repository foundations plus a fixture-backed `Homes.bg` parser slice and offline fixtures. This is useful progress, but Stage 2 persistence verification still remains the main next step.
- 2026-04-08: Reconciled the Cursor-updated roadmap with the actual repository state. Confirmed 21 tests passing with 1 optional DB smoke test skipped, identified source-registry persistence gaps in the DB layer, and kept Stage 2 as the main execution priority before broader connector expansion.
