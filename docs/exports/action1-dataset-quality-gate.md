# Action1 Dataset Quality Gate

Generated: 2026-05-13T13:37:40.127411+00:00

FACT: `LOST` means the row is quarantined as not properly scraped and queued for the next scraping session; the source URL and raw evidence are preserved.
FACT: `GROUPED_PUBLICATION` means the source page appears to describe a multi-unit/development publication, not one sellable/rentable entity.

## Source Summary

| Source | Items | SCRAPED_OK | LOST | GROUPED_PUBLICATION | Multi-unit/development | Top LOST reasons |
|---|---:|---:|---:|---:|---:|---|
| address_bg | 6473 | 3330 | 3143 | 0 | 0 | one_remote_photo_gallery_suspect:1677, missing_city_or_address:1262, suspicious_unit_area_too_large:306, partial_local_gallery:197, suspicious_house_area_too_large:156, missing_area:3, description_too_short:1 |
| bulgarianproperties | 2289 | 12 | 2277 | 0 | 323 | partial_local_gallery:2271, missing_area:510, suspicious_unit_area_too_large:116, suspicious_house_area_too_large:112, thin_title:1, missing_city_or_address:1 |
| homes_bg | 144 | 79 | 62 | 3 | 10 | partial_local_gallery:55, one_remote_photo_gallery_suspect:13, missing_remote_gallery:3, missing_description:1 |
| imot_bg | 9937 | 8986 | 264 | 687 | 692 | partial_local_gallery:209, missing_area:176, description_too_short:25, one_remote_photo_gallery_suspect:9, suspicious_unit_area_too_large:8, missing_description:1 |
| luximmo | 2512 | 1788 | 607 | 117 | 151 | missing_area:518, suspicious_unit_area_too_large:84, partial_local_gallery:4, one_remote_photo_gallery_suspect:1, suspicious_area_below_2sqm:1 |
| property_bg | 3094 | 3053 | 41 | 0 | 0 | suspicious_unit_area_too_large:25, description_too_short:9, suspicious_house_area_too_large:4, partial_local_gallery:3, missing_area:1 |
| suprimmo | 4948 | 3563 | 739 | 646 | 712 | missing_area:684, suspicious_unit_area_too_large:36, suspicious_house_area_too_large:15, partial_local_gallery:5, suspicious_area_below_2sqm:1 |

## Outputs

- `docs/exports/action1-lost-rescrape-queue.json`
- `docs/exports/action1-lost-rescrape-queue.csv`
- `docs/exports/action1-multi-unit-publications.json`
- `docs/exports/action1-dataset-quality-gate.json`

## Pattern Updates

- Address.bg: detail page gallery must use high-resolution `/storage/uploads/offers/.../1000x666/` anchors; one-photo rows are LOST unless source evidence proves only one image.
- BulgarianProperties: full description must come from Product JSON-LD/body text, not the short meta snippet; gallery must use listing `/big/` images and exclude recommendations.
- Homes.bg: parse offer JSON and sqm-specific area, not the first number in title text.
- imot.bg: parse detail `data-src-gallery`, `.adParams`, title/location, and active/inactive markers; one-photo and missing-price rows go to the rescrape queue.
- LUXIMMO/property.bg/SUPRIMMO: use dataLayer plus labeled unit fields and classify development pages separately from single units.
