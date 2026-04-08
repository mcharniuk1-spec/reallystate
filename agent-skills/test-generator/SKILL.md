---
name: test-generator
description: Generate fixture-first test cases for connectors, APIs, and pipelines with no live network dependency. Use when adding tests for new sources, endpoints, or data flows.
---

# Test Generator

## Use When

- Adding a new connector or parser.
- Testing API endpoints without a live database.
- Creating fixture regression suites.

## Fixture-First Pattern

1. Create `tests/fixtures/<source>/<case>/raw.html` (or `raw.json`).
2. Create `tests/fixtures/<source>/<case>/expected.json` with canonical output.
3. Write test class that loads fixture, runs parser, asserts against expected.
4. No `httpx`, `requests`, or network calls in test code.

## Test Categories

- **Unit**: single parser function, single fixture.
- **Integration**: pipeline end-to-end with mocked DB.
- **Smoke**: `make test` must pass in <30s without external services.
- **Golden path**: `make golden-path` with DB service container.

## Quality Rules

- Every source needs at least: `basic_listing`, `blocked_page` fixtures.
- Discovery pagination needs: `discovery_page`, `discovery_empty`, `discovery_last_page`.
- Expected JSON must match the canonical listing schema fields.
- Tests must not import live HTTP clients at module level.
