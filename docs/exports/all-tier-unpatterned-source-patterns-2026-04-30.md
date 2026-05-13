# All-tier unpatterned source candidate patterns (2026-04-30)

- FACT: this file persists reusable pattern candidates for current tier-1/2 unpatterned sources.
- INTERPRETATION: it is a durable planning artifact, not a live-proof claim.

## alo.bg

- Scope: `public_scrape_candidate`
- Promotion gate: `strict_sample_and_gallery_proof`
- Proposed pattern: `html_list_detail_gallery`
- Connector: `HtmlPortalConnector`
- Source route level: `entry_urls_saved`
- Source URLs: https://www.alo.bg/
- Section hypotheses:
  - `buy_personal` | `entry_urls_saved` | https://www.alo.bg/obiavi/imoti-prodajbi/apartamenti-stai/ | Section route is persisted in the Varna section registry; still needs strict item-level proof.
  - `buy_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_personal` | `entry_urls_saved` | https://www.alo.bg/obiavi/imoti-naemi/apartamenti-stai/ | Section route is persisted in the Varna section registry; still needs strict item-level proof.
  - `rent_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
- Detail requirements: title, price or price_status, city or address, description, image_urls, local_image_files, at least two structured fields
- Fixture cases: basic_listing, blocked_page, discovery_page
- Code paths: scripts/live_scraper.py::generic, scripts/live_scraper.py::_parse_alo_bg
- Issues:

## imoti.net

- Scope: `restricted_access_pattern`
- Promotion gate: `legal_or_partner_gate`
- Proposed pattern: `headless_list_detail_gallery`
- Connector: `HtmlPortalConnector`
- Source route level: `primary_url_only`
- Source URLs: https://www.imoti.net/
- Section hypotheses:
  - `buy_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `buy_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
- Detail requirements: title, price or price_status, city or address, description, image_urls, local_image_files, at least two structured fields
- Fixture cases: basic_listing, blocked_page
- Code paths: scripts/live_scraper.py::generic
- Issues:
  - `LEGAL-01` Legal or contract gate blocks promotion: Current legal_mode=legal_review_required, access_mode=headless. :: 1. Validate whether a public scraping pattern is allowed at all. ; 2. If not, switch the source to partner-feed, official API, licensed-data, or manual-only execution. ; 3. Do not attempt live pattern promotion until the legal gate changes.
  - `ROUTE-01` Section or list-route discovery is incomplete: Current route evidence level is primary_url_only. :: 1. Map buy/rent and residential/commercial landing pages explicitly. ; 2. Persist section entry URLs and pagination rules. ; 3. Add at least one route per supported bucket before scaling.
  - `PARSE-01` Only generic HTML parser is wired: The source currently relies on the generic JSON-LD/og:image parser path. :: 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery. ; 2. If not, add a source-specific parser or runtime adapter. ; 3. Prove the parser on at least two materially different property pages.
  - `RUNTIME-01` Headless/browser runtime likely required: Registry marks this source as headless-driven, so HTML-only assumptions are weak. :: 1. Confirm whether SSR HTML is sufficient or whether browser state is required. ; 2. Persist a browser-safe route and extraction approach. ; 3. Add a non-interactive fallback only if it is stable.

## ApartmentsBulgaria.com

- Scope: `public_scrape_candidate`
- Promotion gate: `strict_sample_and_gallery_proof`
- Proposed pattern: `headless_list_detail_gallery`
- Connector: `HtmlPortalConnector`
- Source route level: `primary_url_only`
- Source URLs: https://www.apartmentsbulgaria.bg/
- Section hypotheses:
  - `buy_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `buy_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
- Detail requirements: title, price or price_status, city or address, description, image_urls, local_image_files, at least two structured fields
- Fixture cases: none
- Code paths: scripts/live_scraper.py::generic
- Issues:
  - `EVID-01` No saved full product sample: The repo does not contain one saved detail-page item with full local gallery proof for this source. :: 1. Capture one legal detail page from a supported bucket. ; 2. Persist raw HTML, normalized listing JSON, and local gallery files. ; 3. Re-run strict pattern audit after the sample exists.
  - `ROUTE-01` Section or list-route discovery is incomplete: Current route evidence level is primary_url_only. :: 1. Map buy/rent and residential/commercial landing pages explicitly. ; 2. Persist section entry URLs and pagination rules. ; 3. Add at least one route per supported bucket before scaling.
  - `FIX-01` No fixture-backed parser evidence: This source has no dedicated fixture cases in tests/fixtures. :: 1. Save at least one representative detail page fixture. ; 2. Add one non-happy-path fixture when the site exposes multiple templates. ; 3. Bind the fixture to a parser test before live promotion.
  - `PARSE-01` Only generic HTML parser is wired: The source currently relies on the generic JSON-LD/og:image parser path. :: 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery. ; 2. If not, add a source-specific parser or runtime adapter. ; 3. Prove the parser on at least two materially different property pages.
  - `RUNTIME-01` Headless/browser runtime likely required: Registry marks this source as headless-driven, so HTML-only assumptions are weak. :: 1. Confirm whether SSR HTML is sufficient or whether browser state is required. ; 2. Persist a browser-safe route and extraction approach. ; 3. Add a non-interactive fallback only if it is stable.

## Domaza

- Scope: `public_scrape_candidate`
- Promotion gate: `strict_sample_and_gallery_proof`
- Proposed pattern: `html_list_detail_gallery`
- Connector: `DomazaConnector`
- Source route level: `entry_urls_saved`
- Source URLs: https://www.domaza.bg/
- Section hypotheses:
  - `buy_personal` | `entry_urls_saved` | https://www.domaza.bg/property/index/search/1/s/572da6146f10beb4bf6333d75039731a4d2b9902 | Section route is persisted in the Varna section registry; still needs strict item-level proof.
  - `buy_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_personal` | `entry_urls_saved` | https://www.domaza.bg/property/index/search/1/s/e8780bcda8fa201940f1ce87e404f870d0c5c3fc | Section route is persisted in the Varna section registry; still needs strict item-level proof.
  - `rent_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
