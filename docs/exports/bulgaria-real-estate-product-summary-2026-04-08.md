# Bulgaria Real Estate Product Summary, Backlog, And Dashboard Plan

Date: 2026-04-08
Generated at: 2026-04-08T16:22:29
Workspace: `/Users/getapple/Documents/Real Estate Bulg`

## 1. Executive Summary

This product is a Bulgaria-focused real estate intelligence and operator platform. It ingests listings and lead signals from Bulgarian portals, agencies, public social channels, official/vendor datasets, and partner routes; normalizes them into one canonical database; powers listing search, a 2D/3D map, CRM chat workflows, and operator review; and only allows reverse publishing through compliant official, partner, vendor, or assisted-manual paths.

Today the product is best described as an operator-first MVP foundation with strong source coverage, working fixture-backed scraper slices, a PostgreSQL/PostGIS-ready schema, API scaffolding, and a Next.js shell for `/listings`, `/properties/[id]`, `/map`, `/chat`, `/settings`, and `/admin`.

## 2. Global Idea

The global idea is to build one operator-grade real estate system for Bulgaria that can watch the fragmented market, turn many raw sources into one trusted property database, visualize inventory spatially on a 2D/3D map, coordinate leads in chat/CRM, and later publish back only through compliant channels.

In practice that means:
1. The market layer watches portals, agencies, social overlays, official registers, and vendor feeds.
2. The data layer turns messy source records into canonical Bulgaria property intelligence.
3. The operations layer gives the team one dashboard to start projects, review source health, inspect crawl failures, route leads, and control publishing.
4. The experience layer exposes `/listings`, `/properties/[id]`, `/map`, `/chat`, `/settings`, and `/admin` as the main operating surfaces.

## 3. What The Product Does

1. Tracks the Bulgarian real estate market across portals, agencies, STR/vendor sources, official registers, and social overlays.
2. Stores all incoming listing evidence as raw capture plus normalized canonical listing records.
3. Prepares a national property database for Bulgaria using PostgreSQL/PostGIS, property entities, offers, CRM data, and publishing records.
4. Supports an operator map experience with 3D buildings where geometry exists and 2D fallback pins where it does not.
5. Supports CRM chat and lead handling so agents/operators can organize conversations, notes, and linked properties.
6. Enforces legal mode, access mode, and risk mode before scraper or publisher behavior is allowed.
7. Creates the control plane for future compliant reverse publishing to approved channels only.

## 4. Product Services

| Service | What it does now | Direction |
| --- | --- | --- |
| Source registry and compliance | Stores 44 sources with tier, legal mode, risk mode, access mode, extraction strategy, languages, and listing types. | Control plane for all future connectors and publishing routes. |
| Scraper and connector layer | Tier-1 fixture-backed connectors exist for the main marketplace/agency sites; social contract exists for Telegram-style overlays. | Move from fixture-first to DB-backed, live-safe runs. |
| Canonical Bulgaria database | SQL blueprint defines 59 tables and 13 indexes for sources, crawl jobs, raw captures, canonical listings, property graph, CRM, users, geo, and publishing. | PostgreSQL/PostGIS source of truth. |
| Listings and search APIs | FastAPI routes exist for listings, crawl jobs, CRM, readiness, chat, admin stats, and system endpoints. | Wire all pages to real database-backed search and detail APIs. |
| 2D/3D map layer | Frontend shell exists; map page is reserved for MapLibre GL and deck.gl with building summaries and viewport queries. | Enable 3D when geometry confidence is strong; fall back to 2D pins otherwise. |
| CRM chat | Chat page shell and CRM endpoints are in place for thread/message flow. | Expand to assignment, reminders, linked properties, and operator replies. |
| Admin operations | Admin source stats and dashboard spec exist. | Add parser failures, compliance review, dedupe review, and publish queue panels. |
| Reverse publishing | Control-plane logic exists, but live outbound publishing remains gated. | Official, authorized, partner, vendor, or assisted-manual only. |

## 5. How The Product Works

