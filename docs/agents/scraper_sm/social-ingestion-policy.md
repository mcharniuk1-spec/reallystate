# Social Ingestion Policy (SM-01)

Version: 1.0  
Date: 2026-04-08  
Owner agent: `scraper_sm`

## Scope

This policy defines allowed ingestion behavior for tier-4 social and messenger
sources from `data/source_registry.json`.

This is a **lead-intelligence overlay policy**, not a canonical listing policy.

## Allowed paths by source

| Source | legal_mode | access_mode | Allowed ingestion path |
| --- | --- | --- | --- |
| Telegram public channels | official_api_allowed | official_api | Official Telegram API/client for public channels only |
| X public search/accounts | official_api_allowed | official_api | Official X API only |
| Facebook public groups/pages | consent_or_manual_only | manual_consent_only | Manual/consent workflow only |
| Instagram public profiles | consent_or_manual_only | manual_consent_only | Manual/consent workflow only |
| Threads public profiles | consent_or_manual_only | manual_consent_only | Manual/consent workflow only |
| Viber opt-in communities | consent_or_manual_only | manual_consent_only | Opt-in/manual only |
| WhatsApp opt-in groups | official_partner_or_vendor_only | manual_consent_only | Official partner/vendor workflow only |

## Hard restrictions

1. No scraping of private groups, DMs, or login-gated content.
2. No mass account creation, KYC bypass, or CAPTCHA bypass.
3. No direct social content ingestion into `canonical_listing`.
4. All social content must be redacted before fixture/database persistence.
5. Tests for social parsing must remain offline fixture tests.

## Data handling and outputs

Expected output type: `lead_overlay`.

Minimum extracted fields:
- `intent`
- `property_type`
- `city`
- `district`
- `price`
- `currency`
- `phones` (redacted in fixtures)
- `is_noise`

## Consent checklist

- [ ] Source exists in registry with correct `legal_mode` and `access_mode`.
- [ ] Legal gate behavior is enforced before any live call.
- [ ] Only official API is used when `official_api_allowed`.
- [ ] Manual mode is enforced for `consent_or_manual_only`.
- [ ] Fixtures contain redacted content only (`redaction_applied=true`).
- [ ] No private identifiers (phones/emails/profile links) are stored unredacted.
- [ ] Parsed social data is tagged and routed as lead overlay only.
- [ ] Offline tests pass without network calls.

## Related files

- `docs/agents/scraper_sm/social_ingestion_contract.md` (detailed contract)
- `tests/fixtures/social/` (SM-01 templates)
- `tests/test_social_ingestion_contract.py` (policy/fixture tests)
