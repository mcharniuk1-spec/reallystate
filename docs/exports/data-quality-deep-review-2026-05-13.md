# Data Quality Deep Review

Generated: 2026-05-13 14:22:29Z

## Role Execution

| Step | Acting role | Output |
|---|---|---|
| 1 | data_analyst | Reconciled saved corpus, DA-01, quality gate, importer candidates, media evidence, and denominator gaps. |
| 2 | backend_developer | Reviewed BD-18 schema/import safety and patched source-publication-first importer guardrails. |
| 3 | vision_media_agent | Assessed gallery evidence separately from inactive semantic image descriptions. |
| 4 | market_intelligence_analyst | Produced accepted-only market-analysis readiness notes and limits. |
| 5 | user_analytics_agent | Produced dashboard/funnel data requirements without adding third-party analytics. |

## Verification Summary

- FACT: DA-01 audit rows: 30,334; Action1 rows: 29,397.
- FACT: Importer default candidates: 1,606; pending/missing QA: 26,231.
- FACT: Action1 offline estimate: 20,811 accepted candidates, 7,133 LOST, 1,453 grouped/development.
- FACT: DB-backed counts remain blocked until `DATABASE_URL` exists and `make verify-db-counts` runs.
- FACT: Image semantic descriptions are not active; gallery capture/media counts are evidence, image-description coverage is not.
- INTERPRETATION: scraper repair can proceed fixture-first, but canonical property/offer promotion remains unsafe without BD-18 DB proof.
- GAP: DA-02 denominator reconciliation and BD-18 DB smoke tests still require verifier acceptance.

## Blocked From Canonical Import

- PENDING_QA, missing-QA, UNKNOWN, and unreviewed rows
- LOST or needs_rescrape rows
- grouped/development/multi-unit publications without unit-level evidence
- inactive, removed, expired, stale-review, sold, or rented rows unless source-confirmed and reviewed
- numeric zero-price rows unless converted to null plus explicit price_status
- missing price without on_request/undefined provenance
- missing source URL/provenance, location, area, or required media evidence
- rows with local gallery gaps or image evidence overstated
- contact-only or mass-enriched personal data without provenance/permission metadata

## Source Repair Table

