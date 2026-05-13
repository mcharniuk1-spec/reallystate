# Market Intelligence Baseline

Generated: 2026-05-13

## Evidence Boundary

FACT: This report uses local repository evidence only: `data/source_registry.json`, `deep-research-report.md`, `docs/business/product-ux-structure.md`, `docs/business/unit-economics-market-analysis.md`, `docs/exports/scrape-database-quality-audit-2026-05-13.md`, `docs/exports/action1-dataset-quality-gate.md`, and `docs/exports/website-inventory-analysis.md`.

FACT: No browser, live scraping, private channel access, or external market lookup was used in this run.

FACT: PostgreSQL counts, live URL existence, current competitor changes after the saved reports, and semantic image descriptions remain unverified.

INTERPRETATION: Market strategy can use the current artifacts for prioritization, but public product claims must wait for accepted-only DB-backed evidence.

GAP: Regional supply share, price-per-sqm distributions, price history, and current rival movement are not yet available as reproducible analytics artifacts.

## Market Questions

### Supply Gaps

FACT: The registry tracks 44 sources: 10 tier-1, 17 tier-2, 10 tier-3, and 7 tier-4.

FACT: The file-backed scraped corpus contains 30,334 rows, including 29,397 Action1 rows. Action1 estimated quality is 20,811 accepted single-unit candidates, 7,133 LOST rows, and 1,453 grouped/development publications.

FACT: Stored QA state is not market-ready: 26,231 rows have pending, missing, or unknown QA status, and the default importer currently admits only 1,612 candidates.

FACT: Current corpus intent mix is sale and long-term rent only: 23,240 sale rows and 7,094 long-term rent rows. No short-term-rent, auction, official-register, or STR vendor metric rows are represented in the DA-01 corpus.

INTERPRETATION: The platform has enough raw marketplace material for internal QA and product testing, but the market view is still resale/long-term-rent heavy and cannot yet support complete-market claims.

HYPOTHESIS: The next visible supply uplift will come from repairing Action1 QA states and then expanding to high-volume tier-1/2 gaps: Homes.bg, alo.bg, Bazar.bg, OLX API, and selected tier-2 rental/STR sources after gates.

GAP: DA-02/BD-19 need city, district, price, and property-type rollups from accepted rows before weekly market review can identify actual regional shortage or oversupply.

### Competitor And Source Coverage

FACT: Saved ecosystem research groups important inventory around Rezon Media (`imot.bg`, `Bazar.bg`), Realto Group (`Address.bg`, `Imoteka.bg`, `Unique Estates`), and Stoyanov/SUPRIMMO brands (`SUPRIMMO`, `LUXIMMO`, `property.bg`).

FACT: Existing landed Action1 strength is concentrated in `imot_bg`, `property_bg`, `suprimmo`, `address_bg`, and `luximmo`. `Homes.bg` has only 144 landed rows despite a saved website-total estimate of 120,000. `alo.bg` has 29 rows against a saved lower-bound website count of 75,961. `Bazar.bg` has 250 rows against a saved exact real-estate umbrella count of 221,272.

FACT: `imoti.net`, `Imoteka.bg`, and `Imoti.info` are strategically relevant but have legal/headless/licensing constraints in the registry. They should not be treated as normal crawl targets.

INTERPRETATION: Competitor coverage should be measured in two layers: inventory gravity wells that define market breadth, and compliance-safe access modes that define executable ingestion.

HYPOTHESIS: Strong near-term product coverage is best framed as verified cross-source search across priority portals rather than 95% market coverage until Homes/alo/Bazar/OLX gaps and DB import proof are closed.

GAP: Current rival movement, pricing announcements, new partnership options, and live portal UI changes require explicit future browsing authorization or approved partner data.

### Source Strength

FACT: `imot_bg` has 9,937 rows and 8,986 estimated OK rows, making it the strongest current single-source corpus.

FACT: `property_bg` has 3,094 rows and 3,053 estimated OK rows, but only 5 default import candidates because stored QA remains pending.

FACT: `suprimmo` has 4,948 rows, 3,563 estimated OK rows, and 646 estimated grouped/development publications.

FACT: `address_bg` has 6,473 rows and 3,330 estimated OK rows, but 3,143 estimated LOST rows driven by city/address, area, and gallery issues.

FACT: `bulgarianproperties` has 2,289 rows but only 12 estimated OK rows because local-gallery completeness and area semantics fail current quality gates.

INTERPRETATION: `imot_bg` is the best current anchor for broad market browsing; Stoyanov-family sources are important for agency/new-build/development intelligence; Address.bg is strategically important but needs location/media repair; BulgarianProperties is a high-value foreign-buyer/new-build source but currently not product-grade.

GAP: Strength scoring needs accepted-only DB-backed counts, not estimated file-backed counts, before planner uses it for release prioritization.

### Pricing Visibility

FACT: The registry contains sale, long-term-rent, land, new-build, short-term-rent, auction-sale, and STR metric sources, but the current DA-01 corpus only covers sale and long-term rent.

FACT: The audit flags zero-price rows in Bazar.bg and Yavlena, low-sale-price warnings, grouped/development rows, missing areas, and absent first-class DB fields such as `price_status` and `price_per_sqm`.

INTERPRETATION: Pricing visibility is strongest for single-unit resale and rent rows in `imot_bg`, `property_bg`, `suprimmo`, `luximmo`, and parts of `address_bg`. It is weak for development pages, on-request prices, STR economics, auctions, and price history.

HYPOTHESIS: Buyer trust will improve faster if the product exposes price on request, price history unavailable, location approximate, and limited media states honestly rather than hiding evidence gaps.

