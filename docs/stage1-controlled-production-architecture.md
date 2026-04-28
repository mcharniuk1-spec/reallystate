# Stage 1 / Stage 2 Controlled Crawl Architecture

This document defines the controlled activation layer for the first production-like crawl.

It is intentionally **operator-driven**:

- the agent prepares the DB/control-plane/runtime structure
- the agent prepares the exact manual commands
- the agent does **not** launch live scraping automatically in this stage

## 1. Scope

Stage 1/2 uses a **region-first** architecture:

- only `region_key = varna`
- only tier-1 and tier-2 sources
- controlled source/segment buckets
- full detail-page parsing expectations
- threshold target: **100 valid listings per supported Varna source/segment bucket**

The bucket in this stage is:

- `source_name`
- `segment_key`
- `region_key=varna`
- `vertical_key=all`

Property verticals are still respected, but as **in-bucket filters and metadata**:

- `apartments`
- `houses`
- `land`
- `commercial_properties`
- `offices`
- `new_build`
- any other source-declared classes

This keeps the first activation threshold stable while still preserving source-specific structure.

## 2. Readiness Audit

The following now exist in the repo:

| Requirement | State | Where |
|---|---|---|
| Source registry | present | `data/source_registry.json`, `source_registry` |
| Source section / vertical registry | present | `source_section`, generated from `data/scrape_patterns/regions/varna/sections.json` |
| Source patterns saved | present | `source_section_pattern` with layers `source`, `section`, `list_page`, `detail_page`, `media_gallery` |
| Varna-only enforcement | present | `scrape_region`, manifest validation, `canonical_listing.region_key`, validity policy |
| Source-to-segment mappings | present | `src/bgrealestate/scraping/section_catalog.py` |
| Thresholds defined | present | `segment_fulfillment.target_valid_listings` |
| Crawl status tables | present | `crawl_run`, `crawl_queue_task`, `scrape_runner_state` |
| Failure logging | present | `crawl_error`, existing scraper logs |
| Media pipeline connected | present | `src/bgrealestate/services/media.py`, `listing_media`, local `data/media` |
| Deduplication keys | present | `property_entity.dedupe_key`, `unification.py` |
| Canonicalization path | present | `ingest.py` → `canonical_listing` → `property_entity` |
| Operator approval step | present | `scrape_runner_state.global_pause = true` by default |

## 3. Database Design Recommendation

### 3.1 Recommended architecture

Use a **hybrid model**:

- unified normalized canonical tables for downstream product/data work
- small control-plane tables for source/segment orchestration
- JSONB pattern specs per layer instead of a separate hard-coded table per website

Do **not** create separate physical listing tables per source or per operation type.

Why:

- canonical search/dedupe/CRM/map logic needs one normalized core
- source-specific structure still varies wildly and belongs in JSONB pattern specs
- queue and threshold state are naturally per bucket, not per raw source file

### 3.2 Core control-plane tables

The Stage 1 control-plane migration introduces:

- `scrape_region`
- `source_section`
- `source_section_pattern`
- `crawl_run`
- `crawl_queue_task`
- `crawl_error`
- `segment_fulfillment`
- `scrape_runner_state`
- `canonical_listing_version`

It also extends `canonical_listing` with:

- `region_key`
- `segment_key`
- `vertical_key`
- `source_section_id`
- `list_page_url`
- `detail_url_canonical`
- `combined_text`
- `normalized_text`
- `structured_extra`
- `raw_text_fallback`
- `raw_detail_storage_key`

### 3.3 Why this model is correct here

- `source_registry` stays the global source policy layer
- `source_section` is the controlled activation bucket
- `source_section_pattern` is the reusable parser/runtime contract
- `segment_fulfillment` tracks whether a bucket is still in backfill mode or is already incremental-ready
- `canonical_listing` remains the truth layer for threshold counting, dedupe, and future UI

### 3.4 Threshold-tracking state

`segment_fulfillment` now tracks:

- `target_valid_listings`
- `current_valid_listings`
- `current_total_listings`
- `last_status`
- `threshold_reached_at`
- `incremental_ready`

That is the state transition the operator cares about:

- below threshold => `backfill_required`
- threshold reached => `incremental_ready = true`

## 4. Pattern Registry Design

Patternization is layered and persisted per bucket:

1. `source`
2. `section`
3. `list_page`
4. `detail_page`
5. `media_gallery`

Each layer is stored in `source_section_pattern.spec_jsonb`.

### 4.1 What is stored

Per bucket, the persisted pattern includes:

- source name
- runtime source key (when implemented)
- legal mode
- pattern status
- support status
- activation readiness
- supported verticals
- entry URLs or discovery templates
- listing URL regex
- pagination pattern
- detail-page required fields
- gallery rules
- Varna enforcement rules
- target threshold
- skip reason when not activatable

