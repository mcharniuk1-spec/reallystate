# Bulgaria Real Estate - Scraping Inventory & Source Summary

*Generated: 2026-04-09 09:52 UTC*

## Overview

| Metric | Value |
|--------|-------|
| Total sources in registry | 44 |
| Tier-1 (primary portals) | 10 |
| Tier-2 (expansion) | 17 |
| Tier-3 (partner/official) | 10 |
| Tier-4 (social/lead intel) | 7 |
| Total listing fixtures scraped | 31 |
| Total live listings parsed | 1248 |
| Total live URLs discovered | 1283 |
| Total discovery fixtures | 14 |
| Total photos captured in fixtures | 26 |

## Tier 1 - Primary Portals & Classifieds

### [Address.bg](https://address.bg/)

- **URL**: https://address.bg/
- **Family**: agency
- **Owner**: Realto Group
- **Access**: `html`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg
- **Categories to scrape**: Sale, Long-term Rent, Land, New Build
- **Est. total listings on site**: 18000
- **Extraction method**: crawl listings with ref-id normalization
- **Notes**: Core agency network with strong local branches.

**Fixture Statistics:**

| Metric | Count |
|--------|-------|
| Listing fixtures | 1 |
| Discovery fixtures | 1 |
| Discovery URLs extracted | 2 |
| Blocked/error fixtures | 1 |
| Photos captured | 1 |
| With geo (lat/lon) | 1 |
| With address/city | 1 |
| With price | 1 |
| With area (sqm) | 1 |
| With rooms | 0 |
| Intents covered | sale |
| Property types seen | apartment |

### [alo.bg](https://www.alo.bg/)

- **URL**: https://www.alo.bg/
- **Family**: classifieds
- **Owner**: ALO.BG
- **Access**: `html`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg
- **Categories to scrape**: Sale, Long-term Rent, Short-term Rent, Land, New Build
- **Est. total listings on site**: 35000
- **Extraction method**: scoped HTML crawl with category filtering
- **Notes**: Strong coastal inventory, especially land and new-build.

**Fixture Statistics:**

| Metric | Count |
|--------|-------|
| Listing fixtures | 1 |
| Discovery fixtures | 1 |
| Discovery URLs extracted | 2 |
| Blocked/error fixtures | 1 |
| Photos captured | 1 |
| With geo (lat/lon) | 1 |
| With address/city | 1 |
| With price | 1 |
| With area (sqm) | 1 |
| With rooms | 0 |
| Intents covered | sale |
| Property types seen | apartment |

### [BulgarianProperties](https://www.bulgarianproperties.bg/)

- **URL**: https://www.bulgarianproperties.bg/
- **Family**: agency
- **Owner**: Bulgarian Properties
- **Access**: `html`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg, en
- **Categories to scrape**: Sale, Long-term Rent, Land, New Build
- **Est. total listings on site**: 12000
- **Extraction method**: conservative crawl using stable reference IDs
- **Notes**: Important for new-build and foreign buyer inventory.

**Live Harvest Statistics:**

| Metric | Count |
|--------|-------|
| Live URLs discovered | 250 |
| Live listings parsed | 249 |
| Live photos downloaded | 249 |
| Latest live run | 2026-04-08T16:42:37.971917+00:00 |
| Live product buckets | - |

**Fixture Statistics:**

| Metric | Count |
|--------|-------|
| Listing fixtures | 1 |
| Discovery fixtures | 1 |
| Discovery URLs extracted | 2 |
| Blocked/error fixtures | 1 |
| Photos captured | 1 |
| With geo (lat/lon) | 1 |
| With address/city | 1 |
| With price | 1 |
| With area (sqm) | 1 |
| With rooms | 0 |
| Intents covered | sale |
| Property types seen | apartment |

### [Homes.bg](https://www.homes.bg/)

- **URL**: https://www.homes.bg/
- **Family**: portal
- **Owner**: Jobs.bg
- **Access**: `html`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg
- **Categories to scrape**: Sale, Long-term Rent, Land
- **Est. total listings on site**: 120000
- **Extraction method**: server-rendered HTML crawl
- **Notes**: Crawl-friendly and broad national coverage.

**Fixture Statistics:**