GAP: No reproducible price-per-sqm city/district tables exist yet. STR pricing/yield remains vendor/licensed-data work, not crawl work.

### Missing Geography And Property Types

FACT: The product target is nationwide Bulgaria for map/listing browse, while the DB control plane still has Varna-only source-section constraints.

FACT: The current corpus category mix is apartment-heavy: 20,685 apartments, 3,893 houses, 2,792 land, 1,247 offices, 560 shops, and 1,157 unknown.

FACT: Bucket counts are uneven: 20,082 buy-personal rows, 5,019 rent-personal rows, 3,160 buy-commercial rows, 1,358 rent-commercial rows, and 715 missing bucket rows.

FACT: Missing city/address extraction is material, especially for Address.bg with 1,262 missing city/address gaps.

INTERPRETATION: Current market intelligence cannot yet answer which geography is undersupplied because accepted rows lack a stable geographic rollup. It can answer that the landed corpus is biased toward buy-personal apartments and underdeveloped for rent/commercial/STR/auction/new-build unit matrices.

GAP: Weekly review needs accepted-only city/district/property-type matrix for Sofia, Varna, Burgas, Plovdiv, resort municipalities, and the long tail.

## Strategic Product Positioning

FACT: Existing business docs position the product around fragmented supply, buyer-first search, map-first browsing, AI chat, source provenance, and eventual 95%+ supply aggregation.

INTERPRETATION: Until DA-02, BD-18, BD-19, and DB count verification are complete, the safer positioning is:

> Verified source-first Bulgarian property search: one buyer workspace for comparing listings, source provenance, map context, and operator-reviewed data quality.

HYPOTHESIS: This positioning is credible earlier than complete-market coverage because it turns current quality gates into a trust advantage rather than a hidden weakness.

GAP: Final public copy must be reviewed against accepted-only exports and live frontend surfaces.

## Source Priority Recommendations

1. Stabilize Action1 trust base before source expansion.
   - FACT: 26,231 rows are pending/missing QA and DB-backed counts are blocked.
   - Planner implication: keep `DA-02`, `BD-18`, `BD-19`, `S1-23`, and `DBG-16` ahead of public coverage claims.

2. Treat `imot_bg`, `property_bg`, `suprimmo`, `luximmo`, and repaired `address_bg` as the first market-browse base.
   - FACT: These sources provide the largest usable file-backed corpus today.
   - Planner implication: use them for accepted-only internal demos after importer and dashboard semantics are verified.

3. Make `Homes.bg`, `alo.bg`, `Bazar.bg`, and OLX API the next weekly market gap review group.
   - FACT: Website inventory artifacts show large source-side totals or lower bounds with weak landed coverage.
   - Planner implication: do not start Action2/live widening until Action1 QA gate allows it; prepare count-method and route-mapping tasks now.

4. Keep STR and official/register intelligence separate from canonical listings.
   - FACT: Airbnb/Booking/Vrbo are partner/vendor-only, AirDNA/Airbtics are licensed-data sources, and KAIS/Property Register are consent/manual official routes.
   - Planner implication: S&M should prepare vendor/official data contracts; UX should expose STR/verification as future overlays, not current listing inventory.

5. Delay 95% coverage language.
   - FACT: Current accepted import candidates are 1,612 and accepted-only DB counts are unavailable.
   - UX implication: buyer-facing UI should use evidence labels and source provenance, not market-completeness claims.

## Strategic Tasks For Next Weekly Market Review

### Planner

1. Convert this report into a source-priority decision after `DA-02` and `BD-19` produce accepted-only dashboard/read-model counts.
2. Define a weekly source scorecard with these columns: registry legal mode, access mode, source family, website-total basis, landed rows, accepted rows, grouped rows, LOST rows, media completeness, description coverage, city/district coverage, price-status coverage, and product role.
3. Require any public market claim to cite accepted-only DB-backed counts or explicitly label itself as a source-side estimate.

### Data Analyst

1. Add accepted-only city/district/property-type/intent/price-status rollups to DA-02 or the next market export.
2. Separate source-side inventory totals from landed corpus coverage and accepted canonical candidates.
3. Add price visibility fields: price present, price_status, price_per_sqm availability, on-request/undefined count, and low-price warning count.

### Scraper 1

1. Repair Action1 source issues that block market interpretation: Address.bg location/media, BulgarianProperties gallery/area, Homes.bg route/API expansion, imot.bg area/mojibake/category precision, LUXIMMO/SUPRIMMO development classification, property.bg thin descriptions.
2. Prepare but do not execute Action2 market-gap routes for Homes/alo/Bazar/OLX until operator and QA gates allow it.

### UX/UI Designer

1. Design buyer-facing language around verified source provenance, accepted-only records, limited media, approximate location, and price-on-request states.
2. Do not present grouped/development publications as normal property cards; reserve them for future project/new-build surfaces.
3. Avoid complete-market, 95% coverage, or city-level trend labels until DB-backed accepted counts exist.

### S&M / Market Extensions

1. Keep STR vendors, official registers, and social/messenger leads as overlays or review queues, not default inventory.
2. Track required contracts/API/manual-consent gates for AirDNA, Airbtics, OLX API, KAIS, Property Register, Telegram API, WhatsApp/Viber opt-in routes.

## Next Review Inputs Needed

FACT: The next weekly market review needs DA-02 dashboard metric contract output, BD-18 import proof, BD-19 read-model counts, S1-23 source repair status, and UX-16/UX-18 label decisions.

INTERPRETATION: Without these, market intelligence remains a prioritization tool, not a publishable market analytics product.

GAP: External rival movement and live market pricing changes require explicit authorization to browse or use licensed data.
