# Debugger DA-01 Coordination Report

Generated: 2026-05-13

## Verification Summary

FACT: DA-01 is reproducible as a file-backed scrape/database quality audit.
FACT: The current corpus contains 30,334 scraped JSON rows across 13 saved source directories; the registry contains 44 sources.
FACT: Action1 rows total 29,397 across Address.bg, BulgarianProperties, Homes.bg, imot.bg, LUXIMMO, property.bg, and SUPRIMMO.
FACT: 26,231 rows are still PENDING_QA, missing QA, or UNKNOWN.
FACT: Offline Action1 audit estimate is 20,811 accepted single-unit candidates, 7,133 LOST rows, and 1,453 grouped/development publications.
FACT: Action1 quality gate rollup reports 20,811 good single-unit rows, 6,698 bad/lost rows, and 1,888 grouped-publication rows because grouped evidence can coexist with hard-loss reasons.
FACT: Default import dry-run admits 1,612 files and skips 28,722 files.
FACT: Parser regression tests pass locally; the prior bs4 blocker is no longer present on this host.
FACT: DB-backed verification is blocked because DATABASE_URL is unset.

INTERPRETATION: DA-01 can be trusted for file-backed corpus triage, but not for DB-backed canonical completion.
INTERPRETATION: Canonical import must stay accepted-only until BD-18 persists QA/media/source-publication evidence and make verify-db-counts passes against PostgreSQL.
INTERPRETATION: Dashboard artifacts are current but not semantically aligned with DA-01 estimates; they currently expose stored/importer-state counts, not the offline quality-gate estimate denominator.

GAP: PostgreSQL row counts, SQLAlchemy runtime/model/schema alignment, real import idempotency, live URL availability, and image semantic descriptions remain unverified.
GAP: There is no docs/agents/roles/scraper_t3.md role file; scraper_t3 is documented elsewhere as historical only.

## Commands Run

| Command | Result | Evidence |
|---|---|---|
| `python3 scripts/audit_scrape_database_quality.py` | PASS | Regenerated audit: rows=30334, Action1=29397, pending/missing QA=26231, Action1 OK/LOST/grouped=20811/7133/1453. |
| `python3 scripts/import_scraped_listings.py --dry-run` | PASS | candidate_files=1612; skipped_files=28722; unreviewed_quality_state=26231; lost_rescrape_required=1266; grouped_publication_not_single_entity=1225. |
| `python3 scripts/action1_dataset_quality_gate.py` | PASS | Full Action1 quality exports regenerated; LOST queue=7133; multi-unit/development=1888. |
| `python3 scripts/action1_dataset_quality_gate.py --limit-per-source 20 --output docs/exports/action1-dataset-quality-gate-dryrun.json` | PASS | Bounded smoke export regenerated; LOST queue=43; multi-unit/development=20. |
| `make dashboard-doc` | PASS | Progress, source/photo coverage, pattern status, and scrape status dashboard artifacts regenerated. |
| `make verify-db-counts` | BLOCKED | Failed with `DATABASE_URL is required`. |
| `python3 -m unittest tests.test_action1_parser_regressions -v` | PASS | 7 parser/quality regression tests passed. |

## Dashboard Status

FACT: Dashboard artifacts were regenerated.
FACT: `docs/exports/source-item-photo-coverage.json` reports 30,334 saved listings, 1,612 accepted single-entity candidates, 1,266 lost items, 1,270 grouped publications, 604,488 remote photos, and 611,131 local photos.
FACT: `docs/exports/scrape-status-dashboard.json` reports the same stored/importer-state totals.
INTERPRETATION: These dashboard counts are not the same denominator as DA-01 offline quality estimates or Action1 quality-gate rollups.
REQUIRED GATE: DA-02 must label and reconcile stored status, importer candidates, offline estimated quality, bad/lost rows, grouped rows, and bad-and-grouped overlaps before any release claim.

## Source-By-Source Repair Plan

