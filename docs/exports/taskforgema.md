# Task For Gemma4 / OpenClaw: Full Bulgaria Tier-1/2 Scrape With Complete Galleries

Generated: 2026-04-24
Updated: 2026-04-29 after S1-21 file-backed quality audit, same-location grouping contract, and Action0/Action1/Action2 sequencing

## Objective

Run the Bulgaria Real Estate tier-1/2 scraper to completion for **all Bulgaria**, not only Varna, across all legally allowed, patterned sources and supported buy/rent segments. Save every accepted property with full text, structured fields, source provenance, and all reachable photos as local files.

## Authoritative Action Order

Run the work in this order. Do not swap Action1 before Action0 unless the operator explicitly says to skip existing local-gallery enrichment.

## Operator Command Contract

When the operator asks for an action, execute exactly that action:

- **`Action0`** means: produce image-description and property-QA reports from the already-downloaded local-gallery eligible set. Do not scrape.
- **`Action1`** means: scrape/backfill only the seven priority all-Bulgaria sources across the four screen buckets.
- **`Action2`** means: after Action1 QA, expand to remaining legal tier-1/2 sources.

If the operator says only “continue Gemma/OpenClaw” and no action is named, follow the **Operator acceptance gate** below instead of assuming Action0 first.

### Operator acceptance gate (2026-04-30) — OpenClaw + Telegram cadence

1. **Single prompt context**: every OpenClaw/Gemma4 activation must load **Action0 + Action1 + Action2** contracts from this file so the model never claims it is “waiting for URLs/patterns”.
2. **Start execution only after `Action1 ACCEPT`**: until the operator sends **`Action1 ACCEPT`** in Telegram (or the exact same string in the operator message), OpenClaw must **not** run shell commands that mutate `data/scraped/`, `data/media/`, or live scrape flags — and must **not** start Action0 or Action2 file writes.
3. **After `Action1 ACCEPT`**: execute **Action1 (`S1-22B`)** via `make scrape-all-full` (detached/`nohup` per operator host rules), refresh dashboards on milestones.
4. **Telegram progress**: after every **+100 net new saved listing JSON files** across the seven Action1 sources, send one Telegram message containing:
   - one **markdown table or bullet block**: **7 sources × 4 buckets** (`buy_personal`, `buy_commercial`, `rent_personal`, `rent_commercial`) with **saved item counts** plus **full-gallery %** and **avg description chars** per cell when available;
   - top **errors/warnings** (HTTP, parse, legal gate) since the last ping.
   - Operator shortcut: run `make action1-matrix-snapshot` on the host and paste/send the output.
5. **Action0 (`S1-22A`)**: run only after the operator sends **`Action0 now`** following Action1 completion (or an explicit parallel waiver documented in `docs/agents/scraper_1/JOURNEY.md`).
6. **Action2 (`S1-22C`)**: run only after **`Action2 now`** and debugger QA notes on Action1 allow expansion.

### Action0 — describe already saved property galleries first

Input:

- `docs/exports/s1-21-gemma-action0-eligible.json`
- `docs/exports/s1-21-tier12-quality-audit-2026-04-29.json`
- `data/scraped/*/listings/*.json`
- `data/media/<reference_id>/...`
- `docs/exports/property-quality-and-building-contract.md`

Do:

1. Process every row in `s1-21-gemma-action0-eligible.json`.
2. Work property item by property item.
3. For each property, inspect every local image in the listed order.
4. Write one complete property-level report that combines all image descriptions with scraped title, description, price, area, category, address/location, source links, and QA checks.
5. Check property identity before reporting: one source publication is not always one sellable/rentable unit. If the page describes multiple apartments, a residential building, `1-2 bedroom` inventory, `apartments (various types)`, `selection of` units, or `prices from`, mark it `suspected_multi_unit_publication` and do not invent a single unit unless the source provides unit-level URL, price, area, and media evidence.
6. Do not treat numeric `0` as a property price. Use `on_request` or `undefined` price status when that is what the source page says, otherwise mark the parser output as suspicious.
7. Add a **single-property validity check** for each property item:
   - Decide whether the page is a **single unit** with a coherent price + images + description.
   - If not, mark it as `suspected_multi_unit_publication` and explain why (multi-unit wording, price-from, “selection of”, etc.).
   - If photos do not match the description/category/price, record a mismatch note and set the single-property flag to false.