| Metric | Count |
|--------|-------|
| Listing fixtures | 3 |
| Discovery fixtures | 3 |
| Discovery URLs extracted | 7 |
| Blocked/error fixtures | 2 |
| Photos captured | 3 |
| With geo (lat/lon) | 1 |
| With address/city | 3 |
| With price | 2 |
| With area (sqm) | 0 |
| With rooms | 0 |
| Intents covered | mixed |
| Property types seen | apartment, house |

### [imot.bg](https://www.imot.bg/)

- **URL**: https://www.imot.bg/
- **Family**: portal
- **Owner**: Rezon Media
- **Access**: `html`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg
- **Categories to scrape**: Sale, Long-term Rent, Land, New Build
- **Est. total listings on site**: 200000
- **Extraction method**: respectful crawl or partnership feed
- **Notes**: High-volume benchmark supply source.

**Live Harvest Statistics:**

| Metric | Count |
|--------|-------|
| Live URLs discovered | 254 |
| Live listings parsed | 250 |
| Live photos downloaded | 1 |
| Latest live run | 2026-04-08T16:30:52.841147+00:00 |
| Live product buckets | - |

**Fixture Statistics:**

| Metric | Count |
|--------|-------|
| Listing fixtures | 1 |
| Discovery fixtures | 1 |
| Discovery URLs extracted | 2 |
| Blocked/error fixtures | 1 |
| Photos captured | 1 |
| With geo (lat/lon) | 1 |
| With address/city | 1 |
| With price | 1 |
| With area (sqm) | 1 |
| With rooms | 0 |
| Intents covered | sale |
| Property types seen | apartment |

### [imoti.net](https://www.imoti.net/)

- **URL**: https://www.imoti.net/
- **Family**: portal
- **Owner**: Investor Media Group
- **Access**: `headless`
- **Legal mode**: `legal_review_required`
- **Risk**: `high`
- **Languages**: bg, en
- **Categories to scrape**: Sale, Long-term Rent, Land, New Build
- **Est. total listings on site**: 90000
- **Extraction method**: partnership first, headless as fallback
- **Notes**: 403 and anti-bot patterns raise risk.

**Fixture Statistics:**

| Metric | Count |
|--------|-------|
| Listing fixtures | 1 |
| Discovery fixtures | 0 |
| Discovery URLs extracted | 0 |
| Blocked/error fixtures | 1 |
| Photos captured | 1 |
| With geo (lat/lon) | 1 |
| With address/city | 1 |
| With price | 1 |
| With area (sqm) | 1 |
| With rooms | 0 |
| Intents covered | mixed |
| Property types seen | apartment |

### [LUXIMMO](https://www.luximmo.bg/)

- **URL**: https://www.luximmo.bg/
- **Family**: agency
- **Owner**: Stoyanov Enterprises
- **Access**: `html`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg, en
- **Categories to scrape**: Sale, Long-term Rent, Land, New Build
- **Est. total listings on site**: 4000
- **Extraction method**: careful crawl using stable luxury listing reference IDs
- **Notes**: Luxury coastal segment.

**Fixture Statistics:**

| Metric | Count |
|--------|-------|
| Listing fixtures | 1 |
| Discovery fixtures | 1 |
| Discovery URLs extracted | 2 |
| Blocked/error fixtures | 1 |
| Photos captured | 1 |
| With geo (lat/lon) | 1 |
| With address/city | 1 |
| With price | 1 |
| With area (sqm) | 1 |
| With rooms | 0 |
| Intents covered | sale |
| Property types seen | apartment |

### [OLX.bg](https://www.olx.bg/)

- **URL**: https://www.olx.bg/
- **Family**: classifieds
- **Owner**: Naspers Classifieds Bulgaria / OLX
- **Access**: `official_api`
- **Legal mode**: `official_api_allowed`
- **Risk**: `low`
- **Languages**: bg
- **Categories to scrape**: Sale, Long-term Rent, Land, New Build
- **Est. total listings on site**: 45000
- **Extraction method**: official developer API first
- **Notes**: Primary API-first classifieds source.

**Live Harvest Statistics:**

