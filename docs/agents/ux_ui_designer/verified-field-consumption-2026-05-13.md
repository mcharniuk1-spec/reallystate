# UX Verified Field Consumption Contract

Date: 2026-05-13

## Rule

UX must consume only verified dashboard/read-model fields. File-backed fields can appear in operator/admin dashboards with clear labels. Buyer-facing pages require accepted-only DB/read-model proof.

## Allowed Now For Operator/Admin

- DA-01/DA-02 file-backed counts when labeled as file-backed.
- Action1 quality-gate counts when labeled as quality-gate estimates/rollups.
- Importer default candidate counts when labeled as importer eligibility, not market inventory.
- Media capture counts when labeled as gallery/media capture, not semantic image descriptions.
- DB blockers from `BD-18`, `INFRA-02`, and `make verify-db-counts`.

## Not Allowed For Buyer-Facing UI Yet

- Raw saved-listing totals as available properties.
- Pending QA rows.
- `LOST`, needs-rescrape, inactive, removed, expired, sold, or rented rows.
- Grouped/development publications as normal property cards.
- Semantic room/condition/equipment descriptions before Action0 and local-gallery verification.
- Complete-market, 95% coverage, or city trend claims.

## Required Labels

- `File-backed audit`
- `Quality-gate estimate`
- `Importer candidate`
- `DB-backed verified`
- `Blocked: missing DATABASE_URL`
- `Grouped/development source publication`
- `Image description not generated`

## Next UX Work

- `UX-16`: admin source-publication QA queues can use file-backed fields with labels.
- `UX-18`: buyer-facing trust labels remain blocked until `BD-19` read model and debugger proof.
- `UX-21`: in-platform four-dashboard shell must preserve the same labels and blockers.
