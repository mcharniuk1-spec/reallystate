# Bulgaria Real Estate Platform MVP: Cursor-Agent Technical Build Plan

## 1. Summary
Build a full Bulgaria real estate MVP that ingests all documented market sources, normalizes and deduplicates listings, stores photos and descriptions, shows listings in a scrolling feed and 3D map, manages leads in a CRM chat inbox, supports settings/personal info, and later publishes back to authorized channels.

The current repo is a foundation only: it has `README.md`, `data/source_registry.json`, `sql/schema.sql`, `src/bgrealestate/*`, artifacts, and unit tests, but it does not yet have persistent PostgreSQL/PostGIS runtime, real tier-1 connectors, fixtures, Temporal workers, frontend pages, CRM database, or real publishing adapters. The next agent must extend the scaffold, not replace it.

## 2. Tooling
Use Cursor as the main IDE/agent, with portable repo rules so Codex and Claude can also work safely.

| Category | Use | Link |
|---|---|---|
| Cursor Project Rules | Primary Cursor guidance in `.cursor/rules/*.mdc`; preferred over legacy `.cursorrules` | [Cursor Rules](https://docs.cursor.com/en/context/rules) |
| Cursor `AGENTS.md` | Cross-agent fallback instructions in Markdown | [Cursor Rules / AGENTS.md](https://docs.cursor.com/context/rules-for-ai) |
| Cursor MCP | Connect project tools through `.cursor/mcp.json`; CLI and editor share MCP config | [Cursor MCP](https://docs.cursor.com/en/context/mcp) |
| Cursor CLI | Terminal agent runs with `cursor-agent` | [Cursor CLI](https://cursor.com/en-US/cli) |
| Cursor Background Agents | Remote async work with `.cursor/environment.json` | [Cursor Background Agents](https://docs.cursor.com/en/background-agents) |
| Cursor Bugbot | PR review rules in `.cursor/BUGBOT.md` | [Cursor Bugbot](https://docs.cursor.com/en/bugbot) |
| Codex CLI | Focused terminal patches, review, test loops | [openai/codex](https://github.com/openai/codex) |
| Claude Code | Long-context planning and refactors | [anthropics/claude-code](https://github.com/anthropics/claude-code) |
| Aider | Optional git-aware patching | [Aider](https://github.com/Aider-AI/aider) |
| Continue | Optional open-source coding assistant | [Continue](https://github.com/continuedev/continue) |
| Cline | Optional approval-first autonomous coding extension | [Cline](https://github.com/cline/cline) |
| Roo Code | Optional multi-mode coding agent | [Roo Code](https://github.com/RooCodeInc/Roo-Code) |
| OpenHands | Optional isolated autonomous dev environment | [OpenHands](https://github.com/All-Hands-AI/OpenHands) |

Project skills to create as repo files: `real-estate-source-registry`, `scraper-connector-builder`, `parser-fixture-qa`, `postgres-postgis-schema`, `workflow-runtime`, `dedupe-entity-resolution`, `geo-map-3d`, `crm-chat-inbox`, `publishing-compliance`, `frontend-pages`, `docs-export`, `qa-review-release`.

Store skills in `agent-skills/<name>/SKILL.md`; mirror to `.claude/skills/<name>/SKILL.md` if using Claude; use `.cursor/rules/<name>.mdc` as Cursor’s reliable version-controlled instruction format.

Recommended extensions: [Python](https://github.com/microsoft/vscode-python), [Ruff VS Code](https://github.com/astral-sh/ruff-vscode), [Ruff CLI](https://github.com/astral-sh/ruff), [ESLint](https://github.com/microsoft/vscode-eslint), [Prettier](https://github.com/prettier/prettier-vscode), [YAML](https://github.com/redhat-developer/vscode-yaml), [Docker](https://github.com/microsoft/vscode-docker), [SQLTools](https://github.com/mtxr/vscode-sqltools), [PostgreSQL](https://github.com/microsoft/vscode-pgsql), [Playwright](https://github.com/microsoft/playwright-vscode), [GitHub PRs](https://github.com/microsoft/vscode-pull-request-github), [GitLens](https://github.com/gitkraken/vscode-gitlens), [Code Spell Checker](https://github.com/streetsidesoftware/vscode-spell-checker).

Recommended MCP servers: [Context7](https://github.com/upstash/context7) for current library docs, [Playwright MCP](https://github.com/microsoft/playwright-mcp) for browser/source inspection, [MCP reference servers](https://github.com/modelcontextprotocol/servers) for filesystem/git/fetch/time helpers, and read-only PostgreSQL MCP for schema inspection only.

## 3. Stack
Backend: Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, asyncpg or psycopg3, Temporal Python SDK, Redis, structlog, OpenTelemetry, Sentry.

Storage: PostgreSQL 17+/18 with PostGIS 3.5+, `pg_trgm`, JSONB + GIN indexes, GiST spatial indexes, full-text `tsvector`, optional `pgvector` later, S3 or MinIO for raw captures and media.

Scraping: httpx for HTTP/API, Playwright for JS/headless sources, selectolax or lxml for parsing, BeautifulSoup fallback, extruct/custom JSON-LD extraction, tenacity, phonenumbers, price-parser, dateparser, rapidfuzz, Pillow, imagehash.

Frontend: Next.js App Router, TypeScript, TanStack Query, MapLibre GL JS, deck.gl, Tailwind or one chosen component system, WebSockets or SSE for CRM updates.

Docs/devops: Docker Compose, Makefile, pytest, ruff, mypy or pyright, Mermaid, Mermaid CLI, Pandoc, LibreOffice headless, GitHub Actions or local CI.

## 4. Sources
Every source from the research docs must be in `source_registry` with `source_family`, `owner_group`, `tier`, `access_mode`, `risk_mode`, `freshness_target`, `publish_capable`, `dedupe_cluster_hint`, `legal_mode`, and `mvp_phase`.

| Tier | Sources | Rule |
|---|---|---|
| 1 | `OLX.bg`, `Homes.bg`, `alo.bg`, `imot.bg`, `BulgarianProperties`, `Address.bg`, `SUPRIMMO`, `LUXIMMO`, `property.bg`, `imoti.net` | Build first; API/HTML first; headless only where necessary |
| 2 | `Bazar.bg`, `Imoti.info`, `realestates.bg`, `Domaza`, `Indomio.bg`, `Realistimo`, `Home2U`, `Yavlena`, `Holding Group Real Estate`, `Rentica.bg`, `Svobodni-kvartiri.com`, `Pochivka.bg`, `Vila.bg`, `ApartmentsBulgaria.com`, `Unique Estates`, `Lions Group`, `Imoteka.bg` | Add after tier-1 fixtures and parser gates |
| 3 | `Airbnb`, `Booking.com`, `Vrbo`, `Flat Manager`, `Menada Bulgaria`, `AirDNA`, `Airbtics`, `Property Register`, `KAIS Cadastre`, `BCPEA property auctions` | Partner/API/vendor/official-service only where required |
| 4 | Telegram public channels/groups, X public accounts/search, Facebook public pages/groups where accessible, Instagram public business/profile sources, Threads public profiles if workable, Viber opt-in communities, WhatsApp Business/opt-in groups | Lead-intelligence overlays only; consent-gated where private |

Default cadence: start hourly, then promote only proven high-yield tier-1 sources to 10-minute runs after parser success, block rate, and cost metrics are stable.

Airbnb, Booking, WhatsApp, Viber private groups, and KYC/account workflows must not depend on unauthorized scraping or automatic mass account creation. Use official partner routes, authorized account linking, vendor data, or assisted manual onboarding.

## 5. Architecture
```mermaid
flowchart LR
    A["Market Sources: portals, agencies, OTAs, social, registers"] --> B["Source Registry + Legal Gates"]
    B --> C["Connectors: API, HTML, Headless, Partner, Vendor, Consent"]
    C --> D["Temporal Workflows + Redis Rate Limits"]
    D --> E["Raw Capture Store: S3/MinIO"]
    E --> F["Parser + Normalizer"]
    F --> G["PostgreSQL/PostGIS Canonical Store"]
    G --> H["Dedupe + Property Graph"]
    H --> I["Geo + Building Matching"]
    H --> J["Search/Listings API"]
    I --> K["3D Map API"]
    H --> L["CRM Chat/Lead API"]
    H --> M["Publishing Control Plane"]
    J --> N["/listings + /properties"]
    K --> O["/map"]
    L --> P["/chat"]
    M --> Q["/admin Publishing Queue"]
    G --> R["/settings + User/Team Admin"]
```

## 6. Database
Use PostgreSQL/PostGIS as the source of truth. Store binaries in S3/MinIO, not in Postgres. Use monthly partitions for `raw_capture`, `source_listing_snapshot`, `listing_event`, `lead_message`, and `webhook_event`.

| Area | Tables | Required Purpose |
|---|---|---|
| Sources | `source_registry`, `source_endpoint`, `source_legal_rule` | Source definitions, endpoint templates, legal/compliance gates |
| Crawl | `crawl_job`, `crawl_cursor`, `crawl_attempt`, `raw_capture`, `parser_fixture` | Durable crawl state, retries, saved payloads, fixture tests |
| Listings | `source_listing`, `source_listing_snapshot`, `canonical_listing` | Native listing ID, versioned parsed state, normalized current listing |
| Properties | `property_entity`, `property_offer`, `property_attribute`, `property_description`, `price_history`, `listing_event` | Deduped property graph, sale/rent/STR offers, facts, text, lifecycle |
| Media | `media_asset`, `property_media`, `raw_file`, `media_processing_job` | Photos, object keys, hashes, thumbnails, screenshots, PDFs |
| Contacts | `organization`, `person_contact`, `contact_method`, `property_contact_link` | Agencies, brokers, owners, developers, phones, emails, messenger handles |
| Geo | `address`, `building_entity`, `building_match`, `city_area`, `map_tile_cache` | Geocoding, building footprints, confidence scores, city/resort polygons |
| Users | `app_user`, `organization_account`, `team_membership`, `permission_grant`, `service_account`, `api_key`, `audit_log` | Login profile, teams, roles, automation keys, immutable audit |
| CRM | `conversation_channel_account`, `lead_contact`, `lead_thread`, `lead_thread_property_link`, `lead_message`, `message_attachment`, `thread_assignment_event`, `task_reminder`, `saved_reply_template`, `webhook_event` | Full chat folder/CRM inbox with assignments and follow-ups |
| Publishing | `distribution_profile`, `channel_capability`, `channel_mapping`, `publish_job`, `publish_attempt`, `onboarding_session`, `compliance_flag` | Publish eligibility, dry-run, external IDs, sync state, onboarding |

Canonical listing minimum fields: source, external ID, source URL, sale/rent/STR/auction intent, property type, city/district/resort/region, raw address, lat/lon, geocode confidence, building/project name, area, rooms, floor, floors total, construction type/year/stage, Act 16, amenities, price/currency/fees/price per sqm, agency/broker/owner/developer, phones, messenger handles, title, summary, full description, image URLs, image hashes, first seen, last seen, last changed, removed at, parser version, raw capture reference, compliance flags.

Indexes: GiST on geometry, GIN on JSONB, GIN on `tsvector`, trigram on normalized names/addresses/contact values, B-tree on source/status/timestamps/channel/assignee IDs.

## 7. Backend
Workflows must be Temporal-based and idempotent: `SourceDiscoveryWorkflow`, `ListingDetailWorkflow`, `ListingEnrichmentWorkflow`, `MediaProcessingWorkflow`, `SocialLeadIngestionWorkflow`, `ConversationSyncWorkflow`, `PublishWorkflow`, `DocExportWorkflow`.

APIs to expose: `/sources`, `/crawl-jobs`, `/parser-failures`, `/listings`, `/listings/{id}`, `/properties/{id}`, `/properties/{id}/history`, `/properties/{id}/media`, `/map/viewport`, `/map/buildings/{id}`, `/map/tiles/{z}/{x}/{y}.mvt`, `/crm/threads`, `/crm/threads/{id}/messages`, `/crm/templates`, `/me`, `/settings/team`, `/settings/api-keys`, `/settings/channel-accounts`, `/publishing/capabilities`, `/publishing/profiles`, `/publishing/jobs`, `/publishing/channel-mappings`.

Make commands to create: `make install`, `make db-init`, `make migrate`, `make test`, `make lint`, `make typecheck`, `make run-api`, `make run-worker`, `make run-scheduler`, `make run-frontend`, `make export-docs`, `make connector-fixtures SOURCE=homes_bg`.

## 8. Frontend
App routes must be built in this order: `/listings`, `/properties/[id]`, `/map`, `/chat`, `/settings`, `/admin`.

| Route | Components | Acceptance |
|---|---|---|
| `/listings` | `ListingsPageShell`, `ListingsFilterSidebar`, `ListingsSortBar`, `InfiniteListingFeed`, `ListingCard`, `ListingCardGallery`, `SourceBadge`, `FreshnessBadge`, `DedupeGroupBadge` | Infinite scroll, filters, sorting, photo preview, source links, create-lead action |
| `/properties/[id]` | `PropertyHeader`, `PhotoGallery`, `PriceBox`, `PropertyFactsGrid`, `DescriptionTabs`, `SourceLinksPanel`, `ContactPanel`, `MapMiniPanel`, `PriceHistoryChart`, `LeadActionPanel` | One deduped property view across all sources with provenance |
| `/map` | `MapShell`, `MapToolbar`, `MapSearchBox`, `MapFilterPanel`, `MapLibreCanvas`, `DeckBuildingLayer`, `ListingClusterLayer`, `PropertyPinLayer`, `BuildingSummaryDrawer`, `ListingPreviewCard` | 2D/3D toggle, viewport loading, building summaries, clusters, fallback where geometry is weak |
| `/chat` | `ChatInboxLayout`, `ThreadList`, `ThreadFilters`, `ConversationPane`, `MessageComposer`, `LeadProfilePanel`, `LinkedPropertiesPanel`, `TaskReminderPanel`, `SavedReplyPicker`, `AssignmentMenu`, `AuditTimeline` | Threads, messages, assignment, reminders, templates, manual notes, property/contact links |
| `/settings` | `ProfileSettings`, `NotificationSettings`, `TeamSettings`, `ApiKeySettings`, `ConnectedChannelsSettings`, `CrawlerSettings`, `PublishingSettings`, `SecurityAuditLog` | User profile, team roles, API keys, channel accounts, crawler/publishing state |
| `/admin` | `SourceHealthDashboard`, `CrawlerJobTable`, `ParserFailureQueue`, `DuplicateReviewQueue`, `GeocodeReviewQueue`, `ComplianceReviewQueue`, `PublishQueue`, `SyncStatusTable` | Operators can review source health, parser failures, dedupe, building matches, compliance, publishing |

## 9. Roadmap
1. Documentation and agent foundation. Inputs: PDFs, `deep-research-report.md`, current scaffold. Tools: Cursor, Codex, Claude, Context7. Skills: `docs-export`, `real-estate-source-registry`, `qa-review-release`. Outputs: `platform-mvp-plan.md`, DOCX/PDF, Mermaid diagram, `.cursor/rules`, `AGENTS.md`. Gate: docs preview cleanly and all sources are listed.

2. Database and migrations. Inputs: proposed schema and current `sql/schema.sql`. Tools: Cursor, Codex, PostgreSQL inspection, Docker. Skills: `postgres-postgis-schema`. Outputs: Alembic migrations, SQLAlchemy models, repository layer, Docker Compose for Postgres/PostGIS/Redis/MinIO/Temporal. Gate: `make db-init`, `make migrate`, `make test`.

3. Workflow runtime. Inputs: repositories, source registry, Temporal config. Tools: Cursor, Codex, Context7. Skills: `workflow-runtime`, `qa-review-release`. Outputs: workflows, workers, scheduler, retries, idempotency, rate-limit state. Gate: jobs survive worker restart and cursors persist.

4. First connector. Inputs: `Homes.bg` fixtures and legal rule. Tools: Cursor, Playwright MCP, Codex. Skills: `scraper-connector-builder`, `parser-fixture-qa`. Outputs: connector interface, discovery parser, detail parser, raw capture persistence, canonical output tests. Gate: no live network calls in tests.

5. Tier-1 connector batch. Inputs: `OLX.bg`, `alo.bg`, `imot.bg`, `BulgarianProperties`, `Address.bg`, `SUPRIMMO`, `LUXIMMO`, `property.bg`, `imoti.net`. Tools: Cursor, Playwright MCP, Context7. Skills: `scraper-connector-builder`, `publishing-compliance`. Outputs: at least 3 tier-1 end-to-end connectors, one incremental cursor. Gate: parser success above 95% on fixtures.

6. Media pipeline. Inputs: parsed image URLs. Tools: Cursor, Codex. Skills: `parser-fixture-qa`, `dedupe-entity-resolution`. Outputs: S3/MinIO image storage, hashes, thumbnails, `media_asset`, `property_media`. Gate: duplicate images detected and DB stores only metadata.

7. Dedupe graph. Inputs: listings, contacts, photos, price, area, addresses. Tools: Cursor, Codex. Skills: `dedupe-entity-resolution`. Outputs: property graph, duplicate candidates, merge confidence, review status. Gate: precision target above 0.90 on labeled Bulgarian sample.

8. Geospatial layer. Inputs: coordinates, addresses, city polygons, OSM/EUBUCCO/cadastre where permitted. Tools: Cursor, Codex, PostGIS. Skills: `geo-map-3d`. Outputs: geocoder adapter, building matcher, confidence scores, priority city coverage. Gate: Sofia, Varna, Burgas, Sunny Beach/Nessebar, Bansko support building match or 2D fallback.

9. Search and map APIs. Inputs: property graph, offers, media, building matches. Tools: Cursor, Codex. Skills: `geo-map-3d`, `frontend-pages`. Outputs: listing search, filters, facets, viewport API, building summary API, optional MVT. Gate: search p95 under 300 ms and map p95 under 500 ms on seeded data.

10. Listings and detail UI. Inputs: listing APIs and media. Tools: Cursor, Codex, Playwright. Skills: `frontend-pages`. Outputs: `/listings` and `/properties/[id]`. Gate: infinite scroll, filters, source badges, photo gallery, create-lead action.

11. 3D map UI. Inputs: viewport/building APIs. Tools: Cursor, Playwright MCP, Context7. Skills: `geo-map-3d`, `frontend-pages`. Outputs: `/map` with MapLibre and deck.gl. Gate: 3D works where geometry exists; 2D fallback works elsewhere.

12. CRM backend and chat UI. Inputs: users, contacts, listings, channel accounts. Tools: Cursor, Codex. Skills: `crm-chat-inbox`. Outputs: CRM tables, APIs, `/chat`, manual channel mode, webhook event persistence. Gate: operator can create, assign, reply, follow up, and audit threads.

13. Settings and accounts. Inputs: auth/team/API key/channel state. Tools: Cursor, Codex. Skills: `frontend-pages`, `crm-chat-inbox`. Outputs: `/settings`, API keys, team roles, connected channels, notification settings. Gate: profile/team/channel state works with audit log.

14. Compliance gates. Inputs: source legal rules and channel capabilities. Tools: Cursor, Codex. Skills: `publishing-compliance`, `real-estate-source-registry`. Outputs: runtime blockers and review reasons. Gate: partner-only/consent-only sources cannot be used unsafely.

15. Reverse publishing. Inputs: approved distribution profiles. Tools: Cursor, Codex, Context7. Skills: `publishing-compliance`. Outputs: dry-run adapters, Booking/Airbnb official-route interfaces, Bulgarian portal capability matrix, channel mappings, reconciliation. Gate: no automatic mass account creation; external IDs sync back.

16. Admin UI. Inputs: source health, parser failures, dedupe, geo, compliance, publish jobs. Tools: Cursor, Codex, Playwright. Skills: `frontend-pages`, `qa-review-release`. Outputs: `/admin`. Gate: public launch blocked until operator queues work.

17. Final docs/export. Inputs: implemented state and acceptance results. Tools: Cursor, Codex, Claude, Mermaid, Pandoc, LibreOffice. Skills: `docs-export`. Outputs: `platform-mvp-plan.md`, `platform-mvp-plan.docx`, `platform-mvp-plan.pdf`, rendered block scheme. Gate: docs include source matrix, DB structure, app pages, agent automation setup, and numbered plan.

## 10. Testing
Use fixture tests for crawlers; never require live network for CI parser tests.

Required tests: migration tests, repository tests, connector fixture tests, parser encoding/blocked-page tests, media hash tests, dedupe scoring tests, geocode/building match tests, search/filter tests, map viewport tests, CRM thread/message/reminder tests, settings/API-key tests, compliance blocking tests, publishing dry-run/reconciliation tests, frontend Playwright tests for `/listings`, `/properties/[id]`, `/map`, `/chat`, `/settings`, `/admin`.

Stability targets: tier-1 fixture parser success above 95%, duplicate precision above 0.90, search p95 below 300 ms, map p95 below 500 ms, CRM inbox p95 below 300 ms, publish dry-run success above 98%, zero lost jobs after worker restart.

## 11. Agent Setup
This is the dedicated setup plan for Cursor/Codex/Claude agent automation.

1. Create `AGENTS.md` at repo root. It must say: extend existing scaffold, never replace wholesale, use PostgreSQL/PostGIS, use fixtures for crawler tests, enforce source legal rules, no unsafe social/private scraping, no automatic mass account creation, update progress after every phase.

2. Create `.cursor/rules/00-project.mdc`. Use `alwaysApply: true`. Include architecture defaults, phase gates, output template, and current repo paths.

3. Create scoped Cursor rules. Use `.cursor/rules/backend.mdc` for `src/bgrealestate/**`, `.cursor/rules/frontend.mdc` for `web/**`, `.cursor/rules/scrapers.mdc` for `src/bgrealestate/connectors/**`, `.cursor/rules/database.mdc` for `sql/**` and `migrations/**`, `.cursor/rules/docs.mdc` for docs/export work.

4. Create `.cursor/mcp.json`. Add Context7 for docs, Playwright MCP for browser inspection, GitHub if the repo is connected, and PostgreSQL MCP only as read-only. Do not commit secrets; use `${env:...}` interpolation.

5. Create `.cursor/environment.json` for Background Agents. Include install commands such as `make install`, startup support for Docker if needed, and terminals such as `make run-api`, `make run-worker`, and `make run-frontend` only after those commands exist and are stable.

6. Create `.cursor/BUGBOT.md`. Tell Bugbot to prioritize scraper legal gates, SQL injection, auth/RBAC, workflow idempotency, raw data privacy, accidental live-network tests, and frontend state bugs.

7. Create `agent-skills/<skill>/SKILL.md` for every skill listed in Section 2. Each skill should include when to use it, files to read first, commands to run, acceptance gate, and output format.

8. Use Cursor Background Agents only for bounded tasks. Good background tasks: one connector with fixtures, one frontend page, one migration slice, one review queue. Bad background tasks: “build the whole platform,” live scraping without review, account automation, or anything requiring secrets.

9. Use Cursor foreground Agent for sensitive tasks. Sensitive tasks: legal gate changes, source policy changes, publishing adapters, channel credentials, auth/API keys, and database migrations touching user/chat data.

10. Use Codex for focused patches and reviews. Good Codex prompts: “review this connector for unsafe live network tests,” “implement one migration,” “add fixture tests for Homes.bg parser,” “review publishing compliance blockers.”

11. Use Claude Code for long-context docs/refactors. Good Claude prompts: “synchronize `platform-mvp-plan.md` with the schema and source matrix,” “extract agent skills from the plan,” “review whether all sources from the research report are represented.”

12. Every agent step must end with this output:
```text
Changed files:
Agent tools used:
Skills used:
Extensions/libraries used:
Commands run:
Tests run:
Outputs produced:
Risks / blockers:
Progress update:
Next step:
```

## 12. Assumptions
PostgreSQL/PostGIS is the main operational database; S3/MinIO stores raw captures/photos/docs; Temporal is the durable automation layer; Cursor is the main builder; Codex and Claude are supporting agents; public UI starts only after ingestion, map data, CRM, compliance, and publishing controls are stable.

Booking.com and Airbnb stay in scope for market intelligence and reverse publishing, but only through official/authorized/vendor routes. WhatsApp, Viber, private Facebook groups, and private Telegram groups are opt-in/consent-only. Threads is experimental public-profile monitoring only unless official read/search support is confirmed during implementation.
