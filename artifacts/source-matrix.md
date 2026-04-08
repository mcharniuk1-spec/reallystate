# Source Parser Matrix

| Source | Tier | Family | Primary URL | Access | Legal Mode | MVP Phase | Freshness | Publish Capable | Best Method |
|---|---:|---|---|---|---|---|---|---|---|
| Address.bg | 1 | agency | https://address.bg/ | html | public_crawl_with_review | source_first_ingestion | hourly | yes | crawl listings with ref-id normalization |
| alo.bg | 1 | classifieds | https://www.alo.bg/ | html | public_crawl_with_review | source_first_ingestion | ten_minutes | yes | scoped HTML crawl with category filtering |
| BulgarianProperties | 1 | agency | https://www.bulgarianproperties.bg/ | html | public_crawl_with_review | source_first_ingestion | hourly | yes | conservative crawl using stable reference IDs |
| Homes.bg | 1 | portal | https://www.homes.bg/ | html | public_crawl_with_review | source_first_ingestion | ten_minutes | yes | server-rendered HTML crawl |
| imot.bg | 1 | portal | https://www.imot.bg/ | html | public_crawl_with_review | source_first_ingestion | ten_minutes | yes | respectful crawl or partnership feed |
| imoti.net | 1 | portal | https://www.imoti.net/ | headless | legal_review_required | source_first_ingestion | hourly | yes | partnership first, headless as fallback |
| LUXIMMO | 1 | agency | https://www.luximmo.bg/ | html | public_crawl_with_review | source_first_ingestion | hourly | yes | careful crawl using stable luxury listing reference IDs |
| OLX.bg | 1 | classifieds | https://www.olx.bg/ | official_api | official_api_allowed | source_first_ingestion | ten_minutes | yes | official developer API first |
| property.bg | 1 | portal | https://www.property.bg/ | html | public_crawl_with_review | source_first_ingestion | hourly | yes | targeted listing-page crawl |
| SUPRIMMO | 1 | agency | https://www.suprimmo.bg/ | html | public_crawl_with_review | source_first_ingestion | hourly | yes | crawl listings and unify group reference IDs |
| ApartmentsBulgaria.com | 2 | ota | https://www.apartmentsbulgaria.bg/ | headless | public_crawl_with_review | source_expansion_after_tier1 | daily | yes | direct booking integration or careful crawl |
| Bazar.bg | 2 | classifieds | https://bazar.bg/ | html | public_crawl_with_review | source_expansion_after_tier1 | hourly | yes | limited HTML crawl |
| Domaza | 2 | portal | https://www.domaza.bg/ | html | public_crawl_with_review | source_expansion_after_tier1 | hourly | yes | crawl with language canonicalization |
| Holding Group Real Estate | 2 | agency | https://holdinggroup.bg/ | html | public_crawl_with_review | source_expansion_after_tier1 | hourly | yes | crawl direct site plus dedupe against portal syndication |
| Home2U | 2 | agency | https://home2u.bg/ | html | public_crawl_with_review | source_expansion_after_tier1 | hourly | yes | templated HTML parser |
| Imoteka.bg | 2 | agency | https://imoteka.bg/ | headless | legal_review_required | source_expansion_after_tier1 | daily | yes | partnership/licensed feed preferred; headless only after legal clearance |
| Imoti.info | 2 | classifieds | https://imoti.info/ | partner_feed | licensing_required | source_expansion_after_tier1 | daily | yes | licensing or partnership first; fixture-only parser research until approved |
| Indomio.bg | 2 | portal | https://www.indomio.bg/ | headless | public_crawl_with_review | source_expansion_after_tier1 | daily | yes | hybrid HTML/headless crawler |
| Lions Group | 2 | agency | https://lionsgroup.bg/ | html | public_crawl_with_review | source_expansion_after_tier1 | daily | yes | server-rendered listing crawl |
| Pochivka.bg | 2 | ota | https://pochivka.bg/ | html | public_crawl_with_review | source_expansion_after_tier1 | daily | yes | partnership or limited travel-catalog crawl |
| realestates.bg | 2 | classifieds | https://en.realestates.bg/ | html | public_crawl_with_review | source_expansion_after_tier1 | daily | yes | scope-limited HTML crawl and dedupe against alo.bg |
| Realistimo | 2 | portal | https://realistimo.com/ | headless | public_crawl_with_review | source_expansion_after_tier1 | hourly | yes | HTML crawl with map-filter fallback |
| Rentica.bg | 2 | agency | https://rentica.bg/ | html | public_crawl_with_review | source_expansion_after_tier1 | hourly | yes | rent-only HTML parser |
| Svobodni-kvartiri.com | 2 | portal | https://svobodni-kvartiri.com/ | html | public_crawl_with_review | source_expansion_after_tier1 | hourly | yes | deep pagination crawl by city scope |
| Unique Estates | 2 | agency | https://ues.bg/ | html | public_crawl_with_review | source_expansion_after_tier1 | daily | yes | luxury listing crawler |
| Vila.bg | 2 | ota | https://vila.bg/ | html | public_crawl_with_review | source_expansion_after_tier1 | daily | yes | partnership or limited catalog crawl |
| Yavlena | 2 | agency | https://www.yavlena.com/ | html | public_crawl_with_review | source_expansion_after_tier1 | hourly | yes | incremental crawl with ID-based URLs |
| Airbnb | 3 | ota | https://www.airbnb.com/ | partner_feed | official_partner_or_vendor_only | reverse_publishing_and_str_intelligence | vendor_sync | yes | official authorized partner integration only |
| Airbtics | 3 | analytics_vendor | https://airbtics.com/ | licensed_data | official_partner_or_vendor_only | enrichment_and_verification | vendor_sync | no | REST API or licensed export |
| AirDNA | 3 | analytics_vendor | https://www.airdna.co/ | licensed_data | official_partner_or_vendor_only | enrichment_and_verification | vendor_sync | no | licensed export or enterprise contract |
| BCPEA property auctions | 3 | official_register | https://sales.bcpea.org/properties | html | public_crawl_with_review | enrichment_and_verification | daily | no | HTML crawl plus OCR when notices are scanned |
| Booking.com | 3 | ota | https://www.booking.com/ | partner_feed | official_partner_or_vendor_only | reverse_publishing_and_str_intelligence | vendor_sync | yes | connectivity/content partner APIs only |
| Flat Manager | 3 | ota | https://flatmanager.bg/ | partner_feed | official_partner_or_vendor_only | reverse_publishing_and_str_intelligence | vendor_sync | yes | partnership or direct booking integration only |
| KAIS Cadastre | 3 | official_register | https://kais.cadastre.bg/bg/Map | manual_consent_only | consent_or_manual_only | enrichment_and_verification | consent_driven | no | official services and permitted exports |
| Menada Bulgaria | 3 | ota | https://menadabulgaria.com/ | partner_feed | official_partner_or_vendor_only | reverse_publishing_and_str_intelligence | vendor_sync | yes | partnership/direct booking integration |
| Property Register | 3 | official_register | https://portal.registryagency.bg/en/home-pr | manual_consent_only | consent_or_manual_only | enrichment_and_verification | consent_driven | no | official e-service queries only |
| Vrbo | 3 | ota | https://www.vrbo.com/ | partner_feed | official_partner_or_vendor_only | reverse_publishing_and_str_intelligence | vendor_sync | yes | partnership or licensed feed |
| Facebook public groups/pages | 4 | social_public_channel | https://www.facebook.com/groups/438018083766467/ | manual_consent_only | consent_or_manual_only | lead_intelligence_overlay | daily | no | manual monitoring or explicit partnerships |
| Instagram public profiles | 4 | social_public_channel | https://www.instagram.com/bulgarianproperties.bg/ | manual_consent_only | consent_or_manual_only | lead_intelligence_overlay | daily | no | authorized business integrations or manual review |
| Telegram public channels | 4 | social_public_channel | https://t.me/rentvarna | official_api | official_api_allowed | lead_intelligence_overlay | hourly | no | public API/client ingestion with NLP extraction |
| Threads public profiles | 4 | social_public_channel |  | manual_consent_only | consent_or_manual_only | lead_intelligence_overlay | daily | no | experimental public-profile monitoring only after access review |
| Viber opt-in communities | 4 | private_messenger | https://invite.viber.com/?g2=AQA%2BxCYrr7Jy1VEh6Ic98YLAlDXOmJicE8MDwi%2F0NU%2FsFss%2FWRC%2B0lL9ufcuh96f | manual_consent_only | consent_or_manual_only | lead_intelligence_overlay | consent_driven | no | opt-in community ingestion only |
| WhatsApp opt-in groups | 4 | private_messenger | https://chat.whatsapp.com/HB3Kt48meI08eIaYSuJ1Go?mode=gi_t | manual_consent_only | official_partner_or_vendor_only | lead_intelligence_overlay | consent_driven | no | explicit opt-in via WhatsApp Business only |
| X public search/accounts | 4 | social_public_channel | https://x.com/super_imoti | official_api | official_api_allowed | lead_intelligence_overlay | daily | no | API or public-profile monitoring |
