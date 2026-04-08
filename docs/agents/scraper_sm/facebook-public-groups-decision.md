# SM-07 Facebook Public Groups Decision

Date: 2026-04-08  
Owner: `scraper_sm`

## Decision

Do not implement an autonomous Facebook scraper in MVP.

Proceed with a **consent-gated manual workflow** only, aligned with `legal_mode=consent_or_manual_only` for `Facebook public groups/pages`.

## Why this decision

Facebook group/page access is operationally unstable for unattended extraction and has elevated compliance risk when attempted as broad automation. This conflicts with project guardrails that prohibit unsafe/private scraping patterns.

## Approved MVP path

1. Operator curates approved public group/page targets in a reviewed list.
2. Operator-assisted capture is done manually or through explicitly approved official methods.
3. Captured data is redacted and transformed into lead-overlay records only.
4. Output is routed to CRM (`lead_thread`, `lead_message`) with provenance in `raw_capture`.

## Not approved in MVP

- Login-gated scraping at scale
- Private-group harvesting
- Any automation pattern that bypasses platform or consent boundaries

## Trigger to revisit

Re-open implementation only if both are true:

1. Explicit legal approval for a stable official access path is documented.
2. The access path can be tested fixture-first without introducing live-network dependency in default tests.

## Immediate next action

Keep Facebook in manual/consent mode and prioritize Telegram + X official API channels for automated tier-4 throughput.
