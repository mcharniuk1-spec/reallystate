# Property Identity Anomaly Audit

Generated: 2026-04-29

FACT: This audit uses the current website seed at `public/data/scraped-listings.json` and is file-backed, not PostgreSQL-backed.

## Corpus Summary

Total website listings: 1,549.

| Source | Items | Multi-unit suspects | Price 0 | Price missing | Area < 2 sqm | Area missing |
|---|---:|---:|---:|---:|---:|---:|
| BulgarianProperties | 249 | 55 | 0 | 1 | 0 | 64 |
| OLX.bg | 249 | 18 | 0 | 0 | 0 | 107 |
| Yavlena | 251 | 14 | 13 | 0 | 0 | 0 |
| Homes.bg | 97 | 7 | 0 | 37 | 60 | 37 |
| Bazar.bg | 250 | 6 | 3 | 0 | 0 | 0 |
| imot.bg | 271 | 2 | 0 | 262 | 0 | 262 |
| LUXIMMO | 15 | 2 | 0 | 2 | 0 | 2 |
| property.bg | 15 | 0 | 0 | 3 | 0 | 0 |
| SUPRIMMO | 12 | 0 | 0 | 3 | 0 | 0 |
| Address.bg | 140 | 0 | 0 | 0 | 0 | 0 |

## Findings

FACT: BulgarianProperties has the highest number of likely mixed/development pages. The strongest signals are `Apartments_(various_types)` URLs, residential-building titles, development pages, and price-from/selection wording.

FACT: Homes.bg has 60 area values below 2 sqm, for example `85m²` parsed as `0.85`. This is a parser decimal/locale issue, not real floor area.

FACT: Yavlena and Bazar.bg contain numeric `0` prices. These must not be treated as real property prices; they need `on_request` or `undefined` status in provenance.

FACT: imot.bg currently has 262/271 rows missing price and area in the website seed. The detail parser still needs repair before these rows are publishable.

INTERPRETATION: A source publication is not always one sellable/rentable unit. Mixed inventory pages can still be useful as source evidence, but should not become a single canonical property item unless a unit-level URL, price, area, and media set exist.

HYPOTHESIS: The highest-risk live-source patterns are `BulgarianProperties` development pages, `Homes.bg` area parsing, `imot.bg` detail extraction, and `Yavlena` price-status handling.

GAP: This audit flags text/URL patterns only. It does not fetch live pages to inspect whether unit-level tables are available.

## Required Pattern Updates

- Add `suspected_multi_unit_publication` detection to every scraper result before canonical import.
- Split mixed/development pages only when the source exposes unit-level URL, price, area, and media evidence.
- Preserve mixed pages as grouped/development source publications when unit-level evidence is unavailable.
- Never serialize numeric `0` as a real price. Use `price = null` and provenance `price_status = on_request` or `price_status = undefined`.
- Quarantine area values below 2 sqm for apartment/house/office listings unless the source explicitly proves them.
- Include these checks in publisher eligibility before any reverse-publishing or canonical-property display.