| Source | Rows | Import candidates | Blocked | Risk | Top bad rules | Required scraper action |
|---|---:|---:|---:|---|---|---|
| `address_bg` | 6,473 | 0 | 6,473 | critical | image_semantic_description_unverified:6473, contact_overcapture_suspect:5832, missing_or_unreviewed_qa:5582, local_gallery_exceeds_remote_variants:4159 | Address detail parser, location selectors, gallery expansion, contact-block normalization, pending-to-accepted quality writeback. |
| `alo_bg` | 29 | 0 | 29 | critical | missing_or_unreviewed_qa:29, missing_source_publication_type:29, missing_acceptance_status:29, image_semantic_description_unverified:29 | Alo detail parser output envelope, QA field defaults, bucket assignment, phone/contact provenance. |
| `bazar_bg` | 250 | 0 | 250 | critical | missing_or_unreviewed_qa:250, missing_source_publication_type:250, missing_acceptance_status:250, image_semantic_description_unverified:250 | Price parser, location parser, gallery downloader, phone extraction boundaries, accepted-only QA writer. |
| `bulgarianproperties` | 2,289 | 0 | 2,289 | critical | image_semantic_description_unverified:2289, contact_overcapture_suspect:2289, partial_local_gallery:2271, missing_or_unreviewed_qa:1888 | Area/plot parser, language canonicalization, gallery carousel extraction, contact-list scoping. |
| `domaza` | 40 | 0 | 40 | critical | missing_or_unreviewed_qa:40, missing_source_publication_type:40, missing_acceptance_status:40, image_semantic_description_unverified:40 | Publication-type classifier, area field selectors, complex/development wording, per-language canonical URL mapping. |
| `home2u` | 24 | 0 | 24 | critical | missing_or_unreviewed_qa:24, missing_source_publication_type:24, missing_acceptance_status:24, image_semantic_description_unverified:24 | Title/detail selector, description body, contact provenance, listing_status markers. |
| `homes_bg` | 144 | 60 | 84 | high | image_semantic_description_unverified:144, lost_or_rescrape_required:62, remote_gallery_without_local_files:37, missing_or_unreviewed_qa:20 | Reference-id normalization, duplicate URL handling, gallery downloader, inactive/removed detection. |
| `imot_bg` | 9,937 | 1,535 | 8,402 | critical | image_semantic_description_unverified:9937, missing_or_unreviewed_qa:8124, duplicate_remote_image_urls:1568, local_gallery_exceeds_remote_variants:376 | Detail-page parser, project-page classifier, category mapping, duplicate external_id/reference logic, stale listing markers. |
| `luximmo` | 2,512 | 5 | 2,507 | critical | image_semantic_description_unverified:2512, contact_overcapture_suspect:2512, missing_or_unreviewed_qa:2356, missing_area:518 | Area parser, offer-kind classifier, gallery carousel, contact block scoping, language/region parser. |
| `olx_bg` | 249 | 0 | 249 | critical | missing_or_unreviewed_qa:249, missing_source_publication_type:249, missing_acceptance_status:249, image_semantic_description_unverified:249 | Official API parser, location payload mapping, stale/deleted status, phone extraction allowlist. |
| `property_bg` | 3,094 | 5 | 3,089 | critical | image_semantic_description_unverified:3094, missing_or_unreviewed_qa:3089, thin_description:138, unknown_property_category:118 | Description extraction, category mapper, gallery de-duplication, SUPRIMMO-group dedupe hints. |
| `suprimmo` | 4,948 | 1 | 4,947 | critical | image_semantic_description_unverified:4948, contact_overcapture_suspect:4948, missing_or_unreviewed_qa:4235, grouped_or_development_publication:712 | Project/development classifier, area parser, gallery extraction, contact provenance, category mapper. |
| `yavlena` | 345 | 0 | 345 | critical | missing_or_unreviewed_qa:345, one_remote_photo_gallery_suspect:345, missing_source_publication_type:345, missing_acceptance_status:345 | Detail description selector, category mapper, price parser, gallery selector, active/inactive markers. |

## Source-by-Source Repair Instructions

### address_bg

- FACT: rows=6,473; default import candidates=0; blocked=6,473; risk=critical.
- FACT: media rows with full gallery=6,276; partial gallery=103; one-photo suspect=1,677.
- FACT: image semantic rows=0; image report status={"missing": 6473}.
- What is wrong: Large pending QA queue, many one-photo suspect rows, missing city/address in some categories, and high invalid/duplicated phone extraction.
- Likely reason: List-card/detail merge and contact block extraction over-capture repeated boilerplate; QA state was not finalized after offline estimate.
- Inspect: Address detail parser, location selectors, gallery expansion, contact-block normalization, pending-to-accepted quality writeback.
- Fixture/sample: Use one accepted city row, one missing-location row, one one-photo row, and one commercial/rent row.
- Acceptance condition: Fixture rows preserve source URL, price/status, city/address, full gallery counts, valid contact provenance, and accepted QA only when single-unit evidence is present.
- Must remain blocked: Pending QA, one-photo suspect, missing location, invalid contact-only, and missing/undefined price without source evidence.
- Example paths: {"missing_or_unreviewed_qa": "data/scraped/address_bg/listings/Address.bg_0012a5649f6d.json", "image_semantic_description_unverified": "data/scraped/address_bg/listings/Address.bg_0012a5649f6d.json", "contact_overcapture_suspect": "data/scraped/address_bg/listings/Address.bg_0012a5649f6d.json", "local_gallery_exceeds_remote_variants": "data/scraped/address_bg/listings/Address.bg_001a3d0d094d.json", "missing_location_evidence": "data/scraped/address_bg/listings/Address.bg_001f2a6df8f5.json"}

### alo_bg

