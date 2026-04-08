# Execution Reconciliation Report

Date: 2026-04-08
Workspace: `/Users/getapple/Documents/Real Estate Bulg`

## Purpose

This report reconciles the roadmap after a Cursor pass and a Codex pass, so the next implementation steps can continue from a trustworthy, verified state instead of from mixed assumptions.

## What Changed Since The Last Codex-Only Baseline

Cursor materially advanced three areas:

1. Stage 2 database foundation moved forward.
   - Added DB session helper:
     - [`src/bgrealestate/db/session.py`](/Users/getapple/Documents/Real%20Estate%20Bulg/src/bgrealestate/db/session.py)
   - Added repository foundation:
     - [`src/bgrealestate/db/repositories.py`](/Users/getapple/Documents/Real%20Estate%20Bulg/src/bgrealestate/db/repositories.py)
   - Expanded tests with an optional DB roundtrip smoke test:
     - [`tests/test_db_roundtrip_optional.py`](/Users/getapple/Documents/Real%20Estate%20Bulg/tests/test_db_roundtrip_optional.py)

2. Stage 4 received an early fixture-first parser slice for `Homes.bg`.
   - Added connector protocol/helpers:
     - [`src/bgrealestate/connectors/protocol.py`](/Users/getapple/Documents/Real%20Estate%20Bulg/src/bgrealestate/connectors/protocol.py)
     - [`src/bgrealestate/connectors/fixtures.py`](/Users/getapple/Documents/Real%20Estate%20Bulg/src/bgrealestate/connectors/fixtures.py)
   - Added `Homes.bg` connector shell and fixture parser:
     - [`src/bgrealestate/connectors/homes_bg.py`](/Users/getapple/Documents/Real%20Estate%20Bulg/src/bgrealestate/connectors/homes_bg.py)
   - Added ingestion helper wiring parser output into repositories:
     - [`src/bgrealestate/connectors/ingest.py`](/Users/getapple/Documents/Real%20Estate%20Bulg/src/bgrealestate/connectors/ingest.py)
   - Added offline fixtures:
     - [`tests/fixtures/homes_bg`](/Users/getapple/Documents/Real%20Estate%20Bulg/tests/fixtures/homes_bg)
   - Added parser tests:
     - [`tests/test_homes_bg_fixture_parsing.py`](/Users/getapple/Documents/Real%20Estate%20Bulg/tests/test_homes_bg_fixture_parsing.py)
     - [`tests/test_connector_fixtures_smoke.py`](/Users/getapple/Documents/Real%20Estate%20Bulg/tests/test_connector_fixtures_smoke.py)

3. Documentation/state tracking moved forward.
   - Added dependency/runtime drift analysis:
     - [`docs/reports/dependency-sdk-drift-2026-04-08.md`](/Users/getapple/Documents/Real%20Estate%20Bulg/docs/reports/dependency-sdk-drift-2026-04-08.md)
   - Updated roadmap claims to reflect the extra Stage 2 and Stage 4 groundwork:
     - [`docs/project-status-roadmap.md`](/Users/getapple/Documents/Real%20Estate%20Bulg/docs/project-status-roadmap.md)

## What Was Verified Today

The following claims are confirmed by actual runnable validation in the current workspace:

1. The current local validation command passes:
   - `make validate`
2. Current validation result:
   - 21 tests passed
   - 1 optional DB smoke test skipped because `DATABASE_URL` is unset
3. One-shot development worker and scheduler still start:
   - `bgrealestate.dev_worker --once`
   - `bgrealestate.dev_scheduler --once`
4. The `Homes.bg` fixture parser tests pass offline.
5. Office export packages remain ZIP-valid:
   - source links workbook
   - source report DOCX
   - project status roadmap DOCX

## What Is Real Progress Versus What Is Still Only Scaffold

### Real progress

1. The repo now has a usable fixture-first connector pattern.
2. The repo now has a minimal DB session abstraction and repository shell.
3. The roadmap now correctly acknowledges an early Stage 4 parser slice.
4. The optional DB smoke test is a good bridge toward real migration/runtime validation.

### Still scaffold / not yet operational

1. No real PostgreSQL/PostGIS runtime has been exercised in this shell.
2. No Alembic migration has actually been run against a live database here.
3. `run-api` is still a lightweight placeholder, not a real FastAPI app.
4. `run-worker` and `run-scheduler` are still placeholders, not Temporal workers.
5. `run-frontend` still serves a static HTML shell, not a Next.js app.
6. `Homes.bg` discovery is still empty and there is no validated live crawl path.
7. `Homes.bg` persistence exists as helper code, but not as a validated end-to-end DB-backed ingestion flow in this environment.

