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