- Detail requirements: title, price or price_status, city or address, description, image_urls, local_image_files, at least two structured fields
- Fixture cases: basic_listing, short_term_rent
- Code paths: scripts/live_scraper.py::generic, scripts/live_scraper.py::_parse_domaza
- Issues:

## Holding Group Real Estate

- Scope: `public_scrape_candidate`
- Promotion gate: `strict_sample_and_gallery_proof`
- Proposed pattern: `html_list_detail_gallery`
- Connector: `HtmlPortalConnector`
- Source route level: `primary_url_only`
- Source URLs: https://holdinggroup.bg/
- Section hypotheses:
  - `buy_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `buy_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
- Detail requirements: title, price or price_status, city or address, description, image_urls, local_image_files, at least two structured fields
- Fixture cases: none
- Code paths: scripts/live_scraper.py::generic
- Issues:
  - `EVID-01` No saved full product sample: The repo does not contain one saved detail-page item with full local gallery proof for this source. :: 1. Capture one legal detail page from a supported bucket. ; 2. Persist raw HTML, normalized listing JSON, and local gallery files. ; 3. Re-run strict pattern audit after the sample exists.
  - `ROUTE-01` Section or list-route discovery is incomplete: Current route evidence level is primary_url_only. :: 1. Map buy/rent and residential/commercial landing pages explicitly. ; 2. Persist section entry URLs and pagination rules. ; 3. Add at least one route per supported bucket before scaling.
  - `FIX-01` No fixture-backed parser evidence: This source has no dedicated fixture cases in tests/fixtures. :: 1. Save at least one representative detail page fixture. ; 2. Add one non-happy-path fixture when the site exposes multiple templates. ; 3. Bind the fixture to a parser test before live promotion.
  - `PARSE-01` Only generic HTML parser is wired: The source currently relies on the generic JSON-LD/og:image parser path. :: 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery. ; 2. If not, add a source-specific parser or runtime adapter. ; 3. Prove the parser on at least two materially different property pages.

## Home2U

