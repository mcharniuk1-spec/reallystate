# Messenger Publication Entity Plan — 2026-04-29

## Operating Rule

FACT — Project guardrails forbid unsafe broad scraping of WhatsApp, Viber, private Telegram channels, private Facebook groups, private Telegram groups, private-account access, CAPTCHA bypass, and mass account creation.

INTERPRETATION — Messenger content can be ingested only through official API, public-channel bot visibility, explicit consent/manual export, or partner/vendor routes.

## Platform Matrix

| Platform | Current registry source | Allowed access | Automated MVP route | Entity handling |
|---|---|---:|---|---|
| Telegram | `Telegram public channels` | `official_api_allowed` | Public channel bot/API capture only; no private channels | Save as redacted source publication candidate; promote only after single-unit evidence |
| WhatsApp | `WhatsApp opt-in groups` | `manual_consent_only` / partner-only | WhatsApp Cloud API webhook for business opt-in messages, or manual export with consent | Save as consent-gated publication candidate; human review before property entity |
| Viber | `Viber opt-in communities` | `manual_consent_only` | Viber commercial bot webhook or manual export with consent | Save as consent-gated publication candidate; human review before property entity |
| Facebook/Instagram | public profiles/groups | manual consent only | Manual/partner export until legal approval | CRM lead evidence first |
| X | public search/accounts | official API allowed | Official API fixture/live path | CRM lead evidence first |

## Candidate Record Contract

FACT — Social messages often mix lead, availability, questions, and informal price/location text.

INTERPRETATION — A messenger message is not a canonical property by default. It becomes a candidate source publication with review status.

Required candidate fields:

- `platform`
- `source_name`
- `channel_or_account`
- `message_id`
- `posted_at`
- `consent_status`
- `redaction_applied`
- `raw_text_redacted`
- `media_refs`
- `extracted.intent`
- `extracted.property_type`
- `extracted.city`
- `extracted.district`
- `extracted.price`
- `extracted.currency`
- `identity_status`: `lead_only`, `candidate_single_unit`, `suspected_multi_unit`, `noise`
- `review_status`: `needs_review`, `approved_for_property_entity`, `rejected`
- `promotion_blockers`

## Promotion Gate

Promote to `property_entity` only when all are true:

1. Message or linked detail proves one unit, not a building/development batch.
2. City/location evidence exists.
3. Price is numeric or explicit `on_request` / `undefined`, never numeric `0`.
4. Property type exists.
5. At least one contact/channel provenance route is consent-safe.
6. Media, if present, is stored locally or linked as traceability metadata after redaction.

## Next Slice Proposal

SM-08 should implement fixture-first candidate mapping for Telegram, WhatsApp manual export, and Viber manual export. It must not perform live network calls.

BD-19 should persist approved candidates into the canonical source-publication pipeline after SM-08 proves the schema and debugger signs off.

UX-15 should expose messenger candidates in admin/operator review, not public listing pages, until approved.