- FACT: rows=29; default import candidates=0; blocked=29; risk=critical.
- FACT: media rows with full gallery=29; partial gallery=0; one-photo suspect=0.
- FACT: image semantic rows=0; image report status={"missing": 29}.
- What is wrong: All current rows lack explicit QA/source-publication fields even though estimate marks them OK.
- Likely reason: Legacy parser predates Action1 QA field writeback.
- Inspect: Alo detail parser output envelope, QA field defaults, bucket assignment, phone/contact provenance.
- Fixture/sample: Varna sale fixture with full gallery and phone block; add missing/expired page fixture if available.
- Acceptance condition: Every saved row gets scrape_status, scrape_acceptance_status, source_publication_type, listing_status, bucket_key, and media counts.
- Must remain blocked: All missing-QA rows until explicit Action1 fields exist.
- Example paths: {"missing_or_unreviewed_qa": "data/scraped/alo_bg/listings/alo.bg_10497275.json", "missing_source_publication_type": "data/scraped/alo_bg/listings/alo.bg_10497275.json", "missing_acceptance_status": "data/scraped/alo_bg/listings/alo.bg_10497275.json", "image_semantic_description_unverified": "data/scraped/alo_bg/listings/alo.bg_10497275.json", "thin_description": "data/scraped/alo_bg/listings/alo.bg_11097790.json"}

### bazar_bg

- FACT: rows=250; default import candidates=0; blocked=250; risk=critical.
- FACT: media rows with full gallery=192; partial gallery=57; one-photo suspect=0.
- FACT: image semantic rows=0; image report status={"missing": 250}.
- What is wrong: Missing QA, partial local galleries, missing city/address, numeric zero-price rows, and noisy phone extraction.
- Likely reason: Classified detail pages have variable location/price blocks and legacy parser did not enforce price_status.
- Inspect: Price parser, location parser, gallery downloader, phone extraction boundaries, accepted-only QA writer.
- Fixture/sample: Zero-price fixture, partial-gallery fixture, missing-location fixture, active/rent fixture.
- Acceptance condition: Numeric 0 becomes null plus price_status, location is present or blocked, and local gallery count matches remote count before acceptance.
- Must remain blocked: Zero price, missing location, partial gallery, missing QA, LOST, inactive/stale classified rows.
- Example paths: {"missing_or_unreviewed_qa": "data/scraped/bazar_bg/listings/Bazar.bg_40857836.json", "missing_location_evidence": "data/scraped/bazar_bg/listings/Bazar.bg_40857836.json", "partial_local_gallery": "data/scraped/bazar_bg/listings/Bazar.bg_40857836.json", "missing_source_publication_type": "data/scraped/bazar_bg/listings/Bazar.bg_40857836.json", "missing_acceptance_status": "data/scraped/bazar_bg/listings/Bazar.bg_40857836.json"}

### bulgarianproperties

- FACT: rows=2,289; default import candidates=0; blocked=2,289; risk=critical.
- FACT: media rows with full gallery=18; partial gallery=2,271; one-photo suspect=0.
- FACT: image semantic rows=0; image report status={"missing": 2289}.
- What is wrong: Very high LOST estimate, missing area, partial galleries, and agency contact over-capture.
- Likely reason: Agency pages mix full property pages, area/plot fields, language variants, and boilerplate phone lists.
- Inspect: Area/plot parser, language canonicalization, gallery carousel extraction, contact-list scoping.
- Fixture/sample: House with plot area, apartment with built area, missing-area page, full-gallery page.
- Acceptance condition: Area field has correct semantics, full gallery evidence is durable, and contact provenance identifies agency-level phone lists.
- Must remain blocked: Missing area, partial gallery, LOST, grouped/new-build/project pages without unit evidence.
- Example paths: {"missing_or_unreviewed_qa": "data/scraped/bulgarianproperties/listings/BulgarianProperties_0023d0450186.json", "partial_local_gallery": "data/scraped/bulgarianproperties/listings/BulgarianProperties_0023d0450186.json", "image_semantic_description_unverified": "data/scraped/bulgarianproperties/listings/BulgarianProperties_0023d0450186.json", "contact_overcapture_suspect": "data/scraped/bulgarianproperties/listings/BulgarianProperties_0023d0450186.json", "missing_area": "data/scraped/bulgarianproperties/listings/BulgarianProperties_00880d57f8df.json"}

### domaza