8. Include per-image scene descriptions and one whole-property summary covering style, visual description, layout/planning clues, requirements, visible tools/equipment, furniture/appliances, colors/materials, condition, risks, and confidence.
9. Save outputs under `docs/exports/property-image-reports/<source_key>/<safe_reference_id>.md` and `.json`.
10. Write `docs/exports/property-image-reports/index.md` and `index.json` with source totals, properties described, images described, skipped rows, skip reasons, QA warnings, and fields needing human review.

Acceptance:

- Every Action0 eligible row has a report or a precise skip reason.
- Every report references only local image files that exist.
- Every report includes image-by-image observations plus one whole-property description.
- No rooms, equipment, colors, damage, building facts, or floorplans are invented.

### Action1 — full seven-source all-Bulgaria scrape/backfill

After **`Action1 ACCEPT`** (and after Action0 only if the operator already waived the gate), run the full all-Bulgaria scrape/backfill for these sources only:

1. `Address.bg`
2. `BulgarianProperties`
3. `Homes.bg`
4. `imot.bg`
5. `LUXIMMO`
6. `property.bg`
7. `SUPRIMMO`

Required four screen categories for every source:

- Buy residential -> `buy_personal`
- Buy commercial -> `buy_commercial`
- Rent residential -> `rent_personal`
- Rent commercial -> `rent_commercial`

For every accepted listing, save:

- source name/key, source URL, all equivalent source links when detected conservatively,
- title, full page description, combined text, structured attributes,
- price/currency, area, rooms, floor, property type, buy/rent service type, residential/commercial category,
- city, district, address text, coordinates/geocoding evidence when available,
- all remote image URLs and all downloaded local image files,
- source bucket, category validation evidence, parse warnings, media status, and local file validity.

Acceptance:

- All seven sources are attempted in all four categories under legal/source-registry gates.
- Each source gets per-bucket logs with saved count, skipped count, block/runtime errors, and parser warnings.
- Every row has photo counts, description coverage status, and source-link evidence.
- Dashboards and S1-21 / S1-22A-B-C exports are refreshed after the run.

### Action2 — remaining legal tier-1/2 sources after Action1

After Action1 is complete and QA-reviewed, repeat the same full scrape/backfill and image-report process for the rest of the legal tier-1/2 source set in `data/source_registry.json`.

Action2 must not include sources marked `legal_review_required`, `licensing_required`, private/social/messenger-only, or blocked by `access_mode` without a separate operator/legal approval.

## Non-Negotiable Guardrails

- Use `data/source_registry.json` as the source authority.
- Enforce `legal_mode`, `risk_mode`, and `access_mode`.
- Do not crawl sources marked `legal_review_required` or `licensing_required` unless a separate legal/contract approval exists.
- Do not scrape private social/messenger channels.
- Keep tests fixture-only; live crawling is an operator command, not a unit test.
- Store image binaries under `data/media/<reference_id>/...`; keep remote URLs only as traceability metadata.

## Current Facts

- Latest review artifact: `docs/exports/gemma4-openclaw-run-analysis-2026-04-27.md`.
- Current file-backed corpus has 1,549 saved tier-1/2 items, 18,707 remote photo references, and 5,376 local downloaded photos.
- No completed property image-description reports were found as of 2026-04-29; Action0 must create those reports from the S1-21 eligible local-gallery set before Action1 widens live/backfill scraping.
- S1-21 audit outputs exist: `docs/exports/s1-21-tier12-quality-audit-2026-04-29.json`, `docs/exports/s1-21-tier12-quality-audit-2026-04-29.md`, and `docs/exports/s1-21-gemma-action0-eligible.json`.
- One-call all-Bulgaria runtime function exists: `bgrealestate.scraping.run_parallel_all_scrape(...)`.
- CLI wrapper exists: `python -m bgrealestate scrape-all-full`.
- Legacy Varna-specific function still exists for the old control-plane path: `bgrealestate.scraping.run_parallel_varna_scrape(...)`.
- Dashboard target exists: `docs/dashboard/scrape-status.html`.
- Per-item photo/field JSON exists: `docs/exports/source-item-photo-coverage.json`.
- Property quality endpoint exists for local website QA: `GET /api/property-quality/<encoded reference_id>`.
- Property quality/building contract exists: `docs/exports/property-quality-and-building-contract.md`.
- Dry-run planning output for all-Bulgaria scrape: `docs/exports/all-full-scrape-summary.json`.
- Legacy Varna dry-run planning output: `docs/exports/varna-full-scrape-summary.json`.
- Current strict patterned set from saved evidence includes: `Address.bg`, `BulgarianProperties`, `Homes.bg`, `imot.bg`, `LUXIMMO`, `OLX.bg`, `property.bg`, `SUPRIMMO`, `Bazar.bg`, `Yavlena`.
- Current Gemma priority pattern set is: `Address.bg`, `BulgarianProperties`, `Homes.bg`, `imot.bg`, `LUXIMMO`, `property.bg`, `SUPRIMMO`.
- Those seven sources now have explicit bucket instructions for all four screen categories: `buy_personal` (buy residential), `buy_commercial` (buy commercial), `rent_personal` (rent residential), and `rent_commercial` (rent commercial). Some portals expose mixed sale/rent routes, so category acceptance must be confirmed from card/detail text before saving a row into a bucket.
- Current file-backed source totals from `docs/exports/source-item-photo-coverage.json`: `Address.bg` 140 saved / 140 full-gallery; `BulgarianProperties` 249 / 1; `Homes.bg` 97 / 52; `imot.bg` 271 / 14; `LUXIMMO` 15 / 13; `OLX.bg` 249 / 249; `property.bg` 15 / 1; `SUPRIMMO` 12 / 1; `Bazar.bg` 250 / 192; `Yavlena` 251 / 250.
- `BulgarianProperties`, `imot.bg`, `property.bg`, and `SUPRIMMO` have high remote-gallery counts in older saved rows and must run media backfill before their old corpus can be treated as full-gallery complete.
- Known low/no-sample sources: `alo.bg`, `Domaza`, `Home2U` and several tier-2 sources not yet in `scripts/live_scraper.py`.

