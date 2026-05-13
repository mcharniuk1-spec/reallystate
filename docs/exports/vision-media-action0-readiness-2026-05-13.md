# Vision Media Action0 Readiness

Date: 2026-05-13
Owner: `vision_media_agent`
Status: planning complete; image processing not run

## Inputs

- `docs/agents/TASKS.md`
- `docs/agents/roles/vision_media_agent.md`
- `docs/agents/roles/data_analyst.md`
- `agent-skills/image-media-pipeline/SKILL.md`
- `docs/exports/source-item-photo-coverage.json`
- `docs/exports/s1-21-gemma-action0-eligible.json`
- `docs/exports/scrape-database-quality-audit-2026-05-13.md`
- `docs/exports/action1-dataset-quality-gate.json`
- `docs/exports/property-quality-and-building-contract.md`
- `docs/exports/taskforgema.md`

## Current Evidence

FACT: DA-01 is verified as file-backed only; PostgreSQL-backed import/count proof is still blocked by missing `DATABASE_URL` and `BD-18`.

FACT: Current Action1 quality gate totals are `29397` rows, `20811` accepted single-unit candidates, `7133` LOST rows, and `1888` grouped-publication rollup rows. DA-01 audit reports `1453` grouped/development rows under a different denominator.

FACT: Current Action0 eligible queue has `9620` rows:

| Source | Eligible rows | Local images in eligible queue |
|---|---:|---:|
| `bulgarianproperties` | 4 | 254 |
| `homes_bg` | 63 | 556 |
| `imot_bg` | 7448 | 77926 |
| `luximmo` | 1607 | 13450 |
| `property_bg` | 289 | 17362 |
| `suprimmo` | 209 | 15450 |

FACT: DA-01 media/capture gaps still include one-photo suspects, partial local galleries, missing remote galleries, and gallery-size variant duplication. The highest parser/media repair needs are `Address.bg`, `BulgarianProperties`, `Homes.bg`, `imot.bg`, `LUXIMMO`, `property.bg`, and `SUPRIMMO`.

FACT: `source-item-photo-coverage.json` is useful for media counts, but some accepted-row counters are based on stored corpus QA state and differ from the current quality-gate estimate. Use DA-01 / `action1-dataset-quality-gate.json` for accepted/LOST/grouped status until DA-02 reconciles dashboard semantics.

INTERPRETATION: Vision/media work has two separate gates: media capture completeness and semantic visual evidence. Local photos alone are not enough for promotion; semantic reports must state uncertainty and cannot become final property facts.

HYPOTHESIS: A small manual calibration batch before full Action0 will catch prompt/schema drift and reduce hallucinated room/condition/equipment claims.

GAP: No image semantic descriptions have been generated in this run. Image decodability/readability is not rechecked here. DB persistence fields for media QA and semantic status are still pending `BD-18`/`BD-19`.

## Semantic Media QA Tasks

### 1. Gallery Completeness QA

- Verify remote/local photo counts, full-gallery flag, local file list order, duplicate/variant suspicion, and missing/partial gallery reasons.
- Treat one-photo galleries as valid only when the source detail page truly exposes one image; otherwise queue scraper/media repair.
- Skip semantic report execution for partial-gallery rows unless a debugger/data_analyst waiver marks the missing gallery as source-limited.
- Preserve original remote URLs, local storage keys, source image ordering, content/hash metadata when available, and provenance.

### 2. Per-Image Semantic QA

For every local image in a report, record:

- scene type: living room, bedroom, kitchen, bathroom, balcony, corridor, exterior, entrance, view, floorplan, utility/storage, land/yard, parking/garage, commercial, unknown;
- style/design cues, visible layout clues, furniture/appliances/equipment/tools, colors/materials, condition, visible defects/risks, and image usefulness;
- `confidence` from `0` to `1`;
- uncertainty notes using `unclear`, `not visible`, or `not enough evidence` instead of guessing.

### 3. Whole-Property Visual QA

For each property report, record:

- visual summary, likely room/scene sequence, missing-scene warnings, photo-text match, price/area/category plausibility, and building-match pending state;
- single-property validity with `single_property_ok`, comment, and mismatch notes;
- buyer/renter usability evidence: move-in readiness, rental readiness, family/office suitability, visible risks, and required human review;
- explicit statement that the report is evidence, not a canonical fact overwrite.

### 4. Uncertainty QA

- Never infer unseen rooms, equipment, fixtures, damage, renovation quality, or floorplans.
- Separate `not visible` from `not present`.
- Mark low-quality, blurry, cropped, duplicate, watermarked, floorplan/render, or exterior-only images.
- Require human review when photos conflict with title, category, description, area, price/status, or single-unit identity.

## Visual Evidence Gates

### Buyer-Facing Display Minimum

Display as a normal buyer-facing property only when all are true:

- DA/debugger status is accepted single-unit candidate, not pending QA, `LOST`, inactive, grouped/development, or missing-status.
- Source URL/provenance, price or explicit price status, area when required, city/address/location evidence, and property category are present or the missing state is explicitly labeled.
- At least two decodable local images exist, or the source is explicitly source-limited with a buyer-visible `limited photos` state.
- No known partial-gallery blocker remains for normal display.
- Semantic image statements are hidden or labeled pending until a property image report exists.

### Promotion / Enriched Use Minimum

Use a listing for promoted ranking, smart search, AI summaries, visual condition claims, renovation estimates, or canonical property promotion only when all are true:

- Buyer-facing display minimum passes.
- Full reachable gallery is downloaded or source-limited with debugger/data_analyst approval.
- Semantic report exists with per-image entries and whole-property summary.
- Report includes confidence and uncertainty fields for all non-obvious conclusions.
- No unresolved photo-description mismatch, category mismatch, single-property identity doubt, or grouped/development signal exists.
- Residential listings have enough distinct visual evidence for the main interior plus key wet/service spaces where expected: living/sleeping area, kitchen or kitchenette, bathroom, and exterior/entrance/view when claimed. Commercial/land/development records require type-specific exterior/site/access/floorplan evidence and should not be promoted as normal single-unit homes.

## Execution Queue Rules

- Do not run image processing until operator sends `Action0 now`.
- Use `docs/exports/s1-21-gemma-action0-eligible.json` or a debugger/data_analyst-approved successor queue.
- Use only `local_image_files`; no remote fetch in Action0 semantic reporting.
- Process a calibration sample first: 5 reports per high-volume source where possible, plus all low-volume sources in the queue.
- After calibration, debugger/data_analyst verifies schema, uncertainty, no hallucinated facts, and skip reasons before full batch.
- Write authoritative outputs to `docs/exports/property-image-reports/`.

## Debugger Handoff

Debugger should verify:

- VM-01 planning did not run image processing.
- VM-02 remains blocked until operator `Action0 now`.
- The report schema includes per-image and whole-property uncertainty.
- Action0 reports reference existing local files only.
- Buyer-facing and promotion gates exclude pending QA, `LOST`, inactive, grouped/development, partial-gallery, and no-report rows.
- Dashboard/reporting does not use stale stored accepted counters from media coverage artifacts as the accepted denominator before DA-02.

## Non-Actions In This Run

- No image files opened, decoded, classified, or described.
- No scraper/media backfill run.
- No DB import or dashboard regeneration run.
- No public UI implementation.
