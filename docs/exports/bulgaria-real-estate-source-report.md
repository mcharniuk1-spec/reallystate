# Bulgaria Real Estate Source Links And Debug Report

Generated: 2026-04-08T14:33:00.858630+00:00

## Executive Summary

The repository now has a source/link inventory for 44 Bulgarian real estate, short-term-rental, official-register, analytics, and social/messaging sources. The inventory is stored in `data/source_registry.json` and exported to `docs/exports/bulgaria-real-estate-source-links.xlsx`.

The platform should continue with a source-first implementation sequence: registry and legal gates, PostgreSQL/PostGIS persistence, fixture-backed tier-1 connectors, dedupe and geospatial matching, then map/listing/chat UI and reverse publishing.

## Deliverables

- `docs/exports/bulgaria-real-estate-source-links.xlsx`: workbook with source links, summary, and debug priorities.
- `docs/exports/bulgaria-real-estate-source-links.csv`: CSV copy of the main source/link table.
- `docs/exports/bulgaria-real-estate-source-report.md`: this structured report.
- `docs/exports/bulgaria-real-estate-source-report.docx`: Word-compatible report generated without external dependencies.

## Source Coverage Logic

Tier 1 is for the first ingestion wave: OLX via official API where possible, then crawl-friendly or high-value Bulgarian portals and agencies. Tier 2 is targeted expansion after parser gates. Tier 3 is partner/vendor/official-service first: Airbnb, Booking.com, Vrbo, AirDNA, Airbtics, official registers, cadastre, and auctions. Tier 4 is lead intelligence only: Telegram and public social overlays where appropriate, and consent-only Viber/WhatsApp/private-channel flows.

## Source Link Table