- FACT: rows=40; default import candidates=0; blocked=40; risk=critical.
- FACT: media rows with full gallery=40; partial gallery=0; one-photo suspect=0.
- FACT: image semantic rows=0; image report status={"missing": 40}.
- What is wrong: Small tier-2 corpus includes residential-complex/grouped pages and missing area rows.
- Likely reason: Portal exposes project pages and multi-language/category pages that resemble unit pages.
- Inspect: Publication-type classifier, area field selectors, complex/development wording, per-language canonical URL mapping.
- Fixture/sample: Residential complex page, single unit page, missing-area page.
- Acceptance condition: Grouped/development pages are marked source publications; only unit URLs with price/status, area, and media can be accepted.
- Must remain blocked: Complex/project pages, missing-area rows, ambiguous grouped offers.
- Example paths: {"missing_or_unreviewed_qa": "data/scraped/domaza/listings/Domaza_22334.json", "missing_area": "data/scraped/domaza/listings/Domaza_22334.json", "missing_source_publication_type": "data/scraped/domaza/listings/Domaza_22334.json", "missing_acceptance_status": "data/scraped/domaza/listings/Domaza_22334.json", "image_semantic_description_unverified": "data/scraped/domaza/listings/Domaza_22334.json"}

### home2u

- FACT: rows=24; default import candidates=0; blocked=24; risk=critical.
- FACT: media rows with full gallery=24; partial gallery=0; one-photo suspect=7.
- FACT: image semantic rows=0; image report status={"missing": 24}.
- What is wrong: Small sample has thin titles, missing QA fields, and limited contact evidence.
- Likely reason: Agency template parser extracts short headline but not enough detail/context.
- Inspect: Title/detail selector, description body, contact provenance, listing_status markers.
- Fixture/sample: Rent listing, sale listing, missing detail page, inactive page if saved.
- Acceptance condition: Title and description are complete enough for dedupe/search and QA fields are explicit.
- Must remain blocked: Missing QA, thin title-only rows, missing area/contact provenance.
- Example paths: {"missing_or_unreviewed_qa": "data/scraped/home2u/listings/Home2U_0ed15363bab8.json", "thin_title": "data/scraped/home2u/listings/Home2U_0ed15363bab8.json", "missing_source_publication_type": "data/scraped/home2u/listings/Home2U_0ed15363bab8.json", "missing_acceptance_status": "data/scraped/home2u/listings/Home2U_0ed15363bab8.json", "image_semantic_description_unverified": "data/scraped/home2u/listings/Home2U_0ed15363bab8.json"}

### homes_bg

- FACT: rows=144; default import candidates=60; blocked=84; risk=high.
- FACT: media rows with full gallery=86; partial gallery=18; one-photo suspect=13.
- FACT: image semantic rows=0; image report status={"missing": 144}.
- What is wrong: Duplicate listing URLs, many LOST rows, local-gallery gaps, and some grouped/development rows.
- Likely reason: Offline reparsing recovered fields but source URL/reference normalization and media backfill are inconsistent.
- Inspect: Reference-id normalization, duplicate URL handling, gallery downloader, inactive/removed detection.
- Fixture/sample: Duplicate URL pair, accepted row with full gallery, LOST row, grouped/new-build row.
- Acceptance condition: Duplicate source URLs collapse to one source publication; accepted rows have local gallery and QA state; LOST stays quarantined.
- Must remain blocked: LOST, duplicate unresolved URL clusters, grouped/development, local-gallery-missing rows.
- Example paths: {"lost_or_rescrape_required": "data/scraped/homes_bg/listings/Homes.bg_01bf996371bd.json", "remote_gallery_without_local_files": "data/scraped/homes_bg/listings/Homes.bg_01bf996371bd.json", "image_semantic_description_unverified": "data/scraped/homes_bg/listings/Homes.bg_01bf996371bd.json", "partial_local_gallery": "data/scraped/homes_bg/listings/Homes.bg_0376351f52e1.json", "grouped_or_development_publication": "data/scraped/homes_bg/listings/Homes.bg_09e4e5f2cf98.json"}

### imot_bg

