# Tier-1/2 Four-Bucket Pattern Handoff

Date: 2026-04-28
Updated: 2026-04-29 with S1-21 Action0/Action1/Action2 execution order

## Scope

Priority sources:

- Address.bg
- BulgarianProperties
- Homes.bg
- imot.bg
- LUXIMMO
- property.bg
- SUPRIMMO

Required screen buckets:

- Buy residential -> `buy_personal`
- Buy commercial -> `buy_commercial`
- Rent residential -> `rent_personal`
- Rent commercial -> `rent_commercial`

## Approach

FACT: All seven sources are legally allowed tier-1 sources in `data/source_registry.json`.

FACT: `src/bgrealestate/scraping/section_catalog.py` now contains non-empty supported bucket definitions for all four segment keys for each priority source.

INTERPRETATION: Several portals do not expose stable public URLs that perfectly isolate commercial from residential. For those sources, the reliable pattern is shared discovery plus strict card/detail classification before accepting a row into a bucket.

GAP: Route reachability was not live-network verified in this pass. The next live scrape must treat each route as a controlled-crawl entrypoint and record HTTP/runtime failures per source/segment.

## Gemma4 / OpenClaw Task

Read:

- `docs/exports/taskforgema.md`
- `docs/exports/property-quality-and-building-contract.md`
- `docs/exports/source-item-photo-coverage.json`
- `data/scrape_patterns/regions/varna/sections.json`
- `data/scraped/*/listings/*.json`

Do:

0. **Action0 first**: read `docs/exports/s1-21-gemma-action0-eligible.json` and create one property image/QA report per eligible row from local images only.
1. **Action1 second**: run the all-Bulgaria scrape/backfill for the seven sources above across all four buckets only under operator-approved live runtime.
2. **Action2 third**: after Action1 QA, continue to the remaining legal tier-1/2 sources in `data/source_registry.json`.
3. For every accepted listing, save full text, structured fields, all remote image URLs, all local images, source URL, source bucket, and category validation evidence.
4. Create image-description reports from local files only.
5. For residential listings, describe style, layout, rooms, colors, materials, visible tools/equipment, condition, requirements, and risks.
6. For commercial listings, describe commercial type, access/frontage, workspace or sales-floor layout, storage/service areas, fit-out condition, colors/materials, visible equipment/tools, and operational suitability.
7. Run or replicate the property-quality contract before marking a report complete.
8. Preserve the same-location grouping contract: group rows only when useful address text plus city/district match; do not aggregate city-only or district-only placeholders.

## Acceptance

- Each of the seven sources has a row in all four bucket columns in the source-link dashboard.
- Every processed listing has source bucket, category evidence, photo counts, full-gallery status, and image-report status.
- Every Action0 eligible row has a report or documented skip reason.
- Dashboard artifacts are regenerated after the run.
