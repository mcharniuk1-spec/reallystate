# All-tier source pattern audit (2026-04-30)

## Scope

- FACT: OpenClaw Action1 owns the seven priority patterned sources and is excluded from this run's repair scope.
- FACT: This audit focuses on unpatterned sources across all tiers plus universality checks for patterned non-Action1 sources.
- INTERPRETATION: not every source should become a public scraper; some should stay partner-feed, official-API, or manual-only by design.

## Summary table

| Source | Tier | Lane | Current status | Proposed pattern kind | Connector | Fixtures | Route evidence | Main blocker |
|---|---:|---|---|---|---|---:|---|---|
| Address.bg | 1 | action1_owned | `Patterned` | `html_list_detail_gallery` | `HtmlPortalConnector` | 3 | `entry_urls_saved` | `PARSE-01` |
| alo.bg | 1 | unpatterned_focus | `Patterned` | `html_list_detail_gallery` | `HtmlPortalConnector` | 3 | `entry_urls_saved` | `none` |
| BulgarianProperties | 1 | action1_owned | `Patterned` | `html_list_detail_gallery` | `HtmlPortalConnector` | 3 | `entry_urls_saved` | `PARSE-01` |
| Homes.bg | 1 | action1_owned | `Patterned` | `html_list_detail_gallery` | `HomesBgConnector` | 8 | `primary_url_only` | `ROUTE-01` |
| imot.bg | 1 | action1_owned | `Patterned` | `html_list_detail_gallery` | `HtmlPortalConnector` | 3 | `entry_urls_saved` | `none` |
| imoti.net | 1 | unpatterned_focus | `without_authorized_pattern` | `headless_list_detail_gallery` | `HtmlPortalConnector` | 2 | `primary_url_only` | `LEGAL-01` |
| LUXIMMO | 1 | action1_owned | `Patterned` | `html_list_detail_gallery` | `HtmlPortalConnector` | 3 | `entry_urls_saved` | `PARSE-01` |
| OLX.bg | 1 | patterned_secondary_review | `Patterned` | `official_api_overlay` | `OlxBgConnector` | 6 | `entry_urls_saved` | `none` |
| property.bg | 1 | action1_owned | `Patterned` | `html_list_detail_gallery` | `HtmlPortalConnector` | 3 | `entry_urls_saved` | `PARSE-01` |
| SUPRIMMO | 1 | action1_owned | `Patterned` | `html_list_detail_gallery` | `HtmlPortalConnector` | 3 | `entry_urls_saved` | `PARSE-01` |
| ApartmentsBulgaria.com | 2 | unpatterned_focus | `without_sample_product_capture` | `headless_list_detail_gallery` | `HtmlPortalConnector` | 0 | `primary_url_only` | `EVID-01` |
| Bazar.bg | 2 | patterned_secondary_review | `Patterned` | `html_list_detail_gallery` | `BazarBgConnector` | 2 | `entry_urls_saved` | `none` |
| Domaza | 2 | unpatterned_focus | `Patterned` | `html_list_detail_gallery` | `DomazaConnector` | 2 | `entry_urls_saved` | `none` |
| Holding Group Real Estate | 2 | unpatterned_focus | `without_sample_product_capture` | `html_list_detail_gallery` | `HtmlPortalConnector` | 0 | `primary_url_only` | `EVID-01` |
| Home2U | 2 | unpatterned_focus | `Patterned` | `html_list_detail_gallery` | `Home2UConnector` | 2 | `entry_urls_saved` | `none` |
| Imoteka.bg | 2 | unpatterned_focus | `without_authorized_pattern` | `headless_list_detail_gallery` | `HtmlPortalConnector` | 0 | `primary_url_only` | `LEGAL-01` |
| Imoti.info | 2 | unpatterned_focus | `without_authorized_pattern` | `partner_feed_or_vendor_contract` | `HtmlPortalConnector` | 0 | `primary_url_only` | `LEGAL-01` |
| Indomio.bg | 2 | unpatterned_focus | `without_sample_product_capture` | `headless_list_detail_gallery` | `HtmlPortalConnector` | 0 | `primary_url_only` | `EVID-01` |
| Lions Group | 2 | unpatterned_focus | `without_sample_product_capture` | `html_list_detail_gallery` | `HtmlPortalConnector` | 0 | `primary_url_only` | `EVID-01` |
| Pochivka.bg | 2 | unpatterned_focus | `without_sample_product_capture` | `html_list_detail_gallery` | `HtmlPortalConnector` | 0 | `primary_url_only` | `EVID-01` |
| realestates.bg | 2 | unpatterned_focus | `without_sample_product_capture` | `html_list_detail_gallery` | `HtmlPortalConnector` | 0 | `primary_url_only` | `EVID-01` |
| Realistimo | 2 | unpatterned_focus | `without_sample_product_capture` | `headless_list_detail_gallery` | `HtmlPortalConnector` | 0 | `primary_url_only` | `EVID-01` |
| Rentica.bg | 2 | unpatterned_focus | `without_sample_product_capture` | `html_list_detail_gallery` | `HtmlPortalConnector` | 0 | `primary_url_only` | `EVID-01` |
| Svobodni-kvartiri.com | 2 | unpatterned_focus | `without_sample_product_capture` | `html_list_detail_gallery` | `HtmlPortalConnector` | 0 | `primary_url_only` | `EVID-01` |
| Unique Estates | 2 | unpatterned_focus | `without_sample_product_capture` | `html_list_detail_gallery` | `HtmlPortalConnector` | 0 | `primary_url_only` | `EVID-01` |
| Vila.bg | 2 | unpatterned_focus | `without_sample_product_capture` | `html_list_detail_gallery` | `HtmlPortalConnector` | 0 | `primary_url_only` | `EVID-01` |
| Yavlena | 2 | patterned_secondary_review | `Patterned` | `html_list_detail_gallery` | `YavlenaConnector` | 2 | `entry_urls_saved` | `none` |
| Airbnb | 3 | legal_or_partner_pattern_only | `n/a` | `partner_feed_or_vendor_contract` | `PartnerFeedStubConnector` | 0 | `primary_url_only` | `LEGAL-01` |
| Airbtics | 3 | legal_or_partner_pattern_only | `n/a` | `licensed_data_ingest` | `HtmlPortalConnector` | 0 | `primary_url_only` | `LEGAL-01` |
| AirDNA | 3 | legal_or_partner_pattern_only | `n/a` | `licensed_data_ingest` | `HtmlPortalConnector` | 0 | `primary_url_only` | `LEGAL-01` |
| BCPEA property auctions | 3 | legal_or_partner_pattern_only | `n/a` | `html_list_detail_gallery` | `BcpeaAuctionConnector` | 0 | `primary_url_only` | `ROUTE-01` |
| Booking.com | 3 | legal_or_partner_pattern_only | `n/a` | `partner_feed_or_vendor_contract` | `PartnerFeedStubConnector` | 0 | `primary_url_only` | `LEGAL-01` |
| Flat Manager | 3 | legal_or_partner_pattern_only | `n/a` | `partner_feed_or_vendor_contract` | `HtmlPortalConnector` | 0 | `related_urls_only` | `LEGAL-01` |
| KAIS Cadastre | 3 | legal_or_partner_pattern_only | `n/a` | `manual_or_consent_flow` | `HtmlPortalConnector` | 0 | `primary_url_only` | `LEGAL-01` |
| Menada Bulgaria | 3 | legal_or_partner_pattern_only | `n/a` | `partner_feed_or_vendor_contract` | `HtmlPortalConnector` | 0 | `primary_url_only` | `LEGAL-01` |
| Property Register | 3 | legal_or_partner_pattern_only | `n/a` | `manual_or_consent_flow` | `HtmlPortalConnector` | 0 | `primary_url_only` | `LEGAL-01` |
| Vrbo | 3 | legal_or_partner_pattern_only | `n/a` | `partner_feed_or_vendor_contract` | `PartnerFeedStubConnector` | 0 | `primary_url_only` | `LEGAL-01` |
| Facebook public groups/pages | 4 | legal_or_partner_pattern_only | `n/a` | `manual_or_consent_flow` | `HtmlPortalConnector` | 0 | `primary_url_only` | `LEGAL-01` |
| Instagram public profiles | 4 | legal_or_partner_pattern_only | `n/a` | `manual_or_consent_flow` | `HtmlPortalConnector` | 0 | `related_urls_only` | `LEGAL-01` |
| Telegram public channels | 4 | legal_or_partner_pattern_only | `n/a` | `official_api_overlay` | `HtmlPortalConnector` | 0 | `related_urls_only` | `none` |
| Threads public profiles | 4 | legal_or_partner_pattern_only | `n/a` | `manual_or_consent_flow` | `HtmlPortalConnector` | 0 | `no_route_evidence` | `LEGAL-01` |
| Viber opt-in communities | 4 | legal_or_partner_pattern_only | `n/a` | `manual_or_consent_flow` | `HtmlPortalConnector` | 0 | `related_urls_only` | `LEGAL-01` |
| WhatsApp opt-in groups | 4 | legal_or_partner_pattern_only | `n/a` | `manual_or_consent_flow` | `HtmlPortalConnector` | 0 | `primary_url_only` | `LEGAL-01` |
| X public search/accounts | 4 | legal_or_partner_pattern_only | `n/a` | `official_api_overlay` | `HtmlPortalConnector` | 0 | `primary_url_only` | `ROUTE-01` |

