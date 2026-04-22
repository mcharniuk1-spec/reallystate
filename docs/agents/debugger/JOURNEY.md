# Debugger agent journey

## Scope
- Reproduce failures, isolate root causes, tighten tests, and reduce flakiness.

## Executed tasks (append-only)

### 2026-04-08 — Debugger slice: golden path check

- Implemented `scripts/golden_path_check.py` (migrate → sync → Homes.bg fixture ingest → stats → XLSX; skips when `DATABASE_URL` unset).
- Added `make golden-path`, `tests/test_golden_path_check.py` (no DB, no network), `agent-skills/debugger-golden-path/SKILL.md`.
- Updated `docs/agents/TASKS.md` (debugger slice), `docs/agent-skills-index.md`, `Makefile`.

**Changed files**

- `scripts/golden_path_check.py`
- `tests/test_golden_path_check.py`
- `agent-skills/debugger-golden-path/SKILL.md`
- `Makefile`
- `docs/agents/TASKS.md`
- `docs/agent-skills-index.md`
- `docs/agents/debugger/JOURNEY.md`

**Commands / tests run**

- `PYTHONPATH=src python3 -m unittest tests.test_golden_path_check -v`
- `PYTHONPATH=src python3 -m unittest discover -s tests -v`
- `PYTHONPATH=src python3 scripts/golden_path_check.py` (expect `SKIP` without `DATABASE_URL`)

**Review comments**

- Confusing: `docs/agents/README.md` already points to `TASKS.md` but debugger slice did not name a concrete artifact until now — keep TASKS as the single queue and link scripts from there.
- Improve next time: optional CI job that runs `make golden-path` with a service container when we want true e2e on every push; keep default `make validate` DB-free.
- `export_source_stats_xlsx.py` exits hard if `DATABASE_URL` missing — golden path only calls it after DB steps; OK.

### 2026-04-08 (follow-up) — Golden path DATABASE_URL hygiene

- **Changed**: `scripts/golden_path_check.py` treats whitespace-only `DATABASE_URL` as unset; passes trimmed URL to alembic/export children.
- **Tests**: `tests/test_golden_path_check.py` — `test_skips_when_database_url_is_whitespace_only`.
- **Review**: Empty `.env` lines like `DATABASE_URL=` already skip; `DATABASE_URL=   ` no longer attempts SQLAlchemy with a blank URL.

### 2026-04-08 (follow-up) — Homes.bg discovery pagination regex

- **Evidence**: `test_homes_bg_discovery.TestHomesBgDiscovery.test_discovery_page_with_pagination` failed with `next_cursor None != {'page': 2}`.
- **Cause**: `NEXT_PAGE_RE` required `class="...next-page..."` before `href=`; fixture `tests/fixtures/homes_bg/discovery_page/raw.html` uses `href` first.
- **Fix**: `parse_discovery_html` scans `<a ...>` open tags, finds `next-page` in `class`, then reads `page` from `href` (attribute-order agnostic).
- **Verify**: `PYTHONPATH=src python3 -m unittest discover -s tests -v` — 49 ok, 6 skipped.

### 2026-04-08 (follow-up) — SourceStatRow import without SQLAlchemy

- **Evidence**: `test_control_plane.TestSourceStatsModel.test_source_stat_row_has_registry_fields` → `ModuleNotFoundError: No module named 'sqlalchemy'` when importing `bgrealestate.stats.source_stats`.
- **Cause**: Eager `from sqlalchemy import text` at module import time; minimal/CI environments may run tests without deps even when `skipUnless` misfires or is removed.
- **Fix**: Lazy-import `sqlalchemy.text` inside `fetch_source_stats`; `Engine` only under `TYPE_CHECKING`. Removed `@unittest.skipUnless` on `TestSourceStatsModel`.
- **Verify**: `PYTHONPATH=src python3 -m unittest discover -s tests -v` — 56 ok, 8 skipped.

### 2026-04-08 (follow-up) — Ruff CI failures

