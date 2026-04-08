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

