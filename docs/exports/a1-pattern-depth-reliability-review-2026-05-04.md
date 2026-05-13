# A1 Pattern Depth And Scraping Reliability Review

Generated: 2026-05-04

Scope: first seven Action1 sources: Address.bg, BulgarianProperties, Homes.bg, imot.bg, LUXIMMO, property.bg, SUPRIMMO.

## Executive Summary

FACT: The previous parser changes fixed major generic-fallback defects: one-image Address.bg galleries, thin BulgarianProperties descriptions, Homes.bg decimal-shifted areas, property-family project-wide area selection, and outside-Bulgaria coordinates.

FACT: The current remaining risk is not one parser bug. It is pipeline consistency: discovery route context, source-publication identity, QA quarantine, import/frontend gating, and pattern-status sample selection must all agree.

INTERPRETATION: OpenClaw can continue controlling parsing if it treats scraped rows as `source publications` first, runs the Action1 quality gate after every batch, and imports/exports only accepted single-entity candidates by default.

GAP: PostgreSQL/Docker were not available in the last DB checks, so this review remains file-backed for dataset rows and code-backed for pattern behavior.

## Changes Made In This Pass

1. Added bucket/context hardening in `scripts/live_scraper.py`.

   Detail pages remain primary, but discovery route labels now force obvious operation/property hints after parsing. This prevents rent/land pages from being reclassified by generic body text.

2. Added immediate source-publication status in `scripts/live_scraper.py`.

   New rows now persist `source_publication_type`, `scrape_status`, `scrape_acceptance_status`, and `single_entity_candidate` early enough for OpenClaw/importers to gate them before DB import.

3. Converted Address.bg discovery from ambiguous `search_urls` into labeled buckets.

   `sale_all`, `rent_all`, `sale_sofia`, `sale_varna`, and `rent_sofia` are now explicit source sections instead of anonymous URLs.

4. Hardened imot.bg route labels.

   Default imot.bg discovery routes now preserve `sale_<city>` or `rent_<city>` labels instead of only `grad-*`, reducing operation drift.

5. Hardened `scripts/action1_dataset_quality_gate.py`.

   The gate now honors already-persisted grouped/development status, marks inactive/removed/expired listing statuses as LOST, requires area for land as well as residential/commercial units, and supports `--limit-per-source` for bounded OpenClaw/debugger checks.

6. Hardened `scripts/generate_tier12_pattern_status.py`.

   Patterned proof can no longer be built from `LOST`, inactive, or grouped/development rows.

7. Hardened `scripts/import_scraped_listings.py`.

   Default import now skips inactive/removed/expired rows, with explicit `--include-inactive` override for investigation.

8. Hardened `scripts/generate_frontend_scraped_listings.py`.

   Public seed export excludes inactive/removed/expired rows in addition to `LOST` and grouped/development rows.

9. Added regression tests in `tests/test_action1_parser_regressions.py`.

   Tests now cover route-context correction and persisted grouped/inactive quality-gate handling.

## Source-By-Source Reliability Assessment

### Address.bg

Current depth:
- Source-specific parser extracts high-resolution `/storage/uploads/offers/.../1000x666/` gallery URLs.
- Discovery sections are now explicitly labeled.
- Identity is stable through `offer<id>` URLs and source reference IDs.

Remaining issue:
- Many saved rows still need media backfill before they can be accepted as fully scraped.
- Some rows still miss city/address because detail location can be embedded in title/breadcrumb rather than structured JSON-LD.

Required OpenClaw behavior:
- Reparse/refetch by offer code.
- Run full-gallery media backfill.
- Run Action1 quality gate after the batch.
- Do not import rows with `LOST`, `partial_local_gallery`, or `one_remote_photo_gallery_suspect`.

### BulgarianProperties

Current depth:
- Parser now prefers Product JSON-LD/body text over meta snippets for description.
- Gallery extraction restricts to listing `/big/` images and avoids recommendation-card images.
- Route buckets preserve sale/rent/land/apartment/house context.

