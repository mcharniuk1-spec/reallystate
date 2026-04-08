# Scraper SM (social media overlays) journey

## Scope
- Lead-intelligence overlays only.
- Must remain consent-gated or official-API-only (no private group scraping).

## Executed tasks (append-only)

### Task 0: Social ingestion contract (policy + fixtures + consent checklist)
- **Started**: 2026-04-08
- **Action**: Produced the social ingestion contract as specified in `docs/agents/TASKS.md`.
- **Deliverables**:
  1. **Policy document**: `docs/agents/scraper_sm/social_ingestion_contract.md`
     - Source inventory table (all 7 tier-4 sources with legal mode + allowed path)
     - Hard rules: no private scraping, no login-gated access, no mass accounts
     - Only Telegram public channels approved for automated ingestion in MVP
     - X/Twitter deferred to post-MVP
  2. **Fixture format**: JSON envelope with `source_name`, `channel_id`, `message_id`, `posted_at`, `raw_text` (redacted), `media_urls`, `extracted` fields, `redaction_applied`, `consent_status`
  3. **Telegram fixtures**:
     - `tests/fixtures/telegram_public/rent_listing/` — rental lead, Варна/Чайка, 400 EUR
     - `tests/fixtures/telegram_public/sale_listing/` — sale lead, София/Лозенец, 185k EUR
     - `tests/fixtures/telegram_public/noise_message/` — non-real-estate chatter
  4. **Regex-based social lead parser**: `src/bgrealestate/connectors/social_parser.py`
     - Bulgarian keyword extraction for intent, property type, city, district, price
     - Noise classification
  5. **Redaction policy**: phones/emails/names/private-profile-links stripped before storage
  6. **Consent checklist**: 10-item pre-launch checklist for each social source
- **Tests**: `tests/test_social_ingestion_contract.py`
  - `TestSocialLegalGates`: all 7 social/messenger sources blocked by `assert_live_http_allowed`
  - `TestTelegramFixtureParsing`: 3 fixture cases (rent, sale, noise) pass
  - `TestRedactionContract`: all fixtures have `redaction_applied=true`, no raw phone numbers
- **Verification**: `make test` → 62 tests, 54 pass, 8 skipped, 0 failures.
- **Status**: DONE

## Review comments (after each task)

### 2026-04-08 (follow-up) — SM-01 deliverable alignment

- **Action**: Aligned SM-01 outputs to exact task contract in `docs/agents/TASKS.md`.
- **Added**:
  - `docs/agents/scraper_sm/social-ingestion-policy.md` (requested policy filename)
  - `tests/fixtures/social/README.md`
  - `tests/fixtures/social/telegram_public_message.template.json`
  - `tests/fixtures/social/x_public_message.template.json`
  - `tests/fixtures/social/manual_consent_message.template.json`
- **Task board update**: `SM-01` set to `DONE_AWAITING_VERIFY` (verifier: debugger).
- **Notes**:
  - Existing detailed contract remains at `docs/agents/scraper_sm/social_ingestion_contract.md`.
  - Existing executable fixtures/tests remain in `tests/fixtures/telegram_public/` and `tests/test_social_ingestion_contract.py`.

### 2026-04-08 (follow-up) — SM-02 Telegram public channel connector (fixture-first)

- **Action**: Implemented Telegram social connector mapper that transforms redacted public-channel payloads into CRM-ready `lead_thread` + `lead_message` dictionaries and a `RawCapture` envelope.
- **Added**:
  - `src/bgrealestate/connectors/telegram_public.py`
    - `TelegramPublicConnector.map_message_to_crm(...)`
    - strict source/consent/redaction checks
    - deterministic IDs for idempotent mapping
    - extracted lead metadata via `extract_social_lead(...)`
  - `tests/test_telegram_public_connector.py`
    - rent/sale/noise fixture mapping tests
    - non-redacted fixture rejection test
- **Commands / verification**:
  - `PYTHONPATH=src python3 -m unittest tests.test_telegram_public_connector -v` → 4/4 pass
  - `make test` → fails due unrelated tier-3 parser_version expectation mismatches (`test_tier3_bcpea_fixture_parsing`, `test_tier3_licensed_fixture_parsing`, `test_tier3_official_register_wrappers`, `test_tier3_partner_stubs`)
- **Status**: BLOCKED (external)
- **Blocker**: SM-02 acceptance gate requires `make test` full pass; currently blocked by `scraper_t3` failures not caused by SM-02.
- **Review comments**:
  - Connector remains offline fixture-first and does not perform live Telegram network calls.
  - Once tier-3 tests are green, rerun `make test` and flip SM-02 to `DONE_AWAITING_VERIFY`.

### 2026-04-08 (follow-up) — SM-03 X public monitor connector (fixture-first)

- **Action**: Implemented X public connector mapper for official-API public profile payloads, fixture-first and offline.
- **Added**:
  - `src/bgrealestate/connectors/x_public.py`
    - `XPublicConnector.map_post_to_lead(...)`
    - strict source/consent/redaction checks (`consent_status=public_profile_via_official_api`)
    - deterministic thread/message IDs
    - extracted lead metadata via `extract_social_lead(...)`
  - `tests/test_x_public_connector.py`
    - sale/noise mapping tests
    - redaction enforcement + no raw phone checks
  - `tests/fixtures/x_public/sale_post/{raw.json,expected.json}`
  - `tests/fixtures/x_public/noise_post/{raw.json,expected.json}`
