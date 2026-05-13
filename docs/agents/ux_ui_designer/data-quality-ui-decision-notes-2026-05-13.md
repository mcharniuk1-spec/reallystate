# Data Quality UI Decision Notes - 2026-05-13

## Inputs

- `docs/agents/TASKS.md`
- `docs/agents/roles/ux_ui_designer.md`
- `docs/agents/roles/data_analyst.md`
- `docs/exports/scrape-database-quality-audit-2026-05-13.md`
- `docs/exports/action1-dataset-quality-gate.md`

## Scope Decision

FACT: The current Action1 corpus is large but has many `PENDING_QA`, missing-status, `LOST`, grouped/development, media-gap, and schema-alignment issues.

INTERPRETATION: UX work must start with admin/operator truth surfaces. Buyer-facing surfaces can only consume accepted single-unit records and verified provenance fields.

HYPOTHESIS: Operator review speed improves if QA state, source-publication type, media status, duplicate confidence, and provenance are visible in one queue instead of scattered across exports.

GAP: DB-backed API fields for QA/media/provenance are not yet verified. `BD-18` and `DA-02` must settle the contract before public UI implementation.

## Required UI State Model

| State | Operator UI | Buyer UI | Required evidence |
|---|---|---|---|
| Accepted single-unit | Eligible row with green status, evidence drawer, source links, media counts, confidence | Can appear in feed/detail after debugger verifies import/export path | `scrape_acceptance_status=accepted`, `source_publication_type=single_unit`, price or `price_status`, location, source URL |
| Pending QA | Review queue item with reason chips and required next action | Never shown | `scrape_acceptance_status=pending_qa` or missing status |
| LOST / invalid | Quarantine/rescrape queue with reason and source sample | Never shown | `scrape_status=LOST` or invalid hard-loss reason |
| Grouped/development publication | Development/source-publication review queue, not a property row | Not shown as one property; future development page only after unit-level evidence exists | `source_publication_type=grouped_publication` or suspected multi-unit signals |
| Media gap | Media repair queue with remote/local counts and image-report status | Only visible if row is otherwise accepted and warning copy is approved | `photo_count_remote`, `photo_count_local`, `full_gallery_downloaded`, `image_report_status` |
| Duplicate candidate | Side-by-side review with confidence and evidence chips | Do not auto-merge into one public property until verified | candidate IDs, score, signals, source-provenance comparison |
| Low confidence | Highlight for operator review; confidence explains matching certainty, not property truth | Buyer UI should not expose raw score; use verified source count/provenance instead | `confidence_score`, `geocode_confidence`, match signals |

## Admin / Operator Requirements First

1. Add a source-publication QA queue before expanding public browse UI.
   - Filters: source, bucket, QA state, publication type, reason, media status, confidence band.
   - Columns: source key, bucket, title, city/district, price/status, area, QA state, publication type, media counts, last seen.
   - Drawer: raw source URL, captured timestamps, parser reasons, source registry legal/risk/access modes, normalized fields, local media keys.

2. Add grouped/development review as a separate queue.
   - Do not place grouped/development rows inside duplicate review as if they were single units.
   - Required operator actions: keep grouped, split into units when unit-level evidence exists, send to scraper repair, dismiss as invalid.

3. Add a media-gap queue.
   - Show remote vs local photo count, full-gallery flag, readable image count, image-report status, and semantic image-report coverage.
   - Operator actions: queue media backfill, mark source-limited, queue Action0 image report after operator approval.

4. Add duplicate-candidate review after accepted source-publication import exists.
   - Side-by-side comparison must show source URL, source key, title, address, area, price/status, photos, phones, confidence signals, and conflict fields.
   - Merge is disabled for grouped/development publications and low-confidence candidates.

5. Add provenance drawer everywhere in admin review.
   - Minimum fields: source key/name, source URL, source external ID, bucket/segment key, first seen, last seen, scrape run, parser version if available, legal/risk/access mode.

## Buyer-Facing Requirements Later

1. Public feed and detail pages must default to accepted single-unit records only.
2. Buyer labels should be plain trust labels, not raw pipeline statuses:
   - `Verified source`
   - `Multiple sources`
   - `Limited photos`
   - `Price on request`
   - `Location approximate`
3. Public pages may show source provenance as `Listed on <source>` and `Marketed by sources`, but should not expose parser internals.
4. Grouped/development publications need a separate future product shape, not a normal property card, unless unit-level URL, price/status, area, and media evidence exists.
5. Duplicate confidence is internal. Buyer UI can show merged-source count only after debugger verifies the merge policy.

## Debugger Handoff

Debugger should verify:

- No `PENDING_QA`, missing-status, `LOST`, grouped/development, or inactive rows are exposed in public UI/export defaults.
- Admin labels match data analyst definitions and do not hide grouped denominator drift.
- UX implementation tasks depend on `DA-02`, `BD-18`, and `BD-19` for DB/API-backed truth.
- Future screenshots check both admin review queues and buyer surfaces with accepted-only fixture data.