- **Evidence**: `python -m ruff check .` (CI parity) reported 6 issues: F401 unused imports (`Iterable`, `LegalGateError`, `dataclass`, `String`, `Path`), F841 unused `source` in `HomesBgConnector.discover_listing_urls`.
- **Fix**: Removed dead imports; call `self._source_for_fetch()` for legal gate without assigning; dropped unused `String` from `db/models.py`.
- **Verify**: `ruff check .` → All checks passed; `unittest discover` — 62 ok, 8 skipped.

### 2026-04-08 (follow-up) — Mypy (`make typecheck`)

- **Evidence**: `mypy src tests` reported 16 errors: `chat_service` model arg, `pipeline` haversine coords, optional registry rows in tests, `ClassVar` for social test registry, pipeline test `SourceRegistryEntry | None` / floats / `building_match`.
- **Fix**: Coerce OpenAI model name to `str`; explicit `is not None` guard before `haversine_km`; `ClassVar[SourceRegistry]` + `assert entry is not None` in social tests; narrow types in `test_pipeline` / `test_source_registry`.
- **Verify**: `mypy src tests` → Success; `ruff check .` + `unittest discover` unchanged green.

### 2026-04-08 (follow-up) — CI parity for Mypy

- **Do**: Added `python -m mypy src tests` to `.github/workflows/ci.yml` after Ruff (matches `make typecheck`).
- **Why**: Local `make typecheck` was green while CI only ran Ruff + tests; type regressions could merge unnoticed.

### 2026-04-08 (follow-up) — Cross-agent safety audit (DBG-03)

- **Scope checked**:
  - legal gate enforcement across connector fetch paths
  - live-network usage in tests
  - fixture secrets/PII redaction baseline
  - media binary storage policy (Postgres vs object storage)
- **Evidence / commands**:
  - `make test`
  - `rg "assert_live_http_allowed|LegalGateError|legal_mode|source_legal_rule" src`
  - `rg "def fetch_listing_detail\\(|assert_live_http_allowed\\(" src/bgrealestate/connectors`
  - `rg "httpx|requests|urllib|socket|aiohttp|playwright" tests`
  - `rg "(AKIA[0-9A-Z]{16}|BEGIN PRIVATE KEY|api[_-]?key|token|password|secret|Bearer\\s+[A-Za-z0-9\\-\\._~\\+\\/]+=*)" tests/fixtures -i`
  - `rg "bytea|LargeBinary|BLOB|blob|storage_key|media_asset|raw_file" sql/schema.sql`
- **Findings**:
  1. **PASS**: marketplace connectors enforce legal gate on live fetch (`homes_bg`, `olx_bg`, `scaffold` all call `assert_live_http_allowed` before HTTP).
  2. **PASS**: tests show no direct live network client usage (`httpx/requests/aiohttp/playwright`) in `tests/`.
  3. **PASS**: social fixture redaction tests exist and pass (`test_social_ingestion_contract` redaction checks).
  4. **PASS**: schema stores media via storage keys/metadata (`media_asset`, `raw_file`, `storage_key` fields), not binary blobs.
  5. **BLOCKER FILED**: `make test` currently fails on `tests/test_control_plane.py::test_source_stat_row_has_registry_fields` because `SourceStatRow` now requires additional stats fields (`with_photos`, `photo_coverage_pct`, intent/category counters). Task board updated: `BD-03` marked `BLOCKED` pending test/schema alignment.
- **Outcome**: DBG-03 completed with one documented blocker routed to backend_developer.

### 2026-04-08 (follow-up) — DBG-02 + DBG-03 + DBG-04 completion pass

- **Action**:
  - `DBG-02`: scanned `TASKS.md` for `DONE_AWAITING_VERIFY`; verified `UX-01` against current API payload shape and marked it `VERIFIED`.
  - `DBG-03`: reran safety audit gates (legal fetch gates, no live-network unit tests, fixture secret scan, media-storage policy).
  - `DBG-04`: updated CI workflow to run `make lint`, `make typecheck`, `make test`, `make validate`, and a dedicated PostGIS-backed `make golden-path` job.