1. A source is selected from the registry.
2. The runtime checks `legal_mode`, `risk_mode`, `access_mode`, and whether the path is allowed.
3. A connector gathers data through HTML, API, headless, partner-feed, licensed-data, or consent/manual routes.
4. Raw evidence is captured and normalized into canonical listing records.
5. Canonical listings feed the Bulgaria property database, dedupe graph, CRM, and search surfaces.
6. Search and detail pages expose the listings to operators and later to public-facing UI.
7. The map surface groups results spatially and will render 3D building context when geometry is available.
8. CRM chat links people, messages, properties, and follow-up actions.
9. Publishing stays blocked unless the channel is explicitly compliant.

## 6. Master Backlog

This backlog section is intentionally focused on the global idea and the next buildable slices, so it can work as a project-wide execution plan.

| Backlog lane | What must happen | Current status | Primary owner |
| --- | --- | --- | --- |
| Foundations | Keep registry, legal rules, skills, plans, and coordination docs current. | Complete and active. | lead agent + all agents |
| Persistence | Finish Postgres/PostGIS runtime, migrations, repository coverage, and DB-backed health checks. | In progress. | backend_developer |
| Runtime compliance | Enforce live scraping and publishing gates from registry rules at runtime. | Next. | backend_developer + debugger |
| Tier-1 connectors | Move from fixture-backed coverage to DB-backed, live-safe ingest for tier-1 sources. | Partial. | scraper_1 |
| Tier-2 and overlays | Add stubs and then safe sources for tier-2, Telegram overlays, and approved vendor/register routes. | Not started. | scraper_1 + scraper_sm |
| Dedupe and entity graph | Build duplicate detection, property entities, offers, and review queues. | Not started. | backend_developer |
| Geo and 3D map | Add geocoder, building matching, viewport APIs, and 2D/3D rendering support. | Not started. | backend_developer + ux_ui_designer |
| Backend APIs | Complete listings, properties, map, CRM, admin, settings, auth, and publishing APIs. | Partial. | backend_developer |
| Frontend MVP | Replace route shells with working listings, map, chat, settings, and admin experiences. | Shell only. | ux_ui_designer |
| Publishing | Add dry-run and then compliant live publishing adapters only for approved routes. | Gated. | backend_developer + debugger |

Priority order for the next execution wave:
1. Finish Python 3.12-aligned persistence/runtime validation.
2. Make tier-1 fixture-backed ingestion write verified rows into the database.
3. Expand `/admin` into the central operator control panel.
4. Turn `/listings`, `/chat`, and `/map` from shells into operator-usable workflows.

## 7. By The Numbers

| Metric | Current value |
| --- | --- |
| Total registry sources | 44 |
| Marketplace/official/vendor sources in tiers 1-3 | 37 |
| Tier-1 sources | 10 |
| Tier-2 sources | 17 |
| Tier-3 sources | 10 |
| Tier-4 sources | 7 |
| Publish-capable sources | 32 |
| Non-publish-capable sources | 12 |
| Access modes in use | headless: 5, html: 21, licensed_data: 2, manual_consent_only: 7, official_api: 3, partner_feed: 6 |
| Legal modes in use | consent_or_manual_only: 6, legal_review_required: 2, licensing_required: 1, official_api_allowed: 3, official_partner_or_vendor_only: 8, public_crawl_with_review: 24 |
| Source fixture directories | 11 |
| Fixture cases with expected outputs | 30 |
| Tier-1 fixture coverage | 10/10 |
| Agent skills committed in repo | 21 |
| SQL tables in blueprint | 59 |
| SQL indexes in blueprint | 13 |
| Declared API routes | 14 |
| Roadmap completion | 46/128 |
| Roadmap remaining | 82 |

## 8. Scraper Status

| Scraper metric | Current reading |
| --- | --- |
| Tier-1 connector coverage | 10/10 tier-1 sources have fixture-backed parsing or legal-gated fixture stubs. |
| Social overlay coverage | Telegram public channel fixture contract exists; live social ingestion remains gated. |
| Live crawl telemetry | No live scrape telemetry available in repo evidence. |
| DB-ingested listing telemetry | No live database counts available because `DATABASE_URL` is not set in this shell. |
| Test command result | `Ran 62 tests in 0.082s` / `OK (skipped=8)` |
| Test runtime | Python 3.9.6 |
| Test exit code | 0 |

