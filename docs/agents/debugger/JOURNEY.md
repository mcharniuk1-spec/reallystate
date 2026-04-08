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

## Review comments (after each task)

