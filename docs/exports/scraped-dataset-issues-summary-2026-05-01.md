# Scraped Dataset Issues Summary By Source

Generated: 2026-05-01

Scope: Action1 seven-source file-backed scraped dataset after the debugger quality gate.

## Executive Summary

FACT: `7734` rows were marked `LOST`. These rows are treated as not properly scraped and are queued for the next scraping session.

FACT: `1039` rows were classified as grouped/development source publications. These are not one sellable/rentable property entity unless the source exposes unit-level URL, price, area, and media evidence.

FACT: default frontend export and default DB import now exclude `LOST` rows and grouped/development publications.

INTERPRETATION: the main quality issue is not only missing text. The dominant failure class is incomplete full-gallery/local-media proof, especially for Address.bg and BulgarianProperties.

GAP: PostgreSQL/Docker were unavailable during the run, so this document summarizes file-backed JSON evidence, not a direct canonical database audit.

## Status Definitions

- `SCRAPED_OK`: row currently passes the file-backed single-entity quality gate.
- `LOST`: row is quarantined as wrongly or incompletely scraped and must be rescraped/backfilled before production use.
- `GROUPED_PUBLICATION`: row appears to represent a multi-unit/development publication, not one property entity.
- `multi_unit_or_development`: publication type marker used to keep grouped pages out of canonical single-property import.

## Source Summary Table

| Source | Saved rows | Accepted single candidates | LOST rows | Grouped/development rows | Main reason |
|---|---:|---:|---:|---:|---|
| Address.bg | 5203 | 0 | 5203 | 0 | one-photo/gallery and local-gallery incompleteness |
| BulgarianProperties | 1616 | 4 | 1612 | 279 | partial local galleries, missing/suspicious area, development pages |
| Homes.bg | 132 | 63 | 67 | 10 | partial galleries, one-photo suspects, one unavailable URL |
| imot.bg | 8534 | 7561 | 383 | 603 | partial galleries, missing area, one-photo suspects, inactive URLs |
| LUXIMMO | 2143 | 1619 | 430 | 105 | missing area, missing description, development pages |
| property.bg | 297 | 297 | 0 | 0 | no current LOST rows in file-backed QA |
| SUPRIMMO | 297 | 219 | 39 | 42 | missing area and grouped/development pages |

## Address.bg

FACT:
- `5203` saved rows.
- `5203` rows marked `LOST`.
- `0` accepted single candidates after strict full-gallery QA.
- Main LOST reasons: `one_remote_photo_gallery_suspect:3339`, `partial_local_gallery:1920`, `missing_city_or_address:1072`, `suspicious_unit_area_too_large:205`, `suspicious_house_area_too_large:112`, `missing_area:8`.
- LOST rows reference `23074` remote photos but only `5173` local photo files.

INTERPRETATION:
- The parser/detail evidence is not production-safe because many rows look like they captured only a teaser/OG image or incomplete local media.
- Address.bg likely needs media backfill more than list-page rediscovery.

NEXT ACTION:
- Refetch detail pages by offer code.
- Extract all high-resolution `/storage/uploads/offers/.../1000x666/` gallery images.
- Preserve image order and verify every local file is readable before removing `LOST`.
- Improve city/address extraction for rows where location exists in title but not structured fields.

## BulgarianProperties

FACT:
- `1616` saved rows.
- `4` accepted single candidates.
- `1612` rows marked `LOST`.
- `279` rows classified as grouped/development.
- Main LOST reasons: `partial_local_gallery:1609`, `missing_area:379`, `suspicious_unit_area_too_large:92`, `suspicious_house_area_too_large:65`, `thin_title:1`.
- LOST rows reference `46666` remote photos and `41722` local photo files.

INTERPRETATION:
- The source has many photos, but local gallery completeness is still below strict acceptance for most rows.
- Some rows are development or multi-unit pages and must not become single canonical properties.
- Missing/suspicious area indicates the parser must prefer unit-level labeled fields and avoid development-wide totals.

NEXT ACTION:
- Use detail JSON-LD/body content for full description.
- Extract only the listing gallery `/big/` images and exclude recommendations.
- Split development pages only where unit-level URL, price, area, and media evidence exists.
- Keep grouped pages as source publications, not canonical single properties.

## Homes.bg

FACT:
- `132` saved rows.
- `63` accepted single candidates.
- `67` rows marked `LOST`.
- `10` rows classified as grouped/development.
- Main LOST reasons: `partial_local_gallery:60`, `one_remote_photo_gallery_suspect:13`, `missing_remote_gallery:3`, `source_url_not_available:1`, `missing_description:1`.
- LOST rows reference `424` remote photos and only `28` local photo files.

INTERPRETATION:
- The parser can produce valid rows, but media download/backfill is incomplete for a large share of saved rows.
- At least one checked URL is no longer available and must remain `LOST`.