| Metric | Count |
|--------|-------|
| Live URLs discovered | 257 |
| Live listings parsed | 249 |
| Live photos downloaded | 1365 |
| Latest live run | 2026-04-08T17:31:38.962595+00:00 |
| Live product buckets | - |

**Fixture Statistics:**

| Metric | Count |
|--------|-------|
| Listing fixtures | 2 |
| Discovery fixtures | 3 |
| Discovery URLs extracted | 3 |
| Blocked/error fixtures | 1 |
| Photos captured | 2 |
| With geo (lat/lon) | 2 |
| With address/city | 2 |
| With price | 1 |
| With area (sqm) | 2 |
| With rooms | 1 |
| Intents covered | sale |
| Property types seen | apartment, land |

### [property.bg](https://www.property.bg/)

- **URL**: https://www.property.bg/
- **Family**: portal
- **Owner**: SUPRIMMO group
- **Access**: `html`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg, en
- **Categories to scrape**: Sale, Long-term Rent, Land, New Build
- **Est. total listings on site**: 10000
- **Extraction method**: targeted listing-page crawl
- **Notes**: Cross-check source for foreign-buyer inventory.

**Fixture Statistics:**

| Metric | Count |
|--------|-------|
| Listing fixtures | 1 |
| Discovery fixtures | 1 |
| Discovery URLs extracted | 2 |
| Blocked/error fixtures | 1 |
| Photos captured | 1 |
| With geo (lat/lon) | 1 |
| With address/city | 1 |
| With price | 1 |
| With area (sqm) | 1 |
| With rooms | 0 |
| Intents covered | sale |
| Property types seen | apartment |

### [SUPRIMMO](https://www.suprimmo.bg/)

- **URL**: https://www.suprimmo.bg/
- **Family**: agency
- **Owner**: Stoyanov Enterprises
- **Access**: `html`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg, en
- **Categories to scrape**: Sale, Long-term Rent, Land, New Build
- **Est. total listings on site**: 15000
- **Extraction method**: crawl listings and unify group reference IDs
- **Notes**: High-value coastal and resort inventory.

**Fixture Statistics:**

| Metric | Count |
|--------|-------|
| Listing fixtures | 1 |
| Discovery fixtures | 1 |
| Discovery URLs extracted | 2 |
| Blocked/error fixtures | 1 |
| Photos captured | 1 |
| With geo (lat/lon) | 1 |
| With address/city | 1 |
| With price | 1 |
| With area (sqm) | 1 |
| With rooms | 0 |
| Intents covered | sale |
| Property types seen | apartment |

## Tier 2 - Expansion Sources

### [ApartmentsBulgaria.com](https://www.apartmentsbulgaria.bg/)

- **URL**: https://www.apartmentsbulgaria.bg/
- **Family**: ota
- **Owner**: Property Management BG
- **Access**: `headless`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg, en
- **Categories to scrape**: Short-term Rent
- **Est. total listings on site**: 1800
- **Extraction method**: direct booking integration or careful crawl
- **Notes**: Managed resort inventory.

*No fixtures yet.*


### [Bazar.bg](https://bazar.bg/)

- **URL**: https://bazar.bg/
- **Family**: classifieds
- **Owner**: Rezon Media
- **Access**: `html`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg
- **Categories to scrape**: Sale, Long-term Rent, Land
- **Est. total listings on site**: 8000
- **Extraction method**: limited HTML crawl
- **Notes**: Secondary but useful classifieds source.

**Live Harvest Statistics:**

| Metric | Count |
|--------|-------|
| Live URLs discovered | 272 |
| Live listings parsed | 250 |
| Live photos downloaded | 2487 |
| Latest live run | 2026-04-08T16:54:12.900549+00:00 |
| Live product buckets | - |

**Fixture Statistics:**

| Metric | Count |
|--------|-------|
| Listing fixtures | 2 |
| Discovery fixtures | 0 |
| Discovery URLs extracted | 0 |
| Blocked/error fixtures | 0 |
| Photos captured | 2 |
| With geo (lat/lon) | 2 |
| With address/city | 2 |
| With price | 2 |
| With area (sqm) | 2 |
| With rooms | 0 |
| Intents covered | sale |
| Property types seen | apartment, land |

### [Domaza](https://www.domaza.bg/)

