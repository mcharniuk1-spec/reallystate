# Scraper T3 (vendor/partner/official routes) journey

## Scope

- Tier-3 sources that require official API, partner feed, licensed data, or vendor contracts.
- Sources: Airbnb (partner feed), Booking.com (partner feed), Vrbo (partner feed), Flat Manager (partner feed), Menada Bulgaria (partner feed), AirDNA (licensed data), Airbtics (licensed data), Property Register (manual/consent), KAIS Cadastre (manual/consent), BCPEA property auctions (public crawl).
- No unauthorized scraping — every source in this tier has explicit legal/contractual barriers.
- Integration patterns: REST API clients, partner feed parsers, licensed data importers, official e-service query wrappers.

## Executed tasks (append-only)

### 2026-04-08 — T3-01: Tier-3 ingestion policy and integration contracts

- **Action**: Authored Tier-3 policy with per-source legal/access/risk routes and integration contracts; created fixture template packs for partner feed, licensed data, official register, and public auction parsing.
- **Changed files**:
  - `docs/agents/scraper_t3/tier3-ingestion-policy.md`
  - `tests/fixtures/tier3_templates/README.md`
  - `tests/fixtures/tier3_templates/partner_feed/raw.json`
  - `tests/fixtures/tier3_templates/partner_feed/expected.json`
  - `tests/fixtures/tier3_templates/partner_feed/seed.json`
  - `tests/fixtures/tier3_templates/licensed_data/raw.json`
  - `tests/fixtures/tier3_templates/licensed_data/expected.json`
  - `tests/fixtures/tier3_templates/official_register/raw.json`
  - `tests/fixtures/tier3_templates/official_register/expected.json`
  - `tests/fixtures/tier3_templates/official_register/seed.json`
  - `tests/fixtures/tier3_templates/public_auction/raw.html`
  - `tests/fixtures/tier3_templates/public_auction/expected.json`
  - `docs/agents/TASKS.md` (status update only)
- **Commands run**: none
- **Tests run**: none (T3-01 acceptance is policy/fixture-definition review by verifier)
- **Status**: DONE_AWAITING_VERIFY
- **Review comments**: Next slices (T3-02..T3-05) should consume `tier3_templates` as baseline fixture contracts and enforce `PartnerContractRequired`/`OperatorConsentRequired` before live network calls.

### 2026-04-08 — T3-02: AirDNA / Airbtics licensed data importer (fixture-first)

- **Action**: Implemented licensed STR metrics parser connector (`LicensedStrDataConnector`) with fixture-backed tests for AirDNA and Airbtics.
- **Changed files**:
  - `src/bgrealestate/connectors/tier3.py`
  - `tests/test_tier3_licensed_fixture_parsing.py`
  - `docs/agents/TASKS.md` (status update only)
- **Commands run**:
  - `PYTHONPATH=src python3 -m unittest tests.test_tier3_licensed_fixture_parsing -v`
  - `make test`
- **Tests run**: pass
- **Status**: DONE_AWAITING_VERIFY
- **Review comments**: `metrics_to_dict` output stays intentionally table-ready so backend can persist into dedicated STR analytics storage in a follow-up slice.

### 2026-04-08 — T3-03: BCPEA property auctions connector (fixture-first)

- **Action**: Implemented `BcpeaAuctionConnector` with fixture parser extracting starting price, area, address, court, bailiff, and auction dates.
- **Changed files**:
  - `src/bgrealestate/connectors/tier3.py`
  - `src/bgrealestate/connectors/factory.py`
  - `src/bgrealestate/connectors/__init__.py`
  - `tests/test_tier3_bcpea_fixture_parsing.py`
  - `docs/agents/TASKS.md` (status update only)
- **Commands run**:
  - `PYTHONPATH=src python3 -m unittest tests.test_tier3_bcpea_fixture_parsing -v`
  - `make test`
- **Tests run**: pass
- **Status**: DONE_AWAITING_VERIFY
- **Review comments**: live HTTP path remains legal-gated through `assert_live_http_allowed`; parser remains fixture-first.

### 2026-04-08 — T3-04: Partner feed stub connectors (Airbnb/Booking.com/Vrbo)

- **Action**: Implemented `PartnerFeedStubConnector` stubs with fixture parsing and hard live-call block via `PartnerContractRequired`.
- **Changed files**:
  - `src/bgrealestate/connectors/tier3.py`
  - `src/bgrealestate/connectors/factory.py`
  - `src/bgrealestate/connectors/__init__.py`
  - `tests/test_tier3_partner_stubs.py`
  - `docs/agents/TASKS.md` (status update only)
- **Commands run**:
  - `PYTHONPATH=src python3 -m unittest tests.test_tier3_partner_stubs -v`
  - `make test`