## Unpatterned tier-1/2 sources

### imoti.net

- FACT:
  - tier=1, family=portal, legal_mode=legal_review_required, access_mode=headless
  - listing_types=sale, long_term_rent, land, new_build
  - connector=HtmlPortalConnector, fixture_cases=['basic_listing', 'blocked_page']
  - route_evidence=primary_url_only, entry_urls=https://www.imoti.net/
  - current_pattern_status=`without_authorized_pattern`; issue=Source needs legal review before a live pattern can be promoted.
- INTERPRETATION:
  - proposed_pattern_kind=`headless_list_detail_gallery`
  - content summary: portal; listing_types=sale, long_term_rent, land, new_build.
- GAP:
  - sample evidence: No saved sample item.
  - website_total_active=90000 (estimate)

| Issue ID | Problem | Detail | Steps |
|---|---|---|---|
| `LEGAL-01` | Legal or contract gate blocks promotion | Current legal_mode=legal_review_required, access_mode=headless. | 1. Validate whether a public scraping pattern is allowed at all.<br>2. If not, switch the source to partner-feed, official API, licensed-data, or manual-only execution.<br>3. Do not attempt live pattern promotion until the legal gate changes. |
| `ROUTE-01` | Section or list-route discovery is incomplete | Current route evidence level is primary_url_only. | 1. Map buy/rent and residential/commercial landing pages explicitly.<br>2. Persist section entry URLs and pagination rules.<br>3. Add at least one route per supported bucket before scaling. |
| `PARSE-01` | Only generic HTML parser is wired | The source currently relies on the generic JSON-LD/og:image parser path. | 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery.<br>2. If not, add a source-specific parser or runtime adapter.<br>3. Prove the parser on at least two materially different property pages. |
| `RUNTIME-01` | Headless/browser runtime likely required | Registry marks this source as headless-driven, so HTML-only assumptions are weak. | 1. Confirm whether SSR HTML is sufficient or whether browser state is required.<br>2. Persist a browser-safe route and extraction approach.<br>3. Add a non-interactive fallback only if it is stable. |

### ApartmentsBulgaria.com

- FACT:
  - tier=2, family=ota, legal_mode=public_crawl_with_review, access_mode=headless
  - listing_types=short_term_rent
  - connector=HtmlPortalConnector, fixture_cases=none
  - route_evidence=primary_url_only, entry_urls=https://www.apartmentsbulgaria.bg/
  - current_pattern_status=`without_sample_product_capture`; issue=No saved full product sample exists yet for this source.
- INTERPRETATION:
  - proposed_pattern_kind=`headless_list_detail_gallery`
  - content summary: ota; listing_types=short_term_rent.
- GAP:
  - sample evidence: No saved sample item.
  - website_total_active=1800 (estimate)

| Issue ID | Problem | Detail | Steps |
|---|---|---|---|
| `EVID-01` | No saved full product sample | The repo does not contain one saved detail-page item with full local gallery proof for this source. | 1. Capture one legal detail page from a supported bucket.<br>2. Persist raw HTML, normalized listing JSON, and local gallery files.<br>3. Re-run strict pattern audit after the sample exists. |
| `ROUTE-01` | Section or list-route discovery is incomplete | Current route evidence level is primary_url_only. | 1. Map buy/rent and residential/commercial landing pages explicitly.<br>2. Persist section entry URLs and pagination rules.<br>3. Add at least one route per supported bucket before scaling. |
| `FIX-01` | No fixture-backed parser evidence | This source has no dedicated fixture cases in tests/fixtures. | 1. Save at least one representative detail page fixture.<br>2. Add one non-happy-path fixture when the site exposes multiple templates.<br>3. Bind the fixture to a parser test before live promotion. |
| `PARSE-01` | Only generic HTML parser is wired | The source currently relies on the generic JSON-LD/og:image parser path. | 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery.<br>2. If not, add a source-specific parser or runtime adapter.<br>3. Prove the parser on at least two materially different property pages. |
| `RUNTIME-01` | Headless/browser runtime likely required | Registry marks this source as headless-driven, so HTML-only assumptions are weak. | 1. Confirm whether SSR HTML is sufficient or whether browser state is required.<br>2. Persist a browser-safe route and extraction approach.<br>3. Add a non-interactive fallback only if it is stable. |

### Holding Group Real Estate

- FACT:
  - tier=2, family=agency, legal_mode=public_crawl_with_review, access_mode=html
  - listing_types=sale, long_term_rent, land, new_build
  - connector=HtmlPortalConnector, fixture_cases=none
  - route_evidence=primary_url_only, entry_urls=https://holdinggroup.bg/
  - current_pattern_status=`without_sample_product_capture`; issue=No saved full product sample exists yet for this source.