- **URL**: https://www.domaza.bg/
- **Family**: portal
- **Owner**: Domaza
- **Access**: `html`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg, en
- **Categories to scrape**: Sale, Long-term Rent, Short-term Rent, Land, New Build
- **Est. total listings on site**: 22000
- **Extraction method**: crawl with language canonicalization
- **Notes**: Needs cross-language dedupe.

**Fixture Statistics:**

| Metric | Count |
|--------|-------|
| Listing fixtures | 2 |
| Discovery fixtures | 0 |
| Discovery URLs extracted | 0 |
| Blocked/error fixtures | 0 |
| Photos captured | 2 |
| With geo (lat/lon) | 2 |
| With address/city | 2 |
| With price | 2 |
| With area (sqm) | 2 |
| With rooms | 0 |
| Intents covered | sale, short_term_rent |
| Property types seen | apartment |

### [Holding Group Real Estate](https://holdinggroup.bg/)

- **URL**: https://holdinggroup.bg/
- **Family**: agency
- **Owner**: Holding Group
- **Access**: `html`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg
- **Categories to scrape**: Sale, Long-term Rent, Land, New Build
- **Est. total listings on site**: 3000
- **Extraction method**: crawl direct site plus dedupe against portal syndication
- **Notes**: Strong Varna-side project inventory.

*No fixtures yet.*


### [Home2U](https://home2u.bg/)

- **URL**: https://home2u.bg/
- **Family**: agency
- **Owner**: Home2U
- **Access**: `html`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg, en, ru
- **Categories to scrape**: Sale, Long-term Rent, Land, New Build
- **Est. total listings on site**: 6000
- **Extraction method**: templated HTML parser
- **Notes**: Important for Varna and project inventory.

**Fixture Statistics:**

| Metric | Count |
|--------|-------|
| Listing fixtures | 2 |
| Discovery fixtures | 0 |
| Discovery URLs extracted | 0 |
| Blocked/error fixtures | 0 |
| Photos captured | 2 |
| With geo (lat/lon) | 2 |
| With address/city | 2 |
| With price | 2 |
| With area (sqm) | 2 |
| With rooms | 0 |
| Intents covered | sale |
| Property types seen | house, project |

### [Imoteka.bg](https://imoteka.bg/)

- **URL**: https://imoteka.bg/
- **Family**: agency
- **Owner**: Realto Group
- **Access**: `headless`
- **Legal mode**: `legal_review_required`
- **Risk**: `high`
- **Languages**: bg, en
- **Categories to scrape**: Sale, Long-term Rent, Land, New Build
- **Est. total listings on site**: 14000
- **Extraction method**: partnership/licensed feed preferred; headless only after legal clearance
- **Notes**: JS-heavy source with higher content-use risk.

*No fixtures yet.*


### [Imoti.info](https://imoti.info/)

- **URL**: https://imoti.info/
- **Family**: classifieds
- **Owner**: Bulinfo OOD
- **Access**: `partner_feed`
- **Legal mode**: `licensing_required`
- **Risk**: `high`
- **Languages**: bg, en
- **Categories to scrape**: Sale, Long-term Rent, Land, New Build
- **Est. total listings on site**: 25000
- **Extraction method**: licensing or partnership first; fixture-only parser research until approved
- **Notes**: Terms indicate commercial data use requires authorization/payment.

*No fixtures yet.*


### [Indomio.bg](https://www.indomio.bg/)

- **URL**: https://www.indomio.bg/
- **Family**: portal
- **Owner**: Spitogatos Network
- **Access**: `headless`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg, en
- **Categories to scrape**: Sale, Long-term Rent, Land
- **Est. total listings on site**: 7000
- **Extraction method**: hybrid HTML/headless crawler
- **Notes**: Secondary index for coastal supply.

*No fixtures yet.*


### [Lions Group](https://lionsgroup.bg/)

- **URL**: https://lionsgroup.bg/
- **Family**: agency
- **Owner**: Lions Group
- **Access**: `html`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg, en
- **Categories to scrape**: Sale, Long-term Rent, Land, New Build
- **Est. total listings on site**: 2500
- **Extraction method**: server-rendered listing crawl
- **Notes**: Useful Varna-side agency inventory.

*No fixtures yet.*