### 4.2 Pattern status rule

`Patterned` remains strict:

- a random detail page from that source section must parse fully
- core fields must land
- full reachable gallery must land
- image order must be preserved

If this is not proven, the section is not treated as ready for controlled activation even if the source has some saved samples.

## 5. Varna-only Enforcement

Varna filtering is enforced at five stages:

1. `source_entry`
2. `list_page`
3. `detail_page`
4. `parse`
5. `validation`

Rules:

- prefer exact Varna entry URLs or API filters where known
- if exact Varna entrypoints do not exist, use national fallback routes only with strict downstream rejection
- reject cross-region items explicitly
- never count a row toward threshold unless `region_key = varna`

## 6. Valid Record Criteria

A listing counts toward the `100` threshold only if all of the following are true:

- it belongs to `region_key = varna`
- it belongs to the correct `source_name`
- it belongs to the correct `segment_key`
- it has a valid source identity: `reference_id` and `external_id`
- it has a valid detail-page URL: `detail_url_canonical` or `listing_url`
- it has a location signal: `city` or `address_text`
- it has a text signal: `combined_text`, `description`, or `raw_text_fallback`
- it has at least one structured signal: `price`, `area_sqm`, `rooms`, or non-empty `structured_extra`
- it is not marked inactive through `removed_at`

This policy is codified in:

- `src/bgrealestate/scraping/validity.py`

### 6.1 Media policy

Media is handled separately:

- media is **not required** for threshold counting
- missing media is flagged as a quality issue
- full gallery is still required for a section/source to be called `Patterned`

So:

- description present + media missing can still count toward the `100` target
- but it must remain visible as `media_incomplete`

## 7. Full Detail-Page Collection Contract

For every accepted property, the future crawl worker must save:

- source
- source section / segment / region
- canonical detail URL
- discovered listing URL
- source list-page URL
- title
- price
- currency
- area
- rooms
- floor
- total floors
- construction/building type
- property category
- address/location text
- city / district / region
- description
- structured attributes
- `combined_text`
- `raw_text_fallback`
- all image URLs
- image order
- crawl provenance
- raw HTML or payload reference

Null handling rule:

- if a source truly lacks a field, keep it null
- preserve the unmapped data in `structured_extra` or `raw_text_fallback`
- never silently discard useful raw text blocks

## 8. Activation Logic

The controlled activation pass works bucket by bucket:

1. load `source_section` rows for `region_key = varna`
2. join layered patterns from `source_section_pattern`
3. calculate current threshold counts from `canonical_listing`
4. decide one of:
   - `skipped_unsupported`
   - `skipped_legal_blocked`
   - `skipped_pattern_incomplete`
   - `inactive`
   - `paused_pending_backfill`
   - `backfill_required`
   - `threshold_reached`
5. refresh `segment_fulfillment`
6. if unpaused and operator requested enqueue:
   - create `crawl_run`
   - enqueue `discover` + `threshold_check` tasks for below-threshold supported buckets

### 8.1 Stop / transition rule

When `current_valid_listings >= target_valid_listings`:

- mark bucket `threshold_reached`
- set `incremental_ready = true`
- do not schedule wasteful backfill again
- future runs should only perform incremental discovery/refresh for that bucket

## 9. Runtime / Orchestration Design

### 9.1 Current prepared entrypoints

These exist now:

- manifest generator
- manifest validator
- manifest-to-DB sync
- threshold summary
- queue status summary
- global pause toggle
- controlled runner planner / queue seeder
- manual control worker for `discover` + `threshold_check`
- one-call all-Bulgaria runtime scraper for patterned sources:
  `bgrealestate.scraping.run_parallel_all_scrape(...)` / `scrape-all-full`
- one-call Varna runtime scraper for patterned sources:
  `bgrealestate.scraping.run_parallel_varna_scrape(...)` / `scrape-varna-full`

CLI commands:

- `scrape-generate-varna-manifest`
- `scrape-validate-manifest`
- `scrape-sync-sections`
- `scrape-threshold-summary`
- `scrape-queue-status`
- `scrape-control-worker-once`
- `scrape-set-runner-pause`
- `scrape-runner-once`
- `scrape-all-full`
- `scrape-varna-full`

### 9.2 Recommended activation model

For the first production-like crawl, use **one manual orchestration command** rather than autonomous recurring scheduling:

1. validate manifest
2. sync registry + sections
3. inspect threshold summary
4. clear pause
5. enqueue discover + threshold tasks
6. manually run the control worker to expand discover tasks into concrete `fetch_list` tasks
7. only then move into source-runtime fetch execution