- INTERPRETATION:
  - proposed_pattern_kind=`html_list_detail_gallery`
  - content summary: agency; listing_types=sale, long_term_rent, land, new_build. Agency website with sale/rent search widgets, city filters, and detail pages carrying area, beds/baths, and city labels in public content.
- GAP:
  - sample evidence: No saved sample item.
  - website_total_active=3000 (estimate)

| Issue ID | Problem | Detail | Steps |
|---|---|---|---|
| `EVID-01` | No saved full product sample | The repo does not contain one saved detail-page item with full local gallery proof for this source. | 1. Capture one legal detail page from a supported bucket.<br>2. Persist raw HTML, normalized listing JSON, and local gallery files.<br>3. Re-run strict pattern audit after the sample exists. |
| `ROUTE-01` | Section or list-route discovery is incomplete | Current route evidence level is primary_url_only. | 1. Map buy/rent and residential/commercial landing pages explicitly.<br>2. Persist section entry URLs and pagination rules.<br>3. Add at least one route per supported bucket before scaling. |
| `FIX-01` | No fixture-backed parser evidence | This source has no dedicated fixture cases in tests/fixtures. | 1. Save at least one representative detail page fixture.<br>2. Add one non-happy-path fixture when the site exposes multiple templates.<br>3. Bind the fixture to a parser test before live promotion. |
| `PARSE-01` | Only generic HTML parser is wired | The source currently relies on the generic JSON-LD/og:image parser path. | 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery.<br>2. If not, add a source-specific parser or runtime adapter.<br>3. Prove the parser on at least two materially different property pages. |

### Imoteka.bg

- FACT:
  - tier=2, family=agency, legal_mode=legal_review_required, access_mode=headless
  - listing_types=sale, long_term_rent, land, new_build
  - connector=HtmlPortalConnector, fixture_cases=none
  - route_evidence=primary_url_only, entry_urls=https://imoteka.bg/
  - current_pattern_status=`without_authorized_pattern`; issue=Source needs legal review before a live pattern can be promoted.
- INTERPRETATION:
  - proposed_pattern_kind=`headless_list_detail_gallery`
  - content summary: agency; listing_types=sale, long_term_rent, land, new_build.
- GAP:
  - sample evidence: No saved sample item.
  - website_total_active=14000 (estimate)

| Issue ID | Problem | Detail | Steps |
|---|---|---|---|
| `LEGAL-01` | Legal or contract gate blocks promotion | Current legal_mode=legal_review_required, access_mode=headless. | 1. Validate whether a public scraping pattern is allowed at all.<br>2. If not, switch the source to partner-feed, official API, licensed-data, or manual-only execution.<br>3. Do not attempt live pattern promotion until the legal gate changes. |
| `ROUTE-01` | Section or list-route discovery is incomplete | Current route evidence level is primary_url_only. | 1. Map buy/rent and residential/commercial landing pages explicitly.<br>2. Persist section entry URLs and pagination rules.<br>3. Add at least one route per supported bucket before scaling. |
| `FIX-01` | No fixture-backed parser evidence | This source has no dedicated fixture cases in tests/fixtures. | 1. Save at least one representative detail page fixture.<br>2. Add one non-happy-path fixture when the site exposes multiple templates.<br>3. Bind the fixture to a parser test before live promotion. |
| `PARSE-01` | Only generic HTML parser is wired | The source currently relies on the generic JSON-LD/og:image parser path. | 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery.<br>2. If not, add a source-specific parser or runtime adapter.<br>3. Prove the parser on at least two materially different property pages. |
| `RUNTIME-01` | Headless/browser runtime likely required | Registry marks this source as headless-driven, so HTML-only assumptions are weak. | 1. Confirm whether SSR HTML is sufficient or whether browser state is required.<br>2. Persist a browser-safe route and extraction approach.<br>3. Add a non-interactive fallback only if it is stable. |

### Imoti.info

- FACT:
  - tier=2, family=classifieds, legal_mode=licensing_required, access_mode=partner_feed
  - listing_types=sale, long_term_rent, land, new_build
  - connector=HtmlPortalConnector, fixture_cases=none
  - route_evidence=primary_url_only, entry_urls=https://imoti.info/
  - current_pattern_status=`without_authorized_pattern`; issue=Source is licensing-gated; no public scraping pattern should be marked complete.
- INTERPRETATION:
  - proposed_pattern_kind=`partner_feed_or_vendor_contract`
  - content summary: classifieds; listing_types=sale, long_term_rent, land, new_build.
- GAP:
  - sample evidence: No saved sample item.
  - website_total_active=25000 (estimate)

| Issue ID | Problem | Detail | Steps |
|---|---|---|---|
| `LEGAL-01` | Legal or contract gate blocks promotion | Current legal_mode=licensing_required, access_mode=partner_feed. | 1. Validate whether a public scraping pattern is allowed at all.<br>2. If not, switch the source to partner-feed, official API, licensed-data, or manual-only execution.<br>3. Do not attempt live pattern promotion until the legal gate changes. |
| `ROUTE-01` | Section or list-route discovery is incomplete | Current route evidence level is primary_url_only. | 1. Map buy/rent and residential/commercial landing pages explicitly.<br>2. Persist section entry URLs and pagination rules.<br>3. Add at least one route per supported bucket before scaling. |

### Indomio.bg

- FACT:
  - tier=2, family=portal, legal_mode=public_crawl_with_review, access_mode=headless
  - listing_types=sale, long_term_rent, land
  - connector=HtmlPortalConnector, fixture_cases=none
  - route_evidence=primary_url_only, entry_urls=https://www.indomio.bg/
  - current_pattern_status=`without_sample_product_capture`; issue=No saved full product sample exists yet for this source.
- INTERPRETATION:
  - proposed_pattern_kind=`headless_list_detail_gallery`
  - content summary: portal; listing_types=sale, long_term_rent, land.
- GAP:
  - sample evidence: No saved sample item.
  - website_total_active=7000 (estimate)

| Issue ID | Problem | Detail | Steps |
|---|---|---|---|
| `EVID-01` | No saved full product sample | The repo does not contain one saved detail-page item with full local gallery proof for this source. | 1. Capture one legal detail page from a supported bucket.<br>2. Persist raw HTML, normalized listing JSON, and local gallery files.<br>3. Re-run strict pattern audit after the sample exists. |
| `ROUTE-01` | Section or list-route discovery is incomplete | Current route evidence level is primary_url_only. | 1. Map buy/rent and residential/commercial landing pages explicitly.<br>2. Persist section entry URLs and pagination rules.<br>3. Add at least one route per supported bucket before scaling. |
| `FIX-01` | No fixture-backed parser evidence | This source has no dedicated fixture cases in tests/fixtures. | 1. Save at least one representative detail page fixture.<br>2. Add one non-happy-path fixture when the site exposes multiple templates.<br>3. Bind the fixture to a parser test before live promotion. |
| `PARSE-01` | Only generic HTML parser is wired | The source currently relies on the generic JSON-LD/og:image parser path. | 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery.<br>2. If not, add a source-specific parser or runtime adapter.<br>3. Prove the parser on at least two materially different property pages. |
| `RUNTIME-01` | Headless/browser runtime likely required | Registry marks this source as headless-driven, so HTML-only assumptions are weak. | 1. Confirm whether SSR HTML is sufficient or whether browser state is required.<br>2. Persist a browser-safe route and extraction approach.<br>3. Add a non-interactive fallback only if it is stable. |