NEXT ACTION:
- Use Homes offer JSON/API payload as primary truth.
- Check active status before saving.
- Download all payload gallery images.
- Keep unavailable URLs in the LOST queue with source-url evidence.

## imot.bg

FACT:
- `8534` saved rows.
- `7561` accepted single candidates.
- `383` rows marked `LOST`.
- `603` rows classified as grouped/development.
- Main LOST reasons: `partial_local_gallery:220`, `missing_area:178`, `one_remote_photo_gallery_suspect:134`, `description_too_short:21`, `suspicious_unit_area_too_large:7`, `source_url_not_available:2`, `missing_description:1`.
- LOST rows reference `3109` remote photos and `1128` local photo files.

INTERPRETATION:
- imot.bg is the strongest Action1 corpus by accepted single-property volume.
- Remaining defects are concentrated in gallery backfill, area extraction, thin descriptions, and inactive/removed detail URLs.
- The grouped/development set must stay separate from one-property records.

NEXT ACTION:
- Parse detail `data-src-gallery`, `.adParams`, title/location blocks, and active/inactive markers in one pass.
- Treat HTTP 404 and inactive marker pages as `LOST`.
- Require unit-level price/area/URL/media evidence before promoting multi-unit pages.

## LUXIMMO

FACT:
- `2143` saved rows.
- `1619` accepted single candidates.
- `430` rows marked `LOST`.
- `105` rows classified as grouped/development.
- Main LOST reasons: `missing_area:334`, `missing_description:56`, `suspicious_unit_area_too_large:54`, `partial_local_gallery:4`.
- LOST rows reference `3588` remote photos and `4221` local photo files.

INTERPRETATION:
- Media is less problematic than commercial/structured field extraction.
- Missing area and missing description are the main blockers.
- Some pages describe development inventory and should stay grouped.

NEXT ACTION:
- Use dataLayer plus labeled detail fields.
- Prefer explicit unit area labels over project/land totals.
- Add description/body fallback where structured description is absent.
- Keep development pages out of canonical single-property import.

## property.bg

FACT:
- `297` saved rows.
- `297` accepted single candidates.
- `0` rows marked `LOST`.
- `0` grouped/development rows in the current file-backed QA.

INTERPRETATION:
- property.bg currently has the cleanest Action1 evidence set under this quality gate.
- This does not prove full website coverage; it only means current saved rows passed the file-backed QA rules.

NEXT ACTION:
- Keep current labeled-field and gallery extraction.
- Add active-status refresh in incremental runs.
- Continue monitoring for development-page language and grouped inventory.

## SUPRIMMO

FACT:
- `297` saved rows.
- `219` accepted single candidates.
- `39` rows marked `LOST`.
- `42` rows classified as grouped/development.
- Main LOST reasons: `missing_area:38`, `suspicious_house_area_too_large:1`.
- LOST rows reference `3003` remote photos and `3003` local photo files.

INTERPRETATION:
- Gallery capture is strong, but area semantics and grouped/development classification need stricter handling.
- Missing area blocks single-property acceptance for residential/commercial units.

NEXT ACTION:
- Use dataLayer/labeled fields for unit-level area.
- Keep development pages as source publications unless unit-level rows are exposed.
- Recheck the one unknown URL-check/network-error row in the next live pass.

## Cross-Source Root Causes

1. Generic gallery fallback captured OG/lead images instead of the full detail gallery.
2. Local media backfill did not always download every remote gallery image.
3. Development and multi-unit pages were previously too easy to treat as single properties.
4. Area extraction sometimes selected the wrong numeric value or project-wide total.
5. Some rows had missing/thin description because parsers used meta snippets instead of detail body/JSON-LD.
6. Active URL checks found a small number of unavailable or inactive pages that must not remain accepted.

## Required Next Scraping Session Behavior

- Start with `LOST` queue backfill, not broad rediscovery.
- Refetch each LOST detail URL and re-extract detail body, structured fields, active status, and full gallery.
- Download all reachable photos as local files under `data/media/<reference_id>/`.
- Preserve remote image URLs only as provenance.
- Reclassify every page as `single_unit_candidate` or `multi_unit_or_development`.
- Only clear `LOST` when core fields and full local gallery proof pass source-specific rules.
- Do not import or expose `LOST` or grouped/development rows by default.

## Related Artifacts

- `docs/exports/action1-dataset-quality-gate.md`
- `docs/exports/action1-dataset-quality-gate.json`
- `docs/exports/action1-lost-rescrape-queue.csv`
- `docs/exports/action1-lost-rescrape-queue.json`
- `docs/exports/action1-multi-unit-publications.json`
- `docs/exports/action1-source-identification-methods-2026-05-01.md`
- `docs/dashboard/scrape-status.html`