- FACT: rows=9,937; default import candidates=1,535; blocked=8,402; risk=critical.
- FACT: media rows with full gallery=9,728; partial gallery=25; one-photo suspect=9.
- FACT: image semantic rows=0; image report status={"missing": 9937}.
- What is wrong: Largest source with many pending QA rows, grouped/development pages, missing/unknown categories, thin descriptions, and duplicate IDs risk.
- Likely reason: High-volume portal mixes unit listings, project ads, agency reposts, and short list-card descriptions.
- Inspect: Detail-page parser, project-page classifier, category mapping, duplicate external_id/reference logic, stale listing markers.
- Fixture/sample: Sale unit, rent unit, project page, short-description page, duplicate/external-id row.
- Acceptance condition: Only unit-level detail pages with stable URL, price/status, area, media, and active status are accepted.
- Must remain blocked: Pending QA, grouped/development, unknown category, missing area, inactive/stale rows.
- Example paths: {"missing_or_unreviewed_qa": "data/scraped/imot_bg/listings/imot.bg_000edf42c963.json", "image_semantic_description_unverified": "data/scraped/imot_bg/listings/imot.bg_000edf42c963.json", "duplicate_remote_image_urls": "data/scraped/imot_bg/listings/imot.bg_0027872a2495.json", "local_gallery_exceeds_remote_variants": "data/scraped/imot_bg/listings/imot.bg_002c97644d70.json", "unknown_property_category": "data/scraped/imot_bg/listings/imot.bg_004df16d31a2.json"}

### luximmo

- FACT: rows=2,512; default import candidates=5; blocked=2,507; risk=critical.
- FACT: media rows with full gallery=2,508; partial gallery=4; one-photo suspect=1.
- FACT: image semantic rows=0; image report status={"missing": 2512}.
- What is wrong: Luxury agency rows have missing area, grouped/development pages, partial galleries, and large contact lists.
- Likely reason: Agency template mixes project, office, and luxury descriptions; contact blocks include sitewide phone variants.
- Inspect: Area parser, offer-kind classifier, gallery carousel, contact block scoping, language/region parser.
- Fixture/sample: Long-term rent apartment, sale apartment, project/development page, missing-area row.
- Acceptance condition: Offer kind, area, price/status, and contact provenance are preserved; grouped pages remain source publications.
- Must remain blocked: Missing area, grouped/development, LOST, contact-only unsafe rows, image gaps.
- Example paths: {"missing_or_unreviewed_qa": "data/scraped/luximmo/listings/LUXIMMO_000386d2645f.json", "missing_area": "data/scraped/luximmo/listings/LUXIMMO_000386d2645f.json", "image_semantic_description_unverified": "data/scraped/luximmo/listings/LUXIMMO_000386d2645f.json", "contact_overcapture_suspect": "data/scraped/luximmo/listings/LUXIMMO_000386d2645f.json", "grouped_or_development_publication": "data/scraped/luximmo/listings/LUXIMMO_01286b671353.json"}

### olx_bg

- FACT: rows=249; default import candidates=0; blocked=249; risk=critical.
- FACT: media rows with full gallery=249; partial gallery=0; one-photo suspect=0.
- FACT: image semantic rows=0; image report status={"missing": 249}.
- What is wrong: Missing QA, volatile classified inventory, missing location/area, and excessive phone extraction.
- Likely reason: API/HTML payloads vary and legacy rows lack Action1 quality fields.
- Inspect: Official API parser, location payload mapping, stale/deleted status, phone extraction allowlist.
- Fixture/sample: Active listing, deleted/inactive listing, missing-price row, missing-location row.
- Acceptance condition: Official/source status is preserved; missing or deleted rows are stale/review, not active public offers.
- Must remain blocked: Missing QA, deleted/stale/volatile rows, missing price/status/location, owner-contact uncertainty.
- Example paths: {"missing_or_unreviewed_qa": "data/scraped/olx_bg/listings/OLX.bg_125403576.json", "missing_area": "data/scraped/olx_bg/listings/OLX.bg_125403576.json", "missing_location_evidence": "data/scraped/olx_bg/listings/OLX.bg_125403576.json", "missing_source_publication_type": "data/scraped/olx_bg/listings/OLX.bg_125403576.json", "missing_acceptance_status": "data/scraped/olx_bg/listings/OLX.bg_125403576.json"}