- **Tests run**: pass
- **Status**: DONE_AWAITING_VERIFY
- **Review comments**: live integration stays intentionally blocked until contract-backed feed clients are added.

### 2026-04-08 — T3-05: Official register query wrappers (Property Register / KAIS Cadastre)

- **Action**: Implemented `OfficialRegisterWrapper` with consent-gated live query path and fixture-backed parser for redacted official responses.
- **Changed files**:
  - `src/bgrealestate/connectors/tier3.py`
  - `src/bgrealestate/connectors/__init__.py`
  - `tests/test_tier3_official_register_wrappers.py`
  - `docs/agents/TASKS.md` (status update only)
- **Commands run**:
  - `PYTHONPATH=src python3 -m unittest tests.test_tier3_official_register_wrappers -v`
  - `make test`
- **Tests run**: pass
- **Status**: DONE_AWAITING_VERIFY
- **Review comments**: query wrapper enforces manual/consent workflow and blocks autonomous official-service querying.

### 2026-04-08 — T3-06: Varna-focused enrichment handoff (post stage-1 gate)

- **Action**: Reviewed next slice dependencies before starting implementation.
- **Changed files**:
  - `docs/agents/TASKS.md` (blocker annotation and status update)
- **Commands run**: none
- **Tests run**: none
- **Status**: BLOCKED (`DBG-05` is `TODO`; `T3-02` and `T3-05` not yet `VERIFIED`)
- **Review comments**: Slice cannot start until dependency statuses are advanced by verifier. Resume with `docs/agents/scraper_t3/varna-enrichment-handoff.md` immediately after verifier clears gates.

### 2026-04-08 — CONST-02: Cross-agent note propagation (scraper_t3 blockers)

- **Action**: Propagated Tier-3 blocker mapping into task queue so verifier execution is explicit for unblock path.
- **Changed files**:
  - `docs/agents/TASKS.md` (added mapped follow-up slices to T3-06)
- **Commands run**: none
- **Tests run**: none
- **Status**: DONE_AWAITING_VERIFY
- **Review comments**: `scraper_t3` has no unblocked implementation slice until debugger completes `DBG-06` and `DBG-05`.

### 2026-04-08 — T3-07: BCPEA live scraper (public auctions — legal to crawl)

- **Action**: Built full live scraper for BCPEA property auction register (sales.bcpea.org). Fetched real HTML to understand actual site structure (server-rendered, not SPA). Implemented discovery pagination, detail page parsing, rate limiting, CLI command, Makefile targets, and realistic fixture-backed tests. Successfully scraped 180 real auction listings with full detail (property type, area, price EUR/BGN, court, bailiff, dates, photos, descriptions, scanned PDF documents, bailiff phone/mobile).
- **Changed files**:
  - `src/bgrealestate/connectors/tier3.py` (added `BcpeaDiscoveryItem`, `BcpeaDiscoveryPage`, `parse_bcpea_discovery_html`, `parse_bcpea_detail_html`, rewrote `BcpeaAuctionConnector` with live fetch, discovery pagination, rate limiting, detail parsing; kept legacy `parse_auction_html` for T3-03 backward compat)
  - `src/bgrealestate/connectors/__init__.py` (exported new types and functions)
  - `src/bgrealestate/cli.py` (added `scrape-bcpea` command with `--pages`, `--perpage`, `--rate-limit`, `--fetch-details`, `--out-dir`, `--dry-run`)
  - `Makefile` (added `scrape-bcpea` and `scrape-bcpea-dry` targets)
  - `tests/test_bcpea_live_scraper.py` (new: 7 fixture-backed tests for discovery parsing, detail parsing, backward compat)
  - `tests/fixtures/bcpea/discovery_page1/raw.html` (new: realistic discovery page fixture from real site structure)
  - `tests/fixtures/bcpea/discovery_page1/expected.json` (new: expected parse output)
  - `tests/fixtures/bcpea/detail_87739/raw.html` (new: realistic detail page fixture from real site structure)
  - `tests/fixtures/bcpea/detail_87739/expected.json` (new: expected parse output)
  - `docs/agents/TASKS.md` (status update)
- **Commands run**: `make scrape-bcpea` (5 pages x 36 per page = 180 listings discovered + 180 detail pages fetched)
- **Tests run**: 156 total (7 new), 0 failures, 1 skipped
- **Outputs produced**: `output/bcpea/discovery.json` (180 items), `output/bcpea/details.json` (180 detail records)
- **Status**: DONE_AWAITING_VERIFY
- **Review comments**: BCPEA is `public_crawl_with_review` legal mode — live crawl passes `assert_live_http_allowed`. Rate limit default 1.5s between requests. Prices parsed in both EUR and BGN (лв). Property types extracted from `item__wrapper` header on detail pages. Legacy T3-03 template parser preserved for backward compat. Next: integrate into scraper orchestration loop (BD-15) and unification pipeline.
