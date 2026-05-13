# Entity Resolution: Accepted-Only Candidate Layer

Date: 2026-05-13

## Scope

Design only. No candidate generation and no canonical property merge were executed.

## Accepted-Only Input Contract

A source publication can enter candidate extraction only when all are true:

- `scrape_status = SCRAPED_OK`
- `scrape_acceptance_status = accepted_single_entity_candidate`
- `source_publication_type = single_unit_candidate`
- `listing_status` is active/current, not inactive, removed, expired, sold, rented, or stale-review
- not `LOST`
- not `needs_rescrape`
- not grouped/development/multi-unit
- price is numeric or has explicit `price_status in (on_request, undefined)`
- source URL, source name, reference ID, bucket/segment, and media/description provenance are preserved
- row came through BD-18 source-publication-first import proof or a verifier-approved fixture equivalent

## Candidate Tables

BD-18 now defines the storage targets:

- `entity_resolution_candidate`
- `entity_resolution_review_event`

Candidate records are reviewable evidence, not property entities.

## Candidate Classes

- `source_duplicate`: same source and exact source identity duplicated.
- `same_unit_candidate`: strong cross-source same-unit evidence.
- `same_complex_only`: same building/project/complex evidence but not enough unit proof.
- `conflicting_evidence`: apparent match with price, area, floor, contact, or media conflicts.
- `needs_unit_split`: grouped/development publication that should stay out of matching until unit evidence exists.

## Blocking Keys

Use deterministic blocking before scoring:

- normalized city + district + useful address
- source URL or source external ID
- area bucket
- price/status bucket
- rooms/floor/unit clues when present
- source family and contact/provenance hints

Do not use city-only or district-only placeholders as match keys.

## Score Components

- exact source URL/reference match
- normalized address/building/project match
- area similarity
- price or price-status compatibility
- rooms/floor/unit clues
- contact/agency relation
- photo hash or media-overlap evidence when available
- first/last seen lifecycle compatibility

Hard blockers override any score: grouped/development, pending QA, `LOST`, inactive, numeric zero as real price, contradictory area/price/media/unit evidence.

## Review Actions

- `link`
- `dismiss`
- `defer`
- `mark_conflict`
- `needs_unit_split`
- `needs_parser_repair`

Every action needs actor, timestamp, rationale, and immutable evidence snapshot.

## Next Handoff

- `backend_developer`: implement candidate APIs after BD-18/BD-19 DB proof.
- `ux_ui_designer`: render candidate review internally only.
- `debugger`: fixtures must include grouped/development negatives, same-complex false positives, conflicting price/area/media, and exact source duplicate cases.
