# Action1 Source Identification Methods

Generated: 2026-05-01

FACT: A saved row is a source publication first. It is accepted as one property entity only when the detail page represents one unit with one stable URL, one identity, one price or explicit price-status provenance, one area where applicable, and detail-page media evidence.

## Address.bg

- Stable identity: prefer offer code from URL/title, e.g. `offer688648` / `код на имота: 688648`; fallback to canonical detail URL hash.
- Active URL check: HTTP 200 plus no removed/unavailable marker. Sample checked rows mostly existed, but gallery completeness failed.
- Single-entity acceptance: one offer code, one property type, one price, one usable area; reject pages with development/unit-choice language.
- Current issue: many rows have one remote photo or partial local gallery after parser repair. Marked `LOST` until detail refetch/backfill downloads every `/storage/uploads/offers/.../1000x666/` image.
- Next scrape method: detail-first media backfill by offer code; parse all high-resolution anchors, preserve order, verify local readable files before accepting.

## BulgarianProperties

- Stable identity: prefer source ref number / canonical listing path; fallback to canonical URL hash.
- Active URL check: HTTP 200 plus detail page is a current listing, not search/recommendation content.
- Single-entity acceptance: reject `prices from`, `various types`, development/building pages unless a unit-level URL, price, area, and media set exists.
- Current issue: almost all rows have incomplete local galleries; many development-style pages and missing/suspicious area fields.
- Next scrape method: use detail JSON-LD/body content for full description, extract only listing `/big/` gallery images, and split development pages only when unit rows are explicitly exposed.

## Homes.bg

- Stable identity: prefer Homes offer id from URL/API payload (`as1670331` style); fallback to canonical URL hash.
- Active URL check: HTTP 200 for detail or API item; 404/removed rows are `LOST`.
- Single-entity acceptance: API/detail payload must expose one status-active offer, one operation, one price, one area, and gallery list.
- Current issue: several rows have partial local galleries and one checked detail returned 404.
- Next scrape method: use the offer JSON payload as primary truth, confirm active status before saving, then download all payload gallery images.

## imot.bg

- Stable identity: prefer imot ad id from URL/detail; fallback to canonical URL hash when ad id is absent.
- Active URL check: reject HTTP 404 and detail pages with inactive/removed markers even if they return HTTP 200.
- Single-entity acceptance: one ad URL, one operation, one price or explicit status, one area where applicable; grouped/development language goes to `GROUPED_PUBLICATION`.
- Current issue: generally strongest corpus, but partial local galleries, one-photo gallery suspects, missing area rows, and inactive URLs were detected.
- Next scrape method: parse detail `data-src-gallery`, `.adParams`, title/location blocks, and inactive markers in one pass; never accept map/search aggregate clusters as properties.

## LUXIMMO

- Stable identity: prefer dataLayer/listing reference from detail page; fallback to canonical URL hash.
- Active URL check: HTTP 200 plus current property detail template, not listing/category/development landing page.
- Single-entity acceptance: one advertised unit; development pages with price-from/multiple-unit copy are grouped unless a unit-level record exists.
- Current issue: missing area and missing description rows remain; some development pages are now separated from single candidates.
- Next scrape method: use dataLayer plus labeled detail fields; extract description/body fallback and retain development pages as source publications, not canonical single properties.

## property.bg

- Stable identity: prefer portal listing id/reference from URL/detail; fallback to canonical URL hash.
- Active URL check: HTTP 200 current detail.
- Single-entity acceptance: current sample passes the QA gate with local gallery completeness.
- Current issue: no LOST rows in the current file-backed corpus; keep monitoring grouped/development language.
- Next scrape method: keep current dataLayer/labeled-field extraction and add live active-status refresh during incremental runs.

## SUPRIMMO

- Stable identity: prefer SUPRIMMO reference/listing id from dataLayer/detail page; fallback to canonical URL hash.
- Active URL check: HTTP 200 plus property detail template; unknown network errors are warnings, not automatic LOST.
- Single-entity acceptance: one unit only; development/multi-unit pages are `GROUPED_PUBLICATION`.
- Current issue: missing-area rows and grouped/development pages were separated; one URL-check network error needs recheck.
- Next scrape method: use dataLayer/labeled fields for single units, require area for residential/commercial units, and keep development pages out of canonical single-property import.

## Import Rule

Default DB import and frontend export now exclude `LOST` and `multi_unit_or_development` rows. Operators may include them only with explicit flags for investigation, not production canonicalization.