### [Pochivka.bg](https://pochivka.bg/)

- **URL**: https://pochivka.bg/
- **Family**: ota
- **Owner**: Pochivka BG
- **Access**: `html`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg, en
- **Categories to scrape**: Short-term Rent
- **Est. total listings on site**: 5000
- **Extraction method**: partnership or limited travel-catalog crawl
- **Notes**: Hospitality intelligence more than core sale inventory.

*No fixtures yet.*


### [realestates.bg](https://en.realestates.bg/)

- **URL**: https://en.realestates.bg/
- **Family**: classifieds
- **Owner**: ALO.BG network
- **Access**: `html`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg, en
- **Categories to scrape**: Sale, Long-term Rent, Land
- **Est. total listings on site**: 6000
- **Extraction method**: scope-limited HTML crawl and dedupe against alo.bg
- **Notes**: Foreign-facing Alo network layer.

*No fixtures yet.*


### [Realistimo](https://realistimo.com/)

- **URL**: https://realistimo.com/
- **Family**: portal
- **Owner**: Realistimo
- **Access**: `headless`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg, en
- **Categories to scrape**: Sale, Long-term Rent, Land, New Build
- **Est. total listings on site**: 4500
- **Extraction method**: HTML crawl with map-filter fallback
- **Notes**: Map-driven browsing suggests structured geo data.

*No fixtures yet.*


### [Rentica.bg](https://rentica.bg/)

- **URL**: https://rentica.bg/
- **Family**: agency
- **Owner**: Rentica
- **Access**: `html`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg
- **Categories to scrape**: Long-term Rent
- **Est. total listings on site**: 1200
- **Extraction method**: rent-only HTML parser
- **Notes**: Varna rental specialist.

*No fixtures yet.*


### [Svobodni-kvartiri.com](https://svobodni-kvartiri.com/)

- **URL**: https://svobodni-kvartiri.com/
- **Family**: portal
- **Owner**: Svobodni kvartiri
- **Access**: `html`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg
- **Categories to scrape**: Long-term Rent, Short-term Rent
- **Est. total listings on site**: 3500
- **Extraction method**: deep pagination crawl by city scope
- **Notes**: Useful for worker and student rentals.

*No fixtures yet.*


### [Unique Estates](https://ues.bg/)

- **URL**: https://ues.bg/
- **Family**: agency
- **Owner**: Realto Group
- **Access**: `html`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg, en
- **Categories to scrape**: Sale, Long-term Rent, New Build
- **Est. total listings on site**: 2000
- **Extraction method**: luxury listing crawler
- **Notes**: Luxury sea-segment pages.

*No fixtures yet.*


### [Vila.bg](https://vila.bg/)

- **URL**: https://vila.bg/
- **Family**: ota
- **Owner**: Vila Tours
- **Access**: `html`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg, en
- **Categories to scrape**: Short-term Rent
- **Est. total listings on site**: 4000
- **Extraction method**: partnership or limited catalog crawl
- **Notes**: Villa and guest-house coverage.

*No fixtures yet.*


### [Yavlena](https://www.yavlena.com/)

- **URL**: https://www.yavlena.com/
- **Family**: agency
- **Owner**: Yavlena
- **Access**: `html`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg, en
- **Categories to scrape**: Sale, Long-term Rent
- **Est. total listings on site**: 9000
- **Extraction method**: incremental crawl with ID-based URLs
- **Notes**: Established agency with branch-driven supply.

**Live Harvest Statistics:**

| Metric | Count |
|--------|-------|
| Live URLs discovered | 250 |
| Live listings parsed | 250 |
| Live photos downloaded | 249 |
| Latest live run | 2026-04-08T17:18:17.189285+00:00 |
| Live product buckets | - |

**Fixture Statistics:**

| Metric | Count |
|--------|-------|
| Listing fixtures | 2 |
| Discovery fixtures | 0 |
| Discovery URLs extracted | 0 |
| Blocked/error fixtures | 0 |
| Photos captured | 2 |
| With geo (lat/lon) | 2 |
| With address/city | 2 |
| With price | 2 |
| With area (sqm) | 2 |
| With rooms | 0 |
| Intents covered | long_term_rent, sale |
| Property types seen | apartment |

