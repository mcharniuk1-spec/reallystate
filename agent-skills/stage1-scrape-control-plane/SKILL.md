# Stage 1 scrape control plane and full scrape runners

## When to use

- Preparing **passive** background scraping: DB schema, manifests, queue stubs, **no live HTTP** until the operator clears gates.
- Any task referencing **S1-20**, `scrape_region`, `source_section`, `segment_fulfillment`, or `scrape_runner_state`.
- Running the operator-approved full scrape across all Bulgaria from the already patterned live source configs.

## Hard rules

1. **Control plane compatibility**: the existing DB manifest/control-plane path is still `region_key=varna` and must remain valid until a schema migration widens it. Do not break `scrape-varna-full` or manifest validation.
2. **All-Bulgaria full scrape**: use `scrape-all-full` for the operator request to scrape all locations. This path is file-backed and uses patterned live source configs directly instead of the Varna-only section manifest.
3. **No auto-start**: Default `scrape_runner_state.global_pause = true`. Do not ship cron/systemd that enqueues real `fetch_*` tasks without operator approval.
4. **Patterned bar**: A source or source section is “pattern-complete” only when a random listing detail page can be fully parsed (structured fields, description, **full gallery** with order, URL provenance). Placeholders are **not** pattern-complete.
5. **Tests**: No live network in unit tests; optional DB integration only when `DATABASE_URL` is explicitly available.

## Operator commands (local)

```bash
make scrape-generate-varna-manifest   # rewrite sections.json + control matrix
make scrape-validate-manifest         # JSON + layer checks
make scrape-sync-sections-dry         # load only
export DATABASE_URL=postgresql://...
make migrate                          # or make db-init
make sync-registry                    # source_registry rows
make scrape-sync-sections             # upsert sections + patterns + fulfillment
make scrape-threshold-summary         # DB-backed section counts and actions
make scrape-queue-status              # DB-backed queue counts + next tasks
make scrape-runner-once               # read-only tick by default
make scrape-control-worker-once       # preview next control-plane task by default
make scrape-runner-unpause            # operator approval
make scrape-varna-full                # one-call Varna scrape for patterned sources
make scrape-all-full                  # one-call all-Bulgaria scrape for patterned sources
make backfill-scraped-media           # fill missing local gallery files for saved data/scraped rows
# To enqueue no-op threshold_check tasks after unpausing:
# PYTHONPATH=src python -m bgrealestate scrape-runner-once --apply --enqueue
# To expand one queued discover/threshold task manually:
# PYTHONPATH=src python -m bgrealestate scrape-control-worker-once --apply
# To run the patterned-source Varna scrape:
# make scrape-varna-full EXTRA_ARGS="--parallel-sources 4 --max-pages 8 --max-waves 3 --target-per-section 100 --refresh-dashboard"
# To run the patterned-source all-Bulgaria scrape:
# make scrape-all-full EXTRA_ARGS="--parallel-sources 4 --max-pages 8 --max-waves 3 --target-per-source 100 --refresh-dashboard"
```

## Key paths

- Manifest: `data/scrape_patterns/regions/varna/sections.json`
- Code: `src/bgrealestate/scraping/`
- All-Bulgaria summary: `docs/exports/all-full-scrape-summary.json`
- Migration: `migrations/versions/20260423_0003_stage1_scrape_control_plane.py`
- Design doc: `docs/stage1-controlled-production-architecture.md`

## Next stage (do not run in Stage 1)

Run the controlled activation manually from the architecture doc:

- validate and sync the manifest
- inspect `scrape-threshold-summary`
- clear the global pause explicitly
- enqueue discover + threshold tasks with `scrape-runner-once --apply --enqueue`
- expand queued discover tasks with `scrape-control-worker-once --apply`

Long-running queue-draining workers remain a separate execution step and must not be auto-started in this skill.
