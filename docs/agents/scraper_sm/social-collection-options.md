# SM-05 Social Collection Options (Decision Matrix)

Date: 2026-04-08  
Owner: `scraper_sm`  
Scope: Tier-4 social overlays (`Telegram`, `X`, `Facebook`, `Instagram`, `Threads`, `Viber`, `WhatsApp`)

## Objective

Define reliable and compliant collection options for tier-4 sources, including legal feasibility, operational complexity, expected cost profile, and recommendation for MVP.

This document is for lead-intelligence overlays only. It does not change the canonical listing ingestion policy.

## Evaluation criteria

- **Legality/compliance fit**: can we operate inside `legal_mode` and platform policy?
- **Reliability**: stable access path (API or authorized workflow) over time.
- **Data utility**: likelihood of extracting useful housing leads (rent/sale/intents).
- **Operational effort**: implementation and maintenance complexity.
- **Cost profile**: expected direct + indirect operating costs.

## Decision matrix

| Platform | Registry legal/access mode | Collection options | Pros | Cons | Cost profile | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| Telegram public channels | `official_api_allowed` / `official_api` | Telegram official API/client over public channels only | High lead volume; frequent updates; channel IDs are stable; good fit for NLP extraction | Requires token/session management; message quality is noisy; dedupe load can be high | Low-Medium (infra + maintenance) | **Primary MVP social channel** |
| X public search/accounts | `official_api_allowed` / `official_api` | Official X API (search/accounts) | Public-first model; structured metadata; useful for signal and backlinks | API quotas/policy variability; lead density lower than Telegram for local RE | Medium (API + ops) | **Secondary MVP channel** |
| Facebook public groups/pages | `consent_or_manual_only` / `manual_consent_only` | Manual/consent workflow; optional approved Graph API route if legal scope is explicit | Very active local groups; strong rental lead potential | Login and policy constraints; unstable scraping surface; high compliance risk if automated | Medium-High (manual ops + moderation) | **Manual pilot only (no autonomous scraping)** |
| Instagram public profiles | `consent_or_manual_only` / `manual_consent_only` | Manual profile monitoring; consent-based submissions; official approved API only | Good agency branding and project discovery signals | Most content is marketing-heavy; limited structured listing fields; compliance constraints | Medium (manual + review) | **Manual enrichment only** |
| Threads public profiles | `consent_or_manual_only` / `manual_consent_only` | Manual/experimental monitoring only | Potential trend signal channel | Unclear data value for property leads; API/read pathways still uncertain | Low-Medium (but uncertain ROI) | **Defer (watchlist)** |
| Viber opt-in communities | `consent_or_manual_only` / `manual_consent_only` | Explicit opt-in community workflows only | Can capture local high-intent conversations | Private-messaging context; weak programmatic extraction options; high consent overhead | Medium-High (ops-heavy) | **Defer to opt-in partner program** |
| WhatsApp opt-in groups | `official_partner_or_vendor_only` / `manual_consent_only` | Official WhatsApp Business/vendor integrations with explicit consent | Strong business messaging ecosystem when formalized | Contract/vendor dependency; high compliance bar; private message context | High (vendor + compliance + ops) | **Partner-only, post-MVP** |

## Recommended rollout

1. **MVP live path**: Telegram (primary) + X (secondary), both via official API routes.
2. **Parallel manual overlays**: Facebook + Instagram through operator-assisted consent workflow only.
3. **Deferred channels**: Threads, Viber, WhatsApp until partner/compliance model is fully operational.

## Pricing and budget model (planning level)

Pricing changes frequently and depends on approval tiers, contracts, and message volumes. For planning, use cost bands instead of fixed values:

- **Low**: internal infra + storage + parser runtime only.
- **Medium**: infra plus API quota/usage and moderation time.
- **High**: partner/vendor contracts, compliance overhead, and active operator review.

For MVP budgeting, assume:

- Telegram: low-medium band
- X: medium band
- Facebook/Instagram manual ops: medium-high labor band
- WhatsApp partner route: high band

## Compliance guardrails (must hold for every option)

- No private group scraping, no DMs, no login-gated extraction without explicit authorization.
- No mass account creation or anti-bot bypass.
- Redaction is mandatory before storage.
- Social outputs are persisted as CRM lead overlays (`lead_thread`, `lead_message`, `raw_capture`) and not as direct canonical listings.
- Tests remain fixture-first and offline.

## Final recommendation for operator

Adopt a **two-lane social strategy**:

- **Lane A (automated, compliant)**: Telegram + X official API ingestion.
- **Lane B (assisted/manual, consent-gated)**: Facebook + Instagram review queue handled by operators.

Treat Viber/WhatsApp as partner/opt-in channels only and keep Threads in observation mode until a reliable compliant access path and clear lead ROI are proven.