Remaining issue:
- Partial local gallery evidence is still common.
- Development pages and price-from pages can still appear in search routes.
- Area values must be unit-level, not project-level.

Required OpenClaw behavior:
- Treat development pages as grouped publications unless unit-level URL/price/area/media evidence exists.
- Backfill `/big/` media locally and verify readable files.
- Keep grouped rows out of canonical import.

### Homes.bg

Current depth:
- Parser uses Homes offer JSON/preloaded state.
- Area extraction uses sqm-specific title/attribute values and avoids decimal-shift bugs.
- Route context now preserves rent/sale buckets.

Remaining issue:
- Some rows have incomplete local media and at least some URLs can become unavailable.

Required OpenClaw behavior:
- Check `listing_status`.
- Skip inactive/removed/expired rows by default.
- Download all photos from the offer payload.

### imot.bg

Current depth:
- Parser extracts detail params, title/location, phones, active markers, and `data-src-gallery`.
- Discovery filters out obvious residential-complex listing pages.
- Route labels now preserve `sale_<city>` / `rent_<city>` context.

Remaining issue:
- Some rows still miss area.
- Some accepted-looking rows can be inactive via page marker.
- Some multi-unit/development pages still require grouped handling.

Required OpenClaw behavior:
- Use route label for operation, detail params for fields, and inactive markers for lifecycle.
- Never convert map/search aggregate clusters or residential-building pages into single properties.

### LUXIMMO

Current depth:
- Parser uses dataLayer and source-specific static media domains.
- Area extraction prefers labeled unit fields and title area before broad values.
- Development pages are now separated via source-publication status.

Remaining issue:
- Missing area and missing description are the main residual blockers.

Required OpenClaw behavior:
- Preserve grouped pages as publications.
- Require unit-level area for accepted single candidates.
- Run description/body fallback before acceptance.

### property.bg

Current depth:
- Current file-backed corpus is clean under the latest quality gate.
- Parser shares property-family extraction with LUXIMMO/SUPRIMMO but keeps source domains separate.

Remaining issue:
- Clean current corpus does not equal full website coverage.
- Active status refresh is still needed during incremental runs.

Required OpenClaw behavior:
- Continue incremental refresh.
- Keep active-status and grouped-page checks enabled.

### SUPRIMMO

Current depth:
- Gallery capture is strong.
- Parser uses dataLayer/labeled fields.
- Grouped/development rows are separated.

Remaining issue:
- Missing area remains the primary LOST reason.
- Development pages need unit-level splitting only when evidence exists.

Required OpenClaw behavior:
- Require unit-level area.
- Keep grouped/development rows out of canonical single-property import.

## Consistency Rules Now Required Across The Pipeline

- Discovery route context must be saved as `source_section_id` and used only as a conservative hint.
- Detail-page parser output must remain primary for price, description, gallery, contacts, and area.
- Every row must carry `source_publication_type`.
- `LOST`, grouped/development, and inactive rows must be excluded by default from frontend and DB import.
- Pattern status must select only QA-eligible samples.
- OpenClaw should run bounded QA with `--limit-per-source` during checks and full QA after large batches.

## Commands Verified

- `python3 -m py_compile scripts/action1_dataset_quality_gate.py scripts/live_scraper.py scripts/generate_tier12_pattern_status.py scripts/generate_frontend_scraped_listings.py scripts/import_scraped_listings.py tests/test_action1_parser_regressions.py`
- `python3 -m unittest tests.test_action1_parser_regressions -v`
- `python3 scripts/action1_dataset_quality_gate.py --limit-per-source 20 --output docs/exports/action1-dataset-quality-gate-dryrun.json`
- `python3 scripts/import_scraped_listings.py --dry-run --source property_bg`
- `python3 scripts/import_scraped_listings.py --dry-run --limit 500`

## Runtime Notes

FACT: Full-corpus local scans were slow in this workspace and were manually stopped during this pass. Bounded QA was added specifically so OpenClaw/debugger can check behavior without blocking on the entire on-disk corpus.

INTERPRETATION: Full QA remains necessary after large scraping batches, but bounded QA is the correct default for acceptance smoke checks.