### Lions Group

- FACT:
  - tier=2, family=agency, legal_mode=public_crawl_with_review, access_mode=html
  - listing_types=sale, long_term_rent, land, new_build
  - connector=HtmlPortalConnector, fixture_cases=none
  - route_evidence=primary_url_only, entry_urls=https://lionsgroup.bg/
  - current_pattern_status=`without_sample_product_capture`; issue=No saved full product sample exists yet for this source.
- INTERPRETATION:
  - proposed_pattern_kind=`html_list_detail_gallery`
  - content summary: agency; listing_types=sale, long_term_rent, land, new_build.
- GAP:
  - sample evidence: No saved sample item.
  - website_total_active=2500 (estimate)

| Issue ID | Problem | Detail | Steps |
|---|---|---|---|
| `EVID-01` | No saved full product sample | The repo does not contain one saved detail-page item with full local gallery proof for this source. | 1. Capture one legal detail page from a supported bucket.<br>2. Persist raw HTML, normalized listing JSON, and local gallery files.<br>3. Re-run strict pattern audit after the sample exists. |
| `ROUTE-01` | Section or list-route discovery is incomplete | Current route evidence level is primary_url_only. | 1. Map buy/rent and residential/commercial landing pages explicitly.<br>2. Persist section entry URLs and pagination rules.<br>3. Add at least one route per supported bucket before scaling. |
| `FIX-01` | No fixture-backed parser evidence | This source has no dedicated fixture cases in tests/fixtures. | 1. Save at least one representative detail page fixture.<br>2. Add one non-happy-path fixture when the site exposes multiple templates.<br>3. Bind the fixture to a parser test before live promotion. |
| `PARSE-01` | Only generic HTML parser is wired | The source currently relies on the generic JSON-LD/og:image parser path. | 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery.<br>2. If not, add a source-specific parser or runtime adapter.<br>3. Prove the parser on at least two materially different property pages. |

### Pochivka.bg

- FACT:
  - tier=2, family=ota, legal_mode=public_crawl_with_review, access_mode=html
  - listing_types=short_term_rent
  - connector=HtmlPortalConnector, fixture_cases=none
  - route_evidence=primary_url_only, entry_urls=https://pochivka.bg/
  - current_pattern_status=`without_sample_product_capture`; issue=No saved full product sample exists yet for this source.
- INTERPRETATION:
  - proposed_pattern_kind=`html_list_detail_gallery`
  - content summary: ota; listing_types=short_term_rent.
- GAP:
  - sample evidence: No saved sample item.
  - website_total_active=5000 (estimate)

| Issue ID | Problem | Detail | Steps |
|---|---|---|---|
| `EVID-01` | No saved full product sample | The repo does not contain one saved detail-page item with full local gallery proof for this source. | 1. Capture one legal detail page from a supported bucket.<br>2. Persist raw HTML, normalized listing JSON, and local gallery files.<br>3. Re-run strict pattern audit after the sample exists. |
| `ROUTE-01` | Section or list-route discovery is incomplete | Current route evidence level is primary_url_only. | 1. Map buy/rent and residential/commercial landing pages explicitly.<br>2. Persist section entry URLs and pagination rules.<br>3. Add at least one route per supported bucket before scaling. |
| `FIX-01` | No fixture-backed parser evidence | This source has no dedicated fixture cases in tests/fixtures. | 1. Save at least one representative detail page fixture.<br>2. Add one non-happy-path fixture when the site exposes multiple templates.<br>3. Bind the fixture to a parser test before live promotion. |
| `PARSE-01` | Only generic HTML parser is wired | The source currently relies on the generic JSON-LD/og:image parser path. | 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery.<br>2. If not, add a source-specific parser or runtime adapter.<br>3. Prove the parser on at least two materially different property pages. |

### realestates.bg

- FACT:
  - tier=2, family=classifieds, legal_mode=public_crawl_with_review, access_mode=html
  - listing_types=sale, long_term_rent, land
  - connector=HtmlPortalConnector, fixture_cases=none
  - route_evidence=primary_url_only, entry_urls=https://en.realestates.bg/
  - current_pattern_status=`without_sample_product_capture`; issue=No saved full product sample exists yet for this source.
- INTERPRETATION:
  - proposed_pattern_kind=`html_list_detail_gallery`
  - content summary: classifieds; listing_types=sale, long_term_rent, land.
- GAP:
  - sample evidence: No saved sample item.
  - website_total_active=6000 (estimate)

| Issue ID | Problem | Detail | Steps |
|---|---|---|---|
| `EVID-01` | No saved full product sample | The repo does not contain one saved detail-page item with full local gallery proof for this source. | 1. Capture one legal detail page from a supported bucket.<br>2. Persist raw HTML, normalized listing JSON, and local gallery files.<br>3. Re-run strict pattern audit after the sample exists. |
| `ROUTE-01` | Section or list-route discovery is incomplete | Current route evidence level is primary_url_only. | 1. Map buy/rent and residential/commercial landing pages explicitly.<br>2. Persist section entry URLs and pagination rules.<br>3. Add at least one route per supported bucket before scaling. |
| `FIX-01` | No fixture-backed parser evidence | This source has no dedicated fixture cases in tests/fixtures. | 1. Save at least one representative detail page fixture.<br>2. Add one non-happy-path fixture when the site exposes multiple templates.<br>3. Bind the fixture to a parser test before live promotion. |
| `PARSE-01` | Only generic HTML parser is wired | The source currently relies on the generic JSON-LD/og:image parser path. | 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery.<br>2. If not, add a source-specific parser or runtime adapter.<br>3. Prove the parser on at least two materially different property pages. |

### Realistimo

- FACT:
  - tier=2, family=portal, legal_mode=public_crawl_with_review, access_mode=headless
  - listing_types=sale, long_term_rent, land, new_build
  - connector=HtmlPortalConnector, fixture_cases=none
  - route_evidence=primary_url_only, entry_urls=https://realistimo.com/
  - current_pattern_status=`without_sample_product_capture`; issue=No saved full product sample exists yet for this source.
- INTERPRETATION:
  - proposed_pattern_kind=`headless_list_detail_gallery`
  - content summary: portal; listing_types=sale, long_term_rent, land, new_build. Large SSR portal with city-level buy/rent landing pages, broad property taxonomy, and explicit city result counts in public pages.
- GAP:
  - sample evidence: No saved sample item.
  - website_total_active=4500 (estimate)