## Interpretation

The project is past source discovery for the main tier-1/2 wave. The remaining production work is:

- run the all-Bulgaria scrape/backfill until supported sources reach 100 valid listings each,
- complete or repair sources without a full sample,
- backfill missing local media for older saved rows,
- import scraped rows into PostgreSQL for `canonical_listing` proof,
- refresh the dashboard so per-property photo counts are visible source by source.

## Main Command

Dry-run first:

```bash
make scrape-all-full EXTRA_ARGS="--dry-run --parallel-sources 4 --target-per-source 100"
```

Live run after network and operator approval:

```bash
make scrape-all-full EXTRA_ARGS="--parallel-sources 4 --max-pages 8 --max-waves 3 --target-per-source 100 --refresh-dashboard"
```

Callable Python function:

```python
from bgrealestate.scraping import run_parallel_all_scrape

run_parallel_all_scrape(
    target_per_source=100,
    max_pages=8,
    max_waves=3,
    parallel_sources=4,
    download_photos=True,
    require_full_gallery=True,
    dry_run=False,
    refresh_dashboard=True,
)
```

Use `scrape-varna-full` only when intentionally running the legacy Varna-only control-plane path. The operator request is now to scrape all Bulgaria because the saved corpus already contains listings outside Varna.

## Media Backfill For Existing Saved Rows

Run this for sources where `photo_count_remote > photo_count_local` in `docs/exports/source-item-photo-coverage.json`:

```bash
make backfill-scraped-media EXTRA_ARGS="--source bulgarianproperties"
make backfill-scraped-media EXTRA_ARGS="--source imot_bg"
make backfill-scraped-media EXTRA_ARGS="--source property_bg"
make backfill-scraped-media EXTRA_ARGS="--source suprimmo"
make dashboard-doc
```

Use `--dry-run` first if bandwidth or source blocking is uncertain.

## Action0 Property Image Description Reports

This is the first Gemma/OpenClaw task. It applies to every eligible property item, not only apartments. Do not start from every scraped row blindly; use the Codex-confirmed eligible set in `docs/exports/s1-21-gemma-action0-eligible.json`.

After full-gallery local files exist, create a separate visual report for every accepted property listing. Do this listing by listing, and image by image, preserving the source image order.

Before writing each report, run or replicate the property-quality checks from:

```text
GET /api/property-quality/<encoded reference_id>
```

The report must cover both visual evidence and contextual consistency:

- whether the photos match the scraped description, title, category, size, and price range,
- whether the listing has suspicious photo/description mismatches,
- whether price, area, rooms, floor, and category are plausible for the city/source context,
- whether the property still needs address-to-building footprint matching,
- whether the source links represent the same property conservatively or only the current source.

Output files:

- Per-listing Markdown: `docs/exports/property-image-reports/<source_key>/<safe_reference_id>.md`
- Per-listing JSON: `docs/exports/property-image-reports/<source_key>/<safe_reference_id>.json`
- Global Markdown index: `docs/exports/property-image-reports/index.md`
- Global JSON index: `docs/exports/property-image-reports/index.json`
- Legacy compatibility may mirror apartment-only rows to `docs/exports/apartment-image-reports/`, but the authoritative output is `property-image-reports`.

