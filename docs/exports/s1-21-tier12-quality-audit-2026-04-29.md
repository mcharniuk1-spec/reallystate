# S1-21 Tier-1/2 Scrape Quality Audit

Generated: 2026-05-01T10:55:22.457877+00:00

FACT: This is an offline file-backed audit. It does not prove new live scraping or PostgreSQL `canonical_listing` counts.

## Source Summary

| Source | Items | Accepted single | LOST | Grouped | Desc | Thin desc | Price | Zero price | Area | Area suspect | City/address | Remote photos | Valid local files | One-photo remote | One-photo local | Geo points | Outside-BG geo | Full galleries | Complete local galleries | Action0 eligible | Same-location items | Multi-unit suspects | Top gaps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Address.bg | 5203 | 0 | 5203 | 0 | 5203 | 19 | 5191 | 0 | 5195 | 0 | 4131 | 23074 | 5173 | 3339 | 5121 | 0 | 0 | 3283 | 3283 | 0 | 0 | 0 | lost_rescrape_required:5203, missing_image_report:5203, no_strong_location_group_key:5203, one_remote_photo_gallery_suspect:3339, partial_or_missing_local_gallery:1920, missing_city_or_address:1072, thin_description:19, missing_price:12, missing_area:8 |
| BulgarianProperties | 1616 | 4 | 1612 | 279 | 1616 | 0 | 1603 | 0 | 1220 | 0 | 1616 | 46859 | 41976 | 0 | 14 | 0 | 0 | 7 | 7 | 4 | 0 | 429 | missing_image_report:1616, no_strong_location_group_key:1616, lost_rescrape_required:1612, partial_or_missing_local_gallery:1609, suspected_multi_unit_publication:429, missing_area:396, grouped_publication_not_single_entity:279, missing_price:13 |
| Homes.bg | 132 | 63 | 67 | 10 | 131 | 0 | 132 | 0 | 132 | 0 | 132 | 981 | 603 | 13 | 21 | 9 | 0 | 69 | 69 | 63 | 26 | 12 | missing_image_report:132, no_strong_location_group_key:102, lost_rescrape_required:67, partial_or_missing_local_gallery:60, one_remote_photo_gallery_suspect:13, suspected_multi_unit_publication:12, grouped_publication_not_single_entity:10, missing_description:1 |
| imot.bg | 8534 | 7561 | 383 | 603 | 8533 | 189 | 8226 | 0 | 8356 | 0 | 8534 | 86503 | 85676 | 134 | 2 | 0 | 0 | 8314 | 8295 | 7448 | 7527 | 953 | missing_image_report:8534, suspected_multi_unit_publication:953, grouped_publication_not_single_entity:603, lost_rescrape_required:383, missing_price:308, partial_or_missing_local_gallery:239, no_strong_location_group_key:191, thin_description:189, missing_area:178, one_remote_photo_gallery_suspect:134 |
| LUXIMMO | 2143 | 1619 | 430 | 105 | 2087 | 23 | 2102 | 0 | 1809 | 0 | 2143 | 15547 | 18425 | 0 | 0 | 0 | 0 | 2139 | 2139 | 1607 | 0 | 260 | missing_image_report:2143, no_strong_location_group_key:2143, lost_rescrape_required:430, missing_area:334, suspected_multi_unit_publication:260, grouped_publication_not_single_entity:105, missing_description:56, missing_price:41, thin_description:23, partial_or_missing_local_gallery:4 |
| property.bg | 297 | 297 | 0 | 0 | 297 | 195 | 289 | 0 | 297 | 0 | 297 | 17908 | 17908 | 0 | 0 | 0 | 0 | 297 | 297 | 289 | 0 | 6 | missing_image_report:297, no_strong_location_group_key:297, thin_description:195, missing_price:8, suspected_multi_unit_publication:6 |
| SUPRIMMO | 297 | 219 | 39 | 42 | 297 | 2 | 285 | 0 | 259 | 0 | 297 | 22987 | 22987 | 0 | 0 | 0 | 0 | 297 | 297 | 209 | 0 | 47 | missing_image_report:297, no_strong_location_group_key:297, suspected_multi_unit_publication:47, grouped_publication_not_single_entity:42, lost_rescrape_required:39, missing_area:38, missing_price:12, thin_description:2 |

## Action Sequence

0. **Action0 - image-by-image property report**: use `docs/exports/s1-21-gemma-action0-eligible.json`; describe every local image, then produce one whole-property visual/QA description.
1. **Action1 - full scrape/backfill seven priority sources**: run the all-Bulgaria/full-gallery scrape or backfill for `Address.bg`, `BulgarianProperties`, `Homes.bg`, `imot.bg`, `LUXIMMO`, `property.bg`, and `SUPRIMMO` across buy residential, buy commercial, rent residential, and rent commercial.
2. **Action2 - remaining sources**: after Action1, widen to the rest of the legal tier-1/2 source set and repeat Action0 reporting for newly complete local galleries.

## Same-Location Grouping

Same-location grouping is intentionally based on useful `address_text` plus city/district. It excludes city-only or district-only labels, so the website Aggregate filter does not group whole districts as duplicate properties.

## Property Identity Rules

- A saved row is one source publication. It becomes one property item only when the source page clearly advertises one unit with its own price or explicit on-request/undefined price state.
- Multi-unit publications such as `1-2 bedroom`, `apartments (various types)`, whole residential buildings, or price-from development pages must be flagged as `suspected_multi_unit_publication` and split into unit rows only when the source exposes unit-level price/area/URL evidence.
- Numeric `0` must not be treated as a real price. Store no numeric price and preserve `price_status = on_request` or `price_status = undefined` in provenance until the schema has a first-class field.
- Suspicious areas below 2 sqm indicate parser decimal mistakes and must not pass publishing QA.
- Any saved coordinate outside Bulgaria bounds (lat 41.0-44.5, lon 22.0-29.5) is a hard geospatial QA failure.
- One-photo rows are only accepted when the source detail page truly exposes one gallery image; otherwise they indicate gallery-pattern or media-backfill failure.

- Same-location groups found: 522
- Action0 eligible rows: 9620
- Item gaps sampled in JSON: 500

## Outputs

- `docs/exports/s1-21-tier12-quality-audit-2026-04-29.json`
- `docs/exports/s1-21-gemma-action0-eligible.json`
- `docs/exports/s1-21-tier12-quality-audit-2026-04-29.md`
