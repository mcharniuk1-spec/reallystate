# S&M Tier-3/Tier-4 Intelligence Paths — 2026-05-13

Purpose: prepare legal, consent, partner, and manual intelligence routes that can later complement data analyst findings without unsafe scraping and without mixing overlay signals into canonical listings.

## Boundary

FACT — `scraper_sm` owns tier-3 official/vendor/partner routes and tier-4 social/messenger overlays.

FACT — `data/source_registry.json` classifies tier-3/tier-4 sources by `legal_mode`, `risk_mode`, and `access_mode`.

FACT — S&M signals are source publications, CRM evidence, STR analytics overlays, partner-route candidates, or review candidates first.

INTERPRETATION — The useful next work is not more crawling. It is evidence-path design, fixture contracts, consent gates, and review queues that let data analyst compare overlay evidence against accepted marketplace rows later.

HYPOTHESIS — The highest near-term value comes from BCPEA auction evidence, licensed STR metrics, partner feed eligibility, Telegram/X public lead overlays, and manual/consent brand/social monitoring.

GAP — Live credentials, partner contracts, official API access, consent records, and DB-backed review tables are not confirmed in this run.

## Legal/Consent Blockers

| Source/path | Allowed route | Blocker before live use | Output class |
|---|---|---|---|
| Airbnb | Official authorized partner integration only | partner contract/API access | partner inventory or publishing capability evidence |
| Booking.com | Connectivity/content partner APIs only | certification/contract/API access | partner inventory or publishing capability evidence |
| Vrbo | Partnership or licensed feed | contract/API access | partner inventory or STR channel evidence |
| Flat Manager | Partnership or direct booking integration | written partner route | managed-STR inventory candidate |
| Menada Bulgaria | Partnership/direct booking integration | written partner route | managed-STR inventory candidate |
| AirDNA | Licensed export or enterprise contract | license/export sample | STR metric snapshot |
| Airbtics | REST API or licensed export | license/API key/export sample | STR metric snapshot |
| BCPEA property auctions | Public crawl with review | rate limit/review queue/fixture parity | auction source publication |
| KAIS Cadastre | Official services and permitted exports only | consent/manual operator action/export rights | parcel/building verification evidence |
| Property Register | Official e-service queries only | consent/manual operator action/legal basis | ownership verification evidence |
| Telegram public channels | Official API/client for public channels only | token/session approval, public-channel list, redaction gate | redacted lead signal |
| X public search/accounts | Official API only | API access/rate-limit policy | public lead/news/backlink signal |
| Facebook groups/pages | Manual monitoring or explicit partnership | legal approval and manual/partner capture path | manual social lead evidence |
| Instagram public profiles | Authorized business integrations or manual review | official approval or manual capture procedure | brand/project signal |
| Threads profiles | Deferred until access review | confirmed official/public read path | deferred signal only |
| Viber communities | Opt-in community ingestion only | explicit opt-in and bot/manual export path | consented messenger lead evidence |
| WhatsApp groups | WhatsApp Business/vendor route only | partner/vendor contract plus explicit opt-in | consented business-message evidence |

## Evidence Paths

### Official/Register Evidence

FACT — BCPEA is `public_crawl_with_review`; KAIS and Property Register are `consent_or_manual_only`.

INTERPRETATION — These sources should support verification and opportunistic auction intelligence, not broad acquisition.

Next task: `SM-11` should define the official-evidence queue, review states, fixture requirements, and data analyst comparison fields.

### Vendor/Analytics Evidence

FACT — AirDNA and Airbtics are licensed-data sources.

INTERPRETATION — Their output should be aggregated STR metrics by geography, property type, date window, and confidence, not listing rows.

Next task: `SM-12` should define licensed export/API fixture schemas and the blocker checklist for real credentials.

### Partner/Distribution Evidence

FACT — Airbnb, Booking.com, Vrbo, Flat Manager, and Menada require partner, vendor, direct-booking, or official integration routes.

INTERPRETATION — Treat them as contract-backed import/export/distribution candidates. They can later enrich channel availability, publishing eligibility, and managed-STR signals.

Next task: `SM-12` should keep partner feed stubs live-call blocked until contracts and docs exist.

### Social/Messenger Overlay Evidence

FACT — Telegram and X have official API paths. Facebook, Instagram, Threads, Viber, and WhatsApp are manual/consent/partner-only or deferred.

INTERPRETATION — These channels should create redacted lead signals, CRM threads, and publication candidates only. They must not create canonical listings without single-unit evidence and operator review.

Next task: `SM-13` should define the social-overlay review queue and data analyst handoff metrics.

## Separation Contract

1. Store S&M evidence as `lead_thread`, `lead_message`, review candidate, source publication, or analytics overlay.
2. Do not write S&M evidence directly as a canonical listing.
3. Promotion requires legal allowance, consent proof where needed, redaction, single-unit evidence, operator review, and data analyst accepted status.
4. Dashboards must show S&M signals separately from tier-1/2 marketplace completeness.
5. Tests remain fixture-first and must not depend on live network calls.

## Next Task Set

| Task | Purpose | Status after this run |
|---|---|---|
| `SM-10` | Record this tier-3/tier-4 intelligence path matrix | `DONE_AWAITING_VERIFY` |
| `SM-11` | Official/register evidence queue for BCPEA, KAIS, and Property Register | `TODO` |
| `SM-12` | Vendor/partner readiness for STR metrics and partner feeds | `TODO` |
| `SM-13` | Social-overlay evidence queue and data analyst handoff | `TODO` |