- **Changed files**:
  - `.github/workflows/ci.yml`
  - `docs/agents/TASKS.md`
  - `docs/agents/debugger/JOURNEY.md`
  - `scripts/generate_architecture_guide.py`
  - `scripts/generate_product_summary_report.py`
- **Gate commands run**:
  - `make lint`
  - `make typecheck`
  - `make test`
  - `make validate`
  - `make golden-path`
  - `make dashboard-doc`
  - `rg "httpx|requests|urllib|socket|aiohttp|urlopen|Client\\(" tests`
  - `rg "AKIA|AIza|secret|password|BEGIN (RSA|OPENSSH|PRIVATE)|Bearer\\s+[A-Za-z0-9\\-_\\.]+" tests/fixtures`
  - `rg "bytea|blob|binary|large object|lo_" sql/schema.sql`
  - `rg "assert_live_http_allowed\\(" src/bgrealestate/connectors`
- **Results**:
  - `make lint`: PASS
  - `make typecheck`: PASS (`59` files checked)
  - `make test`: PASS (`64` tests, `9` skipped)
  - `make validate`: PASS (`project validation ok`)
  - `make golden-path`: PASS (skip mode without DB is expected; CI job now covers DB-backed path)
  - audit scans: PASS (no new blockers)
- **Status**:
  - `DBG-02`: VERIFIED
  - `DBG-03`: VERIFIED
  - `DBG-04`: VERIFIED
  - `UX-01`: VERIFIED
- **Review comments**:
  - CI now enforces the same Make targets used locally; keep Makefile target semantics stable.
  - Golden-path DB execution is now delegated to CI service containers; local skip behavior remains useful for dev laptops.
  - Report-generation scripts are part of the lint surface and should stay clean because `make validate` regenerates docs every run.

### 2026-04-08 — VERIFY: BD-03 / T3-01 / SM-01 (agent: backend_developer / scraper_t3 / scraper_sm)

- **Gate commands run**:
  - `make lint`
  - `make typecheck`
  - `make test`
  - `make validate`
  - `make golden-path`
  - `make dashboard-doc`
  - `rg "assert_live_http_allowed\\(" src/bgrealestate/connectors`
  - `rg "httpx|requests|urllib|socket|aiohttp|urlopen|Client\\(" tests`
  - `rg "AKIA|AIza|secret|password|BEGIN (RSA|OPENSSH|PRIVATE)|Bearer\\s+[A-Za-z0-9\\-_\\.]+" tests/fixtures`
  - `rg "bytea|blob|binary|large object|lo_" sql/schema.sql`
- **Result**: PASS
- **Verification details**:
  - `BD-03`: `/admin/source-stats` includes coverage/intent/category fields and the admin page renders coverage bars; XLSX export includes the new stats columns.
  - `T3-01`: `docs/agents/scraper_t3/tier3-ingestion-policy.md` defines source-by-source legal/access integration patterns and fixture templates; policy contract complete.
  - `SM-01`: `docs/agents/scraper_sm/social-ingestion-policy.md` + `social_ingestion_contract.md` include consent checklist and redaction rules; social fixture templates exist under `tests/fixtures/social/`.
  - Safety checks found no live-network unit tests, no secret-pattern matches in fixtures, and no media-binary schema storage.
- **Task status updates**:
  - `BD-03` → `VERIFIED`
  - `T3-01` → `VERIFIED`
  - `SM-01` → `VERIFIED`
- **Review comments**:
  - Keep policy docs and fixture templates in lockstep with `data/source_registry.json` when legal modes change.
  - For future verifier runs, keep one explicit command mapping per acceptance gate to reduce ambiguity.

### 2026-04-08 (follow-up) — Gate regression fix (auth + tier2 typecheck)

- **Evidence**:
  - `make lint` failed with `src/bgrealestate/api/auth.py: F401 fastapi.Depends imported but unused`.
  - After that, `make typecheck` failed with 7 mypy errors in `tests/test_tier2_stub_fixture_parsing.py` (`registry` class attribute typing and `Connector` protocol method typing for `parse_and_normalize_from_html`).