## Tier 3 - Partner / Official / Vendor

### [Airbnb](https://www.airbnb.com/)

- **URL**: https://www.airbnb.com/
- **Family**: ota
- **Owner**: Airbnb, Inc.
- **Access**: `partner_feed`
- **Legal mode**: `official_partner_or_vendor_only`
- **Risk**: `prohibited_without_contract`
- **Languages**: multi
- **Categories to scrape**: Short-term Rent
- **Est. total listings on site**: N/A (partner)
- **Extraction method**: official authorized partner integration only
- **Notes**: Do not rely on scraping as a core acquisition path.

*No fixtures yet.*


### [Airbtics](https://airbtics.com/)

- **URL**: https://airbtics.com/
- **Family**: analytics_vendor
- **Owner**: Airbtics
- **Access**: `licensed_data`
- **Legal mode**: `official_partner_or_vendor_only`
- **Risk**: `low`
- **Languages**: en
- **Categories to scrape**: STR Metrics
- **Est. total listings on site**: N/A (licensed)
- **Extraction method**: REST API or licensed export
- **Notes**: Use for coastal STR benchmarks.

*No fixtures yet.*


### [AirDNA](https://www.airdna.co/)

- **URL**: https://www.airdna.co/
- **Family**: analytics_vendor
- **Owner**: AirDNA
- **Access**: `licensed_data`
- **Legal mode**: `official_partner_or_vendor_only`
- **Risk**: `low`
- **Languages**: en
- **Categories to scrape**: STR Metrics
- **Est. total listings on site**: N/A (licensed)
- **Extraction method**: licensed export or enterprise contract
- **Notes**: Use for STR enrichment, not primary listings.

*No fixtures yet.*


### [BCPEA property auctions](https://sales.bcpea.org/properties)

- **URL**: https://sales.bcpea.org/properties
- **Family**: official_register
- **Owner**: Chamber of Private Bailiffs
- **Access**: `html`
- **Legal mode**: `public_crawl_with_review`
- **Risk**: `medium`
- **Languages**: bg
- **Categories to scrape**: Auction Sale
- **Est. total listings on site**: 1224
- **Extraction method**: HTML crawl plus OCR when notices are scanned
- **Notes**: Useful opportunistic inventory source.

**Fixture Statistics:**

| Metric | Count |
|--------|-------|
| Listing fixtures | 1 |
| Discovery fixtures | 1 |
| Discovery URLs extracted | 3 |
| Blocked/error fixtures | 0 |
| Photos captured | 3 |
| With geo (lat/lon) | 0 |
| With address/city | 1 |
| With price | 0 |
| With area (sqm) | 1 |
| With rooms | 0 |
| Intents covered | auction_sale |
| Property types seen | Къща |

### [Booking.com](https://www.booking.com/)

- **URL**: https://www.booking.com/
- **Family**: ota
- **Owner**: Booking Holdings
- **Access**: `partner_feed`
- **Legal mode**: `official_partner_or_vendor_only`
- **Risk**: `prohibited_without_contract`
- **Languages**: multi
- **Categories to scrape**: Short-term Rent
- **Est. total listings on site**: N/A (partner)
- **Extraction method**: connectivity/content partner APIs only
- **Notes**: Certification-first publishing route.

*No fixtures yet.*


### [Flat Manager](https://flatmanager.bg/)

- **URL**: https://flatmanager.bg/
- **Family**: ota
- **Owner**: Flat Manager / Renters.pl
- **Access**: `partner_feed`
- **Legal mode**: `official_partner_or_vendor_only`
- **Risk**: `medium`
- **Languages**: bg, en
- **Categories to scrape**: Short-term Rent, Property Management
- **Est. total listings on site**: N/A (partner)
- **Extraction method**: partnership or direct booking integration only
- **Notes**: Managed STR/direct-booking inventory and potential distribution partner.

*No fixtures yet.*


### [KAIS Cadastre](https://kais.cadastre.bg/bg/Map)

