---
name: publishing-compliance
description: Use for reverse publishing, channel capabilities, distribution profiles, dry-run adapters, compliance flags, and blocking unsafe account or private-channel automation.
---

# publishing-compliance

Use this skill for reverse publishing, channel capability, and compliance blockers.

## Read First
- `src/bgrealestate/publishing.py`
- `data/source_registry.json`
- `PLAN.md`

## Workflow
1. Build `channel_capability`, `distribution_profile`, `channel_mapping`, `publish_job`, `publish_attempt`, and `compliance_flag` flows.
2. Use dry-run adapters before real publishing.
3. Booking.com and Airbnb must use official/authorized partner routes.
4. Bulgarian portals must use feed/API/upload if available; otherwise assisted manual workflow.
5. Never automate mass account creation, KYC, CAPTCHA, or private-channel posting.

## Acceptance
- Unsafe channels are blocked with clear reasons.
- External listing IDs reconcile back to local state.
- Publishing attempts are auditable.