| Source | Tier | Family | Primary URL | Related URLs | Owner Group | Access Mode | Legal Mode | Risk Mode | Freshness | Publish Capable | Listing Types | Best Extraction Method | MVP Phase | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Address.bg | 1 | agency | https://address.bg/ |  | Realto Group | html | public_crawl_with_review | medium | hourly | yes | sale, long_term_rent, land, new_build | crawl listings with ref-id normalization | source_first_ingestion | Core agency network with strong local branches. |
| alo.bg | 1 | classifieds | https://www.alo.bg/ |  | ALO.BG | html | public_crawl_with_review | medium | ten_minutes | yes | sale, long_term_rent, short_term_rent, land, new_build | scoped HTML crawl with category filtering | source_first_ingestion | Strong coastal inventory, especially land and new-build. |
| BulgarianProperties | 1 | agency | https://www.bulgarianproperties.bg/ | https://www.bulgarianproperties.com/ | Bulgarian Properties | html | public_crawl_with_review | medium | hourly | yes | sale, long_term_rent, land, new_build | conservative crawl using stable reference IDs | source_first_ingestion | Important for new-build and foreign buyer inventory. |
| Homes.bg | 1 | portal | https://www.homes.bg/ |  | Jobs.bg | html | public_crawl_with_review | medium | ten_minutes | yes | sale, long_term_rent, land | server-rendered HTML crawl | source_first_ingestion | Crawl-friendly and broad national coverage. |
| imot.bg | 1 | portal | https://www.imot.bg/ |  | Rezon Media | html | public_crawl_with_review | medium | ten_minutes | yes | sale, long_term_rent, land, new_build | respectful crawl or partnership feed | source_first_ingestion | High-volume benchmark supply source. |
| imoti.net | 1 | portal | https://www.imoti.net/ |  | Investor Media Group | headless | legal_review_required | high | hourly | yes | sale, long_term_rent, land, new_build | partnership first, headless as fallback | source_first_ingestion | 403 and anti-bot patterns raise risk. |
| LUXIMMO | 1 | agency | https://www.luximmo.bg/ |  | Stoyanov Enterprises | html | public_crawl_with_review | medium | hourly | yes | sale, long_term_rent, land, new_build | careful crawl using stable luxury listing reference IDs | source_first_ingestion | Luxury coastal segment. |
| OLX.bg | 1 | classifieds | https://www.olx.bg/ | https://developer.olx.bg/ | Naspers Classifieds Bulgaria / OLX | official_api | official_api_allowed | low | ten_minutes | yes | sale, long_term_rent, land, new_build | official developer API first | source_first_ingestion | Primary API-first classifieds source. |
| property.bg | 1 | portal | https://www.property.bg/ |  | SUPRIMMO group | html | public_crawl_with_review | medium | hourly | yes | sale, long_term_rent, land, new_build | targeted listing-page crawl | source_first_ingestion | Cross-check source for foreign-buyer inventory. |
| SUPRIMMO | 1 | agency | https://www.suprimmo.bg/ |  | Stoyanov Enterprises | html | public_crawl_with_review | medium | hourly | yes | sale, long_term_rent, land, new_build | crawl listings and unify group reference IDs | source_first_ingestion | High-value coastal and resort inventory. |
| ApartmentsBulgaria.com | 2 | ota | https://www.apartmentsbulgaria.bg/ |  | Property Management BG | headless | public_crawl_with_review | medium | daily | yes | short_term_rent | direct booking integration or careful crawl | source_expansion_after_tier1 | Managed resort inventory. |
| Bazar.bg | 2 | classifieds | https://bazar.bg/ |  | Rezon Media | html | public_crawl_with_review | medium | hourly | yes | sale, long_term_rent, land | limited HTML crawl | source_expansion_after_tier1 | Secondary but useful classifieds source. |
| Domaza | 2 | portal | https://www.domaza.bg/ |  | Domaza | html | public_crawl_with_review | medium | hourly | yes | sale, long_term_rent, short_term_rent, land, new_build | crawl with language canonicalization | source_expansion_after_tier1 | Needs cross-language dedupe. |
| Holding Group Real Estate | 2 | agency | https://holdinggroup.bg/ |  | Holding Group | html | public_crawl_with_review | medium | hourly | yes | sale, long_term_rent, land, new_build | crawl direct site plus dedupe against portal syndication | source_expansion_after_tier1 | Strong Varna-side project inventory. |
| Home2U | 2 | agency | https://home2u.bg/ |  | Home2U | html | public_crawl_with_review | medium | hourly | yes | sale, long_term_rent, land, new_build | templated HTML parser | source_expansion_after_tier1 | Important for Varna and project inventory. |
| Imoteka.bg | 2 | agency | https://imoteka.bg/ |  | Realto Group | headless | legal_review_required | high | daily | yes | sale, long_term_rent, land, new_build | partnership/licensed feed preferred; headless only after legal clearance | source_expansion_after_tier1 | JS-heavy source with higher content-use risk. |
| Imoti.info | 2 | classifieds | https://imoti.info/ |  | Bulinfo OOD | partner_feed | licensing_required | high | daily | yes | sale, long_term_rent, land, new_build | licensing or partnership first; fixture-only parser research until approved | source_expansion_after_tier1 | Terms indicate commercial data use requires authorization/payment. |
| Indomio.bg | 2 | portal | https://www.indomio.bg/ |  | Spitogatos Network | headless | public_crawl_with_review | medium | daily | yes | sale, long_term_rent, land | hybrid HTML/headless crawler | source_expansion_after_tier1 | Secondary index for coastal supply. |
| Lions Group | 2 | agency | https://lionsgroup.bg/ |  | Lions Group | html | public_crawl_with_review | medium | daily | yes | sale, long_term_rent, land, new_build | server-rendered listing crawl | source_expansion_after_tier1 | Useful Varna-side agency inventory. |
| Pochivka.bg | 2 | ota | https://pochivka.bg/ |  | Pochivka BG | html | public_crawl_with_review | medium | daily | yes | short_term_rent | partnership or limited travel-catalog crawl | source_expansion_after_tier1 | Hospitality intelligence more than core sale inventory. |
| realestates.bg | 2 | classifieds | https://en.realestates.bg/ |  | ALO.BG network | html | public_crawl_with_review | medium | daily | yes | sale, long_term_rent, land | scope-limited HTML crawl and dedupe against alo.bg | source_expansion_after_tier1 | Foreign-facing Alo network layer. |
| Realistimo | 2 | portal | https://realistimo.com/ |  | Realistimo | headless | public_crawl_with_review | medium | hourly | yes | sale, long_term_rent, land, new_build | HTML crawl with map-filter fallback | source_expansion_after_tier1 | Map-driven browsing suggests structured geo data. |
| Rentica.bg | 2 | agency | https://rentica.bg/ |  | Rentica | html | public_crawl_with_review | medium | hourly | yes | long_term_rent | rent-only HTML parser | source_expansion_after_tier1 | Varna rental specialist. |
| Svobodni-kvartiri.com | 2 | portal | https://svobodni-kvartiri.com/ |  | Svobodni kvartiri | html | public_crawl_with_review | medium | hourly | yes | long_term_rent, short_term_rent | deep pagination crawl by city scope | source_expansion_after_tier1 | Useful for worker and student rentals. |
| Unique Estates | 2 | agency | https://ues.bg/ |  | Realto Group | html | public_crawl_with_review | medium | daily | yes | sale, long_term_rent, new_build | luxury listing crawler | source_expansion_after_tier1 | Luxury sea-segment pages. |
| Vila.bg | 2 | ota | https://vila.bg/ |  | Vila Tours | html | public_crawl_with_review | medium | daily | yes | short_term_rent | partnership or limited catalog crawl | source_expansion_after_tier1 | Villa and guest-house coverage. |
| Yavlena | 2 | agency | https://www.yavlena.com/ |  | Yavlena | html | public_crawl_with_review | medium | hourly | yes | sale, long_term_rent | incremental crawl with ID-based URLs | source_expansion_after_tier1 | Established agency with branch-driven supply. |
| Airbnb | 3 | ota | https://www.airbnb.com/ |  | Airbnb, Inc. | partner_feed | official_partner_or_vendor_only | prohibited_without_contract | vendor_sync | yes | short_term_rent | official authorized partner integration only | reverse_publishing_and_str_intelligence | Do not rely on scraping as a core acquisition path. |
| Airbtics | 3 | analytics_vendor | https://airbtics.com/ |  | Airbtics | licensed_data | official_partner_or_vendor_only | low | vendor_sync | no | short_term_rent_metrics | REST API or licensed export | enrichment_and_verification | Use for coastal STR benchmarks. |
| AirDNA | 3 | analytics_vendor | https://www.airdna.co/ |  | AirDNA | licensed_data | official_partner_or_vendor_only | low | vendor_sync | no | short_term_rent_metrics | licensed export or enterprise contract | enrichment_and_verification | Use for STR enrichment, not primary listings. |
| BCPEA property auctions | 3 | official_register | https://sales.bcpea.org/properties |  | Chamber of Private Bailiffs | html | public_crawl_with_review | medium | daily | no | auction_sale | HTML crawl plus OCR when notices are scanned | enrichment_and_verification | Useful opportunistic inventory source. |
| Booking.com | 3 | ota | https://www.booking.com/ |  | Booking Holdings | partner_feed | official_partner_or_vendor_only | prohibited_without_contract | vendor_sync | yes | short_term_rent | connectivity/content partner APIs only | reverse_publishing_and_str_intelligence | Certification-first publishing route. |
| Flat Manager | 3 | ota | https://flatmanager.bg/ | https://reserve.flatmanager.bg/ | Flat Manager / Renters.pl | partner_feed | official_partner_or_vendor_only | medium | vendor_sync | yes | short_term_rent, property_management | partnership or direct booking integration only | reverse_publishing_and_str_intelligence | Managed STR/direct-booking inventory and potential distribution partner. |
| KAIS Cadastre | 3 | official_register | https://kais.cadastre.bg/bg/Map |  | Agency for Geodesy, Cartography and Cadastre | manual_consent_only | consent_or_manual_only | high | consent_driven | no | building_geometry, parcel_validation | official services and permitted exports | enrichment_and_verification | Geospatial backbone for building matching. |
| Menada Bulgaria | 3 | ota | https://menadabulgaria.com/ |  | Menada Bulgaria | partner_feed | official_partner_or_vendor_only | medium | vendor_sync | yes | short_term_rent, property_management | partnership/direct booking integration | reverse_publishing_and_str_intelligence | Black Sea property management and STR inventory. |
| Property Register | 3 | official_register | https://portal.registryagency.bg/en/home-pr |  | Registry Agency | manual_consent_only | consent_or_manual_only | high | consent_driven | no | ownership_verification | official e-service queries only | enrichment_and_verification | Verification layer, not acquisition feed. |
| Vrbo | 3 | ota | https://www.vrbo.com/ |  | Expedia Group | partner_feed | official_partner_or_vendor_only | high | vendor_sync | yes | short_term_rent | partnership or licensed feed | reverse_publishing_and_str_intelligence | Not a crawl-first source. |
| Facebook public groups/pages | 4 | social_public_channel | https://www.facebook.com/groups/438018083766467/ |  | Meta | manual_consent_only | consent_or_manual_only | high | daily | no | leads, long_term_rent | manual monitoring or explicit partnerships | lead_intelligence_overlay | Do not rely on unstable login-restricted scraping. |
| Instagram public profiles | 4 | social_public_channel | https://www.instagram.com/bulgarianproperties.bg/ | https://www.instagram.com/bulgarianpropertiesagency/<br>https://www.instagram.com/suprimmo.bg/<br>https://www.instagram.com/suprimmo.varna/<br>https://www.instagram.com/suprimmo.burgas/<br>https://www.instagram.com/luximmo.bg/<br>https://www.instagram.com/luximmo.burgas/<br>https://www.instagram.com/rentica.bg/ | Meta | manual_consent_only | consent_or_manual_only | high | daily | no | leads, branding | authorized business integrations or manual review | lead_intelligence_overlay | Treat as agency-branding and lead overlay. |
| Telegram public channels | 4 | social_public_channel | https://t.me/rentvarna | https://t.me/varnarents<br>https://t.me/real_estate_bg<br>https://t.me/ads_in_bulgaria<br>https://t.me/bgvarna_en<br>https://t.me/kvartirivarna | Telegram | official_api | official_api_allowed | medium | hourly | no | leads, sale, long_term_rent | public API/client ingestion with NLP extraction | lead_intelligence_overlay | Lead-intelligence overlay only. |
| Threads public profiles | 4 | social_public_channel |  |  | Meta | manual_consent_only | consent_or_manual_only | high | daily | no | leads, branding, links | experimental public-profile monitoring only after access review | lead_intelligence_overlay | Deferred overlay until official/public read coverage is confirmed. |
| Viber opt-in communities | 4 | private_messenger | https://invite.viber.com/?g2=AQA%2BxCYrr7Jy1VEh6Ic98YLAlDXOmJicE8MDwi%2F0NU%2FsFss%2FWRC%2B0lL9ufcuh96f | https://invite.viber.com/?g2=AQAskgj%2FMFVozlMMEjg%2BuNw%2FEqgzSfOC5b8ZiLELo85k4haoyw9L%2B8j8wGKeBc0t<br>https://invite.viber.com/?g2=AQBsW%2FKtZgB8VFEa8o8E52s45eL4D9wCwntSBjZysufmDhq3fLznCnlBiYx6vHYN&lang=en<br>https://invite.viber.com/?g2=AQBqiGrgkj4dFFS6JHR01wsv8ntsQAaiglrdOkkM4MlwzwqoJZ%2FQ49cp0nvXLpUr&lang=bg | Rakuten Viber | manual_consent_only | consent_or_manual_only | high | consent_driven | no | leads, sale, long_term_rent | opt-in community ingestion only | lead_intelligence_overlay | Privacy-restricted and unstructured. |
| WhatsApp opt-in groups | 4 | private_messenger | https://chat.whatsapp.com/HB3Kt48meI08eIaYSuJ1Go?mode=gi_t |  | Meta | manual_consent_only | official_partner_or_vendor_only | prohibited_without_contract | consent_driven | no | leads, sale, long_term_rent | explicit opt-in via WhatsApp Business only | lead_intelligence_overlay | Useful for owned-business communication, not broad scraping. |
| X public search/accounts | 4 | social_public_channel | https://x.com/super_imoti |  | X | official_api | official_api_allowed | low | daily | no | news, links, leads | API or public-profile monitoring | lead_intelligence_overlay | Useful mostly for market chatter and backlinks. |