- **Commands / verification**:
  - `PYTHONPATH=src python3 -m unittest tests.test_x_public_connector -v` → 4/4 pass
  - `PYTHONPATH=src python3 -m unittest tests.test_social_ingestion_contract tests.test_telegram_public_connector tests.test_x_public_connector -v` → 14/14 pass
- **Status**: DONE_AWAITING_VERIFY
- **Acceptance gate**:
  - `make test` → 86 tests OK, 11 skipped (full-suite gate now satisfied)
- **Review comments**:
  - X connector mirrors Telegram mapper contract so debugger/backend can verify CRM round-trip consistently.
  - No live API calls were added; all behavior validated via fixtures.

### 2026-04-08 (follow-up) — SM-02 blocker cleared

- **Action**: Re-ran full acceptance gate after repository-wide test fixes landed.
- **Verification**:
  - `make test` → 86 tests OK, 11 skipped
- **Status update**:
  - `SM-02` moved from `BLOCKED` to `DONE_AWAITING_VERIFY` in `docs/agents/TASKS.md`.

### 2026-04-08 (follow-up) — SM-06 Tier-4 links + post/message DB package + PDF plan

- **Action**: Added a full tier-4 operational package to sync social links to DB, prepare one-row-per-message social datasets, and generate a paragraph-based `Tier4plan.pdf`.
- **Added**:
  - `src/bgrealestate/social_tier4.py`
    - collect tier-4 links from `data/source_registry.json`
    - collect fixture-backed tier-4 posts/messages (Telegram + X)
    - export JSON/CSV datasets (`tier4-social-links`, `tier4-social-posts`)
  - `src/bgrealestate/social_seed.py`
    - build fixture-backed CRM payloads
    - seed `lead_thread`, `lead_message`, `raw_capture` rows into DB (`seed-social-fixtures`)
  - `scripts/generate_tier4_plan.py`
    - writes `docs/exports/Tier4plan.md` and `docs/exports/Tier4plan.pdf`
  - CLI updates in `src/bgrealestate/cli.py`
    - `sync-social-database`
    - `export-tier4`
    - `seed-social-fixtures`
  - Makefile targets
    - `sync-social-registry`, `export-tier4-data`, `seed-social-fixtures`, `tier4-plan`
- **Commands / verification**:
  - `PYTHONPATH=src python3 -m bgrealestate export-tier4 --out-dir docs/exports`
  - `python3 scripts/generate_tier4_plan.py`
  - `make test` (full suite)
- **Status**: DONE_AWAITING_VERIFY
- **Review comments**:
  - All outputs remain fixture-first and legal-gated; no live social scraping was introduced.
  - Facebook/Instagram/Threads/Viber/WhatsApp stay consent/manual or official-partner mode per policy.

### 2026-04-08 (follow-up) — SM-05 social collection options decision matrix

- **Action**: Completed cross-platform collection options analysis for all tier-4 sources with legality, reliability, cost-band, and rollout recommendation.
- **Added**:
  - `docs/agents/scraper_sm/social-collection-options.md`
    - matrix for Telegram, X, Facebook, Instagram, Threads, Viber, WhatsApp
    - pros/cons, cost profile bands, legal access path per platform
    - operator recommendation: Telegram + X automated, Facebook/Instagram manual-consent, others deferred/partner-only
- **Status**: DONE_AWAITING_VERIFY
- **Review comments**:
  - No connector/runtime changes introduced in this slice (doc-only by contract).
  - Recommendations remain aligned with `source_registry` legal modes and SM-01 policy.

### 2026-04-08 (follow-up) — SM-07 Facebook path decision (consent-gated defer)

- **Action**: Executed SM-07 as a legal decision output and deferred autonomous Facebook scraping in MVP.
- **Added**:
  - `docs/agents/scraper_sm/facebook-public-groups-decision.md`
    - explicit no-go for autonomous scrape
    - approved manual/consent workflow
    - revisit conditions (documented legal approval + fixture-first testability)
- **Status**: DONE_AWAITING_VERIFY
- **Review comments**:
  - Decision matches hard guardrails: no private/login-gated social scraping.
  - Keeps tier-4 automation focus on Telegram + X official paths.

### After Task 0
- The contract correctly blocks all 7 social sources at the legal gate layer. Even Telegram, which is the only approved automated path, is blocked by `assert_live_http_allowed` because `source_family=social_public_channel` always triggers the family block. This is correct: the social connector will need a dedicated `assert_telegram_api_allowed` function that checks `legal_mode=official_api_allowed` but bypasses the family block.
- Fixture JSON format is deliberately simple (flat envelope + extracted fields) to keep the parser testable offline. Production Telegram ingestion will wrap this in the standard `RawCapture` model.
- The regex NLP parser handles the most common Bulgarian patterns (продавам/отдавам + property keywords + city names) but will miss colloquial phrasings. LLM-based enrichment is noted as a future phase.
- Noise detection is binary (has real-estate signal or not). A confidence score would be better for production.

### Files changed
```
New files:
  docs/agents/scraper_sm/social_ingestion_contract.md
  src/bgrealestate/connectors/social_parser.py
  tests/test_social_ingestion_contract.py
  tests/fixtures/telegram_public/rent_listing/{raw.json, expected.json}
  tests/fixtures/telegram_public/sale_listing/{raw.json, expected.json}
  tests/fixtures/telegram_public/noise_message/{raw.json, expected.json}
```