### property_bg

- FACT: rows=3,094; default import candidates=5; blocked=3,089; risk=critical.
- FACT: media rows with full gallery=3,091; partial gallery=3; one-photo suspect=0.
- FACT: image semantic rows=0; image report status={"missing": 3094}.
- What is wrong: Many thin descriptions, unknown categories, and possible gallery over-count/duplicate variants.
- Likely reason: English/Bulgarian agency pages include repeated marketing boilerplate and large gallery variants.
- Inspect: Description extraction, category mapper, gallery de-duplication, SUPRIMMO-group dedupe hints.
- Fixture/sample: High-photo listing, thin-description listing, unknown-category listing, accepted row.
- Acceptance condition: Description has property-specific text, category is mapped, duplicate image variants are not overstated.
- Must remain blocked: Thin-description-only, unknown category, grouped/development, media duplicate variants until reviewed.
- Example paths: {"missing_or_unreviewed_qa": "data/scraped/property_bg/listings/property.bg_0001c7d93103.json", "image_semantic_description_unverified": "data/scraped/property_bg/listings/property.bg_0001c7d93103.json", "unknown_property_category": "data/scraped/property_bg/listings/property.bg_00b600ae04e7.json", "thin_description": "data/scraped/property_bg/listings/property.bg_01bba875be73.json", "partial_local_gallery": "data/scraped/property_bg/listings/property.bg_01fade04055f.json"}

### suprimmo

- FACT: rows=4,948; default import candidates=1; blocked=4,947; risk=critical.
- FACT: media rows with full gallery=4,943; partial gallery=5; one-photo suspect=0.
- FACT: image semantic rows=0; image report status={"missing": 4948}.
- What is wrong: Large grouped/development queue, missing area, unknown categories, and contact over-capture.
- Likely reason: Agency/developer inventory mixes houses, projects, resorts, and repeated contact blocks.
- Inspect: Project/development classifier, area parser, gallery extraction, contact provenance, category mapper.
- Fixture/sample: Project page, single house, rent unit, missing-area page.
- Acceptance condition: Grouped/development source publications never become canonical units without unit-level evidence.
- Must remain blocked: Grouped/development, missing area, LOST, contact-only unsafe rows, pending QA.
- Example paths: {"missing_or_unreviewed_qa": "data/scraped/suprimmo/listings/SUPRIMMO_ SOF 112646.json", "image_semantic_description_unverified": "data/scraped/suprimmo/listings/SUPRIMMO_ SOF 112646.json", "contact_overcapture_suspect": "data/scraped/suprimmo/listings/SUPRIMMO_ SOF 112646.json", "grouped_or_development_publication": "data/scraped/suprimmo/listings/SUPRIMMO_001ffd8c3731.json", "unknown_property_category": "data/scraped/suprimmo/listings/SUPRIMMO_001ffd8c3731.json"}

### yavlena

- FACT: rows=345; default import candidates=0; blocked=345; risk=critical.
- FACT: media rows with full gallery=344; partial gallery=0; one-photo suspect=345.
- FACT: image semantic rows=0; image report status={"missing": 345}.
- What is wrong: Many missing descriptions, one-photo rows, unknown categories, and zero-price rows.
- Likely reason: Parser under-extracts detail body/category and treats placeholder price/media as real evidence.
- Inspect: Detail description selector, category mapper, price parser, gallery selector, active/inactive markers.
- Fixture/sample: Hotel/commercial page, apartment unit, zero-price page, one-photo page.
- Acceptance condition: Commercial category is explicit, zero price is null plus status, and one-photo rows are blocked unless source truly has one image.
- Must remain blocked: Missing description, unknown category, zero price, one-photo suspect, missing QA.
- Example paths: {"missing_or_unreviewed_qa": "data/scraped/yavlena/listings/Yavlena_023103601cb5.json", "unknown_property_category": "data/scraped/yavlena/listings/Yavlena_023103601cb5.json", "one_remote_photo_gallery_suspect": "data/scraped/yavlena/listings/Yavlena_023103601cb5.json", "missing_source_publication_type": "data/scraped/yavlena/listings/Yavlena_023103601cb5.json", "missing_acceptance_status": "data/scraped/yavlena/listings/Yavlena_023103601cb5.json"}