Use only local image files from `local_image_files`. Do not analyze remote URLs unless the local file is missing and the row is explicitly marked as a gap. Do not invent unseen rooms, furniture, condition, or colors. If an element is unclear, write `unclear` and include a confidence value.

For each property, the report must include:

- source name, source key, reference ID, listing URL, title, price, size, rooms, floor, city, district, address text,
- photo counts: remote, local, full-gallery flag, photo download status,
- image group summary: how many images, image ordering, likely room/scene sequence or commercial/exterior sequence, missing-scene warnings,
- property visual summary: overall style, likely renovation level, condition, natural-light impression, finish/material quality, cleanliness/readiness impression,
- color palette: dominant wall, floor, cabinet, furniture, textile, bathroom, exterior, and accent colors,
- planning/layout description: visible room sequence, kitchen relationship to living area, balcony/terrace evidence, corridor/hallway evidence, bathroom count evidence, storage/utility evidence, floorplan evidence,
- what is present: furniture, appliances, heating/cooling units, sanitary fixtures, lighting, built-ins, balcony items, exterior views, parking/garage evidence, garden/yard evidence,
- tools/equipment present: visible kitchen equipment, construction/repair tools, cleaning tools, HVAC units, boilers, meters, radiators, security systems, smart-home devices, or `none visible`,
- requirements: obvious repair/renovation needs, missing fixtures, moisture/damage signs, dated finishes, furnishing gaps, staging/photo-quality gaps, accessibility concerns, and items requiring human verification,
- buyer/renter usability note: move-in readiness, rental readiness, family suitability, office/work suitability, and risks visible in photos,
- consistency QA: photo-to-description match, price/size plausibility, missing fields, suspected parser issues, and whether a human should verify the listing,
- **single-property validity**:
  - `single_property_ok` (boolean)
  - `single_property_comment` (string; why OK/not OK)
  - `mismatch_notes` (array of strings; photo/description/category/price inconsistencies)
- confidence and uncertainty notes for every non-obvious conclusion.

For each image inside the property group, create one numbered subsection or JSON object with:

- image order and local file path,
- matching remote URL if available,
- detected scene type: living room, bedroom, kitchen, bathroom, balcony, corridor, exterior, building entrance, view, floorplan, utility/storage, land/yard, parking/garage, commercial, unknown,
- visual description in plain language,
- style and design cues,
- visible layout/planning clues,
- present objects/furniture/appliances/equipment/tools,
- dominant colors and materials,
- condition/quality observations,
- defects or risks visible in the image,
- whether the image is useful for listing quality, duplicate detection, or room classification,
- confidence score from 0 to 1.

Suggested JSON shape:

```json
{
  "source_key": "olx_bg",
  "reference_id": "OLX.bg:example",
  "listing_url": "https://...",
  "property_category": "apartment",
  "photo_counts": {
    "remote": 8,
    "local": 8,
    "full_gallery_downloaded": true,
    "photo_download_status": "full_gallery"
  },
  "property_visual_summary": {
    "overall_style": "modern / classic / dated / luxury / unfinished / unclear",
    "visual_description": "...",
    "planning": "...",
    "requirements": ["..."],
    "visible_equipment_and_tools": ["..."],
    "dominant_colors": ["..."],
    "missing_or_unclear": ["..."],
    "confidence": 0.82
  },
  "quality_checks": {
    "photo_description_match": "pass / warn / fail",
    "price_size_plausibility": "pass / warn / fail",
    "missing_or_suspicious_fields": ["..."],
    "building_match_status": "pending",
    "human_review_required": true
  },
  "single_property_validity": {
    "single_property_ok": true,
    "single_property_comment": "Looks like one unit; consistent photos + single price + coherent description.",
    "mismatch_notes": []
  },
  "images": [
    {
      "order": 0,
      "local_path": "data/media/ref/0000_hash.jpg",
      "scene_type": "living room",
      "description": "...",
      "style": "...",
      "planning_clues": "...",
      "present": ["sofa", "table", "window"],
      "colors": ["white", "light wood", "gray"],
      "materials": ["laminate", "painted walls"],
      "condition": "...",
      "requirements": ["..."],
      "quality_use": ["room_classification", "listing_presentation"],
      "confidence": 0.9
    }
  ]
}
```

Recommended execution order:

1. Run Action0 from `docs/exports/s1-21-gemma-action0-eligible.json`.
2. Inspect 5 property reports per high-volume source manually before the full Action0 batch.
3. Write the global index with source totals, property counts, images analyzed, reports created, skipped items, and skip reasons.
4. Run Action1 seven-source all-Bulgaria scrape/backfill.
5. Re-run Action0 for newly complete local-gallery rows.
6. Run Action2 for the remaining legal tier-1/2 source set after Action1 is accepted.