- **Fix**:
  - Removed unused `Depends` import in `src/bgrealestate/api/auth.py`.
  - Added typed class attribute `registry: ClassVar[SourceRegistry]` and safe narrowing/casting in `tests/test_tier2_stub_fixture_parsing.py`.
- **Verification**:
  - `make lint` → PASS
  - `make typecheck` → PASS (`Success: no issues found in 69 source files`)
  - `make test` → PASS (`82` tests, `11` skipped)
  - `make validate` → PASS
  - `make golden-path` → PASS (expected SKIP without `DATABASE_URL`)
  - `make dashboard-doc` → PASS
- **Review comments**:
  - New slices can increase static-analysis surface quickly; rerunning full make gates is required before marking verifier tasks complete.
  - Connector factory returns a broad protocol; tests that call source-specific parse methods should cast/narrow explicitly for mypy.

## Review comments (after each task)

### 2026-04-21 — VERIFY: scraper_1 heartbeat incremental run (agent: scraper_1)

- **Gate commands run**:
  - reviewed scraper_1 heartbeat command output from `python3 scripts/live_scraper.py --sources homes_bg,imot_bg --max-pages 1 --max-listings 4 --download-photos`
- **Result**: FAIL
- **Failure details**:
  - The run was blocked before discovery because DNS resolution failed for `www.homes.bg` and `www.imot.bg` (`nodename nor servname provided, or not known`).
  - No evidence suggests parser regression; the failure happened at network resolution.
- **Review comments**:
  - Treat this as an environment/runtime blocker, not a source-parser blocker.
  - The next debugger follow-up should verify a live heartbeat only after outbound DNS/network access is available again.

### 2026-04-21 — VERIFY: scraper_1 heartbeat retry (agent: scraper_1)

- **Gate commands run**:
  - reviewed retry output from `python3 scripts/live_scraper.py --sources homes_bg --max-pages 1 --max-listings 1 --download-photos`
- **Result**: FAIL
- **Failure details**:
  - `www.homes.bg` still failed on hostname resolution before discovery started.
  - No new evidence of parser breakage appeared in this retry.
- **Review comments**:
  - Repeated failure confirms the blocker is environmental in this heartbeat environment.
  - Keep the heartbeat automation active; do not demote source pattern readiness because of this retry.

### 2026-04-21 — debugger follow-up queued: strict pattern audit and local-media proof (agent: scraper_1)

- **Gate commands run**:
  - deferred formal verification until the refreshed `tier12-pattern-status` artifacts and dashboard outputs are the stable latest versions for this run
- **Result**: DEFERRED
- **Failure details**:
  - No parser failure is implied here. This is an explicit handoff note so the stricter `Patterned` classification can be spot-checked after artifact regeneration is complete.
- **Review comments**:
  - The verifier should confirm that only sources with local image-file evidence plus core and structured item fields remain `Patterned`.
  - The verifier should also confirm that downgraded sources still keep their filesystem media evidence visible in the report instead of disappearing from readiness tracking.

### 2026-04-21 — debugger follow-up queued: parser repair wave + DB-runtime blocker proof (agent: scraper_1)

- **Gate commands run**:
  - deferred formal verification until the refreshed strict pattern artifacts and the environment-runtime checks are preserved in `scraper_1` JOURNEY for this run
- **Result**: DEFERRED
- **Failure details**:
  - No parser failure is implied by this handoff note.
  - The remaining blocker to full acceptance is environment runtime, not code: PostgreSQL is not running on `localhost:5432`, and Docker daemon/socket are unavailable for starting the repo stack here.
- **Review comments**:
  - Verify that the promoted sources now have sample evidence matching the saved report entries in `docs/exports/tier12-pattern-status.md`.
  - Verify that the DB proof is correctly marked as blocked by runtime availability rather than misreported as a parser or ingest-code failure.