| Source | Rows | Main issue | Likely reason | Inspect next | Fixture/sample gate | Must remain blocked |
|---|---:|---|---|---|---|---|
| address_bg | 6,473 | 1,262 missing city/address, one-photo suspects, oversized area suspects, 49,665 invalid phone-like tokens. | Address detail/location parsing and broad phone regex pick UI/JS/IDs. | Address parser location block, offer code extraction, gallery anchors, contact block selector. | Fixture for missing city/address plus full 1000x666 gallery and valid contact extraction. | All PENDING_QA, missing city/address, one-photo suspect, invalid area, noisy-contact rows. |
| bulgarianproperties | 2,289 | 2,277 estimated LOST; 510 missing area; local gallery incomplete; development pages risk. | Parser uses partial gallery or recommendation/media variants; area labels mixed with project data. | Product JSON-LD/body description, `/big/` gallery URLs, unit area labels, development wording. | Fixture proves unit-level URL, area, price/status, full local gallery; development fixture remains grouped. | Partial-gallery, missing-area, grouped/development, recommendation-media rows. |
| homes_bg | 144 | Duplicate URL keys=36, partial local gallery, narrow sale-apartment coverage, active status not proven. | Discovery/detail/API pairing is incomplete; offer JSON status/photos not fully consumed. | Offer JSON/API payload, canonical URL de-dupe, active/inactive markers, photo array. | Fixture covers buy/rent, duplicate URL collapse, inactive skip, all gallery images. | Duplicate URL rows, inactive/removed rows, missing/partial gallery rows, grouped pages. |
| imot_bg | 9,937 | Strong corpus but 8,124 pending QA, 176 missing area, 211 unknown category, mojibake/thin descriptions. | Encoding/template variants and card/detail field drift. | CP1251 decode path, detail `.adParams`, category label map, gallery data-src, grouped/development markers. | Regression covers mojibake description, missing-area recovery, grouped exclusion, category precision. | Pending QA, missing area without status, grouped/development, mojibake-only rows. |
| luximmo | 2,512 | 518 missing area, 117 grouped audit estimate, gallery variant duplication, thin descriptions. | Property-family templates expose project/complex totals and image size variants. | dataLayer, labeled RZP/ZP/total-area fields, variant-normalized gallery keys, project markers. | Fixture separates unit area from complex area and de-dupes gallery variants. | Missing/oversized area, development, variant-only gallery inflation, thin-description rows. |
| property_bg | 3,094 | Offline estimate strong, but 3,089 rows remain PENDING_QA and 2,075 thin descriptions. | QA not applied to corpus; parser may retain short snippets. | Detail description source, low-price warnings, category labels, QA application flow. | Quality gate converts accepted rows out of PENDING_QA only when source URL/provenance/media evidence exists. | All PENDING_QA, thin-description-only, low-price suspect, grouped/unsafe rows. |
| suprimmo | 4,948 | 684 missing area, 646 grouped audit estimate, gallery variants, 64,194 invalid phone-like tokens. | Shared property-family parser and broad contact extraction. | dataLayer, unit labels, contact panel selectors, development markers, gallery variant keying. | Fixture proves unit area, clean contacts, development classification, de-duped full gallery. | Missing area, grouped/development, noisy-contact, low-price suspect rows. |
| alo_bg | 29 | All rows missing formal QA; 136/139 phone-like tokens invalid. | Legacy rows predate QA fields and contact cleanup. | Source-specific contact selector and QA backfill. | Fixture-backed QA status, valid contact provenance, bucket keys. | Missing QA and invalid-contact rows. |
| bazar_bg | 250 | 250 missing QA; 73 LOST estimate; missing city/address and zero-price rows. | Legacy parser lacks QA/bucket/contact cleanup and price-status handling. | City/address extraction, price parser, contact block, bucket assignment. | Fixture proves zero price becomes null plus price_status and city/address captured. | Missing QA, zero-price, missing location, partial gallery rows. |
| domaza | 40 | 13 missing area and 2 grouped/development estimates. | Development/building pages mixed with unit pages. | Unit vs residential-complex classifier and area labels. | Fixture covers complex page as grouped and unit page as accepted candidate. | Missing-area and grouped/development rows. |
| home2u | 24 | 14 LOST estimate; thin titles; missing area. | Detail title/body extraction incomplete. | Title normalization, detail attributes, absent-description status. | Fixture proves full title, area, city/address, and source description status. | Thin-title, missing-area, missing-description-without-status rows. |
| olx_bg | 249 | 131 LOST estimate; missing area/location; 13,071 invalid phone-like tokens. | API param mapping and contact extraction/noise are incomplete. | Official API params, location hierarchy, phone provenance, bucket keys. | Fixture covers area/location/category and consent-safe contact provenance. | Missing area/location, invalid-contact, grouped pages. |
| yavlena | 345 | 194 LOST estimate; 166 missing descriptions; 9 zero-price rows. | Parser misses description body and uses numeric zero for unavailable price. | Detail description block, category map, price status, one-photo rows. | Fixture proves price 0 becomes null+status and description extracted or marked absent. | All zero-price, missing-description, unknown QA/status rows. |