Separate long-running HTTP/detail/media workers are still intentionally operator-controlled. In this pass, the system is prepared for controlled activation, not auto-launched by the agent.

## 10. Docker / Environment Guidance

### 10.1 Manual operator check required

Before any run, manually inspect:

- [docker-compose.yml](/Users/getapple/Documents/Real%20Estate%20Bulg/docker-compose.yml)

Important:

- edit compose image/tag if needed
- confirm the PostGIS image supports your architecture
- on Apple Silicon, do **not** assume a random PostGIS tag works

Current guidance in the repo uses:

- `postgis/postgis:16-3.4`

That is a better multi-arch default than some `17-3.5` tags, but you still must verify it on your machine.

### 10.2 Required services

For local controlled execution:

- PostgreSQL/PostGIS
- Redis
- MinIO
- Temporal (optional now, recommended later)
- Temporal UI (optional)

### 10.3 Required environment

At minimum:

- `DATABASE_URL`
- `REDIS_URL`
- `S3_ENDPOINT_URL`
- `S3_BUCKET`
- `S3_ACCESS_KEY_ID`
- `S3_SECRET_ACCESS_KEY`
- `MEDIA_STORAGE_PATH`

### 10.4 Initialization order

1. start Docker services
2. confirm Postgres is healthy
3. copy `.env.example` to `.env`
4. export `DATABASE_URL`
5. run migrations
6. sync source registry
7. generate + validate manifest
8. sync sections/patterns
9. inspect threshold summary
10. only then consider unpausing + enqueueing

## 11. Operational Safeguards

The control plane now supports:

- dry-run mode
- source subset mode
- one-section mode
- threshold summary output
- global pause / unpause
- explicit skip reasons
- incremental readiness transition

### 11.1 Failure behavior

- unsupported buckets are skipped with reason
- legal-blocked buckets are skipped with reason
- pattern-incomplete buckets are skipped with reason
- paused buckets are surfaced explicitly as `paused_pending_backfill`

### 11.2 Retry behavior

Queue tasks have:

- `attempt_count`
- `max_attempts`
- `next_attempt_at`
- `lease_until`

This is the right place for future worker retry logic.

### 11.3 Stop / resume behavior

Use the global switch:

- `scrape_runner_state.global_pause = true` => stop new activation
- `false` => allow queue seeding

Operator-friendly command:

```bash
PYTHONPATH=src python -m bgrealestate scrape-set-runner-pause --paused true --note "Paused by operator"
```

## 12. Exact Operator Commands

These commands are **manual**. The agent must not execute them automatically as part of Stage 1 preparation.

### 12.1 Preflight

```bash
cp .env.example .env
make dev-up
make dev-ready
export DATABASE_URL=postgresql+psycopg://bgrealestate:bgrealestate@localhost:5432/bgrealestate
make migrate
make sync-registry
```

### 12.2 Manifest and pattern sync

```bash
make scrape-generate-varna-manifest
make scrape-validate-manifest
make scrape-sync-sections
```

### 12.3 Inspect readiness and counts

```bash
make scrape-threshold-summary
make scrape-queue-status
PYTHONPATH=src python -m bgrealestate scrape-threshold-summary --source-name Homes.bg
PYTHONPATH=src python -m bgrealestate scrape-threshold-summary --section-id homes_bg__varna__buy_personal__all
```

### 12.4 Approve activation

```bash
make scrape-runner-unpause
```

Equivalent explicit form:

```bash
PYTHONPATH=src python -m bgrealestate scrape-set-runner-pause --paused false --note "Operator approved first controlled Varna crawl"
```

### 12.5 Seed the first controlled activation wave

```bash
PYTHONPATH=src python -m bgrealestate scrape-runner-once --apply --enqueue
```

Optional focused activation:

```bash
PYTHONPATH=src python -m bgrealestate scrape-runner-once --apply --enqueue --source-name Homes.bg
PYTHONPATH=src python -m bgrealestate scrape-runner-once --apply --enqueue --section-id homes_bg__varna__buy_personal__all
```

### 12.6 Expand queue tasks manually

Preview the next eligible control-plane task without mutating DB state:

```bash
make scrape-control-worker-once
```

Process one queued `discover` or `threshold_check` task:

```bash
PYTHONPATH=src python -m bgrealestate scrape-control-worker-once --apply
```

Restrict to one source while validating:

```bash
PYTHONPATH=src python -m bgrealestate scrape-control-worker-once --apply --source-name Homes.bg
```

Inspect the queue again:

```bash
make scrape-queue-status
```

### 12.7 Run the one-call all-Bulgaria full scrape

The operator request is now to scrape **all Bulgaria**, not only Varna. Use this path for the full file-backed scrape because the saved corpus already contains non-Varna listings and the live source configs include national and multi-city routes.

