# Reporting And Instruction Index

Updated: 2026-05-13

## Repo-Owned DOCX Pack

| File | Owner | Use |
|---|---|---|
| `docs/exports/bulgaria-real-estate-source-report.docx` | lead / scraper_1 | Source registry, four-bucket pattern status, source item counts, photo counts, and Gemma4 handoff rules. |
| `docs/exports/project-architecture-execution-guide.docx` | lead / architecture | Product, backend, frontend, scraper, compliance, and agent execution model. |
| `docs/exports/project-status-roadmap.docx` | lead / debugger | Current stage, completed gates, open risks, and next execution order. |

## Current Scrape Reporting Sources

| Artifact | Purpose |
|---|---|
| `docs/exports/source-item-photo-coverage.json` | Per-source and per-item photo, field, and gallery counts. |
| `docs/exports/s1-21-tier12-quality-audit-2026-04-29.md` | S1-21 seven-source quality audit summary with Action0/Action1/Action2 sequence and same-location grouping contract. |
| `docs/exports/s1-21-tier12-quality-audit-2026-04-29.json` | Machine-readable S1-21 source/item gaps, same-location groups, and Action0 eligible rows. |
| `docs/exports/s1-21-gemma-action0-eligible.json` | Authoritative Action0 input list for Gemma4/OpenClaw property image reports from complete local-gallery rows. |
| `docs/exports/scrape-status-dashboard.json` | Source status and dashboard data used by `/dashboard/scraper-status.html`. |
| `docs/exports/tier12-pattern-status.md` | Tier-1/2 source pattern status and live-count notes. |
| `docs/exports/tier12-four-bucket-pattern-handoff-2026-04-28.md` | Operator handoff for the four screen buckets. |
| `data/scrape_patterns/regions/varna/sections.json` | Reusable four-bucket source/section/list/detail/media patterns. |
| `docs/exports/taskforgema.md` | Next Gemma4/OpenClaw scrape and image-description task. |
| `docs/exports/property-quality-and-building-contract.md` | Property QA contract used by Codex, debugger, and Gemma4. |

## Current Product/Data Reporting Sources

| Artifact | Purpose |
|---|---|
| `docs/agents/SELF_DEVELOPMENT_ARCHITECTURE.md` | Current self-development agent architecture, review loop, and Plan B cadence. |
| `docs/agents/AGENT_LOOP_AND_CADENCE.md` | Constant vs triggered agent cadence and review ring. |
| `docs/operator/agent-team-operating-manual.md` | Human-readable operating manual for activating agents and reading outputs. |
| `docs/runbooks/server-db-migration.md` | Server and PostgreSQL/PostGIS migration runbook for the next execution step. |
| `docs/integrations/mcp-and-skills-setup.md` | Safe MCP setup and role-to-skill mapping. |
| `docs/exports/strategic-code-manager-review-2026-04-29.md` | Strategic review covering BD-17, UX-14, SM-08, account/chat contracts, and next verification tasks. |
| `docs/agents/scraper_sm/messenger-publication-entity-plan-2026-04-29.md` | Fixture-first plan for public Telegram and manual/consent-gated WhatsApp/Viber publication candidates. |
| `migrations/versions/20260429_0004_user_property_state_chat.py` | Database migration for liked-property status history and user-property chat joins. |
| `components/account/AccountCabinet.tsx` | `/settings` account cabinet surface for mode, liked properties, saved searches, and chat entry points. |
| `components/chat/ChatWorkspace.tsx` | `/chat` workspace for global and selected-property chat through the backend proxy. |

## Active Four-Bucket Sources

These sources are the current Gemma4/OpenClaw focus across buy residential, buy commercial, rent residential, and rent commercial:

1. `Address.bg`
2. `BulgarianProperties`
3. `Homes.bg`
4. `imot.bg`
5. `LUXIMMO`
6. `property.bg`
7. `SUPRIMMO`

## Active Gemma/OpenClaw Tasks

| Task | Action | Purpose | Primary input | Primary output |
|---|---|---|---|---|
| `S1-22A` | Action0 | Local-gallery image reports and property QA | `docs/exports/s1-21-gemma-action0-eligible.json` | `docs/exports/property-image-reports/` |
| `S1-22B` | Action1 | Seven-source all-Bulgaria scrape/backfill across four buckets | `docs/exports/taskforgema.md` + source patterns | refreshed `data/scraped/`, `data/media/`, dashboards |
| `S1-22C` | Action2 | Remaining legal tier-1/2 expansion after QA | `data/source_registry.json` | refreshed source metrics, patterns, dashboards |

## Reporting Rules

1. DOCX files must be regenerated from repo artifacts before handoff or push.
2. Do not claim a property is visually complete unless local image files exist and photo counts match the listing JSON.
3. Gemma4/OpenClaw must run Action1 first after operator `Action1 ACCEPT`; Action0 runs only after operator `Action0 now`, and Action2 only after operator `Action2 now` plus Action1 QA.
4. Each property report must include source links, scraped description, one ordered description per image, one whole-property visual summary, price, size, category, address/city, same-location status, and quality flags.
5. Same-location aggregation is based on useful address text plus city/district; city-only or district-only placeholders must not create aggregate groups.
6. Dashboard JSON/HTML and markdown reports must be refreshed with `make dashboard-doc` after scrape or pattern changes.
7. Live scraping remains operator-approved and constrained by `data/source_registry.json`.
8. User-property state changes must be saved as status events; do not delete liked-property rows to represent unlike.
9. Messenger/social publication candidates must remain source publications first and must not use private WhatsApp, Viber, Telegram, or Facebook access without explicit authorization and consent.