| Issue ID | Problem | Detail | Steps |
|---|---|---|---|
| `EVID-01` | No saved full product sample | The repo does not contain one saved detail-page item with full local gallery proof for this source. | 1. Capture one legal detail page from a supported bucket.<br>2. Persist raw HTML, normalized listing JSON, and local gallery files.<br>3. Re-run strict pattern audit after the sample exists. |
| `ROUTE-01` | Section or list-route discovery is incomplete | Current route evidence level is primary_url_only. | 1. Map buy/rent and residential/commercial landing pages explicitly.<br>2. Persist section entry URLs and pagination rules.<br>3. Add at least one route per supported bucket before scaling. |
| `FIX-01` | No fixture-backed parser evidence | This source has no dedicated fixture cases in tests/fixtures. | 1. Save at least one representative detail page fixture.<br>2. Add one non-happy-path fixture when the site exposes multiple templates.<br>3. Bind the fixture to a parser test before live promotion. |
| `PARSE-01` | Only generic HTML parser is wired | The source currently relies on the generic JSON-LD/og:image parser path. | 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery.<br>2. If not, add a source-specific parser or runtime adapter.<br>3. Prove the parser on at least two materially different property pages. |
| `RUNTIME-01` | Headless/browser runtime likely required | Registry marks this source as headless-driven, so HTML-only assumptions are weak. | 1. Confirm whether SSR HTML is sufficient or whether browser state is required.<br>2. Persist a browser-safe route and extraction approach.<br>3. Add a non-interactive fallback only if it is stable. |

### Rentica.bg

- FACT:
  - tier=2, family=agency, legal_mode=public_crawl_with_review, access_mode=html
  - listing_types=long_term_rent
  - connector=HtmlPortalConnector, fixture_cases=none
  - route_evidence=primary_url_only, entry_urls=https://rentica.bg/
  - current_pattern_status=`without_sample_product_capture`; issue=No saved full product sample exists yet for this source.
- INTERPRETATION:
  - proposed_pattern_kind=`html_list_detail_gallery`
  - content summary: agency; listing_types=long_term_rent. Rent-first Varna agency catalog with numeric offer detail pages, district pages, and explicit long-term rental descriptions.
- GAP:
  - sample evidence: No saved sample item.
  - website_total_active=1200 (estimate)

| Issue ID | Problem | Detail | Steps |
|---|---|---|---|
| `EVID-01` | No saved full product sample | The repo does not contain one saved detail-page item with full local gallery proof for this source. | 1. Capture one legal detail page from a supported bucket.<br>2. Persist raw HTML, normalized listing JSON, and local gallery files.<br>3. Re-run strict pattern audit after the sample exists. |
| `ROUTE-01` | Section or list-route discovery is incomplete | Current route evidence level is primary_url_only. | 1. Map buy/rent and residential/commercial landing pages explicitly.<br>2. Persist section entry URLs and pagination rules.<br>3. Add at least one route per supported bucket before scaling. |
| `FIX-01` | No fixture-backed parser evidence | This source has no dedicated fixture cases in tests/fixtures. | 1. Save at least one representative detail page fixture.<br>2. Add one non-happy-path fixture when the site exposes multiple templates.<br>3. Bind the fixture to a parser test before live promotion. |
| `PARSE-01` | Only generic HTML parser is wired | The source currently relies on the generic JSON-LD/og:image parser path. | 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery.<br>2. If not, add a source-specific parser or runtime adapter.<br>3. Prove the parser on at least two materially different property pages. |

### Svobodni-kvartiri.com

- FACT:
  - tier=2, family=portal, legal_mode=public_crawl_with_review, access_mode=html
  - listing_types=long_term_rent, short_term_rent
  - connector=HtmlPortalConnector, fixture_cases=none
  - route_evidence=primary_url_only, entry_urls=https://svobodni-kvartiri.com/
  - current_pattern_status=`without_sample_product_capture`; issue=No saved full product sample exists yet for this source.
- INTERPRETATION:
  - proposed_pattern_kind=`html_list_detail_gallery`
  - content summary: portal; listing_types=long_term_rent, short_term_rent.
- GAP:
  - sample evidence: No saved sample item.
  - website_total_active=3500 (estimate)

| Issue ID | Problem | Detail | Steps |
|---|---|---|---|
| `EVID-01` | No saved full product sample | The repo does not contain one saved detail-page item with full local gallery proof for this source. | 1. Capture one legal detail page from a supported bucket.<br>2. Persist raw HTML, normalized listing JSON, and local gallery files.<br>3. Re-run strict pattern audit after the sample exists. |
| `ROUTE-01` | Section or list-route discovery is incomplete | Current route evidence level is primary_url_only. | 1. Map buy/rent and residential/commercial landing pages explicitly.<br>2. Persist section entry URLs and pagination rules.<br>3. Add at least one route per supported bucket before scaling. |
| `FIX-01` | No fixture-backed parser evidence | This source has no dedicated fixture cases in tests/fixtures. | 1. Save at least one representative detail page fixture.<br>2. Add one non-happy-path fixture when the site exposes multiple templates.<br>3. Bind the fixture to a parser test before live promotion. |
| `PARSE-01` | Only generic HTML parser is wired | The source currently relies on the generic JSON-LD/og:image parser path. | 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery.<br>2. If not, add a source-specific parser or runtime adapter.<br>3. Prove the parser on at least two materially different property pages. |

### Unique Estates

- FACT:
  - tier=2, family=agency, legal_mode=public_crawl_with_review, access_mode=html
  - listing_types=sale, long_term_rent, new_build
  - connector=HtmlPortalConnector, fixture_cases=none
  - route_evidence=primary_url_only, entry_urls=https://ues.bg/
  - current_pattern_status=`without_sample_product_capture`; issue=No saved full product sample exists yet for this source.
- INTERPRETATION:
  - proposed_pattern_kind=`html_list_detail_gallery`
  - content summary: agency; listing_types=sale, long_term_rent, new_build. Luxury agency portal with explicit buy/rent navigation, editorial landing pages, and premium listing detail pages.
- GAP:
  - sample evidence: No saved sample item.
  - website_total_active=2000 (estimate)

| Issue ID | Problem | Detail | Steps |
|---|---|---|---|
| `EVID-01` | No saved full product sample | The repo does not contain one saved detail-page item with full local gallery proof for this source. | 1. Capture one legal detail page from a supported bucket.<br>2. Persist raw HTML, normalized listing JSON, and local gallery files.<br>3. Re-run strict pattern audit after the sample exists. |
| `ROUTE-01` | Section or list-route discovery is incomplete | Current route evidence level is primary_url_only. | 1. Map buy/rent and residential/commercial landing pages explicitly.<br>2. Persist section entry URLs and pagination rules.<br>3. Add at least one route per supported bucket before scaling. |
| `FIX-01` | No fixture-backed parser evidence | This source has no dedicated fixture cases in tests/fixtures. | 1. Save at least one representative detail page fixture.<br>2. Add one non-happy-path fixture when the site exposes multiple templates.<br>3. Bind the fixture to a parser test before live promotion. |
| `PARSE-01` | Only generic HTML parser is wired | The source currently relies on the generic JSON-LD/og:image parser path. | 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery.<br>2. If not, add a source-specific parser or runtime adapter.<br>3. Prove the parser on at least two materially different property pages. |

### Vila.bg

- FACT:
  - tier=2, family=ota, legal_mode=public_crawl_with_review, access_mode=html
  - listing_types=short_term_rent
  - connector=HtmlPortalConnector, fixture_cases=none
  - route_evidence=primary_url_only, entry_urls=https://vila.bg/
  - current_pattern_status=`without_sample_product_capture`; issue=No saved full product sample exists yet for this source.
