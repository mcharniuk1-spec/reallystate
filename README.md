# Bulgaria Real Estate Ingestion Platform

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

```bash
docs/development-setup.md
```

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
