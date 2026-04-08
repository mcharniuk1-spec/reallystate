# Bugbot Review Rules

Prioritize findings in these areas:

- Scraper legal gates are missing or bypassed.
- Tests perform live network calls.
- Publishing adapters attempt unsupported account creation, CAPTCHA bypass, KYC bypass, or private-channel access.
- SQL queries risk injection or bypass tenant/account boundaries.
- Auth/RBAC checks are missing for CRM, settings, API keys, publishing, and admin routes.
- Temporal workflows are not idempotent or can duplicate side effects on retry.
- Raw captures, contact data, or message logs leak secrets or private information.
- Frontend map/list/chat state can show stale or cross-account data.
- Media binaries are stored directly in PostgreSQL instead of object storage.
- High-risk sources are treated as normal public-crawl sources.