The single callable runtime is:

```python
from bgrealestate.scraping import run_parallel_all_scrape

run_parallel_all_scrape(
    target_per_source=100,
    max_pages=8,
    max_waves=3,
    parallel_sources=4,
    download_photos=True,
    require_full_gallery=True,
    dry_run=False,
    refresh_dashboard=True,
)
```

Equivalent operator command:

```bash
make scrape-all-full EXTRA_ARGS="--parallel-sources 4 --max-pages 8 --max-waves 3 --target-per-source 100 --refresh-dashboard"
```

Dry-run planning command:

```bash
make scrape-all-full EXTRA_ARGS="--dry-run --parallel-sources 4 --target-per-source 100"
```

This path counts complete saved rows per source across all cities/regions. It does not apply `is_varna_listing` and does not require `region_key = varna`.

### 12.8 Run the legacy one-call Varna full scrape

The single callable runtime is:

```python
from bgrealestate.scraping import run_parallel_varna_scrape

run_parallel_varna_scrape(
    target_per_section=100,
    max_pages=8,
    max_waves=3,
    parallel_sources=4,
    download_photos=True,
    require_full_gallery=True,
    dry_run=False,
    refresh_dashboard=True,
)
```

Equivalent operator command:

```bash
make scrape-varna-full EXTRA_ARGS="--parallel-sources 4 --max-pages 8 --max-waves 3 --target-per-section 100 --refresh-dashboard"
```

Dry-run planning command:

```bash
make scrape-varna-full EXTRA_ARGS="--dry-run --parallel-sources 4 --target-per-section 100"
```

Use this only when intentionally validating the older Varna control-plane scope.

For old saved corpora where remote gallery URLs exist but local files are incomplete, run the media backfill utility:

```bash
make backfill-scraped-media EXTRA_ARGS="--source bulgarianproperties"
make dashboard-doc
```

## 13. How the Operator Verifies Correctness

### 13.1 Verify the system started planning correctly

Check:

```bash
PYTHONPATH=src python -m bgrealestate scrape-runner-once
PYTHONPATH=src python -m bgrealestate scrape-control-worker-once
```

You should see:

- `global_pause`
- per-section `action`
- planned task counts
- explicit skip reasons

### 13.2 Verify Varna-only behavior

Check the persisted section specs:

- `data/scrape_patterns/regions/varna/sections.json`
- `docs/exports/varna-controlled-crawl-matrix.md`

And verify every bucket has:

- `region_key = varna`
- strict Varna enforcement stages

### 13.3 Verify section / segment correctness

Use:

```bash
PYTHONPATH=src python -m bgrealestate scrape-threshold-summary --source-name "imot.bg"
```

Confirm each section row shows:

- correct source
- correct segment
- correct support status
- correct activation action

### 13.4 Verify bucket counts

Use:

```bash
make scrape-threshold-summary
make scrape-queue-status
```

Key fields:

- `current_valid_listings`
- `current_total_listings`
- `target_valid_listings`
- `action`

### 13.5 Know when the target is reached

The bucket is done with backfill when:

- `action = threshold_reached`
- `current_valid_listings >= 100`
- `incremental_ready = true` in `segment_fulfillment`

### 13.6 What happens next

After threshold is reached, the system should:

- stop treating the bucket as backfill-required
- keep the bucket in incremental mode readiness only
- avoid wasteful full backfill re-enqueueing

### 13.7 Service split for the first manual run

For this Stage 2 controlled run, the recommended manual split is:

- scheduler: `scrape-runner-once --apply --enqueue`
- control worker: `scrape-control-worker-once --apply`
- threshold monitor: `scrape-threshold-summary` + `scrape-queue-status`
- HTTP/detail/media execution: still operator-controlled and source-runtime-specific; do not daemonize this automatically in Stage 2 preparation

Parser worker and media worker are not separate mandatory services yet because the current repo still uses source runtimes and the media pipeline together at ingestion time. Keep them manual until the unified HTTP executor is implemented and verified.

## 14. Manual / Agent Boundary

### The agent prepares

- schema changes
- models
- pattern catalog
- manifest
- section matrix
- threshold summary logic
- queue seeding logic
- operator commands
- runbook

### The operator does manually

- verify Docker image compatibility
- set environment variables
- run migrations
- sync registries and sections
- unpause the runner
- launch the first controlled activation command
- decide when live background collection may start

## 15. Explicit Non-Execution Rule

Repeat clearly:

- do **not** launch the crawl automatically
- do **not** start background collection automatically
- do **not** clear the pause switch automatically
- only prepare the activation procedure and manual commands

The human operator decides when the first live background collection begins.