- **URL**: https://kais.cadastre.bg/bg/Map
- **Family**: official_register
- **Owner**: Agency for Geodesy, Cartography and Cadastre
- **Access**: `manual_consent_only`
- **Legal mode**: `consent_or_manual_only`
- **Risk**: `high`
- **Languages**: bg
- **Categories to scrape**: Building Geometry, Parcel Validation
- **Est. total listings on site**: N/A (manual)
- **Extraction method**: official services and permitted exports
- **Notes**: Geospatial backbone for building matching.

*No fixtures yet.*


### [Menada Bulgaria](https://menadabulgaria.com/)

- **URL**: https://menadabulgaria.com/
- **Family**: ota
- **Owner**: Menada Bulgaria
- **Access**: `partner_feed`
- **Legal mode**: `official_partner_or_vendor_only`
- **Risk**: `medium`
- **Languages**: bg, en, pl
- **Categories to scrape**: Short-term Rent, Property Management
- **Est. total listings on site**: N/A (partner)
- **Extraction method**: partnership/direct booking integration
- **Notes**: Black Sea property management and STR inventory.

*No fixtures yet.*


### [Property Register](https://portal.registryagency.bg/en/home-pr)

- **URL**: https://portal.registryagency.bg/en/home-pr
- **Family**: official_register
- **Owner**: Registry Agency
- **Access**: `manual_consent_only`
- **Legal mode**: `consent_or_manual_only`
- **Risk**: `high`
- **Languages**: bg, en
- **Categories to scrape**: Ownership Verification
- **Est. total listings on site**: N/A (manual)
- **Extraction method**: official e-service queries only
- **Notes**: Verification layer, not acquisition feed.

*No fixtures yet.*


### [Vrbo](https://www.vrbo.com/)

- **URL**: https://www.vrbo.com/
- **Family**: ota
- **Owner**: Expedia Group
- **Access**: `partner_feed`
- **Legal mode**: `official_partner_or_vendor_only`
- **Risk**: `high`
- **Languages**: multi
- **Categories to scrape**: Short-term Rent
- **Est. total listings on site**: N/A (partner)
- **Extraction method**: partnership or licensed feed
- **Notes**: Not a crawl-first source.

*No fixtures yet.*


## Tier 4 - Social & Lead Intelligence

### [Facebook public groups/pages](https://www.facebook.com/groups/438018083766467/)

- **URL**: https://www.facebook.com/groups/438018083766467/
- **Family**: social_public_channel
- **Owner**: Meta
- **Access**: `manual_consent_only`
- **Legal mode**: `consent_or_manual_only`
- **Risk**: `high`
- **Languages**: bg
- **Categories to scrape**: Leads / Intelligence, Long-term Rent
- **Est. total listings on site**: N/A (social)
- **Extraction method**: manual monitoring or explicit partnerships
- **Notes**: Do not rely on unstable login-restricted scraping.

*No fixtures yet.*


### [Instagram public profiles](https://www.instagram.com/bulgarianproperties.bg/)

- **URL**: https://www.instagram.com/bulgarianproperties.bg/
- **Family**: social_public_channel
- **Owner**: Meta
- **Access**: `manual_consent_only`
- **Legal mode**: `consent_or_manual_only`
- **Risk**: `high`
- **Languages**: bg, en
- **Categories to scrape**: Leads / Intelligence, Branding
- **Est. total listings on site**: N/A (social)
- **Extraction method**: authorized business integrations or manual review
- **Notes**: Treat as agency-branding and lead overlay.

*No fixtures yet.*


### [Telegram public channels](https://t.me/rentvarna)

- **URL**: https://t.me/rentvarna
- **Family**: social_public_channel
- **Owner**: Telegram
- **Access**: `official_api`
- **Legal mode**: `official_api_allowed`
- **Risk**: `medium`
- **Languages**: bg, en, ru
- **Categories to scrape**: Leads / Intelligence, Sale, Long-term Rent
- **Est. total listings on site**: N/A (social)
- **Extraction method**: public API/client ingestion with NLP extraction
- **Notes**: Lead-intelligence overlay only.

**Fixture Statistics:**

| Metric | Count |
|--------|-------|
| Listing fixtures | 3 |
| Discovery fixtures | 0 |
| Discovery URLs extracted | 0 |
| Blocked/error fixtures | 0 |
| Photos captured | 0 |
| With geo (lat/lon) | 0 |
| With address/city | 2 |
| With price | 2 |
| With area (sqm) | 0 |
| With rooms | 0 |
| Intents covered | long_term_rent, sale |
| Property types seen | apartment |

