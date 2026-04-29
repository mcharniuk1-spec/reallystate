# S1-21 Tier-1/2 Scrape Quality Audit

Generated: 2026-04-29T07:54:58.544006+00:00

FACT: This is an offline file-backed audit. It does not prove new live scraping or PostgreSQL `canonical_listing` counts.

## Source Summary

| Source | Items | Desc | Thin desc | Price | Area | City/address | Remote photos | Valid local files | Full galleries | Complete local galleries | Action0 eligible | Same-location items | Top gaps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Address.bg | 140 | 140 | 0 | 140 | 140 | 98 | 140 | 141 | 140 | 140 | 140 | 0 | missing_image_report:140, no_strong_location_group_key:140, missing_city_or_address:42 |
| BulgarianProperties | 249 | 249 | 248 | 248 | 185 | 249 | 8114 | 286 | 1 | 1 | 185 | 0 | missing_image_report:249, no_strong_location_group_key:249, thin_description:248, partial_or_missing_local_gallery:248, missing_area:64, missing_price:1 |
| Homes.bg | 97 | 97 | 0 | 60 | 60 | 60 | 489 | 304 | 32 | 52 | 32 | 2 | missing_image_report:97, no_strong_location_group_key:83, partial_or_missing_local_gallery:43, missing_price:37, missing_area:37, missing_city_or_address:37 |
| imot.bg | 271 | 271 | 25 | 9 | 9 | 271 | 3191 | 147 | 14 | 14 | 9 | 2 | missing_image_report:271, missing_price:262, missing_area:262, no_strong_location_group_key:262, partial_or_missing_local_gallery:257, thin_description:25 |
| LUXIMMO | 15 | 12 | 0 | 13 | 13 | 15 | 114 | 128 | 13 | 13 | 10 | 0 | missing_image_report:15, no_strong_location_group_key:15, missing_description:3, missing_price:2, partial_or_missing_local_gallery:2, missing_area:2 |
| property.bg | 15 | 15 | 5 | 12 | 15 | 15 | 1341 | 101 | 1 | 1 | 12 | 0 | missing_image_report:15, no_strong_location_group_key:15, partial_or_missing_local_gallery:14, thin_description:5, missing_price:3 |
| SUPRIMMO | 12 | 12 | 0 | 9 | 12 | 12 | 1095 | 166 | 1 | 1 | 9 | 0 | missing_image_report:12, no_strong_location_group_key:12, partial_or_missing_local_gallery:11, missing_price:3 |

## Action Sequence

0. **Action0 - image-by-image property report**: use `docs/exports/s1-21-gemma-action0-eligible.json`; describe every local image, then produce one whole-property visual/QA description.
1. **Action1 - full scrape/backfill seven priority sources**: run the all-Bulgaria/full-gallery scrape or backfill for `Address.bg`, `BulgarianProperties`, `Homes.bg`, `imot.bg`, `LUXIMMO`, `property.bg`, and `SUPRIMMO` across buy residential, buy commercial, rent residential, and rent commercial.
2. **Action2 - remaining sources**: after Action1, widen to the rest of the legal tier-1/2 source set and repeat Action0 reporting for newly complete local galleries.

## Same-Location Grouping

Same-location grouping is intentionally based on useful `address_text` plus city/district. It excludes city-only or district-only labels, so the website Aggregate filter does not group whole districts as duplicate properties.

- Same-location groups found: 2
- Action0 eligible rows: 397
- Item gaps sampled in JSON: 500

## Outputs

- `docs/exports/s1-21-tier12-quality-audit-2026-04-29.json`
- `docs/exports/s1-21-gemma-action0-eligible.json`
- `docs/exports/s1-21-tier12-quality-audit-2026-04-29.md`