Registry-only sources have no current saved corpus rows in DA-01. They stay out of S1-23 except where already in corpus; Action2 and S&M must use legal/access gates from `data/source_registry.json`. Legal-review, licensing, partner-only, consent-only, private messenger, and prohibited-without-contract sources remain blocked unless the operator/legal path explicitly opens them.

## Backend And Schema Blockers For BD-18

FACT: `CanonicalListingRepository.upsert` sends the full `CanonicalListing` dataclass into `CanonicalListingModel`, but the DB model is missing fields such as floor, total_floors, construction_type, price_per_sqm, phones, broker/agency/owner/developer names, geocode_confidence, building_name, stage, fees, amenities, and outbound hints.
FACT: SQL lacks first-class fields for price_status, source_publication_type, scrape_status, scrape_acceptance_status, single_entity_candidate, listing_status, photo_count_remote, photo_count_local, full_gallery_downloaded, local_image_storage_keys, image_report_status, and image_description_coverage.
FACT: `source_section` and `crawl_run` are still Varna-region constrained while Action1 uses all-Bulgaria bucket/segment provenance.
FACT: Listing media upsert generates a new media_id for every image on every import, so repeated imports can duplicate media rows instead of using a deterministic listing+URL/order key.

Required BD-18 structure:

- `source_publications`: raw/publication-level source evidence.
- `canonical_properties`: deduplicated property/building/unit identity.
- `listing_offers`: sale, long-term rent, short-term rent, commercial, and mixed-use offers.
- `qa_reviews`: QA state, reviewer, timestamp, import eligibility, blocked reason.
- `status_history`: source/listing/property status transitions.
- `contacts`: normalized contacts with type, provenance, permission, and source.
- `media_assets` and `media_descriptions`: local/source media evidence and future semantic reports.
- `dedupe_clusters`: conservative entity-resolution groups and confidence.
- `availability_calendars`, `availability_slots`, `availability_observations`: availability without assuming listing existence means stock.
- `viewing_or_inquiry_requests`: platform/company request workflow to owner/realtor/company contacts.
- `external_chat_refs`: safe references only; chat content stays in the future chat service/database.

Availability rules:

- Age alone can trigger stale review, not SOLD_CONFIRMED or RENTED_CONFIRMED.
- Long-term rent stale thresholds must be stricter than sale.
- Short-term rent availability must be calendar/slot based.
- Statuses must include ACTIVE_CONFIRMED, ACTIVE_UNVERIFIED, PENDING_QA, STALE_REVIEW_REQUIRED, EXPIRED_SOURCE, SOLD_CONFIRMED, RENTED_CONFIRMED, LOST, GROUPED_PUBLICATION, DEVELOPMENT_PUBLICATION, and UNSAFE_FOR_CANONICAL_IMPORT.

## Product Surface Alignment

