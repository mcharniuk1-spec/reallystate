---
name: scraper-connector-builder
description: Use when implementing one real estate source connector with source registry enforcement, raw capture hooks, typed parser output, and offline fixture tests.
---

# scraper-connector-builder

Use this skill when implementing one source connector.

## Read First
- `AGENTS.md`
- `data/source_registry.json`
- `src/bgrealestate/pipeline.py`
- `src/bgrealestate/source_registry.py`
- `tests/test_pipeline.py`

## Workflow
1. Implement one source at a time.
2. Start with `Homes.bg` unless OLX API credentials are configured.
3. Add a source legal/access gate before discovery or fetch work.
4. Store raw capture metadata before parse/normalize logic.
5. Return typed parsed and canonical output.
6. Add fixture-backed parser tests with no live network calls.

## Acceptance
- Fixture tests pass.
- Raw capture and canonical listing output are reproducible.
- No unsafe high-risk source bypass is introduced.
