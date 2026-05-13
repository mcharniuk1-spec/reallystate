# SM-13 Social Overlay Evidence Queue And Handoff

Date: 2026-05-13
Owner: `scraper_sm`

## Queue States

| State | Meaning | Allowed next action |
|---|---|---|
| `discovered_public_candidate` | Candidate URL/name found from registry or public search | Validate public status and route |
| `manual_consent_required` | Platform/source requires operator capture or explicit consent | Wait for operator/manual sample |
| `official_api_candidate` | Platform has official API route but credentials/permissions are not verified | Create fixture and approval checklist |
| `partner_required` | Source needs partner/vendor/business route | Wait for contract/vendor docs |
| `blocked_private_or_group` | Private, login-gated, DM, or group content cannot be collected safely | Do not ingest |
| `redacted_fixture_ready` | Sample is redacted and testable offline | Parser/review tests allowed |
| `lead_only` | Message indicates demand/supply but lacks single-unit evidence | CRM lead only |
| `candidate_single_unit` | Message appears to describe one unit with price/location/contact/source evidence | Human review before source publication |
| `suspected_multi_unit` | Message suggests multiple units, development, price-from, or vague availability | Grouped/development review only |
| `noise` | No actionable real-estate signal | Exclude |
| `promotion_blocked` | Any legal/consent/redaction/evidence gate failed | Keep out of canonical listing |

## Required Envelope

Every stored social evidence record must include:

- `platform`
- `source_candidate_id`
- `channel_or_profile_url`
- `channel_type`
- `message_or_post_id`
- `posted_at`
- `captured_at`
- `capture_method`
- `legal_route`
- `consent_status`
- `redaction_applied`
- `raw_text_redacted`
- `media_refs`
- `source_links`
- `extracted.intent`
- `extracted.property_type`
- `extracted.city`
- `extracted.district`
- `extracted.price`
- `extracted.currency`
- `classification`
- `promotion_blockers`
- `review_status`

## Platform Handoff

Telegram:
- Use candidate file as validation queue.
- Start with `rentvarna`, `varnarents`, `kvartirivarna`, and `addressbg`.
- Add fixtures only from public/allowed samples and redact phones/emails/names before storage.

Facebook:
- Groups are manual/consent only.
- Pages require Graph API approval or manual review.
- Store only redacted operator-captured snippets or approved API payloads.

Instagram:
- Use Business Discovery/manual review.
- Treat as brand/project/source-link signal, not listing evidence, unless a post links to a canonical source URL and passes review.

Viber:
- Use commercial bot or partner/manual opt-in only.
- Invite links are not authorization to collect messages.

WhatsApp:
- Use WhatsApp Business Platform webhook for opted-in conversations only.
- Group invite links are not authorization to collect messages.

## Data Analyst Metrics

Report S&M separately from tier-1/2 marketplace inventory:

- candidates by platform
- candidates by route
- official API candidates
- manual/consent candidates
- blocked private/group candidates
- redacted fixtures ready
- lead-only messages
- candidate single-unit messages
- suspected multi-unit messages
- noise
- promotion blocked

## Acceptance Notes

FACT — No live collection was implemented.

INTERPRETATION — The next safe work is fixture expansion and route validation, not scraping.

HYPOTHESIS — Telegram will produce the first reliable automated overlay; Facebook and Instagram will mostly be manual/API-review support; Viber and WhatsApp will become inbound opt-in CRM channels.

GAP — Production credentials, legal approvals, consent records, and DB queue tables are not verified.