- INTERPRETATION:
  - proposed_pattern_kind=`html_list_detail_gallery`
  - content summary: ota; listing_types=short_term_rent. Hospitality catalog oriented around villa/guest-house short-term stays with region/occasion pages rather than classic property-sale inventory.
- GAP:
  - sample evidence: No saved sample item.
  - website_total_active=4000 (estimate)

| Issue ID | Problem | Detail | Steps |
|---|---|---|---|
| `EVID-01` | No saved full product sample | The repo does not contain one saved detail-page item with full local gallery proof for this source. | 1. Capture one legal detail page from a supported bucket.<br>2. Persist raw HTML, normalized listing JSON, and local gallery files.<br>3. Re-run strict pattern audit after the sample exists. |
| `ROUTE-01` | Section or list-route discovery is incomplete | Current route evidence level is primary_url_only. | 1. Map buy/rent and residential/commercial landing pages explicitly.<br>2. Persist section entry URLs and pagination rules.<br>3. Add at least one route per supported bucket before scaling. |
| `FIX-01` | No fixture-backed parser evidence | This source has no dedicated fixture cases in tests/fixtures. | 1. Save at least one representative detail page fixture.<br>2. Add one non-happy-path fixture when the site exposes multiple templates.<br>3. Bind the fixture to a parser test before live promotion. |
| `PARSE-01` | Only generic HTML parser is wired | The source currently relies on the generic JSON-LD/og:image parser path. | 1. Validate whether generic extraction is enough for price, area, rooms, address, and full gallery.<br>2. If not, add a source-specific parser or runtime adapter.<br>3. Prove the parser on at least two materially different property pages. |

## Durable candidate patterns for unpatterned tier-1/2 sources

### alo.bg

- FACT:
  - pattern_scope=public_scrape_candidate, promotion_gate=strict_sample_and_gallery_proof
  - connector=HtmlPortalConnector, access_mode=html, legal_mode=public_crawl_with_review
- INTERPRETATION:
  - source-level pattern: `html_list_detail_gallery`
  - list-page mode: `html_listing_grid`
  - detail-page proof status: `saved_sample_exists`
  - gallery proof status: `full_gallery_sample_exists`
- Known section hypotheses:
  - `buy_personal` -> https://www.alo.bg/obiavi/imoti-prodajbi/apartamenti-stai/ (entry_urls_saved; Section route is persisted in the Varna section registry; still needs strict item-level proof.)
  - `buy_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_personal` -> https://www.alo.bg/obiavi/imoti-naemi/apartamenti-stai/ (entry_urls_saved; Section route is persisted in the Varna section registry; still needs strict item-level proof.)
  - `rent_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)

### imoti.net

- FACT:
  - pattern_scope=restricted_access_pattern, promotion_gate=legal_or_partner_gate
  - connector=HtmlPortalConnector, access_mode=headless, legal_mode=legal_review_required
- INTERPRETATION:
  - source-level pattern: `headless_list_detail_gallery`
  - list-page mode: `browser_or_ssr_listing_grid`
  - detail-page proof status: `missing_saved_sample`
  - gallery proof status: `no_full_gallery_item_saved`
- Known section hypotheses:
  - `buy_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `buy_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)

### ApartmentsBulgaria.com

- FACT:
  - pattern_scope=public_scrape_candidate, promotion_gate=strict_sample_and_gallery_proof
  - connector=HtmlPortalConnector, access_mode=headless, legal_mode=public_crawl_with_review
- INTERPRETATION:
  - source-level pattern: `headless_list_detail_gallery`
  - list-page mode: `browser_or_ssr_listing_grid`
  - detail-page proof status: `missing_saved_sample`
  - gallery proof status: `no_full_gallery_item_saved`
- Known section hypotheses:
  - `buy_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `buy_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)

### Domaza

- FACT:
  - pattern_scope=public_scrape_candidate, promotion_gate=strict_sample_and_gallery_proof
  - connector=DomazaConnector, access_mode=html, legal_mode=public_crawl_with_review
- INTERPRETATION:
  - source-level pattern: `html_list_detail_gallery`
  - list-page mode: `html_listing_grid`
  - detail-page proof status: `saved_sample_exists`
  - gallery proof status: `full_gallery_sample_exists`
- Known section hypotheses:
  - `buy_personal` -> https://www.domaza.bg/property/index/search/1/s/572da6146f10beb4bf6333d75039731a4d2b9902 (entry_urls_saved; Section route is persisted in the Varna section registry; still needs strict item-level proof.)
  - `buy_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_personal` -> https://www.domaza.bg/property/index/search/1/s/e8780bcda8fa201940f1ce87e404f870d0c5c3fc (entry_urls_saved; Section route is persisted in the Varna section registry; still needs strict item-level proof.)
  - `rent_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)

### Holding Group Real Estate

- FACT:
  - pattern_scope=public_scrape_candidate, promotion_gate=strict_sample_and_gallery_proof
  - connector=HtmlPortalConnector, access_mode=html, legal_mode=public_crawl_with_review
- INTERPRETATION:
  - source-level pattern: `html_list_detail_gallery`
  - list-page mode: `html_listing_grid`
  - detail-page proof status: `missing_saved_sample`
  - gallery proof status: `no_full_gallery_item_saved`
- Known section hypotheses:
  - `buy_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `buy_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)

### Home2U

- FACT:
  - pattern_scope=public_scrape_candidate, promotion_gate=strict_sample_and_gallery_proof
  - connector=Home2UConnector, access_mode=html, legal_mode=public_crawl_with_review
- INTERPRETATION:
  - source-level pattern: `html_list_detail_gallery`
  - list-page mode: `html_listing_grid`
  - detail-page proof status: `saved_sample_exists`
  - gallery proof status: `full_gallery_sample_exists`
