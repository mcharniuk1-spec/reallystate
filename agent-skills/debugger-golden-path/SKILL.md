# Debugger: golden path check

## When to use

- After DB/sync/ingest/stats changes; before claiming the debugger slice from `docs/agents/TASKS.md` is done.
- When reducing fragility: confirm migrate → registry sync → fixture ingest → stats → XLSX export in one pass.

## Preconditions

- **With DB**: `DATABASE_URL` set (see `docs/development-setup.md`), Postgres up (`make dev-up`), Python 3.12+ and `pip install -e ".[dev]"`.
- **Without DB**: script exits 0 and prints `SKIP` — safe for `make validate` / CI that only runs unit tests. Whitespace-only `DATABASE_URL` is treated as unset (avoids bogus engine URLs).

## Commands

```bash
make golden-path
# or
PYTHONPATH=src python3 scripts/golden_path_check.py
```

## Rules

- Ingestion uses **offline** `tests/fixtures/homes_bg/basic_listing` HTML only — no live HTTP in this check.
- Unit tests must not require a database: `tests/test_golden_path_check.py` only asserts skip behavior without `DATABASE_URL`.

## Verification

- No DB: `python3 -m unittest tests.test_golden_path_check -v`
- Full stack: run `make golden-path` with `DATABASE_URL` set; expect `OK — golden path complete`.
- Project gate: `make validate` (unchanged; does not require DB).

## Related files

- `scripts/golden_path_check.py`
- `scripts/export_source_stats_xlsx.py`
- `src/bgrealestate/db_sync.py`, `src/bgrealestate/connectors/ingest.py`
- `src/bgrealestate/stats/source_stats.py`