- Scope: `public_scrape_candidate`
- Promotion gate: `strict_sample_and_gallery_proof`
- Proposed pattern: `html_list_detail_gallery`
- Connector: `Home2UConnector`
- Source route level: `entry_urls_saved`
- Source URLs: https://home2u.bg/
- Section hypotheses:
  - `buy_personal` | `entry_urls_saved` | https://home2u.bg/nedvizhimi-imoti-varna/ | Section route is persisted in the Varna section registry; still needs strict item-level proof.
  - `buy_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_personal` | `entry_urls_saved` | https://home2u.bg/apartamenti-pod-naem-varna/ | Section route is persisted in the Varna section registry; still needs strict item-level proof.
  - `rent_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
- Detail requirements: title, price or price_status, city or address, description, image_urls, local_image_files, at least two structured fields
- Fixture cases: basic_listing, new_build
- Code paths: scripts/live_scraper.py::generic, scripts/live_scraper.py::_parse_home2u
- Issues:

## Imoteka.bg

- Scope: `restricted_access_pattern`
- Promotion gate: `legal_or_partner_gate`
- Proposed pattern: `headless_list_detail_gallery`
- Connector: `HtmlPortalConnector`
- Source route level: `primary_url_only`
- Source URLs: https://imoteka.bg/
- Section hypotheses:
  - `buy_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `buy_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
- Detail requirements: title, price or price_status, city or address, description, image_urls, local_image_files, at least two structured fields
- Fixture cases: none
- Code paths: scripts/live_scraper.py::generic
- Issues:
  - `LEGAL-01` Legal or contract gate blocks promotion: Current legal_mode=legal_review_required, access_mode=headless. :: 1. Validate whether a public scraping pattern is allowed at all. ; 2. If not, switch the source to partner-feed, official API, licensed-data, or manual-only execution. ; 3. Do not attempt live pattern promotion until the legal gate changes.
  - `ROUTE-01` Section or list-route discovery is incomplete: Current route evidence level is primary_url_only. :: 1. Map buy/rent and residential/commercial landing pages explicitly. ; 2. Persist section entry URLs and pagination rules. ; 3. Add at least one route per supported bucket before scaling.
  - `FIX-01` No fixture-backed parser evidence: This source has no dedicated fixture cases in tests/fixtures. :: 1. Save at least one representative detail page fixture. ; 2. Add one non-happy-path fixture when the site exposes multiple templates. ; 3. Bind the fixture to a parser test before live promotion.
  - `PARSE-01` Only generic HTML parser is wired: The source currently relies on the generic JSON-LD/og:image parser path. :: 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery. ; 2. If not, add a source-specific parser or runtime adapter. ; 3. Prove the parser on at least two materially different property pages.
  - `RUNTIME-01` Headless/browser runtime likely required: Registry marks this source as headless-driven, so HTML-only assumptions are weak. :: 1. Confirm whether SSR HTML is sufficient or whether browser state is required. ; 2. Persist a browser-safe route and extraction approach. ; 3. Add a non-interactive fallback only if it is stable.

## Imoti.info

- Scope: `restricted_access_pattern`
- Promotion gate: `legal_or_partner_gate`
- Proposed pattern: `partner_feed_or_vendor_contract`
- Connector: `HtmlPortalConnector`
- Source route level: `primary_url_only`
- Source URLs: https://imoti.info/
- Section hypotheses:
  - `buy_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `buy_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
- Detail requirements: title, price or price_status, city or address, description, image_urls, local_image_files, at least two structured fields
- Fixture cases: none
- Code paths: scripts/live_scraper.py::generic
- Issues:
  - `LEGAL-01` Legal or contract gate blocks promotion: Current legal_mode=licensing_required, access_mode=partner_feed. :: 1. Validate whether a public scraping pattern is allowed at all. ; 2. If not, switch the source to partner-feed, official API, licensed-data, or manual-only execution. ; 3. Do not attempt live pattern promotion until the legal gate changes.
  - `ROUTE-01` Section or list-route discovery is incomplete: Current route evidence level is primary_url_only. :: 1. Map buy/rent and residential/commercial landing pages explicitly. ; 2. Persist section entry URLs and pagination rules. ; 3. Add at least one route per supported bucket before scaling.

## Indomio.bg

- Scope: `public_scrape_candidate`
- Promotion gate: `strict_sample_and_gallery_proof`
- Proposed pattern: `headless_list_detail_gallery`
- Connector: `HtmlPortalConnector`
- Source route level: `primary_url_only`
- Source URLs: https://www.indomio.bg/
- Section hypotheses:
  - `buy_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `buy_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
- Detail requirements: title, price or price_status, city or address, description, image_urls, local_image_files, at least two structured fields
- Fixture cases: none
- Code paths: scripts/live_scraper.py::generic
- Issues:
  - `EVID-01` No saved full product sample: The repo does not contain one saved detail-page item with full local gallery proof for this source. :: 1. Capture one legal detail page from a supported bucket. ; 2. Persist raw HTML, normalized listing JSON, and local gallery files. ; 3. Re-run strict pattern audit after the sample exists.
  - `ROUTE-01` Section or list-route discovery is incomplete: Current route evidence level is primary_url_only. :: 1. Map buy/rent and residential/commercial landing pages explicitly. ; 2. Persist section entry URLs and pagination rules. ; 3. Add at least one route per supported bucket before scaling.
  - `FIX-01` No fixture-backed parser evidence: This source has no dedicated fixture cases in tests/fixtures. :: 1. Save at least one representative detail page fixture. ; 2. Add one non-happy-path fixture when the site exposes multiple templates. ; 3. Bind the fixture to a parser test before live promotion.
  - `PARSE-01` Only generic HTML parser is wired: The source currently relies on the generic JSON-LD/og:image parser path. :: 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery. ; 2. If not, add a source-specific parser or runtime adapter. ; 3. Prove the parser on at least two materially different property pages.
  - `RUNTIME-01` Headless/browser runtime likely required: Registry marks this source as headless-driven, so HTML-only assumptions are weak. :: 1. Confirm whether SSR HTML is sufficient or whether browser state is required. ; 2. Persist a browser-safe route and extraction approach. ; 3. Add a non-interactive fallback only if it is stable.

## Lions Group

- Scope: `public_scrape_candidate`
- Promotion gate: `strict_sample_and_gallery_proof`
- Proposed pattern: `html_list_detail_gallery`
- Connector: `HtmlPortalConnector`
- Source route level: `primary_url_only`
- Source URLs: https://lionsgroup.bg/
- Section hypotheses:
  - `buy_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `buy_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
- Detail requirements: title, price or price_status, city or address, description, image_urls, local_image_files, at least two structured fields
- Fixture cases: none
- Code paths: scripts/live_scraper.py::generic
- Issues:
  - `EVID-01` No saved full product sample: The repo does not contain one saved detail-page item with full local gallery proof for this source. :: 1. Capture one legal detail page from a supported bucket. ; 2. Persist raw HTML, normalized listing JSON, and local gallery files. ; 3. Re-run strict pattern audit after the sample exists.
  - `ROUTE-01` Section or list-route discovery is incomplete: Current route evidence level is primary_url_only. :: 1. Map buy/rent and residential/commercial landing pages explicitly. ; 2. Persist section entry URLs and pagination rules. ; 3. Add at least one route per supported bucket before scaling.
  - `FIX-01` No fixture-backed parser evidence: This source has no dedicated fixture cases in tests/fixtures. :: 1. Save at least one representative detail page fixture. ; 2. Add one non-happy-path fixture when the site exposes multiple templates. ; 3. Bind the fixture to a parser test before live promotion.
  - `PARSE-01` Only generic HTML parser is wired: The source currently relies on the generic JSON-LD/og:image parser path. :: 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery. ; 2. If not, add a source-specific parser or runtime adapter. ; 3. Prove the parser on at least two materially different property pages.

## Pochivka.bg

- Scope: `public_scrape_candidate`
- Promotion gate: `strict_sample_and_gallery_proof`
- Proposed pattern: `html_list_detail_gallery`
- Connector: `HtmlPortalConnector`
- Source route level: `primary_url_only`
- Source URLs: https://pochivka.bg/
- Section hypotheses:
  - `buy_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `buy_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
- Detail requirements: title, price or price_status, city or address, description, image_urls, local_image_files, at least two structured fields
- Fixture cases: none
- Code paths: scripts/live_scraper.py::generic
- Issues:
  - `EVID-01` No saved full product sample: The repo does not contain one saved detail-page item with full local gallery proof for this source. :: 1. Capture one legal detail page from a supported bucket. ; 2. Persist raw HTML, normalized listing JSON, and local gallery files. ; 3. Re-run strict pattern audit after the sample exists.
  - `ROUTE-01` Section or list-route discovery is incomplete: Current route evidence level is primary_url_only. :: 1. Map buy/rent and residential/commercial landing pages explicitly. ; 2. Persist section entry URLs and pagination rules. ; 3. Add at least one route per supported bucket before scaling.
  - `FIX-01` No fixture-backed parser evidence: This source has no dedicated fixture cases in tests/fixtures. :: 1. Save at least one representative detail page fixture. ; 2. Add one non-happy-path fixture when the site exposes multiple templates. ; 3. Bind the fixture to a parser test before live promotion.
  - `PARSE-01` Only generic HTML parser is wired: The source currently relies on the generic JSON-LD/og:image parser path. :: 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery. ; 2. If not, add a source-specific parser or runtime adapter. ; 3. Prove the parser on at least two materially different property pages.

## realestates.bg

- Scope: `public_scrape_candidate`
- Promotion gate: `strict_sample_and_gallery_proof`
- Proposed pattern: `html_list_detail_gallery`
- Connector: `HtmlPortalConnector`
- Source route level: `primary_url_only`
- Source URLs: https://en.realestates.bg/
- Section hypotheses:
  - `buy_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `buy_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
- Detail requirements: title, price or price_status, city or address, description, image_urls, local_image_files, at least two structured fields
- Fixture cases: none
- Code paths: scripts/live_scraper.py::generic
- Issues:
  - `EVID-01` No saved full product sample: The repo does not contain one saved detail-page item with full local gallery proof for this source. :: 1. Capture one legal detail page from a supported bucket. ; 2. Persist raw HTML, normalized listing JSON, and local gallery files. ; 3. Re-run strict pattern audit after the sample exists.
  - `ROUTE-01` Section or list-route discovery is incomplete: Current route evidence level is primary_url_only. :: 1. Map buy/rent and residential/commercial landing pages explicitly. ; 2. Persist section entry URLs and pagination rules. ; 3. Add at least one route per supported bucket before scaling.
  - `FIX-01` No fixture-backed parser evidence: This source has no dedicated fixture cases in tests/fixtures. :: 1. Save at least one representative detail page fixture. ; 2. Add one non-happy-path fixture when the site exposes multiple templates. ; 3. Bind the fixture to a parser test before live promotion.
  - `PARSE-01` Only generic HTML parser is wired: The source currently relies on the generic JSON-LD/og:image parser path. :: 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery. ; 2. If not, add a source-specific parser or runtime adapter. ; 3. Prove the parser on at least two materially different property pages.

## Realistimo

- Scope: `public_scrape_candidate`
- Promotion gate: `strict_sample_and_gallery_proof`
- Proposed pattern: `headless_list_detail_gallery`
- Connector: `HtmlPortalConnector`
- Source route level: `primary_url_only`
- Source URLs: https://realistimo.com/
- Section hypotheses:
  - `buy_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `buy_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
- Detail requirements: title, price or price_status, city or address, description, image_urls, local_image_files, at least two structured fields
- Fixture cases: none
- Code paths: scripts/live_scraper.py::generic
- Issues:
  - `EVID-01` No saved full product sample: The repo does not contain one saved detail-page item with full local gallery proof for this source. :: 1. Capture one legal detail page from a supported bucket. ; 2. Persist raw HTML, normalized listing JSON, and local gallery files. ; 3. Re-run strict pattern audit after the sample exists.
  - `ROUTE-01` Section or list-route discovery is incomplete: Current route evidence level is primary_url_only. :: 1. Map buy/rent and residential/commercial landing pages explicitly. ; 2. Persist section entry URLs and pagination rules. ; 3. Add at least one route per supported bucket before scaling.
  - `FIX-01` No fixture-backed parser evidence: This source has no dedicated fixture cases in tests/fixtures. :: 1. Save at least one representative detail page fixture. ; 2. Add one non-happy-path fixture when the site exposes multiple templates. ; 3. Bind the fixture to a parser test before live promotion.
  - `PARSE-01` Only generic HTML parser is wired: The source currently relies on the generic JSON-LD/og:image parser path. :: 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery. ; 2. If not, add a source-specific parser or runtime adapter. ; 3. Prove the parser on at least two materially different property pages.
  - `RUNTIME-01` Headless/browser runtime likely required: Registry marks this source as headless-driven, so HTML-only assumptions are weak. :: 1. Confirm whether SSR HTML is sufficient or whether browser state is required. ; 2. Persist a browser-safe route and extraction approach. ; 3. Add a non-interactive fallback only if it is stable.

## Rentica.bg

- Scope: `public_scrape_candidate`
- Promotion gate: `strict_sample_and_gallery_proof`
- Proposed pattern: `html_list_detail_gallery`
- Connector: `HtmlPortalConnector`
- Source route level: `primary_url_only`
- Source URLs: https://rentica.bg/
- Section hypotheses:
  - `buy_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `buy_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
- Detail requirements: title, price or price_status, city or address, description, image_urls, local_image_files, at least two structured fields
- Fixture cases: none
- Code paths: scripts/live_scraper.py::generic
- Issues:
  - `EVID-01` No saved full product sample: The repo does not contain one saved detail-page item with full local gallery proof for this source. :: 1. Capture one legal detail page from a supported bucket. ; 2. Persist raw HTML, normalized listing JSON, and local gallery files. ; 3. Re-run strict pattern audit after the sample exists.
  - `ROUTE-01` Section or list-route discovery is incomplete: Current route evidence level is primary_url_only. :: 1. Map buy/rent and residential/commercial landing pages explicitly. ; 2. Persist section entry URLs and pagination rules. ; 3. Add at least one route per supported bucket before scaling.
  - `FIX-01` No fixture-backed parser evidence: This source has no dedicated fixture cases in tests/fixtures. :: 1. Save at least one representative detail page fixture. ; 2. Add one non-happy-path fixture when the site exposes multiple templates. ; 3. Bind the fixture to a parser test before live promotion.
  - `PARSE-01` Only generic HTML parser is wired: The source currently relies on the generic JSON-LD/og:image parser path. :: 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery. ; 2. If not, add a source-specific parser or runtime adapter. ; 3. Prove the parser on at least two materially different property pages.

## Svobodni-kvartiri.com

- Scope: `public_scrape_candidate`
- Promotion gate: `strict_sample_and_gallery_proof`
- Proposed pattern: `html_list_detail_gallery`
- Connector: `HtmlPortalConnector`
- Source route level: `primary_url_only`
- Source URLs: https://svobodni-kvartiri.com/
- Section hypotheses:
  - `buy_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `buy_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
- Detail requirements: title, price or price_status, city or address, description, image_urls, local_image_files, at least two structured fields
- Fixture cases: none
- Code paths: scripts/live_scraper.py::generic
- Issues:
  - `EVID-01` No saved full product sample: The repo does not contain one saved detail-page item with full local gallery proof for this source. :: 1. Capture one legal detail page from a supported bucket. ; 2. Persist raw HTML, normalized listing JSON, and local gallery files. ; 3. Re-run strict pattern audit after the sample exists.
  - `ROUTE-01` Section or list-route discovery is incomplete: Current route evidence level is primary_url_only. :: 1. Map buy/rent and residential/commercial landing pages explicitly. ; 2. Persist section entry URLs and pagination rules. ; 3. Add at least one route per supported bucket before scaling.
  - `FIX-01` No fixture-backed parser evidence: This source has no dedicated fixture cases in tests/fixtures. :: 1. Save at least one representative detail page fixture. ; 2. Add one non-happy-path fixture when the site exposes multiple templates. ; 3. Bind the fixture to a parser test before live promotion.
  - `PARSE-01` Only generic HTML parser is wired: The source currently relies on the generic JSON-LD/og:image parser path. :: 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery. ; 2. If not, add a source-specific parser or runtime adapter. ; 3. Prove the parser on at least two materially different property pages.

## Unique Estates

- Scope: `public_scrape_candidate`
- Promotion gate: `strict_sample_and_gallery_proof`
- Proposed pattern: `html_list_detail_gallery`
- Connector: `HtmlPortalConnector`
- Source route level: `primary_url_only`
- Source URLs: https://ues.bg/
- Section hypotheses:
  - `buy_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `buy_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
- Detail requirements: title, price or price_status, city or address, description, image_urls, local_image_files, at least two structured fields
- Fixture cases: none
- Code paths: scripts/live_scraper.py::generic
- Issues:
  - `EVID-01` No saved full product sample: The repo does not contain one saved detail-page item with full local gallery proof for this source. :: 1. Capture one legal detail page from a supported bucket. ; 2. Persist raw HTML, normalized listing JSON, and local gallery files. ; 3. Re-run strict pattern audit after the sample exists.
  - `ROUTE-01` Section or list-route discovery is incomplete: Current route evidence level is primary_url_only. :: 1. Map buy/rent and residential/commercial landing pages explicitly. ; 2. Persist section entry URLs and pagination rules. ; 3. Add at least one route per supported bucket before scaling.
  - `FIX-01` No fixture-backed parser evidence: This source has no dedicated fixture cases in tests/fixtures. :: 1. Save at least one representative detail page fixture. ; 2. Add one non-happy-path fixture when the site exposes multiple templates. ; 3. Bind the fixture to a parser test before live promotion.
  - `PARSE-01` Only generic HTML parser is wired: The source currently relies on the generic JSON-LD/og:image parser path. :: 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery. ; 2. If not, add a source-specific parser or runtime adapter. ; 3. Prove the parser on at least two materially different property pages.

## Vila.bg

- Scope: `public_scrape_candidate`
- Promotion gate: `strict_sample_and_gallery_proof`
- Proposed pattern: `html_list_detail_gallery`
- Connector: `HtmlPortalConnector`
- Source route level: `primary_url_only`
- Source URLs: https://vila.bg/
- Section hypotheses:
  - `buy_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `buy_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_personal` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
  - `rent_commercial` | `needs_route_discovery` | route not saved yet | Section exists logically but lacks a saved route.