Interpretation:
- The scraper architecture is well-covered in fixtures, but not yet validated as a live production crawler in this local environment.
- The main blocker visible in this run is environment drift: the local shell is using Python 3.9 while the repo targets Python 3.12, so backend/runtime validation is still lower confidence than a true Python 3.12 run.

## 9. Product Surfaces

| Surface | Current meaning | Current state |
| --- | --- | --- |
| `/listings` | Searchable listings feed for Bulgaria. | Shell exists; still wired to source/demo data rather than real listing search. |
| `/properties/[id]` | Canonical property detail page. | Route shell exists. |
| `/map` | 2D/3D market map using MapLibre + deck.gl. | Shell exists; waiting for `/map/viewport` and building APIs. |
| `/chat` | CRM inbox with threads, messages, and linked properties. | Shell exists; CRM APIs partially scaffolded. |
| `/settings` | Team, keys, channel accounts, crawler/publishing settings. | Shell exists. |
| `/admin` | Operator dashboard for source health and review queues. | Stats route exists; detailed multi-panel spec exists. |

## 10. Detailed Dashboard Instruction

This section is written as a practical instruction set for the project dashboard and the project-creation dashboard. It is based on the current admin spec, roadmap, schema, and source registry.

### Dashboard purpose

The dashboard should be the operating system for the project. It should let an operator create a new market-monitoring project, choose compliant source packs, see scraper and database readiness, watch milestone progress, and then move directly into source health, map, CRM, and publishing review.

### Dashboard layout

1. Top health strip: Postgres, Redis, API, worker, scheduler, and object storage state.
2. KPI row: enabled sources, live-safe sources, canonical listings, crawl failures, parser failures, duplicate-review count, CRM open threads.
3. Left navigation: Project setup, Sources, Crawl jobs, Parser failures, Dedupe review, Geocode review, CRM, Publish queue, Settings.
4. Main work area: switchable tables, map panels, drawers, and project forms.
5. Right context drawer: raw metadata, legal notes, source config, audit trail, and retry actions.

### Project creation flow

1. Define project identity: project name, team owner, country/city/resort focus, and property intents to track.
2. Pick source packs: tier-1 portals, agencies, vendor feeds, official registers, and any approved social overlays.
3. Review compliance: every selected source must show legal mode, access mode, risk mode, and whether publishing is allowed.
4. Configure cadence: choose hourly vs ten-minute runs, priority, and which sources remain fixture-only vs live-safe.
5. Set data rules: dedupe sensitivity, geocode confidence threshold, required listing fields, and photo expectations.
6. Set CRM routing: default owner, inbox rules, note templates, reminder defaults, and linked listing behavior.
7. Set milestone targets: current phase, acceptance gate, verifier, and next required slice.
8. Save and launch only when environment, migration, and source-gate checks are green.

### Dashboard blocks

| Dashboard block | What it should contain | Why it matters |
| --- | --- | --- |
| Project identity | Project name, city/resort focus, team owner, deal type focus (sale, rent, STR, land, new-build). | Defines scope for the whole workspace. |
| Source pack picker | Tier-1, tier-2, vendor, register, and social overlay toggles with legal-mode badges. | Lets operators choose only compliant source bundles. |
| Geography and map preview | Bulgaria map with Varna, Burgas, Sofia, Bansko, Plovdiv, and resort filters; 2D/3D coverage preview. | Makes project coverage visible before scraping starts. |
| Scraper plan | Cadence, priority, endpoint type, expected freshness, fixture availability, and risk mode. | Turns strategy into an execution plan. |
| Database readiness | Migration status, source sync status, object storage status, and queue health. | Prevents launching work into a broken stack. |
| CRM setup | Team inbox owner, lead routing rules, reminder templates, assignment defaults. | Makes chat and follow-up usable on day one. |
| Compliance gate | Legal mode summary, partner requirements, consent/manual requirements, publish restrictions. | Stops unsafe scraping or publishing early. |
| KPI board | Sources enabled, listings expected, listings ingested, crawl failures, parser failures, duplicates awaiting review. | Gives the operator an instant health read. |
| Milestone tracker | Stage path, current milestone, verification owner, blocker list, next gate. | Keeps the project moving in a visible, Duolingo-like sequence. |