## Gaps And Inconsistencies Found

### 1. Source registry persistence is lossy

The JSON source registry includes planning and discovery fields such as:

- `primary_url`
- `related_urls`
- `languages`
- `listing_types`

But the DB schema and current repository upsert path do not persist those fields into `source_registry`.

Affected files:

- [`data/source_registry.json`](/Users/getapple/Documents/Real%20Estate%20Bulg/data/source_registry.json)
- [`sql/schema.sql`](/Users/getapple/Documents/Real%20Estate%20Bulg/sql/schema.sql)
- [`src/bgrealestate/db/models.py`](/Users/getapple/Documents/Real%20Estate%20Bulg/src/bgrealestate/db/models.py)
- [`src/bgrealestate/db/repositories.py`](/Users/getapple/Documents/Real%20Estate%20Bulg/src/bgrealestate/db/repositories.py)

Impact:

- If registry data is loaded into PostgreSQL today, useful planning/discovery metadata is dropped.
- This weakens the DB as a future control plane for connectors and operator tooling.

Required follow-up:

1. Decide whether these fields belong in `source_registry` or in `source_endpoint`.
2. Add them to schema/models/repositories consistently.
3. Add repository tests that prove the full registry entry round-trips.

### 2. Runtime contract is still drifted locally

Confirmed from the dependency drift report:

- project target: Python 3.12+
- current shell: Python 3.9.6
- Node tooling: not present in this shell
- SQLAlchemy/Alembic runtime packages: not installed in this shell

Impact:

- Today’s validation proves the scaffold, not the real runtime stack.
- Stage 2 cannot be considered complete until the migration/runtime path is exercised on Python 3.12 with installed dependencies.

### 3. Roadmap numbering expanded from 125 to 128 items

This happened because Cursor added:

- `38a`
- `38b`
- `38c`

That is fine, but it means any future status summaries should use the current checklist counts, not the earlier 125-item total.

Current roadmap count:

- 45 done
- 83 todo
- 128 total

## Current True Project Stage

The most accurate summary is:

1. Stage 0 is complete.
2. Stage 1 is complete.
3. Stage 2 is in progress.
4. There is a useful but partial Stage 4 `Homes.bg` fixture parser slice.
5. The next correct execution priority is still Stage 2, not broad connector expansion.

## Recommended Execution Order From Here

The next implementation should be executed in this order:

1. Finish Stage 2 completely.
   - Complete item 39: broaden SQLAlchemy coverage toward the full schema.
   - Complete item 40: broaden repository coverage beyond the current small subset.
   - Complete item 41: add tenant/account boundaries consistently.
   - Complete item 42: add repository tests, not just migration/fixture tests.
   - Complete item 43: add PostGIS geometry/index tests once a real DB is available.
   - Complete item 44: decide raw-body retention strategy.

2. Exercise the real DB path.
   - Run Alembic against PostgreSQL/PostGIS with a real `DATABASE_URL`.
   - Run the optional DB smoke test against that environment.
   - Add one repository roundtrip test that proves persisted `source_listing`, `snapshot`, and `canonical_listing` rows can be retrieved.

3. Close the `Homes.bg` gap before adding other sources.
   - implement discovery
   - validate DB-backed persistence for `Homes.bg`
   - keep all tests fixture-only in CI

4. Only after that, move to Stage 3.
   - compliance evaluator
   - legal gates
   - Temporal skeletons
   - idempotency keys
   - retry/cursor/dead-letter infrastructure

5. Only after Stage 3 is stable, expand tier-1 connectors.

## Immediate Next Slice Recommendation

The best next bounded implementation slice is:

1. Add the remaining high-value `SourceRegistry` persistence fields to schema/models/repositories.
2. Add repository tests for:
   - source registry upsert/load
   - raw capture insert
   - source listing upsert
   - snapshot insert
   - canonical listing upsert
3. Prepare a Python 3.12-ready DB runtime path so `make migrate` can be executed in Docker or a proper local environment.

This is the most leverage-positive step because it stabilizes the control plane before we multiply connector surface area.

## Commands Used In This Reconciliation

```bash
make validate
find src -maxdepth 4 -type f | sort
find tests -maxdepth 3 -type f | sort
sed -n '1,280p' docs/project-status-roadmap.md
sed -n '1,260p' docs/reports/dependency-sdk-drift-2026-04-08.md
```