## Database/BD-18 Review

| Concept | Status | Existing tables | Gap |
|---|---|---|---|
| source_publications | partial | source_listing, source_listing_snapshot, raw_capture, source_publication_qa_review, status_history | Publication-level evidence exists and BD-18 added QA/status tables; PostgreSQL migration/import proof is still pending. |
| canonical_properties | partial | property_entity | Entity table exists but current promotion can happen before reviewed source-publication import and dedupe confidence gates. |
| listing_offers | partial | property_offer | Offer table exists but sale/long-term/short-term/commercial flows lack price_status, availability status, and offer-kind constraints. |
| qa_reviews | implemented_pending_db_proof | source_publication_qa_review | First-class QA review table is defined; it still needs PostgreSQL migration, smoke import, and count parity verification. |
| status_history | implemented_pending_db_proof | status_history, listing_event, price_history | Generic status-history table is defined; runtime migration/import proof is still pending. |
| contacts | partial | contact_entity, person_contact, contact_method, property_contact_link | Contact provenance, permission/source, inferred/agency/owner/company type, and mass-enrichment guardrails are not first-class. |
| media_assets | partial | media_asset, listing_media, property_media | Local/source media exists, but source photo count, local count, storage keys, hash variants, and evidence status need source-publication linkage. |
| media_descriptions | implemented_pending_action0_and_db_proof | media_description | Table is defined, but semantic image descriptions are inactive until local-gallery verification, Action0 approval, and DB proof. |
| entity_resolution_candidates | implemented_pending_db_proof | entity_resolution_candidate, entity_resolution_review_event, property_entity.dedupe_key | Reviewable candidate/review-event tables are defined; canonical promotion remains blocked until accepted-only DB proof and review policy pass. |
| availability_calendars | implemented_pending_db_proof | availability_calendar | Calendar table is defined; short-term availability logic and migration/import proof remain pending. |
| availability_slots | implemented_pending_db_proof | availability_slot | Slot table is defined; viewing/booking semantics and runtime proof remain pending. |
| availability_observations | implemented_pending_db_proof | availability_observation | Observation table is defined; timestamped source-observed availability evidence still needs ingest/read-model proof. |
| viewing_or_inquiry_requests | implemented_pending_db_proof | viewing_inquiry_request, lead_thread, lead_thread_property_link | Request table is defined; platform-to-owner/realtor/company workflow still needs API/review implementation and DB proof. |
| external_chat_refs | implemented_pending_db_proof | external_chat_ref, user_property_chat, lead_thread | External chat-ref table is defined; safe handoff metadata still needs runtime verification and API policy. |

### Required Corrections

- Keep import default accepted-only and source-publication-first; property_entity/property_offer promotion requires explicit reviewed flag.
- Convert numeric price 0 to null plus price_status provenance before persistence.
- Run BD-18 migration and DB smoke import for source_publication_qa_review, status_history, entity_resolution_candidate/review_event, media_description, availability, inquiry, and external_chat_ref tables.
- Verify status_history for source_publication, listing_offer, canonical_property transitions with observed_at and provenance.
- Refine availability_calendars, availability_slots, and availability_observations before short-term rental publication/search.
- Use media_descriptions only after gallery identity/local image completeness is reliable and Action0 is approved; do not mix semantic status with raw gallery capture.
- Use entity_resolution_candidate and review events before entity-resolution promotion; keep candidates out of public APIs.
- Implement viewing_inquiry_request and external_chat_ref API/read-model policy with chat DB remaining external and refs only.

### Field Mapping

