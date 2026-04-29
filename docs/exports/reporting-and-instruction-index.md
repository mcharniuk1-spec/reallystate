# Reporting And Instruction Index

Updated: 2026-04-28

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
| `docs/exports/scrape-status-dashboard.json` | Source status and dashboard data used by `/dashboard/scraper-status.html`. |
| `docs/exports/tier12-pattern-status.md` | Tier-1/2 source pattern status and live-count notes. |
| `docs/exports/tier12-four-bucket-pattern-handoff-2026-04-28.md` | Operator handoff for the four screen buckets. |
| `data/scrape_patterns/regions/varna/sections.json` | Reusable four-bucket source/section/list/detail/media patterns. |
| `docs/exports/taskforgema.md` | Next Gemma4/OpenClaw scrape and image-description task. |
| `docs/exports/property-quality-and-building-contract.md` | Property QA contract used by Codex, debugger, and Gemma4. |

## Active Four-Bucket Sources

These sources are the current Gemma4/OpenClaw focus across buy residential, buy commercial, rent residential, and rent commercial:

1. `Address.bg`
2. `BulgarianProperties`
3. `Homes.bg`
4. `imot.bg`
5. `LUXIMMO`
6. `property.bg`
7. `SUPRIMMO`

## Reporting Rules

1. DOCX files must be regenerated from repo artifacts before handoff or push.
2. Do not claim a property is visually complete unless local image files exist and photo counts match the listing JSON.
3. Each property report must include source links, scraped description, image descriptions, price, size, category, address/city, and quality flags.
4. Dashboard JSON/HTML and markdown reports must be refreshed with `make dashboard-doc` after scrape or pattern changes.
5. Live scraping remains operator-approved and constrained by `data/source_registry.json`.
