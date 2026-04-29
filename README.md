# reallystate (Bulgaria Real Estate Ingestion Platform)

This workspace now contains a first working implementation of the source-first ingestion and reverse-publishing plan.

It includes:

- a seeded source registry based on `deep-research-report.md`
- canonical domain models for listings, contacts, buildings, publishing, and compliance
- a standard ingestion flow for apartment/building pages
- a dedupe scorer and basic building matcher
- a publication control plane with eligibility checks and payload mapping
- SQL schema definitions for the core entities
- tests and generated source/legal matrix artifacts

## Layout

- `AGENTS.md`: cross-agent implementation rules for Cursor, Codex, and Claude
- `PLAN.md`: detailed numbered MVP roadmap and technical build plan
- `platform-mvp-plan.md`: portable entrypoint for the current MVP plan
- `.cursor/`: Cursor rules, MCP config, Background Agent config, and Bugbot review guidance
- `agent-skills/`: reusable project skill files for focused agent execution
- `docs/`: agent automation notes, diagram source, and exported plan artifacts
- `docs/project-status-roadmap.md`: current stage, what works, what is missing, and 30+ point execution checklist
- `docs/linear-integration.md`: Linear workflow, issue structure, branch/PR conventions, and import guidance
- `docs/project-architecture-execution-guide.md`: full architecture, setup, continuous scraping model, and stage explanation
- `docs/skills-used.md`: repo-local skills, agent guidance files, and session-level skills used
- `docs/exports/linear-import-roadmap.csv`: import-ready CSV for creating the initial Linear backlog
- `docs/exports/project-architecture-execution-guide.pdf`: PDF handoff document for architecture and execution
- `data/source_registry.json`: seeded registry of sources and routing strategy
- `sql/schema.sql`: relational schema for ingestion and publishing
- `src/bgrealestate/`: Python package
- `tests/`: unit tests
- `artifacts/`: generated matrices

## Commands

Start local infrastructure:

```bash
make dev-up
```

See the detailed setup guide:

- [`docs/development-setup.md`](docs/development-setup.md) — Python, tests, env
- [`docs/docker-and-database.md`](docs/docker-and-database.md) — Docker Compose, Postgres/MinIO/Temporal, migrations, media on disk vs S3, SQL helpers

Run the standard test target:

```bash
make test
```

List sources:

```bash
PYTHONPATH=src python3 -m bgrealestate list-sources
```

Export parser and legal matrices:

```bash
PYTHONPATH=src python3 -m bgrealestate export-matrices --out-dir artifacts
```

Or through Make:

```bash
make export-matrices
make export-docs
```

Generate the source-link workbook and detailed debug report:

```bash
make source-report
```

Generate the project status roadmap DOCX/Markdown export:

```bash
make status-report
```

Generate the Linear backlog CSV export:

```bash
make linear-export
```

Generate the architecture guide markdown and PDF:

```bash
make architecture-doc
```

Generate/update the progress dashboard artifacts:

```bash
make dashboard-doc
```

## Local public view (LAN / demo phone)

1. Start Postgres stack if the UI will hit the API with a real DB: `make dev-up` + `export DATABASE_URL=...` + `make db-init`.
2. Bind FastAPI on all interfaces: `make run-api-public` (sets `API_HOST=0.0.0.0`). Keep `API_BASE_URL` as `http://127.0.0.1:8000` on the **same machine** so Next server-side `fetch` still works; add your LAN origin to `CORS_ALLOW_ORIGINS` if the browser calls the API **directly**.
3. Bind Next on all interfaces: `make run-frontend-public` (runs `npm run dev:public`).
4. Open from another device: `http://<your-lan-ip>:3000`.

**Action1 Telegram matrix helper**: `make action1-matrix-snapshot` — prints the seven-source × four-bucket counts from `data/scraped/*/listings/*.json`.

**Orchestration detective brief**: `docs/exports/detective-product-orchestration-2026-04-30.md`.

List reusable project skills:

```bash
make list-skills
```

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## What Is Implemented

The current codebase is designed to be the execution backbone for the roadmap:

- `SourceRegistry` is the control plane for source priority, legal mode, cadence, and extraction strategy.
- `StandardIngestionPipeline` implements the normalized apartment/building page flow.
- `PublishEligibilityEngine` blocks unsupported publishing paths and supports official/authorized onboarding models.
- `ChannelPayloadMapper` prepares outbound payloads for Booking, Airbnb, Bulgarian portals, and agency syndication.
- Cursor/Codex/Claude agent automation files define safe phase-by-phase implementation rules.
- The SQL blueprint now includes source, crawl, property, media, geospatial, user, CRM, and publishing tables.
- The source-link workbook and detailed debug report are generated under `docs/exports/`.

## What Comes Next

- Add per-source crawler connectors for tier-1 sources.
- Add persistent storage and queue workers.
- Add HTML/XHR fixtures from real source pages.
- Add geocoding and cadastral connectors.
- Add partner-specific publishing adapters.
- Connect a live Linear workspace and import the prepared backlog CSV.

---

One-line summary: Real estate market ingestion + dedupe + operator tooling for rent and purchase, with a compliance-first publishing control plane.