| Required field | Current state |
|---|---|
| qa_state | first_class_pending_db_proof: source_publication_qa_review.qa_state |
| qa_reviewer | first_class_pending_db_proof: source_publication_qa_review.reviewer |
| qa_reviewed_at | first_class_pending_db_proof: source_publication_qa_review.reviewed_at |
| source_publication_type | crawl_provenance_only |
| source_publication_status | partial: source_listing.status |
| listing_status | crawl_provenance_only |
| listing_status_history | first_class_pending_db_proof: status_history |
| price_status | crawl_provenance_only |
| price_currency | first_class: canonical_listing.currency/property_offer.currency |
| price_period | missing |
| price_provenance | crawl_provenance_only |
| offer_kind | partial: listing_intent/property_offer.intent |
| use_class | partial: property_category + bucket_key JSON |
| property_type | first_class: property_category/entity_type |
| building_or_development_flag | crawl_provenance_only |
| canonical_property_id | first_class: property_entity.property_id |
| canonical_listing_offer_id | first_class: property_offer.offer_id |
| source_publication_id | partial: source_listing.source_listing_id |
| duplicate_cluster_id | candidate_layer_pending_db_proof: entity_resolution_candidate.candidate_id |
| entity_resolution_confidence | candidate_layer_pending_db_proof: entity_resolution_candidate.confidence_score |
| photo_count_from_source | crawl_provenance_only |
| local_image_count | crawl_provenance_only |
| local_image_storage_keys | crawl_provenance_only |
| image_hash | partial: media_asset.sha256/listing_media.content_hash |
| image_perceptual_hash | first_class: media_asset.perceptual_hash |
| image_description_coverage | first_class_pending_action0_and_db_proof: media_description.coverage_state |
| image_evidence_status | partial: media_asset.download_status/listing_media.download_status |
| contact_provenance | missing_first_class |
| contact_type | partial: person_contact.role/contact metadata only |
| contact_permission_source | missing |
| geo_scope | crawl_provenance_only |
| bucket_key | crawl_provenance_only |
| inactive_expired_sold_rented_stale_markers | partial: removed_at/listing_event/status JSON |
| last_seen_at | first_class: source_listing.last_seen_at/canonical_listing.last_seen |
| first_seen_at | first_class: source_listing.first_seen_at/canonical_listing.first_seen |
| source_observed_at | partial: raw_capture.fetched_at/source_snapshot.created_at |
| import_eligibility_reason | first_class_pending_db_proof: source_publication_qa_review.import_eligibility_reason |
| blocked_import_reason | first_class_pending_db_proof: source_publication_qa_review.blocked_import_reason |

## Market Intelligence Readiness

- FACT: Market analysis must use accepted/import-candidate evidence and clearly label file-backed scope.
- INTERPRETATION: raw saved source volume shows scraper coverage and parser health, not market share.
- GAP: DB-backed dedupe, current availability, and stale/out-of-stock status are not verified.

### Accepted Offer Mix

| Offer kind | Accepted rows | Price count | Median price |
|---|---:|---:|---:|
| sale | 997 | 19,616 | 150,000.0 |
| long_term_rent | 517 | 5,619 | 650.0 |
| long_term_rent_commercial | 54 | 1,396 | 1,278.5 |
| sale_commercial | 38 | 3,054 | 102,000.0 |

## User Analytics Handoff

- FACT: No live product analytics were queried or added in this run.
- Required future events: listing impression, listing detail open, map result open, filter apply, save, contact intent, inquiry request, chat handoff, admin QA decision, media confidence interaction.
- Payload rule: no raw source URLs, image URLs, phones, emails, names, raw chat text, IP addresses, user agents, or private notes in analytics events.
- Dashboard denominator rule: funnels use first-party events after UI launch; corpus counts use DA/BD read models, not product telemetry.

## Acceptance Gates Still Missing

- DA-02 denominator contract must reconcile audit, importer, quality-gate, scrape-status, and operational dashboard semantics.
- BD-18 DB smoke test must prove accepted-only source-publication import, zero-price null/status, grouped import blocking, media idempotency, and no default property_entity promotion.
- INFRA-02 must run DB counts after `DATABASE_URL` is provided.
- VM-02/VM-04 must verify gallery identity/local completeness before semantic image descriptions are trusted.
- DBG gate must verify this dashboard/report and rerun importer dry-run plus parser/backend focused tests.
