# Social Ingestion Contract

Version: 1.0 — 2026-04-08

## Purpose

This document defines the ingestion policy for all tier-4 social and messenger
sources in the Bulgaria Real Estate MVP. It is the binding reference for what
the `scraper_sm` agent and any future social connectors are allowed to do.

## Source inventory (from `data/source_registry.json`)

| Source | Family | access_mode | legal_mode | Allowed path |
|--------|--------|-------------|------------|--------------|
| Facebook public groups/pages | social_public_channel | manual_consent_only | consent_or_manual_only | Manual monitoring only; no automated scraping |
| Instagram public profiles | social_public_channel | manual_consent_only | consent_or_manual_only | Authorized business integrations or manual review only |
| Telegram public channels | social_public_channel | official_api | official_api_allowed | **Official Telegram Bot/Client API** — only public channels |
| Threads public profiles | social_public_channel | manual_consent_only | consent_or_manual_only | Deferred; no automated access |
| Viber opt-in communities | private_messenger | manual_consent_only | consent_or_manual_only | Explicit opt-in only; no automated scraping |
| WhatsApp opt-in groups | private_messenger | manual_consent_only | official_partner_or_vendor_only | WhatsApp Business API only; no group scraping |
| X public search/accounts | social_public_channel | official_api | official_api_allowed | Official X/Twitter API only |

## Hard rules

1. **No private group/messenger scraping.** Viber, WhatsApp, and private
   Facebook groups are permanently off-limits for automated ingestion.
2. **No login-gated scraping.** Any source that requires authentication to
   access content must use an official API or explicit partnership.
3. **No mass account creation or CAPTCHA bypass.**
4. **Telegram public channels are the only tier-4 source approved for
   automated ingestion in MVP**, using the official Bot API or TDLib client
   library against public channels only.
5. **X/Twitter** may be added post-MVP via official API (v2) with rate limits.
6. Social sources produce **lead-intelligence overlays**, not primary listings.
   They are never treated as canonical listing sources.

## Fixture format

All social overlay fixtures use the same JSON envelope:

```json
{
  "source_name": "Telegram public channels",
  "channel_id": "rentvarna",
  "message_id": 42001,
  "posted_at": "2026-04-06T14:32:00+03:00",
  "raw_text": "Отдавам двустаен апартамент Варна, кв. Чайка. 400 EUR/месец. Тел: [REDACTED]",
  "media_urls": [],
  "extracted": {
    "intent": "long_term_rent",
    "property_type": "apartment",
    "city": "Варна",
    "district": "Чайка",
    "price": 400,
    "currency": "EUR",
    "phones": []
  },
  "redaction_applied": true,
  "consent_status": "public_channel_broadcast"
}
```

Key fields:
- `raw_text`: the message after PII redaction (see below).
- `extracted`: NLP-parsed structured fields (best-effort).
- `redaction_applied`: must be `true` in all stored fixtures.
- `consent_status`: one of `public_channel_broadcast`, `opt_in_community`,
  `manual_operator_entry`, `not_determined`.

## Redaction policy (PII handling)

Before any social message text is stored (fixture, database, or log):

1. **Phone numbers** → replaced with `[REDACTED]`.
2. **Email addresses** → replaced with `[REDACTED]`.
3. **Full names** (when identifiable from context) → replaced with `[REDACTED]`.
4. **Profile links** to private accounts → removed entirely.
5. **Location precision**: city + district is kept; exact street addresses are
   redacted to district level unless publicly part of a listing URL.

Redaction must happen at ingestion time, before the message reaches the
database or any log file.

## Consent checklist

Before enabling any social source connector:

- [ ] Source is registered in `data/source_registry.json` with correct
      `legal_mode` and `access_mode`.
- [ ] `derive_default_legal_rule()` in `connectors/legal.py` returns the
      correct gate (blocks_live_scrape, requires_consent, etc.).
- [ ] `assert_live_http_allowed()` blocks the source if it is
      `social_public_channel` or `private_messenger` family.
- [ ] Access uses only the official API documented by the platform owner.
- [ ] No private groups, DMs, or login-gated content is accessed.
- [ ] PII redaction is applied before storage.
- [ ] Extracted data is tagged as `lead_overlay`, not `canonical_listing`.
- [ ] Operator review is required before any extracted lead is surfaced to CRM.
- [ ] Rate limits follow the official API terms of service.
- [ ] Fixture tests exist and pass without network access.

## Telegram public channel — implementation notes

Telegram is the only approved automated path for MVP:

- Use `telethon` or `python-telegram-bot` with a registered Bot token.
- Subscribe to public channels only (no join requests for private groups).
- Polling interval: per `freshness_target` = hourly.
- Message format: JSON as shown in fixture format above.
- NLP extraction: regex-first for Bulgarian property keywords (same keyword
  set as `GenericHtmlListingParser` in `pipeline.py`), with optional LLM
  enrichment in a later phase.
- Persistence: messages go into `raw_capture` with `content_type=application/json`
  and `source_name=Telegram public channels`. Extracted fields populate a
  `lead_overlay` table (schema TBD), not `canonical_listing`.

## What is NOT implemented

- Facebook group scraping
- Instagram scraping
- WhatsApp group monitoring
- Viber community monitoring
- Threads monitoring
- X/Twitter integration
- Any login-gated or private-account access

These remain blocked by `assert_live_http_allowed()` and the consent gates in
`derive_default_legal_rule()`.