- Detail requirements: title, price or price_status, city or address, description, image_urls, local_image_files, at least two structured fields
- Fixture cases: none
- Code paths: scripts/live_scraper.py::generic
- Issues:
  - `EVID-01` No saved full product sample: The repo does not contain one saved detail-page item with full local gallery proof for this source. :: 1. Capture one legal detail page from a supported bucket. ; 2. Persist raw HTML, normalized listing JSON, and local gallery files. ; 3. Re-run strict pattern audit after the sample exists.
  - `ROUTE-01` Section or list-route discovery is incomplete: Current route evidence level is primary_url_only. :: 1. Map buy/rent and residential/commercial landing pages explicitly. ; 2. Persist section entry URLs and pagination rules. ; 3. Add at least one route per supported bucket before scaling.
  - `FIX-01` No fixture-backed parser evidence: This source has no dedicated fixture cases in tests/fixtures. :: 1. Save at least one representative detail page fixture. ; 2. Add one non-happy-path fixture when the site exposes multiple templates. ; 3. Bind the fixture to a parser test before live promotion.
  - `PARSE-01` Only generic HTML parser is wired: The source currently relies on the generic JSON-LD/og:image parser path. :: 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery. ; 2. If not, add a source-specific parser or runtime adapter. ; 3. Prove the parser on at least two materially different property pages.
