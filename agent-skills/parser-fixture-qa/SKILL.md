---
name: parser-fixture-qa
description: Use when creating offline HTML or JSON fixtures, expected parser outputs, and regression tests for scraper connectors.
---

# parser-fixture-qa

Use this skill when creating parser fixtures and regression tests.

## Read First
- `tests/`
- `data/source_registry.json`
- `src/bgrealestate/pipeline.py`

## Workflow
1. Save representative HTML/JSON fixture inputs under `tests/fixtures/<source>/`.
2. Include list page, detail page, expired/removed page, encoding-sensitive page, and blocked/empty page cases where available.
3. Store expected normalized fields next to the fixture.
4. Assert stable external ID, title, price, area, city, contact, image URLs, and parser version.
5. Keep tests offline-only.

## Acceptance
- At least 20 tier-1 fixtures per active source before production cadence.
- Parser success is measurable and above the active gate.
