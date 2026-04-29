# Scraper activity snapshot

_Generated: 2026-04-29T08:18:13.809361+00:00_

Summary of **fixture and live** work across scraper lanes. Authoritative logs: `docs/agents/scraper_1/JOURNEY.md`, `docs/agents/scraper_t3/JOURNEY.md`, `docs/agents/scraper_sm/JOURNEY.md`.

## Scraper 1 (tier-1/2 marketplaces)

- **Tier-1:** All 10 sources have fixture paths: Homes.bg, OLX.bg (API JSON), alo.bg, imot.bg, BulgarianProperties, Address.bg, SUPRIMMO, LUXIMMO, property.bg, imoti.net (legal-gated live).
- **Parser hardening:** Bulgarian keywords for intent/category; legal gate on fetch-only for `legal_review_required` sources.
- **Discovery:** `parse_discovery_html` + OLX JSON discovery; fixtures for tier-1 discovery pagination (**S1-14**).
- **Tier-2 stubs:** bazar_bg, domaza, yavlena, home2u (**S1-12**).
- **Stage-1 product types:** Coverage matrix + tests (**S1-13**); export `docs/exports/stage1-product-type-coverage.md`.
- **CLI:** `ingest-fixture`, live-safe runner tests (**S1-11**).
- **Inventory:** `make scraping-inventory` → XLSX / MD / PDF under `docs/exports/`.
- **Media:** Download/proxy pipeline, `listing_media`, `download-images` CLI (**image pipeline** — see JOURNEY Task 18).
- **Live harvest (2026-04-09):** `scripts/live_scraper.py` + `make import-scraped`; file-backed corpus for multiple sources (e.g. Bazar.bg, BulgarianProperties, imot.bg, OLX.bg, Yavlena ~250 each); repaired Address.bg, SUPRIMMO, LUXIMMO, property.bg discovery. **S1-18** still requires PostgreSQL ingest evidence (`DATABASE_URL` + `canonical_listing` counts).

## Scraper T3 (tier-3)

- Policy + tier3 fixture templates (**T3-01**).
- Licensed STR metrics parser (**T3-02**), BCPEA auctions (**T3-03**), partner feed stubs (**T3-04**), official register wrappers (**T3-05**). Status: see `TASKS.md` / verifier.

## Scraper SM (tier-4 social)

- Social ingestion contract, Telegram fixtures, redaction tests (**SM-01**).
- Telegram connector mapper (**SM-02**); X public mapper (**SM-03**) — see JOURNEY for any BLOCKED notes tied to unrelated test failures.

---
Regenerate with `make dashboard-doc` (rewrites this file).