### [Threads public profiles]()

- **URL**: 
- **Family**: social_public_channel
- **Owner**: Meta
- **Access**: `manual_consent_only`
- **Legal mode**: `consent_or_manual_only`
- **Risk**: `high`
- **Languages**: bg, en
- **Categories to scrape**: Leads / Intelligence, Branding, Links
- **Est. total listings on site**: N/A (social)
- **Extraction method**: experimental public-profile monitoring only after access review
- **Notes**: Deferred overlay until official/public read coverage is confirmed.

*No fixtures yet.*


### [Viber opt-in communities](https://invite.viber.com/?g2=AQA%2BxCYrr7Jy1VEh6Ic98YLAlDXOmJicE8MDwi%2F0NU%2FsFss%2FWRC%2B0lL9ufcuh96f)

- **URL**: https://invite.viber.com/?g2=AQA%2BxCYrr7Jy1VEh6Ic98YLAlDXOmJicE8MDwi%2F0NU%2FsFss%2FWRC%2B0lL9ufcuh96f
- **Family**: private_messenger
- **Owner**: Rakuten Viber
- **Access**: `manual_consent_only`
- **Legal mode**: `consent_or_manual_only`
- **Risk**: `high`
- **Languages**: bg
- **Categories to scrape**: Leads / Intelligence, Sale, Long-term Rent
- **Est. total listings on site**: N/A (social)
- **Extraction method**: opt-in community ingestion only
- **Notes**: Privacy-restricted and unstructured.

*No fixtures yet.*


### [WhatsApp opt-in groups](https://chat.whatsapp.com/HB3Kt48meI08eIaYSuJ1Go?mode=gi_t)

- **URL**: https://chat.whatsapp.com/HB3Kt48meI08eIaYSuJ1Go?mode=gi_t
- **Family**: private_messenger
- **Owner**: Meta
- **Access**: `manual_consent_only`
- **Legal mode**: `official_partner_or_vendor_only`
- **Risk**: `prohibited_without_contract`
- **Languages**: bg
- **Categories to scrape**: Leads / Intelligence, Sale, Long-term Rent
- **Est. total listings on site**: N/A (social)
- **Extraction method**: explicit opt-in via WhatsApp Business only
- **Notes**: Useful for owned-business communication, not broad scraping.

*No fixtures yet.*


### [X public search/accounts](https://x.com/super_imoti)

- **URL**: https://x.com/super_imoti
- **Family**: social_public_channel
- **Owner**: X
- **Access**: `official_api`
- **Legal mode**: `official_api_allowed`
- **Risk**: `low`
- **Languages**: bg, en
- **Categories to scrape**: News, Links, Leads / Intelligence
- **Est. total listings on site**: N/A (social)
- **Extraction method**: API or public-profile monitoring
- **Notes**: Useful mostly for market chatter and backlinks.

**Fixture Statistics:**

| Metric | Count |
|--------|-------|
| Listing fixtures | 2 |
| Discovery fixtures | 0 |
| Discovery URLs extracted | 0 |
| Blocked/error fixtures | 0 |
| Photos captured | 0 |
| With geo (lat/lon) | 0 |
| With address/city | 1 |
| With price | 1 |
| With area (sqm) | 0 |
| With rooms | 0 |
| Intents covered | sale |
| Property types seen | apartment |

---

## Legend

- **Tier 1**: Highest-volume national portals and classifieds. First to be fully connected.
- **Tier 2**: Regional agencies, secondary portals, travel/OTA sites. Expanded after tier-1 is stable.
- **Tier 3**: Partner feeds (Airbnb, Booking.com), licensed data vendors (AirDNA), official registers (BCPEA, KAIS). Require contracts or manual consent.
- **Tier 4**: Social and messaging platforms. Lead intelligence overlay only; consent-gated.
- **Fixture**: Offline HTML/JSON snapshot used for parser testing without live network calls.
- **Discovery fixture**: Simulates a search results page to test URL extraction and pagination.
- **Blocked fixture**: Simulates anti-bot / access-denied responses for error handling tests.