- Known section hypotheses:
  - `buy_personal` -> https://home2u.bg/nedvizhimi-imoti-varna/ (entry_urls_saved; Section route is persisted in the Varna section registry; still needs strict item-level proof.)
  - `buy_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_personal` -> https://home2u.bg/apartamenti-pod-naem-varna/ (entry_urls_saved; Section route is persisted in the Varna section registry; still needs strict item-level proof.)
  - `rent_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)

### Imoteka.bg

- FACT:
  - pattern_scope=restricted_access_pattern, promotion_gate=legal_or_partner_gate
  - connector=HtmlPortalConnector, access_mode=headless, legal_mode=legal_review_required
- INTERPRETATION:
  - source-level pattern: `headless_list_detail_gallery`
  - list-page mode: `browser_or_ssr_listing_grid`
  - detail-page proof status: `missing_saved_sample`
  - gallery proof status: `no_full_gallery_item_saved`
- Known section hypotheses:
  - `buy_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `buy_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)

### Imoti.info

- FACT:
  - pattern_scope=restricted_access_pattern, promotion_gate=legal_or_partner_gate
  - connector=HtmlPortalConnector, access_mode=partner_feed, legal_mode=licensing_required
- INTERPRETATION:
  - source-level pattern: `partner_feed_or_vendor_contract`
  - list-page mode: `non_public_feed_or_api`
  - detail-page proof status: `missing_saved_sample`
  - gallery proof status: `no_full_gallery_item_saved`
- Known section hypotheses:
  - `buy_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `buy_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)

### Indomio.bg

- FACT:
  - pattern_scope=public_scrape_candidate, promotion_gate=strict_sample_and_gallery_proof
  - connector=HtmlPortalConnector, access_mode=headless, legal_mode=public_crawl_with_review
- INTERPRETATION:
  - source-level pattern: `headless_list_detail_gallery`
  - list-page mode: `browser_or_ssr_listing_grid`
  - detail-page proof status: `missing_saved_sample`
  - gallery proof status: `no_full_gallery_item_saved`
- Known section hypotheses:
  - `buy_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `buy_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)

### Lions Group

- FACT:
  - pattern_scope=public_scrape_candidate, promotion_gate=strict_sample_and_gallery_proof
  - connector=HtmlPortalConnector, access_mode=html, legal_mode=public_crawl_with_review
- INTERPRETATION:
  - source-level pattern: `html_list_detail_gallery`
  - list-page mode: `html_listing_grid`
  - detail-page proof status: `missing_saved_sample`
  - gallery proof status: `no_full_gallery_item_saved`
- Known section hypotheses:
  - `buy_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `buy_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)

### Pochivka.bg

- FACT:
  - pattern_scope=public_scrape_candidate, promotion_gate=strict_sample_and_gallery_proof
  - connector=HtmlPortalConnector, access_mode=html, legal_mode=public_crawl_with_review
- INTERPRETATION:
  - source-level pattern: `html_list_detail_gallery`
  - list-page mode: `html_listing_grid`
  - detail-page proof status: `missing_saved_sample`
  - gallery proof status: `no_full_gallery_item_saved`
- Known section hypotheses:
  - `buy_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `buy_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)

### realestates.bg

- FACT:
  - pattern_scope=public_scrape_candidate, promotion_gate=strict_sample_and_gallery_proof
  - connector=HtmlPortalConnector, access_mode=html, legal_mode=public_crawl_with_review
- INTERPRETATION:
  - source-level pattern: `html_list_detail_gallery`
  - list-page mode: `html_listing_grid`
  - detail-page proof status: `missing_saved_sample`
  - gallery proof status: `no_full_gallery_item_saved`
- Known section hypotheses:
  - `buy_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `buy_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)

### Realistimo

- FACT:
  - pattern_scope=public_scrape_candidate, promotion_gate=strict_sample_and_gallery_proof
  - connector=HtmlPortalConnector, access_mode=headless, legal_mode=public_crawl_with_review
- INTERPRETATION:
  - source-level pattern: `headless_list_detail_gallery`
  - list-page mode: `browser_or_ssr_listing_grid`
  - detail-page proof status: `missing_saved_sample`
  - gallery proof status: `no_full_gallery_item_saved`
- Known section hypotheses:
  - `buy_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `buy_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)

### Rentica.bg

- FACT:
  - pattern_scope=public_scrape_candidate, promotion_gate=strict_sample_and_gallery_proof
  - connector=HtmlPortalConnector, access_mode=html, legal_mode=public_crawl_with_review
- INTERPRETATION:
  - source-level pattern: `html_list_detail_gallery`
  - list-page mode: `html_listing_grid`
  - detail-page proof status: `missing_saved_sample`
  - gallery proof status: `no_full_gallery_item_saved`
- Known section hypotheses:
  - `buy_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `buy_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)

### Svobodni-kvartiri.com

- FACT:
  - pattern_scope=public_scrape_candidate, promotion_gate=strict_sample_and_gallery_proof
  - connector=HtmlPortalConnector, access_mode=html, legal_mode=public_crawl_with_review
- INTERPRETATION:
  - source-level pattern: `html_list_detail_gallery`
  - list-page mode: `html_listing_grid`
  - detail-page proof status: `missing_saved_sample`
  - gallery proof status: `no_full_gallery_item_saved`
- Known section hypotheses:
  - `buy_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `buy_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)

### Unique Estates

- FACT:
  - pattern_scope=public_scrape_candidate, promotion_gate=strict_sample_and_gallery_proof
  - connector=HtmlPortalConnector, access_mode=html, legal_mode=public_crawl_with_review
- INTERPRETATION:
  - source-level pattern: `html_list_detail_gallery`
  - list-page mode: `html_listing_grid`
  - detail-page proof status: `missing_saved_sample`
  - gallery proof status: `no_full_gallery_item_saved`
- Known section hypotheses:
  - `buy_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `buy_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)

### Vila.bg

- FACT:
  - pattern_scope=public_scrape_candidate, promotion_gate=strict_sample_and_gallery_proof
  - connector=HtmlPortalConnector, access_mode=html, legal_mode=public_crawl_with_review
- INTERPRETATION:
  - source-level pattern: `html_list_detail_gallery`
  - list-page mode: `html_listing_grid`
  - detail-page proof status: `missing_saved_sample`
  - gallery proof status: `no_full_gallery_item_saved`
- Known section hypotheses:
  - `buy_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `buy_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_personal` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)
  - `rent_commercial` -> route not saved yet (needs_route_discovery; Section exists logically but lacks a saved route.)

## Tier-3 and tier-4 pattern model

### Airbnb

- FACT:
  - tier=3, family=ota, legal_mode=official_partner_or_vendor_only, access_mode=partner_feed
  - listing_types=short_term_rent
- INTERPRETATION:
  - proposed_pattern_kind=`partner_feed_or_vendor_contract`
  - content summary: ota; listing_types=short_term_rent.
- GAP:
  - main blocker: Legal or contract gate blocks promotion

### Airbtics

- FACT:
  - tier=3, family=analytics_vendor, legal_mode=official_partner_or_vendor_only, access_mode=licensed_data
  - listing_types=short_term_rent_metrics
- INTERPRETATION:
  - proposed_pattern_kind=`licensed_data_ingest`
  - content summary: analytics_vendor; listing_types=short_term_rent_metrics.
- GAP:
  - main blocker: Legal or contract gate blocks promotion

### AirDNA

- FACT:
  - tier=3, family=analytics_vendor, legal_mode=official_partner_or_vendor_only, access_mode=licensed_data
  - listing_types=short_term_rent_metrics
- INTERPRETATION:
  - proposed_pattern_kind=`licensed_data_ingest`
  - content summary: analytics_vendor; listing_types=short_term_rent_metrics.
- GAP:
  - main blocker: Legal or contract gate blocks promotion

### BCPEA property auctions

- FACT:
  - tier=3, family=official_register, legal_mode=public_crawl_with_review, access_mode=html
  - listing_types=auction_sale
- INTERPRETATION:
  - proposed_pattern_kind=`html_list_detail_gallery`
  - content summary: official_register; listing_types=auction_sale.
- GAP:
  - main blocker: Section or list-route discovery is incomplete

### Booking.com

- FACT:
  - tier=3, family=ota, legal_mode=official_partner_or_vendor_only, access_mode=partner_feed
  - listing_types=short_term_rent