### Dashboard acceptance criteria

1. A new project cannot be activated if any selected source violates legal mode or requires a missing partner route.
2. A new project cannot be activated if migrations are missing or the registry is not synced.
3. KPI cards must match the same underlying stats that power `/admin/source-stats` and future crawl failure queues.
4. Every top-level number must open a drill-down table or drawer.
5. The milestone tracker must show who owns the next slice and which gate must pass next.

## 11. Dashboard Delivery Backlog

| Dashboard backlog item | What to build | Status |
| --- | --- | --- |
| Dashboard A | Project creation wizard with identity, source pack, compliance, cadence, CRM, and milestone steps. | Not started. |
| Dashboard B | Live health strip and KPI row from readiness plus source stats. | Partially ready in backend. |
| Dashboard C | Source health table with filters, tier badges, legal badges, and drill-down. | Spec ready, implementation pending. |
| Dashboard D | Crawl jobs table with retry and metadata drawer. | Backend route ready, frontend pending. |
| Dashboard E | Parser failure, dedupe review, geocode review, compliance review, and publish queue panels. | Backend pending. |
| Dashboard F | Map preview inside dashboard for project geography and 3D readiness. | Not started. |
| Dashboard G | CRM inbox summary widgets and assignment/status shortcuts. | Partial backend, frontend pending. |

## 12. Project Progress Path

```text
[1] Foundations and Source Registry      COMPLETE
    |
    v
[2] Database and Persistence            IN PROGRESS
    |
    v
[3] Runtime and Compliance Gates        NEXT
    |
    v
[4] Tier-1 Connectors                   PARTIAL
    |
    v
[5] Tier-2, STR, and Social Overlays    NOT STARTED
    |
    v
[6] Media, Dedupe, Entity Graph         NOT STARTED
    |
    v
[7] Geospatial and 3D Map               NOT STARTED
    |
    v
[8] Backend APIs                        PARTIAL
    |
    v
[9] Frontend MVP                        SHELL ONLY
    |
    v
[10] Reverse Publishing                 GATED

Overall roadmap completion: 46/128 steps (35%).
```

## 13. Agent Updates

### backend_developer

| Metric | Value |
| --- | --- |
| Verified slices | 2 |
| Open TODO slices | 3 |
| Blocked slices | 0 |
| Latest journal heading | After 2026-04-08 session 2 — control plane bootstrap |
| Latest note | - **Blocker:** Docker was unavailable in this session's sandbox, so the Python 3.12 full-dep Docker test (`make test-docker`) was not run. CI (GitHub Actions) covers this. |
| Next slice | BD-03: Stats v2 (coverage breakdown) |
### scraper_1

| Metric | Value |
| --- | --- |
| Verified slices | 3 |
| Open TODO slices | 2 |
| Blocked slices | 0 |
| Latest journal heading | After Tasks 11–12 |
| Latest note | - The `ingest-fixture` CLI is the foundation for offline testing of the full parse→persist pipeline without DB access (via `--dry-run`), and will be critical for the Debugger golden-path check. |
| Next slice | S1-11: Live-safe ingestion runner (small) |
### scraper_sm

| Metric | Value |
| --- | --- |
| Verified slices | 0 |
| Open TODO slices | 3 |
| Blocked slices | 0 |
| Latest journal heading | After Task 0 |
| Latest note | - Noise detection is binary (has real-estate signal or not). A confidence score would be better for production. |
| Next slice | SM-01: Social ingestion contract (policy + fixtures) |
### ux_ui_designer

| Metric | Value |
| --- | --- |
| Verified slices | 0 |
| Open TODO slices | 2 |
| Blocked slices | 0 |
| Latest journal heading | Task 2 — Operator dashboard UI plan |
| Latest note | - A Storybook or component-viewer setup would accelerate shared component validation without needing the full Next.js dev server. Consider adding it in Phase B. |
| Next slice | UX-01: Operator dashboard UI plan |
### debugger

