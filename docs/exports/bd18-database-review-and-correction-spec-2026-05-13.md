# BD-18 Database Review And Correction Spec

Generated: 2026-05-13 14:22:29Z

## Result

- FACT: DB-backed counts are still blocked by missing `DATABASE_URL`.
- FACT: The current schema has partial source/publication, property, offer, media, contact, and CRM structures.
- FACT: BD-18 evidence tables are now defined in schema/migration/ORM for QA reviews, status history, entity-resolution candidates/reviews, media descriptions, availability, inquiry requests, and external chat refs.
- INTERPRETATION: scraper repair can write better source-publication evidence now, but default DB import must not promote to canonical property/offer until BD-18 DB tests pass.

## Concept Coverage

| Required concept | Status | Current mapping | Required correction |
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

## Safe Import Rules

- Default import is accepted-only and source-publication-first.
- Numeric price `0` is converted to `null` and preserved as `price_status=undefined` unless source evidence says `on_request`.
- `PENDING_QA`, missing-QA, `UNKNOWN`, `LOST`, `needs_rescrape`, grouped/development, inactive, removed, expired, stale-review, sold, and rented rows remain blocked by default.
- Property/entity promotion requires an explicit reviewed path and should not run from the scraped-corpus import default.
- Source publication provenance, bucket, geo scope, QA state, media counts, local image keys, and contact provenance must survive import.

## Tables To Add Or Refine

1. `source_publication_qa_review`: migrate and smoke-test QA state, reviewer, reviewed_at, import_eligible, import_eligibility_reason, blocked_import_reason, evidence_jsonb.
2. `status_history`: migrate and verify subject_type, subject_id, from_status, to_status, observed_at, source_observed_at, provenance_jsonb.
3. `entity_resolution_candidate` / `entity_resolution_review_event`: keep reviewable candidate evidence separate from property promotion.
4. `availability_calendar`, `availability_slot`, `availability_observation`: refine long-term viewing/inquiry availability separately from short-term booking calendars.
5. `viewing_inquiry_request`: implement request workflow from platform/company to owner/realtor/company contact.
6. `media_description`: use only after gallery identity/local image completeness is reliable and Action0 is approved.
7. `external_chat_ref`: store thread/request/listing/offer handoff refs only; chat content remains outside listing truth.

## Field Mapping

| Field | Current state |
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