Completion rule: a property with photos is not fully enriched until it has both all local images and one per-property visual report covering every local image in order.

## PostgreSQL Proof Path

After local Postgres is running:

```bash
export DATABASE_URL=postgresql+psycopg://bgrealestate:bgrealestate@localhost:5432/bgrealestate
make migrate
make sync-registry
make import-scraped EXTRA_ARGS="--download-images"
make dashboard-doc
```

Then verify `canonical_listing` counts by source. The `S1-18` gate is not complete until at least five tier-1/2 sources each have 100+ rows in `canonical_listing`.

## Source/Segment Targets

For each supported patterned source across all Bulgaria:

- `buy_personal`: apartments, houses, land, new-build where source supports them.
- `rent_personal`: apartments/houses where source supports them.
- `buy_commercial` and `rent_commercial`: only when routes are legally allowed and parser patterns are explicit enough to preserve full detail and gallery capture.

Priority four-bucket source matrix for the next Gemma/OpenClaw scrape and image-description wave:

| Source | Buy residential | Buy commercial | Rent residential | Rent commercial | Category rule |
|---|---:|---:|---:|---:|---|
| Address.bg | yes | yes | yes | yes | Shared sale/rent routes are allowed only after detail estate type confirms residential/commercial. |
| BulgarianProperties | yes | yes | yes | yes | Use sale/rent plus office/business routes; validate category on detail. |
| Homes.bg | yes | yes | yes | yes | Homes API offerType separates buy/rent; residential/commercial must be classified from returned card/detail metadata. |
| imot.bg | yes | yes | yes | yes | Varna/sale/rent routes can be shared; final bucket assignment comes from card/detail property type. |
| LUXIMMO | yes | yes | yes | yes | Sale/rent/business routes are patterned; accept only when detail category matches the target bucket. |
| property.bg | yes | yes | yes | yes | Selection/business routes are patterned; accept only when detail category matches the target bucket. |
| SUPRIMMO | yes | yes | yes | yes | Selection/business routes are patterned; accept only when detail category matches the target bucket. |

Gemma must create image-description reports for accepted listings from all four categories, not only apartments. Apartment reports keep the deepest room-by-room structure; commercial reports must describe workspaces, shopfronts, storage/warehouse space, building access, service areas, and fit-out condition when visible.

For each accepted property, save:

- source name and source section ID,
- country scope marker (`all_bulgaria`) plus city, region, district, and address/location text when present,
- buy/rent segment,
- listing URL and canonical detail URL,
- title,
- price and currency,
- area/size,
- rooms,
- floor / total floors where present,
- construction/building type where present,
- property category/type,
- city, district, address/location text,
- full description,
- combined text / raw text fallback,
- phones or contact metadata where legally present,
- structured extras / source attributes,
- all remote image URLs in order,
- all downloaded local image files in order,
- `photo_count_remote`, `photo_count_local`, `full_gallery_downloaded`, and `photo_download_status`.
- visual analysis report paths, once generated: `image_report_md`, `image_report_json`, `image_report_status`, and `image_report_generated_at`.

## Dashboard Requirement

After every run:

```bash
make dashboard-doc
```

Confirm `docs/dashboard/scrape-status.html` shows, source by source:

- total saved listings,
- total remote photos,
- total local photos,
- full-gallery item count,
- landed corpus matrix by buy/rent and property type,
- per-item table with parsed fields and photo counts for every property.

## Completion Criteria

- At least five legally allowed tier-1/2 sources have 100+ valid all-Bulgaria listings in PostgreSQL `canonical_listing`.
- For every listed item that exposes photos, `photo_count_local >= photo_count_remote` or the row is explicitly marked with `partial_gallery` / `no_local_files`.
- Every source section called `Patterned` has at least one saved sample with full local gallery, description, price, city/address, and at least two structured fields.
- Dashboard and JSON exports are regenerated.
- Property image description reports exist for every Action0 eligible listing with complete local galleries, with one grouped report per property and one description entry per image.
- Any blocked source has an explicit reason: legal gate, pattern incomplete, HTTP/DNS failure, anti-bot, or no usable all-Bulgaria/category route.

## Gaps To Close

- `alo.bg`, `Domaza`, and `Home2U` need first full product samples before they can be included in strict activation.
- `imoti.net`, `Imoteka.bg`, and `Imoti.info` remain legal/authorization blocked.
- Local environment previously lacked PostgreSQL and Docker daemon access; DB proof must run where Postgres is available.