| Metric | Value |
| --- | --- |
| Verified slices | 1 |
| Open TODO slices | 3 |
| Blocked slices | 0 |
| Latest journal heading | 2026-04-08 (follow-up) — CI parity for Mypy |
| Latest note | - **Why**: Local `make typecheck` was green while CI only ran Ruff + tests; type regressions could merge unnoticed. |
| Next slice | DBG-02: Verify all DONE_AWAITING_VERIFY slices |

## 14. Source-By-Source Website Numbers

Columns: source number, website/source name, tier, access mode, legal mode, risk, count of listing types, count of languages, count of tracked URLs, count of fixture cases, implementation status.

| # | Source | Tier | Access | Legal | Risk | Types | Langs | URLs | Fixtures | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Address.bg | 1 | html | public_crawl_with_review | medium | 4 | 1 | 1 | 2 | fixture-backed |
| 2 | alo.bg | 1 | html | public_crawl_with_review | medium | 5 | 1 | 1 | 2 | fixture-backed |
| 3 | BulgarianProperties | 1 | html | public_crawl_with_review | medium | 4 | 2 | 2 | 2 | fixture-backed |
| 4 | Homes.bg | 1 | html | public_crawl_with_review | medium | 3 | 1 | 1 | 8 | fixture-backed |
| 5 | imot.bg | 1 | html | public_crawl_with_review | medium | 4 | 1 | 1 | 2 | fixture-backed |
| 6 | imoti.net | 1 | headless | legal_review_required | high | 4 | 2 | 1 | 2 | fixture-only legal-gated |
| 7 | LUXIMMO | 1 | html | public_crawl_with_review | medium | 4 | 2 | 1 | 2 | fixture-backed |
| 8 | OLX.bg | 1 | official_api | official_api_allowed | low | 4 | 1 | 2 | 3 | fixture-backed |
| 9 | property.bg | 1 | html | public_crawl_with_review | medium | 4 | 2 | 1 | 2 | fixture-backed |
| 10 | SUPRIMMO | 1 | html | public_crawl_with_review | medium | 4 | 2 | 1 | 2 | fixture-backed |
| 11 | ApartmentsBulgaria.com | 2 | headless | public_crawl_with_review | medium | 1 | 2 | 1 | 0 | registry-ready, connector pending |
| 12 | Bazar.bg | 2 | html | public_crawl_with_review | medium | 3 | 1 | 1 | 0 | registry-ready, connector pending |
| 13 | Domaza | 2 | html | public_crawl_with_review | medium | 5 | 2 | 1 | 0 | registry-ready, connector pending |
| 14 | Holding Group Real Estate | 2 | html | public_crawl_with_review | medium | 4 | 1 | 1 | 0 | registry-ready, connector pending |
| 15 | Home2U | 2 | html | public_crawl_with_review | medium | 4 | 3 | 1 | 0 | registry-ready, connector pending |
| 16 | Imoteka.bg | 2 | headless | legal_review_required | high | 4 | 2 | 1 | 0 | blocked pending legal review |
| 17 | Imoti.info | 2 | partner_feed | licensing_required | high | 4 | 2 | 1 | 0 | partner/vendor route |
| 18 | Indomio.bg | 2 | headless | public_crawl_with_review | medium | 3 | 2 | 1 | 0 | registry-ready, connector pending |
| 19 | Lions Group | 2 | html | public_crawl_with_review | medium | 4 | 2 | 1 | 0 | registry-ready, connector pending |
| 20 | Pochivka.bg | 2 | html | public_crawl_with_review | medium | 1 | 2 | 1 | 0 | registry-ready, connector pending |
| 21 | realestates.bg | 2 | html | public_crawl_with_review | medium | 3 | 2 | 1 | 0 | registry-ready, connector pending |
| 22 | Realistimo | 2 | headless | public_crawl_with_review | medium | 4 | 2 | 1 | 0 | registry-ready, connector pending |
| 23 | Rentica.bg | 2 | html | public_crawl_with_review | medium | 1 | 1 | 1 | 0 | registry-ready, connector pending |
| 24 | Svobodni-kvartiri.com | 2 | html | public_crawl_with_review | medium | 2 | 1 | 1 | 0 | registry-ready, connector pending |
| 25 | Unique Estates | 2 | html | public_crawl_with_review | medium | 3 | 2 | 1 | 0 | registry-ready, connector pending |
| 26 | Vila.bg | 2 | html | public_crawl_with_review | medium | 1 | 2 | 1 | 0 | registry-ready, connector pending |
| 27 | Yavlena | 2 | html | public_crawl_with_review | medium | 2 | 2 | 1 | 0 | registry-ready, connector pending |
| 28 | Airbnb | 3 | partner_feed | official_partner_or_vendor_only | prohibited_without_contract | 1 | 1 | 1 | 0 | partner/vendor route |
| 29 | Airbtics | 3 | licensed_data | official_partner_or_vendor_only | low | 1 | 1 | 1 | 0 | partner/vendor route |
| 30 | AirDNA | 3 | licensed_data | official_partner_or_vendor_only | low | 1 | 1 | 1 | 0 | partner/vendor route |
| 31 | BCPEA property auctions | 3 | html | public_crawl_with_review | medium | 1 | 1 | 1 | 0 | registry-ready, connector pending |
| 32 | Booking.com | 3 | partner_feed | official_partner_or_vendor_only | prohibited_without_contract | 1 | 1 | 1 | 0 | partner/vendor route |
| 33 | Flat Manager | 3 | partner_feed | official_partner_or_vendor_only | medium | 2 | 2 | 2 | 0 | partner/vendor route |
| 34 | KAIS Cadastre | 3 | manual_consent_only | consent_or_manual_only | high | 2 | 1 | 1 | 0 | manual or consent-only |
| 35 | Menada Bulgaria | 3 | partner_feed | official_partner_or_vendor_only | medium | 2 | 3 | 1 | 0 | partner/vendor route |
| 36 | Property Register | 3 | manual_consent_only | consent_or_manual_only | high | 1 | 2 | 1 | 0 | manual or consent-only |
| 37 | Vrbo | 3 | partner_feed | official_partner_or_vendor_only | high | 1 | 1 | 1 | 0 | partner/vendor route |
| 38 | Facebook public groups/pages | 4 | manual_consent_only | consent_or_manual_only | high | 2 | 1 | 1 | 0 | manual or consent-only |
| 39 | Instagram public profiles | 4 | manual_consent_only | consent_or_manual_only | high | 2 | 2 | 8 | 0 | manual or consent-only |
| 40 | Telegram public channels | 4 | official_api | official_api_allowed | medium | 3 | 3 | 6 | 0 | policy-approved, connector pending |
| 41 | Threads public profiles | 4 | manual_consent_only | consent_or_manual_only | high | 3 | 2 | 1 | 0 | manual or consent-only |
| 42 | Viber opt-in communities | 4 | manual_consent_only | consent_or_manual_only | high | 3 | 1 | 4 | 0 | manual or consent-only |
| 43 | WhatsApp opt-in groups | 4 | manual_consent_only | official_partner_or_vendor_only | prohibited_without_contract | 3 | 1 | 1 | 0 | partner/vendor route |
| 44 | X public search/accounts | 4 | official_api | official_api_allowed | low | 3 | 2 | 1 | 0 | policy-approved, connector pending |

## 15. Key Risks And Gaps

1. Live database and live scraping telemetry are still missing in this local shell, so the numbers above are coverage numbers, not production crawl-output numbers.
2. The local runtime is misaligned with repo targets: `python3 --version` returned Python 3.9.6, while the repo targets Python 3.12, so full backend/runtime confidence still depends on a Python 3.12 environment.
3. The 3D map, CRM, and public listing experience are scaffolded but not yet fully backed by live APIs and data.
4. Reverse publishing remains intentionally gated by compliance requirements, which is correct but means outbound integrations are still ahead of us.

## 16. Bottom Line

The product already has the shape of a serious Bulgaria real estate platform: source registry, compliance control plane, fixture-backed scrapers, a canonical Bulgaria database design, 3D map intent, chat/CRM intent, and operator workflows. The next value jump is not more new UI, but completing the live persistence and runtime path so the existing shells can run on real Bulgarian listing data.
