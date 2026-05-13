# Entity Resolution Queue Plan

Generated: 2026-05-13

## Scope

FACT: This is a planning and handoff artifact only. It does not promote any record to `property_entity`, does not create `property_offer` links, and does not change scraped corpus rows.

FACT: Current accepted-only import evidence is not DB-backed yet. `DA-01` is verified as file-backed; `BD-18`, `BD-19`, and DB count proof remain open.

INTERPRETATION: Entity resolution must operate on accepted source publications first, then produce reviewable duplicate/match candidates. It must not treat raw scrape volume, grouped/development pages, or pending QA rows as property identity evidence.

GAP: PostgreSQL-backed accepted rows, candidate tables/API, review events, and live DB idempotency are not verified.

## Read Inputs

- `docs/agents/TASKS.md`
- `docs/agents/roles/entity_resolution_agent.md`
- `docs/agents/roles/data_analyst.md`
- `docs/agents/README.md`
- `agent-skills/dedupe-entity-resolution/SKILL.md`
- `agent-skills/postgres-analysis/SKILL.md`
- `src/bgrealestate/services/unification.py`
- `src/bgrealestate/pipeline.py`
- `tests/test_unification.py`
- `sql/schema.sql`
- `scripts/import_scraped_listings.py`
- `docs/exports/property-identity-anomaly-audit-2026-04-29.md`
- `docs/exports/action1-multi-unit-publications.json`
- `docs/exports/scrape-database-quality-audit-2026-05-13.md`
- `docs/exports/action1-dataset-quality-gate.md`
- `data/source_registry.json`

## Known Constraints

FACT: `scripts/import_scraped_listings.py --dry-run` now skips unreviewed, `LOST`, grouped/development, and inactive rows by default.

FACT: The current unification service can create `property_entity` and `property_offer` links from `canonical_listing` via dedupe keys. That behavior is too aggressive for the current dirty Action1 corpus unless it is constrained by accepted-only source-publication evidence.

FACT: Current SQL has `property_entity.review_status` and `confidence_score`, but it does not yet have first-class QA/source-publication fields on `canonical_listing` or dedicated entity-resolution candidate/review tables.

FACT: Grouped/development evidence appears in `source_publication_type = multi_unit_or_development`, `scrape_status = GROUPED_PUBLICATION`, `scrape_acceptance_status = not_single_entity`, and warning reasons such as `multi_unit_publication:*`.

INTERPRETATION: The identity pipeline needs a reviewable candidate layer between accepted source publications and canonical property entities.

## Accepted-Only Source Publication Filter

Use a publication as an entity-resolution input only when all conditions are true:

- `scrape_status = SCRAPED_OK`.
- `scrape_acceptance_status` indicates accepted/single-unit, or `single_entity_candidate = true`.
- `source_publication_type` is not `multi_unit_or_development`.
- `listing_status` is not `inactive`, `removed`, or `expired`.
- Source is present in `data/source_registry.json` and its `legal_mode`, `risk_mode`, and `access_mode` allow storing the evidence already collected.
- The row has a stable source identity: source key/name plus one of `external_id`, detail URL, or source reference id.
- The row has minimum unit evidence: detail URL, price or explicit `price_status`, area or explicit unknown reason, city/location evidence, and media/provenance fields preserved.

Rows outside this filter remain source evidence or QA work items. They must not enter candidate scoring as property units.

## Case Taxonomy

### Single-Unit

FACT: A single-unit candidate represents one sellable/rentable unit with its own source detail URL and one price or explicit non-numeric price state.

Required handling:

- Eligible for duplicate-candidate scoring only after accepted-only filter passes.
- Can be matched to other accepted single-unit source publications.
- Still needs operator review before any merge/promotion when evidence is not exact.

### Grouped Or Development

FACT: Development pages, whole-building pages, `apartments (various types)`, price-from pages, and mixed unit pages are source publications, not single property entities.

Required handling:

- Exclude from duplicate-candidate scoring.
- Queue as `development_review` or `unit_split_needed`.
- Split only when source evidence provides unit-level URL, price or price status, area, floor/rooms, and unit media.
- Never auto-merge as one property.

### Unknown

FACT: Unknown rows include pending/missing QA state, missing source-publication type, missing accepted/single-entity flag, missing source identity, or missing critical unit fields without provenance.

Required handling:

- Exclude from candidate scoring.
- Queue to `data_analyst`/`scraper_1` as QA/parser/provenance repair.
- Re-evaluate only after DA/BD evidence updates.

### Duplicate

FACT: Duplicate means duplicate source-publication evidence, not automatically the same canonical property.

Required handling:

- Same source plus same external id or normalized detail URL is a source-publication duplicate.
- Cross-source duplicates require strong same-unit evidence: normalized city/location, address/building/project signal, compatible area, compatible price/price status, compatible room/floor/unit signals, contact/agency/source-family context, and photo overlap or media corroboration.
- Store as a reviewable candidate with evidence and reason codes.
- Operator action can be `link`, `dismiss`, `defer`, or `mark_conflict`.

### Conflicting Evidence

FACT: Candidate pairs can share location/title tokens but still represent different units in the same building/project.

Conflict triggers:

- Different source records from the same source unless one is an exact source duplicate.
- Area difference above tolerance without source-provided explanation.
- Price difference above tolerance without price-status/lifecycle explanation.
- Same building/project but different floor, rooms, unit code, or media set.
- Zero or near-zero photo overlap when both records have real galleries, unless other exact unit evidence exists.
- One side has grouped/development or unknown state.

Required handling:

- Do not merge.
- Queue as `conflicting_evidence`.
- Preserve all source links and conflict reasons for admin review.

## Candidate Evidence Fields

Minimum candidate evidence payload:

- `left_reference_id`, `right_reference_id`
- source names/keys, owner group, legal/risk/access modes
- source external ids and normalized detail URLs
- source-publication state fields: `scrape_status`, `scrape_acceptance_status`, `source_publication_type`, `single_entity_candidate`, `listing_status`
- city, district, address text, building/project name, coordinates, geocode confidence
- category, intent, rooms, floor, area, construction attributes
- price, currency, `price_status`, first_seen, last_seen, listing lifecycle state
- phone/contact overlap after contact cleanup
- normalized title tokens and unit identifiers
- remote/local photo counts, image URL keys, local image storage keys, photo overlap score, image report status when available
- score component JSON, conflict reason codes, recommended review action

## Scoring Policy

Scoring is only for accepted single-unit source publications.

- Exact source duplicate: same source plus same external id or normalized detail URL. Queue as `source_duplicate`, no property merge action.
- Strong cross-source same-unit candidate: useful address/building evidence plus compatible area and price/status plus media/contact corroboration. Queue as `same_unit_candidate`.
- Weak same-building/project candidate: city/district/title/project match without unit-level agreement. Queue as `same_complex_only`, not mergeable.
- Conflict candidate: any strong contradiction. Queue as `conflicting_evidence`, not mergeable.
- Unknown/blocked candidate: missing accepted state or missing required fields. Exclude and send to QA repair.

Recommended thresholds for later labeled-sample validation:

- `score >= 0.90`: high-confidence candidate, still reviewable before merge.
- `0.70 <= score < 0.90`: medium candidate, side-by-side review required.
- `0.50 <= score < 0.70`: low/weak same-building candidate, do not offer merge.
- `< 0.50`: ignore unless an exact source duplicate signal exists.

No score can override grouped/development, unknown, inactive, `LOST`, or pending QA exclusion.

## Backend Developer Handoff

Schema/API needs:

1. Add or expose an identity candidate layer independent from `property_entity`:
   - `entity_resolution_candidate`
   - `entity_resolution_candidate_evidence`
   - `entity_resolution_review_event`
2. Add accepted-only query inputs from `BD-18`/`BD-19`:
   - first-class or structured-extra fields for `price_status`, `source_publication_type`, `scrape_status`, `scrape_acceptance_status`, `single_entity_candidate`, `listing_status`, media counts, local image keys, image report status, bucket/segment provenance.
3. Add import/unification safety:
   - scraped import should support accepted source-publication persistence without automatically creating `property_entity`/`property_offer` links.
   - candidate generation should be idempotent and deterministic.
4. Add admin API:
   - `GET /admin/entity-resolution/candidates`
   - `GET /admin/entity-resolution/candidates/{id}`
   - `POST /admin/entity-resolution/candidates/{id}/review`
5. Keep public `/properties` output accepted-only and verified. Do not expose ER candidates to buyer-facing routes.

## Debugger Handoff

Verification needs:

1. Fixture tests prove pending QA, missing-status, `LOST`, inactive, grouped/development, and unknown rows are excluded from candidate scoring.
2. Fixture tests prove grouped/development rows cannot create `property_entity` or `property_offer`.
3. Candidate generation is deterministic and idempotent.
4. Conflict fixtures remain unmerged and carry reason codes.
5. Existing `src/bgrealestate/services/unification.py` behavior is gated so it cannot run broad auto-promotion against unreviewed Action1 rows.
6. Tests remain fixture-only with no live network dependency.

## Next Slices

- `ER-02`: accepted-only duplicate candidate extraction contract.
- `ER-03`: evidence scoring and case-classification matrix.
- `ER-04`: source-publication relationship and conflict review policy.
- `BD-21`: entity-resolution candidate schema/API and import safety handoff.
- `DBG-18`: verifier gate for ER accepted-only/no-promotion behavior.