- INTERPRETATION:
  - proposed_pattern_kind=`partner_feed_or_vendor_contract`
  - content summary: ota; listing_types=short_term_rent.
- GAP:
  - main blocker: Legal or contract gate blocks promotion

### Flat Manager

- FACT:
  - tier=3, family=ota, legal_mode=official_partner_or_vendor_only, access_mode=partner_feed
  - listing_types=short_term_rent, property_management
- INTERPRETATION:
  - proposed_pattern_kind=`partner_feed_or_vendor_contract`
  - content summary: ota; listing_types=short_term_rent, property_management.
- GAP:
  - main blocker: Legal or contract gate blocks promotion

### KAIS Cadastre

- FACT:
  - tier=3, family=official_register, legal_mode=consent_or_manual_only, access_mode=manual_consent_only
  - listing_types=building_geometry, parcel_validation
- INTERPRETATION:
  - proposed_pattern_kind=`manual_or_consent_flow`
  - content summary: official_register; listing_types=building_geometry, parcel_validation.
- GAP:
  - main blocker: Legal or contract gate blocks promotion

### Menada Bulgaria

- FACT:
  - tier=3, family=ota, legal_mode=official_partner_or_vendor_only, access_mode=partner_feed
  - listing_types=short_term_rent, property_management
- INTERPRETATION:
  - proposed_pattern_kind=`partner_feed_or_vendor_contract`
  - content summary: ota; listing_types=short_term_rent, property_management.
- GAP:
  - main blocker: Legal or contract gate blocks promotion

### Property Register

- FACT:
  - tier=3, family=official_register, legal_mode=consent_or_manual_only, access_mode=manual_consent_only
  - listing_types=ownership_verification
- INTERPRETATION:
  - proposed_pattern_kind=`manual_or_consent_flow`
  - content summary: official_register; listing_types=ownership_verification.
- GAP:
  - main blocker: Legal or contract gate blocks promotion

### Vrbo

- FACT:
  - tier=3, family=ota, legal_mode=official_partner_or_vendor_only, access_mode=partner_feed
  - listing_types=short_term_rent
- INTERPRETATION:
  - proposed_pattern_kind=`partner_feed_or_vendor_contract`
  - content summary: ota; listing_types=short_term_rent.
- GAP:
  - main blocker: Legal or contract gate blocks promotion

### Facebook public groups/pages

- FACT:
  - tier=4, family=social_public_channel, legal_mode=consent_or_manual_only, access_mode=manual_consent_only
  - listing_types=leads, long_term_rent
- INTERPRETATION:
  - proposed_pattern_kind=`manual_or_consent_flow`
  - content summary: social_public_channel; listing_types=leads, long_term_rent.
- GAP:
  - main blocker: Legal or contract gate blocks promotion

### Instagram public profiles

- FACT:
  - tier=4, family=social_public_channel, legal_mode=consent_or_manual_only, access_mode=manual_consent_only
  - listing_types=leads, branding
- INTERPRETATION:
  - proposed_pattern_kind=`manual_or_consent_flow`
  - content summary: social_public_channel; listing_types=leads, branding.
- GAP:
  - main blocker: Legal or contract gate blocks promotion

### Telegram public channels

- FACT:
  - tier=4, family=social_public_channel, legal_mode=official_api_allowed, access_mode=official_api
  - listing_types=leads, sale, long_term_rent
- INTERPRETATION:
  - proposed_pattern_kind=`official_api_overlay`
  - content summary: social_public_channel; listing_types=leads, sale, long_term_rent.
- GAP:
  - no tier12-style pattern issue row exists; this source should follow its legal/access pattern.

### Threads public profiles

- FACT:
  - tier=4, family=social_public_channel, legal_mode=consent_or_manual_only, access_mode=manual_consent_only
  - listing_types=leads, branding, links
- INTERPRETATION:
  - proposed_pattern_kind=`manual_or_consent_flow`
  - content summary: social_public_channel; listing_types=leads, branding, links.
- GAP:
  - main blocker: Legal or contract gate blocks promotion

### Viber opt-in communities

- FACT:
  - tier=4, family=private_messenger, legal_mode=consent_or_manual_only, access_mode=manual_consent_only
  - listing_types=leads, sale, long_term_rent
- INTERPRETATION:
  - proposed_pattern_kind=`manual_or_consent_flow`
  - content summary: private_messenger; listing_types=leads, sale, long_term_rent.
- GAP:
  - main blocker: Legal or contract gate blocks promotion

### WhatsApp opt-in groups

- FACT:
  - tier=4, family=private_messenger, legal_mode=official_partner_or_vendor_only, access_mode=manual_consent_only
  - listing_types=leads, sale, long_term_rent
- INTERPRETATION:
  - proposed_pattern_kind=`manual_or_consent_flow`
  - content summary: private_messenger; listing_types=leads, sale, long_term_rent.
- GAP:
  - main blocker: Legal or contract gate blocks promotion

### X public search/accounts

- FACT:
  - tier=4, family=social_public_channel, legal_mode=official_api_allowed, access_mode=official_api
  - listing_types=news, links, leads
- INTERPRETATION:
  - proposed_pattern_kind=`official_api_overlay`
  - content summary: social_public_channel; listing_types=news, links, leads.
- GAP:
  - main blocker: Section or list-route discovery is incomplete

## Patterned non-Action1 universality review

| Source | Status | Saved items | Services seen | Categories seen | Fixture cases | Reason |
|---|---|---:|---|---|---|---|
| OLX.bg | `broad_schema_but_not_fully_proven_universal` | 249 | long_term_rent, sale | apartment, house, land, office, unknown | basic_listing, blocked_page, discovery_empty, discovery_last_page, discovery_page, missing_price | API-backed parser covers sale/rent plus apartment/house/land/office in saved corpus, but fixture proof is limited to basic + missing-price detail shapes and no new_build-specific evidence exists. |
| Bazar.bg | `not_proven_universal` | 250 | long_term_rent, sale | apartment, office, unknown | basic_listing, land_listing | Saved corpus spans sale/rent and some office rows, but fixtures only prove apartment and land; rent/commercial layouts are not directly fixture-backed. |
| Yavlena | `not_proven_universal` | 251 | long_term_rent, sale | apartment, house, land, office, unknown | basic_listing, long_term_rent | Saved corpus spans sale houses/land/offices and some rent, but fixtures only prove one sale and one rent case; gallery depth is also only one image in the best sample. |

## Conclusions

- FACT: the strongest unpatterned public-scrape candidates already have some route or fixture evidence: `alo.bg`, `Domaza`, and `Home2U`.
- FACT: several tier-2 sources remain route-poor and fixture-poor; they need route discovery before parser promotion.
- FACT: tier-3 and much of tier-4 should not be judged by the same public-scrape `Patterned` bar because their legal access model is different.
- INTERPRETATION: the repo needs a second status axis: `pattern model exists` versus `strict live sample proof exists`.
- GAP: `OLX.bg`, `Bazar.bg`, and `Yavlena` remain operational but not universally proven across every property/service template on their websites.