## Debugging And Inefficiency Audit

| Area | Inefficiency / Gap | Why It Matters | Recommended Fix | Skill / Owner | Priority |
| --- | --- | --- | --- | --- | --- |
| Development environment | Local Python is 3.9.6 while the target stack says Python 3.12+. | New language/library choices may fail locally or in Cursor agents. | Create a pinned Python 3.12 toolchain through pyenv, uv, or Docker before backend expansion. | postgres-postgis-schema / qa-review-release | High |
| Document exports | pandoc, Mermaid CLI, LibreOffice, python-docx, reportlab, openpyxl, pandas, and xlsxwriter are not installed. | DOCX/PDF/XLSX workflows become less visual and harder to validate. | Install export tooling or keep using the standard-library generator until the docs-export phase. | docs-export | Medium |
| Persistence | The SQL file is a blueprint, not an Alembic migration set. | Agents cannot safely evolve schema without migration history. | Implement Alembic migrations and repository tests before live connectors. | postgres-postgis-schema | High |
| Crawler runtime | There are no real Temporal workers, queues, rate-limit state, or crawl cursors yet. | Source freshness and retries cannot be trusted in production. | Implement SourceDiscoveryWorkflow, ListingDetailWorkflow, and durable crawl jobs. | workflow-runtime | High |
| Connectors | No tier-1 source connector has offline fixtures or production parser coverage. | The source matrix is useful, but ingestion is not market-complete yet. | Start with Homes.bg fixture parser, then OLX API/alo.bg/imot.bg in gated slices. | scraper-connector-builder / parser-fixture-qa | High |
| Object storage | raw_capture still includes body text for compatibility, despite the desired S3/MinIO raw store. | Large captures and screenshots will bloat PostgreSQL. | Make body optional or retention-limited when object storage is implemented. | postgres-postgis-schema | Medium |
| Frontend | There is no Next.js web app yet. | The product MVP pages are still only planned. | Build /listings, /properties/[id], /map, /chat, /settings, and /admin after APIs exist. | frontend-pages | High |
| Compliance | Source legal modes are in the registry, but not yet enforced by runtime middleware. | A future connector could accidentally bypass source policy. | Add a compliance gate before fetch, parse, publish, and channel onboarding. | publishing-compliance / real-estate-source-registry | High |
| MCP automation | .cursor/mcp.json uses npx commands that need network and local Node availability. | Cursor agents may fail if offline or if Node tooling is unavailable. | Document prerequisites and allow agents to continue without MCP when unavailable. | qa-review-release | Medium |

## Recommended Next Execution Order

1. Install or containerize Python 3.12+, PostgreSQL/PostGIS, Redis, MinIO, and Temporal.
2. Convert `sql/schema.sql` into Alembic migrations and repository tests.
3. Implement compliance gates for `legal_mode`, `access_mode`, and `risk_mode` before fetch/publish operations.
4. Build the first fixture-backed connector for `Homes.bg`.
5. Add OLX API integration only when credentials are configured; otherwise keep fixture-only parser work.
6. Implement media object-storage adapters before downloading real photo binaries at scale.
7. Build dedupe, geocoding, and building match review queues before public UI work.
8. Build `/listings` and `/properties/[id]` after search APIs exist, then `/map`, `/chat`, `/settings`, and `/admin`.
9. Keep Airbnb/Booking/Vrbo publishing on official partner/vendor paths only.

## Notes

The `.xlsx` and `.docx` were generated using standard-library Office Open XML packaging because spreadsheet/document libraries are not installed locally. Install `openpyxl`, `python-docx`, `pandoc`, Mermaid CLI, and LibreOffice for richer visual review in the docs-export phase.
