# Tier-3 Ingestion Policy and Integration Contracts

This policy defines the allowed ingestion route for Tier-3 sources and the required legal and operational controls.

Scope: `scraper_t3` sources only.

Guardrails:

- No unauthorized scraping for OTA partner-feed sources.
- No live-network dependency in tests; fixture-first only.
- Consent-only official register access must require explicit operator authorization.
- Every connector must enforce `legal_mode`, `risk_mode`, and `access_mode` from `data/source_registry.json`.

## Integration contract fields (required per source)

Each Tier-3 connector must require:

- `source_name`
- `access_mode`
- `legal_mode`
- `risk_mode`
- `authorization_artifact_id` (contract ID, subscription ID, or operator approval ticket)
- `allowed_live_calls` (boolean computed at runtime)
- `denial_reason` (explicit string when blocked)

## Source-by-source policy

| Source | Access mode | Legal mode | Risk mode | Allowed ingestion route | Blocked route | Action website |
| --- | --- | --- | --- | --- | --- | --- |
| Airbnb | `partner_feed` | `official_partner_or_vendor_only` | `prohibited_without_contract` | Official partner/vendor feed only after signed contract | Any crawler/headless scraping | [airbnb.com](https://www.airbnb.com/) |
| Booking.com | `partner_feed` | `official_partner_or_vendor_only` | `prohibited_without_contract` | Connectivity/content partner API/feed only | Any crawler/headless scraping | [booking.com](https://www.booking.com/) |
| Vrbo | `partner_feed` | `official_partner_or_vendor_only` | `high` | Partnership/licensed feed only | Any crawler/headless scraping | [vrbo.com](https://www.vrbo.com/) |
| Flat Manager | `partner_feed` | `official_partner_or_vendor_only` | `medium` | Direct partner feed or direct-booking integration only | Unapproved crawling beyond explicit contract scope | [reserve.flatmanager.bg](https://reserve.flatmanager.bg/) |
| Menada Bulgaria | `partner_feed` | `official_partner_or_vendor_only` | `medium` | Partner/direct integration only | Unapproved crawling beyond explicit contract scope | [menadabulgaria.com](https://menadabulgaria.com/) |
| AirDNA | `licensed_data` | `official_partner_or_vendor_only` | `low` | Licensed subscription export/API only | Any crawling or reverse engineering from OTA websites | [airdna.co](https://www.airdna.co/) |
| Airbtics | `licensed_data` | `official_partner_or_vendor_only` | `low` | Licensed REST/API only | Any crawling or reverse engineering from OTA websites | [airbtics.com](https://airbtics.com/) |
| BCPEA property auctions | `html` | `public_crawl_with_review` | `medium` | Public crawl allowed with legal review and OCR fallback for scanned notices | Bypassing legal review; overbroad non-scoped crawl | [sales.bcpea.org/properties](https://sales.bcpea.org/properties) |
| Property Register | `manual_consent_only` | `consent_or_manual_only` | `high` | Official e-service queries with explicit operator consent per query window | Any autonomous bulk crawl/query automation | [portal.registryagency.bg/en/home-pr](https://portal.registryagency.bg/en/home-pr) |
| KAIS Cadastre | `manual_consent_only` | `consent_or_manual_only` | `high` | Official service/export flows with explicit operator consent | Any autonomous bulk crawl/query automation | [kais.cadastre.bg/bg/Map](https://kais.cadastre.bg/bg/Map) |

## Runtime enforcement contract

Connectors must fail closed with explicit exceptions:

- `PartnerContractRequired`: contract/subscription missing for `official_partner_or_vendor_only`.
- `OperatorConsentRequired`: missing operator approval for `consent_or_manual_only`.
- `LegalReviewRequired`: source flagged for review path but not approved.

Before any live call:

1. Lookup source record from registry.
2. Verify connector mode equals registry `access_mode`.
3. Verify authorization artifact exists and is active.
4. If any check fails, raise one of the above exceptions before network access.

## Fixture format definition (Tier-3)

Tier-3 fixture templates are defined under `tests/fixtures/tier3_templates/`:

- `partner_feed/` for Airbnb, Booking.com, Vrbo, Flat Manager, Menada.
- `licensed_data/` for AirDNA and Airbtics.
- `official_register/` for Property Register and KAIS.
- `public_auction/` for BCPEA.

Template files:

- `raw.*` source payload sample (JSON/HTML)
- `expected.json` canonical parse expectation
- `seed.json` optional gate/seed metadata where needed

Redaction requirements:

- No personal identifiers from real persons.
- No real account IDs, contract IDs, tokens, or credentials.
- Use synthetic phone/email values in expected outputs.

## Per-source implementation pattern

- Airbnb/Booking.com/Vrbo/Flat Manager/Menada: `PartnerFeedConnector` stub with fixture parsing; live routes blocked unless contract present.
- AirDNA/Airbtics: `LicensedDataImporter` fixture parser for STR metrics payloads.
- BCPEA: `PublicAuctionConnector` parser with court/bailiff/date/price extraction and optional OCR branch.
- Property Register/KAIS: `OfficialRegisterWrapper` parser in manual/consent mode only.

## Acceptance mapping for T3-01

This document satisfies:

- Integration pattern defined for each Tier-3 source.
- Allowed/blocked legal route documented per source.
- Fixture format and redaction rules documented for Tier-3 templates.
