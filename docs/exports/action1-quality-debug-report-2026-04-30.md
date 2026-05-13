# Action1 Seven-Source Scrape Quality Debug Report

Generated: 2026-04-30T21:39:17.827952

## Scope

FACT: This report covers the Action1 source group: Address.bg, BulgarianProperties, Homes.bg, imot.bg, LUXIMMO, property.bg, SUPRIMMO.
FACT: The repair was file-backed/offline: local raw HTML was reparsed; no live crawl was launched by this debugger run.
GAP: PostgreSQL/Docker were unavailable locally, so DB table checks could not run; file-backed JSON corpus and frontend fallback data were checked.

## Root Causes Found

| Issue | Sources | Cause | Fix Applied | Remaining Work |
|---|---|---|---|---|
| Single-photo rows although detail page had gallery | Address.bg primarily; smaller Homes/imot true/needs review | Parser retained OG/list teaser image instead of Address.bg detail gallery anchors | Added Address.bg gallery extraction from `/storage/uploads/offers/.../1000x666/` and offline-reparsed 4,718 rows | Run media backfill to download newly discovered remote images locally |
| Thin/wrong descriptions | BulgarianProperties primarily | Parser kept meta/list snippet instead of full JSON-LD/body description | Added longest full-description selection and offline-reparsed 1,616 rows | Some sources still have naturally short descriptions; keep per-source QA flag |
| Area decimal shift | Homes.bg | Generic `_parse_number(title)` parsed `Четиристаен, 165m²` as `0.165` | Homes now extracts area only from sqm-specific title/attribute patterns; 132 rows reparsed | None for this class; test added |
| Project/complex land area saved as unit area | SUPRIMMO/property-family sources | Parser picked global max/first area from full HTML, including complex land totals like 200,000 sqm | Property-family parser now prefers labeled unit fields such as `РЗП`, `ЗП`, `Обща площ`, then title sqm; raw max kept in source attributes | Development/multi-unit pages still require operator review, not canonical unit promotion |
| Outside-Bulgaria map suspicion | Map/API layer; not proven in file-backed Action1 JSON | Saved Action1 JSON has no outside-Bulgaria coordinates; screenshot likely came from DB/API data, geocoder, or frontend marker price outside current fallback sample | Added conservative Bulgaria polygon rejection/swap handling for parsed coordinates and audit flag | DB unavailable; rerun SQL gate when Postgres is up |

## Offline Reparse Result

| Source | Scanned | Updated | Unchanged | Missing raw | Parse failed |
|---|---:|---:|---:|---:|---:|
| address_bg | 4718 | 4530 | 188 | 0 | 0 |
| bulgarianproperties | 1616 | 1616 | 0 | 0 | 0 |
| homes_bg | 132 | 132 | 0 | 0 | 0 |
| imot_bg | 8298 | 2005 | 6293 | 0 | 0 |
| luximmo | 1732 | 540 | 1192 | 0 | 0 |
| property_bg | 297 | 25 | 272 | 0 | 0 |
| suprimmo | 297 | 72 | 225 | 0 | 0 |

## Post-Repair Quality Snapshot

| Source | Items | Desc | Thin desc | Remote photos | Valid local files | Full local galleries | One remote photo | One local photo | Geo | Outside-BG geo | Area suspects | Multi-unit suspects |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| address_bg | 4718 | 4718 | 19 | 35976 | 4698 | 1070 | 1116 | 4646 | 0 | 0 | 0 | 0 |
| bulgarianproperties | 1616 | 1616 | 0 | 46859 | 41976 | 7 | 0 | 14 | 0 | 0 | 0 | 429 |
| homes_bg | 132 | 131 | 0 | 981 | 603 | 69 | 13 | 21 | 9 | 0 | 0 | 12 |
| imot_bg | 8323 | 8322 | 184 | 84083 | 83532 | 8084 | 139 | 2 | 0 | 0 | 0 | 948 |
| luximmo | 1732 | 1732 | 53 | 11989 | 13930 | 1730 | 0 | 0 | 0 | 0 | 0 | 208 |
| property_bg | 297 | 297 | 195 | 17908 | 17908 | 297 | 0 | 0 | 0 | 0 | 0 | 6 |
| suprimmo | 297 | 297 | 2 | 22987 | 22987 | 297 | 0 | 0 | 0 | 0 | 0 | 47 |

## Media Backfill Dry-Run

FACT: Remote gallery references are now larger after parser repair, especially Address.bg. These images are not all local files yet.

| Source | Listings | Missing local images before backfill |
|---|---:|---:|
| Address.bg | 4718 | 31078 |
| BulgarianProperties | 1616 | 5027 |
| Homes.bg | 132 | 396 |
| LUXIMMO | 1732 | 2 |
| SUPRIMMO | 297 | 0 |
| imot.bg | 8330 | 2115 |
| property.bg | 297 | 0 |

## Acceptance Gate

FACT: Parser regression tests passed for Address.bg gallery, BulgarianProperties description, Homes.bg area, SUPRIMMO unit area, and outside-Bulgaria coordinate rejection.
FACT: Dashboard and frontend scraped-listing fallback artifacts were regenerated.
FACT: A DB follow-up gate was added at `sql/helpers/03_action1_quality_gate.sql` for source totals, coarse geospatial failures, border-spillover suspects, and content-quality failures.
INTERPRETATION: Patterns are materially safer for the seven Action1 sources, but local-media completion is not done for Address.bg/BulgarianProperties/Homes/imot because the run intentionally did not download tens of thousands of images.
HYPOTHESIS: The screenshot marker outside Bulgaria is not caused by the current file-backed Action1 JSON lat/lon; it likely comes from live DB/API rows or geocoding.
GAP: PostgreSQL was not reachable and Docker daemon was down, so the canonical_listing/source_listing SQL geospatial gate must be rerun once services are available.
