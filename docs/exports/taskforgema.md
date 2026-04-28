# Task For Gemma4 / OpenClaw: Full Bulgaria Tier-1/2 Scrape With Complete Galleries

Generated: 2026-04-24
Updated: 2026-04-27 after Gemma/OpenClaw output review

## Objective

Run the Bulgaria Real Estate tier-1/2 scraper to completion for **all Bulgaria**, not only Varna, across all legally allowed, patterned sources and supported buy/rent segments. Save every accepted property with full text, structured fields, source provenance, and all reachable photos as local files.

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
- No completed apartment image-description reports were found as of 2026-04-27; the next Gemma pass should focus on those reports after Codex finishes `S1-21`.
- One-call all-Bulgaria runtime function exists: `bgrealestate.scraping.run_parallel_all_scrape(...)`.
- CLI wrapper exists: `python -m bgrealestate scrape-all-full`.
- Legacy Varna-specific function still exists for the old control-plane path: `bgrealestate.scraping.run_parallel_varna_scrape(...)`.
- Dashboard target exists: `docs/dashboard/scrape-status.html`.
- Per-item photo/field JSON exists: `docs/exports/source-item-photo-coverage.json`.
- Dry-run planning output for all-Bulgaria scrape: `docs/exports/all-full-scrape-summary.json`.
- Legacy Varna dry-run planning output: `docs/exports/varna-full-scrape-summary.json`.
- Current strict patterned set from saved evidence includes: `Address.bg`, `BulgarianProperties`, `Homes.bg`, `imot.bg`, `LUXIMMO`, `OLX.bg`, `property.bg`, `SUPRIMMO`, `Bazar.bg`, `Yavlena`.
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

## Apartment Image Description Reports

This is now the next Gemma/OpenClaw task after Codex completes the tier-1/2 quality audit and pattern repair pass (`S1-21`). Do not start from every scraped row blindly; use the Codex-confirmed eligible set of apartment listings with complete local galleries.

After full-gallery local files exist, create a separate visual report for every accepted apartment listing. Do this listing by listing, and image by image, preserving the source image order.

Output files:

- Per-listing Markdown: `docs/exports/apartment-image-reports/<source_key>/<reference_id>.md`
- Per-listing JSON: `docs/exports/apartment-image-reports/<source_key>/<reference_id>.json`
- Global Markdown index: `docs/exports/apartment-image-reports/index.md`
- Global JSON index: `docs/exports/apartment-image-reports/index.json`

Use only local image files from `local_image_files`. Do not analyze remote URLs unless the local file is missing and the row is explicitly marked as a gap. Do not invent unseen rooms, furniture, condition, or colors. If an element is unclear, write `unclear` and include a confidence value.

For each apartment, the report must include:

- source name, source key, reference ID, listing URL, title, price, size, rooms, floor, city, district, address text,
- photo counts: remote, local, full-gallery flag, photo download status,
- image group summary: how many images, image ordering, likely room/scene sequence, missing-scene warnings,
- apartment visual summary: overall style, likely renovation level, condition, natural-light impression, finish/material quality, cleanliness/readiness impression,
- color palette: dominant wall, floor, cabinet, furniture, textile, bathroom, exterior, and accent colors,
- planning/layout description: visible room sequence, kitchen relationship to living area, balcony/terrace evidence, corridor/hallway evidence, bathroom count evidence, storage/utility evidence, floorplan evidence,
- what is present: furniture, appliances, heating/cooling units, sanitary fixtures, lighting, built-ins, balcony items, exterior views, parking/garage evidence, garden/yard evidence,
- tools/equipment present: visible kitchen equipment, construction/repair tools, cleaning tools, HVAC units, boilers, meters, radiators, security systems, smart-home devices, or `none visible`,
- requirements: obvious repair/renovation needs, missing fixtures, moisture/damage signs, dated finishes, furnishing gaps, staging/photo-quality gaps, accessibility concerns, and items requiring human verification,
- buyer/renter usability note: move-in readiness, rental readiness, family suitability, office/work suitability, and risks visible in photos,
- confidence and uncertainty notes for every non-obvious conclusion.

For each image inside the apartment group, create one numbered subsection or JSON object with:

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
  "apartment_summary": {
    "overall_style": "modern / classic / dated / luxury / unfinished / unclear",
    "visual_description": "...",
    "planning": "...",
    "requirements": ["..."],
    "visible_equipment_and_tools": ["..."],
    "dominant_colors": ["..."],
    "missing_or_unclear": ["..."],
    "confidence": 0.82
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

1. Finish local gallery backfill.
2. Build the per-listing image report generator.
3. Run it first on 5 apartments per high-volume source and inspect the Markdown manually.
4. Run it for all apartment listings with complete local galleries.
5. Write the global index with source totals, apartment counts, images analyzed, reports created, skipped items, and skip reasons.

Completion rule: an apartment with photos is not fully enriched until it has both all local images and one per-apartment visual report covering every local image in order.

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
- Apartment image description reports exist for every apartment listing with complete local galleries, with one grouped report per apartment and one description entry per image.
- Any blocked source has an explicit reason: legal gate, pattern incomplete, HTTP/DNS failure, anti-bot, or no usable all-Bulgaria/category route.

## Gaps To Close

- `alo.bg`, `Domaza`, and `Home2U` need first full product samples before they can be included in strict activation.
- `imoti.net`, `Imoteka.bg`, and `Imoti.info` remain legal/authorization blocked.
- Local environment previously lacked PostgreSQL and Docker daemon access; DB proof must run where Postgres is available.