| Surface | Required backend contract | Current blocker |
|---|---|---|
| `/listings` | accepted listing_offers only, filters by offer kind, price/status, source provenance, stale/availability state | Accepted-only DB import and offer schema not verified. |
| `/properties/[id]` | canonical property with linked source_publications, offers, media, QA, status history, contacts, dedupe confidence | Canonical property identity and source-publication separation incomplete. |
| `/map` | lat/lon/geom with confidence, source evidence, stale filtering, grouped publication exclusion | DB geospatial counts and confidence not verified. |
| `/chat` | external chat refs plus request/listing/property IDs, no chat content forced into listing DB | Request/chat reference contract not modeled for property offers. |
| `/settings` | user/account/profile preferences and safe contact settings | Mostly separate from DA-01; do not mix PII enrichment into listings. |
| `/admin` | QA queues, blocked reasons, source publication review, stale review, import eligibility, media coverage | QA review/status model and dashboard denominator repair still missing. |

## Acceptance Gates Still Required

- No PENDING_QA, missing-QA, UNKNOWN, LOST, inactive, grouped/development, or unsafe rows imported by default.
- Numeric 0 price must never persist as real price.
- Accepted canonical candidates must have source URL/provenance and QA import eligibility.
- Grouped/development publications must remain non-canonical unless unit-level URL/identifier, price/status, area, rooms/floor where applicable, media, contacts, and QA state exist.
- Source-publication records must remain separate from canonical property and listing offer records.
- Parser, fixture, source, QA, bucket, media, price, contact, and status provenance must survive import.
- Local gallery coverage must not be overstated; semantic image descriptions must wait for reliable gallery identity and completeness.
- Contacts must be provenance-tagged, permission-aware, and not mass-enriched.
- Dashboard counts must match or explicitly label audit, quality-gate, and importer denominators.
- Dry-run import must reject unsafe rows.
- DB-backed counts must pass when DATABASE_URL exists.
- Parser regression tests must stay fixture-only and pass before scraper repair closes.

## Blocked From Canonical Import

Default canonical import must continue to block:

- 26,231 unreviewed, missing, or UNKNOWN QA rows.
- 1,266 rows currently skipped by importer as lost_rescrape_required, and the broader 7,133 Action1 LOST audit estimate until QA semantics are reconciled.
- 1,225 rows currently skipped by importer as grouped_publication_not_single_entity, and the broader 1,888 Action1 grouped-publication rollup until denominator semantics are reconciled.
- Any row with numeric price 0.
- Any grouped/development/project/landing/multi-unit page without unit-level evidence.
- Any inactive, removed, expired, stale-review-required, sold/rented-confirmed, or unsafe row.
- Any row whose source legal/access mode is not allowed by `data/source_registry.json`.
- Any row that would lose source provenance, QA state, price status, publication type, contact provenance, media evidence, duplicate/source relationship, or grouped/development distinction.

## Next Owner Sequence

1. `planner`: keep DA-02, BD-18, S1-23, ER-01, VM-01, INFRA-02, DBG-16, DBG-17, and DBG-22 ordered; no Action2 widening before Action1 QA repair or explicit waiver.
2. `data_analyst`: execute DA-02 to reconcile dashboard/audit/importer denominators.
3. `backend_developer`: execute BD-18 schema/model/import alignment and DB-backed fixture import.
4. `infra_db_operator`: provide DATABASE_URL/runtime and run `make verify-db-counts`.
5. `entity_resolution_agent`: define conservative dedupe queue after accepted source-publication import evidence exists.
6. `vision_media_agent`: verify gallery completeness before image semantic descriptions.
7. `scraper_1`: execute S1-23 source-by-source repair with fixture regressions and no live tests.
8. `scraper_sm`: keep tier-3/tier-4 work legal/consent-gated and separate from Action1 marketplace completeness.
9. `ux_ui_designer`: map UI states only after backend contracts are explicit; use verified data labels.
10. `debugger`: rerun acceptance gates after BD-18/S1-23/DA-02/INFRA-02.
11. `ops_release_manager`: release hygiene only after debugger pass; current state is not release-clear for DB/canonical import.
