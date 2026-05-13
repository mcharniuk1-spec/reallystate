# Tier 1-2 Pattern Status

Generated: 2026-05-13 13:46 UTC

Media storage mode: image binaries are stored as local files under `data/media/<reference_id>/...`; remote `image_urls` remain only as source traceability, while listing JSON artifacts now also store `local_image_files` and `local_image_storage_keys`.

This report separates four questions for each source:
- Can we count the live active site inventory?
- Can we count posted-within-2-months inventory?
- Can we split Varna city vs Varna region at website level?
- Do we have a saved code pattern that lands one full product item with full gallery evidence and local image files?

Strict patterned sources: Address.bg, alo.bg, BulgarianProperties, Homes.bg, imot.bg, LUXIMMO, OLX.bg, property.bg, SUPRIMMO, Bazar.bg, Domaza, Home2U, Yavlena

## Address.bg (Tier 1)

- Pattern status: `Patterned`
- Pattern issue: Code pattern exists and the best saved sample proves full local image-file capture plus core and structured detail-page fields.
- Count status: `recounted_live`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 18701 (exact)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: crawl listings with ref-id normalization
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Source listing root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/address_bg/listings
- Source raw root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/address_bg/raw
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/address_bg/listings/Address.bg_65ec51a198da.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/address_bg/raw/Address.bg_65ec51a198da.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/Address.bg_65ec51a198da
- Sample listing URL: https://address.bg/zavoy-kashta-vila-offer664502
- Sample title: Къща/Вила в Завой - код на имота: 664502
- Sample gallery: 63/63 saved locally (100.0%)
- Local image files saved: 63
- Local image file preview: data/media/Address.bg_65ec51a198da/0000_a54347b5.jpg, data/media/Address.bg_65ec51a198da/0001_456115c0.jpg, data/media/Address.bg_65ec51a198da/0002_2b7c40e8.jpg, data/media/Address.bg_65ec51a198da/0003_20a96c53.jpg, data/media/Address.bg_65ec51a198da/0004_d1da2846.jpg
- Sample completeness: description=True, price=True, area=True, rooms=False, floor=False, phones=True, city=True, address=True
- Source description status: captured
- Structured fields count: 2
- Source attributes count: 1

## alo.bg (Tier 1)

- Pattern status: `Patterned`
- Pattern issue: Code pattern exists and the best saved sample proves full local image-file capture plus core and structured detail-page fields.
- Count status: `recounted_live`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 75961 (lower_bound)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: Varna-filtered category pages + `alo.bg` detail parser for params table, meta/body description, local gallery images, and source attributes.
- Code paths: scripts/live_scraper.py::generic, scripts/live_scraper.py::_parse_alo_bg
- DB status: `without_database_target`
- Source listing root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/alo_bg/listings
- Source raw root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/alo_bg/raw
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/alo_bg/listings/alo.bg_11012820.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/alo_bg/raw/alo.bg_11012820.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/alo.bg_11012820
- Sample listing URL: https://www.alo.bg/dvustaen-s-akt-16-v-kompleks-s-basein-parkomyasto-kv-galata-gr-varna-11012820
- Sample title: Двустаен с АКТ 16 в комплекс с басейн, паркомясто, кв. Галата, гр. Варна Двустаен апартаме..
- Sample gallery: 10/10 saved locally (100.0%)
- Local image files saved: 10
- Local image file preview: data/media/alo.bg_11012820/0000_99033d89.jpg, data/media/alo.bg_11012820/0001_6a58d132.jpg, data/media/alo.bg_11012820/0002_8e2e1ac2.jpg, data/media/alo.bg_11012820/0003_fbdaa1c6.jpg, data/media/alo.bg_11012820/0004_bed78a0a.jpg
- Sample completeness: description=True, price=True, area=True, rooms=True, floor=True, phones=True, city=True, address=True
- Source description status: captured
- Structured fields count: 4
- Source attributes count: 13

## BulgarianProperties (Tier 1)

- Pattern status: `Patterned`
- Pattern issue: Code pattern exists and the best saved sample proves full local image-file capture plus core and structured detail-page fields.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 12000 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: conservative crawl using stable reference IDs
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Source listing root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/bulgarianproperties/listings
- Source raw root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/bulgarianproperties/raw
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/bulgarianproperties/listings/BulgarianProperties_756254aa3f13.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/bulgarianproperties/raw/BulgarianProperties_756254aa3f13.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/BulgarianProperties_756254aa3f13
- Sample listing URL: https://www.bulgarianproperties.com/1-bedroom_apartments_in_Bulgaria/AD90088BG_1-bedroom_apartment_for_sale_in_Bansko.html
- Sample title: Renovated one-bedroom apartment in Regnum Bansko Mountain Resort
- Sample gallery: 82/44 saved locally (186.4%)
- Local image files saved: 82
- Local image file preview: data/media/BulgarianProperties_756254aa3f13/0000_1c680d8d.jpg, data/media/BulgarianProperties_756254aa3f13/0000_c91ab2e2.jpg, data/media/BulgarianProperties_756254aa3f13/0001_1c680d8d.jpg, data/media/BulgarianProperties_756254aa3f13/0001_c91ab2e2.jpg, data/media/BulgarianProperties_756254aa3f13/0002_ac54d652.jpg
- Sample completeness: description=True, price=True, area=True, rooms=True, floor=False, phones=True, city=True, address=True
- Source description status: captured
- Structured fields count: 3
- Source attributes count: 4

## Homes.bg (Tier 1)

- Pattern status: `Patterned`
- Pattern issue: Code pattern exists and the best saved sample proves full local image-file capture plus core and structured detail-page fields.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 120000 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: Homes JSON discovery API + detail-page `__PRELOADED_STATE__` extraction with full gallery download.
- Code paths: scripts/live_scraper.py::_scrape_homes_bg, scripts/live_scraper.py::parse_homes_detail
- DB status: `without_database_target`
- Source listing root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/homes_bg/listings
- Source raw root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/homes_bg/raw
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/homes_bg/listings/Homes.bg_1592983.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/homes_bg/raw/Homes.bg_1592983.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/Homes.bg_1592983
- Sample listing URL: https://www.homes.bg/offer/apartament-za-prodazhba/tristaen-93m2-sofiya-zhk.-nadezhda-2/as1592983
- Sample title: Тристаен, 93m² - жк. Надежда 2, София
- Sample gallery: 10/10 saved locally (100.0%)
- Local image files saved: 10
- Local image file preview: data/media/Homes.bg_1592983/0000_009644d4.jpg, data/media/Homes.bg_1592983/0001_1117535e.jpg, data/media/Homes.bg_1592983/0002_a2425ab6.jpg, data/media/Homes.bg_1592983/0003_b749f1d8.jpg, data/media/Homes.bg_1592983/0004_b02f09a7.jpg
- Sample completeness: description=True, price=True, area=True, rooms=True, floor=True, phones=True, city=True, address=True
- Source description status: captured
- Structured fields count: 4
- Source attributes count: 16

## imot.bg (Tier 1)

- Pattern status: `Patterned`
- Pattern issue: Code pattern exists and the best saved sample proves full local image-file capture plus core and structured detail-page fields.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 200000 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: Server-rendered search pagination + filtered `obiava-*` detail URLs + structured detail-page blocks for params, text, phones, and full gallery.
- Code paths: scripts/live_scraper.py::_scrape_imot_bg, scripts/live_scraper.py::parse_imot_detail
- DB status: `without_database_target`
- Source listing root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/imot_bg/listings
- Source raw root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/imot_bg/raw
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/imot_bg/listings/imot.bg_37fae7324a6a.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/imot_bg/raw/imot.bg_37fae7324a6a.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/imot.bg_37fae7324a6a
- Sample listing URL: https://www.imot.bg/obiava-1c176960985075002-prodava-tristaen-apartament-grad-stara-zagora-ayazmoto
- Sample title: Продава 3-СТАЕН град Стара Загора, Аязмото Обява: 1c176960985075002
- Sample gallery: 18/18 saved locally (100.0%)
- Local image files saved: 18
- Local image file preview: data/media/imot.bg_37fae7324a6a/0000_9c354005.jpg, data/media/imot.bg_37fae7324a6a/0001_93d94c15.jpg, data/media/imot.bg_37fae7324a6a/0002_51cc5c47.jpg, data/media/imot.bg_37fae7324a6a/0003_bffa64e3.jpg, data/media/imot.bg_37fae7324a6a/0004_6d540fd9.jpg
- Sample completeness: description=True, price=True, area=True, rooms=True, floor=True, phones=True, city=True, address=True
- Source description status: captured
- Structured fields count: 4
- Source attributes count: 5

## imoti.net (Tier 1)

- Pattern status: `without_authorized_pattern`
- Pattern issue: Source needs legal review before a live pattern can be promoted.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 90000 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: partnership first, headless as fallback
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Sample evidence: none saved yet

## LUXIMMO (Tier 1)

- Pattern status: `Patterned`
- Pattern issue: Code pattern exists and the best saved sample proves full local image-file capture plus core and structured detail-page fields.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 4000 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: careful crawl using stable luxury listing reference IDs
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Source listing root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/luximmo/listings
- Source raw root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/luximmo/raw
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/luximmo/listings/LUXIMMO_fb4b943b5305.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/luximmo/raw/LUXIMMO_fb4b943b5305.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/LUXIMMO_fb4b943b5305
- Sample listing URL: https://www.luximmo.bg/bulgaria/oblast-plovdiv/plovdiv/luksozni-imoti-dvustayni-apartamenti/luksozen-imot-48660-dvustaen-apartament-pod-naem-v-plovdiv.html
- Sample title: Стилен двустаен апартамент в нова модерна сграда в кв. "Христо Смирненски"
- Sample gallery: 62/30 saved locally (206.7%)
- Local image files saved: 62
- Local image file preview: data/media/LUXIMMO_fb4b943b5305/0000_af8da876.jpg, data/media/LUXIMMO_fb4b943b5305/0001_af8da876.jpg, data/media/LUXIMMO_fb4b943b5305/0002_719a8ab2.jpg, data/media/LUXIMMO_fb4b943b5305/0003_ad76ca58.jpg, data/media/LUXIMMO_fb4b943b5305/0004_936d0742.jpg
- Sample completeness: description=True, price=True, area=True, rooms=True, floor=False, phones=True, city=True, address=True
- Source description status: captured
- Structured fields count: 3
- Source attributes count: 4

## OLX.bg (Tier 1)

- Pattern status: `Patterned`
- Pattern issue: Code pattern exists and the best saved sample proves full local image-file capture plus core and structured detail-page fields.
- Count status: `recounted_live`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 1000 (lower_bound)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: official developer API first
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Source listing root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/olx_bg/listings
- Source raw root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/olx_bg/raw
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/olx_bg/listings/OLX.bg_147593402.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/olx_bg/raw/OLX.bg_147593402.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/OLX.bg_147593402
- Sample listing URL: https://www.olx.bg/d/ad/predstavyame-vi-prekrasna-oferta-koyato-nyama-analog-na-pazara-CID368-ID9ZhMK.html?search_reason=search%7Corganic
- Sample title: Представяме Ви прекрасна оферта, която няма АНАЛОГ на пазара!
- Sample gallery: 6/6 saved locally (100.0%)
- Local image files saved: 6
- Local image file preview: data/media/OLX.bg_147593402/0000_81ed1c35.webp, data/media/OLX.bg_147593402/0001_0af518c5.webp, data/media/OLX.bg_147593402/0002_ea675f00.webp, data/media/OLX.bg_147593402/0003_c238bd3a.webp, data/media/OLX.bg_147593402/0004_cfdb72dc.webp
- Sample completeness: description=True, price=True, area=True, rooms=True, floor=False, phones=True, city=True, address=True
- Source description status: captured
- Structured fields count: 3
- Source attributes count: 0

## property.bg (Tier 1)

- Pattern status: `Patterned`
- Pattern issue: Code pattern exists and the best saved sample proves full local image-file capture plus core and structured detail-page fields.
- Count status: `recounted_live`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 4229 (lower_bound)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: targeted listing-page crawl
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Source listing root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/property_bg/listings
- Source raw root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/property_bg/raw
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/property_bg/listings/property.bg_02760f3b26be.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/property_bg/raw/property.bg_02760f3b26be.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/property.bg_02760f3b26be
- Sample listing URL: https://www.property.bg/property-128771-two-bedroom-apartment-in-an-exclusive-holiday-complex-in-bansko/
- Sample title: Two-bedroom apartment in an exclusive holiday complex in Bansko
- Sample gallery: 195/195 saved locally (100.0%)
- Local image files saved: 195
- Local image file preview: data/media/property.bg_02760f3b26be/0000_04949099.jpg, data/media/property.bg_02760f3b26be/0001_0d6a0301.jpg, data/media/property.bg_02760f3b26be/0002_5f66d79b.jpg, data/media/property.bg_02760f3b26be/0003_919f76b6.jpg, data/media/property.bg_02760f3b26be/0004_c1cc6b0c.jpg
- Sample completeness: description=True, price=True, area=True, rooms=True, floor=False, phones=True, city=True, address=True
- Source description status: captured
- Structured fields count: 3
- Source attributes count: 4

## SUPRIMMO (Tier 1)

- Pattern status: `Patterned`
- Pattern issue: Code pattern exists and the best saved sample proves full local image-file capture plus core and structured detail-page fields.
- Count status: `recounted_live`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 4628 (lower_bound)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: crawl listings and unify group reference IDs
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Source listing root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/suprimmo/listings
- Source raw root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/suprimmo/raw
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/suprimmo/listings/SUPRIMMO_LXH-69845.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/suprimmo/raw/SUPRIMMO_LXH-69845.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/SUPRIMMO_LXH-69845
- Sample listing URL: https://www.suprimmo.bg/imot-69845-mnogostaen-apartament-do-klyuch-v-elitna-sgrada-do-cacao-beach/
- Sample title: Многостаен апартамент "до ключ" в елитна сграда до Cacao Beach
- Sample gallery: 211/211 saved locally (100.0%)
- Local image files saved: 211
- Local image file preview: data/media/SUPRIMMO_LXH-69845/0000_07ac6fb1.jpg, data/media/SUPRIMMO_LXH-69845/0001_96ebd1d7.jpg, data/media/SUPRIMMO_LXH-69845/0002_b191c247.jpg, data/media/SUPRIMMO_LXH-69845/0003_7b1c8e64.jpg, data/media/SUPRIMMO_LXH-69845/0004_24053783.jpg
- Sample completeness: description=True, price=True, area=True, rooms=True, floor=False, phones=True, city=True, address=True
- Source description status: captured
- Structured fields count: 3
- Source attributes count: 4

## ApartmentsBulgaria.com (Tier 2)

- Pattern status: `without_sample_product_capture`
- Pattern issue: No saved full product sample exists yet for this source.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 1800 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: direct booking integration or careful crawl
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Sample evidence: none saved yet

## Bazar.bg (Tier 2)

- Pattern status: `Patterned`
- Pattern issue: Code pattern exists and the best saved sample proves full local image-file capture plus core and structured detail-page fields.
- Count status: `recounted_live`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 221272 (exact)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: limited HTML crawl
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Source listing root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/bazar_bg/listings
- Source raw root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/bazar_bg/raw
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/bazar_bg/listings/Bazar.bg_54105310.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/bazar_bg/raw/Bazar.bg_54105310.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/Bazar.bg_54105310
- Sample listing URL: https://bazar.bg/obiava-54105310/dawa-pod-naem-3-staen-gr-sofiia-lagera
- Sample title: Дава под наем 3-СТАЕН, гр. София, Лагера → Обява 54105310
- Sample gallery: 15/15 saved locally (100.0%)
- Local image files saved: 15
- Local image file preview: data/media/Bazar.bg_54105310/0000_fbce90af.jpg, data/media/Bazar.bg_54105310/0001_cce79a98.jpg, data/media/Bazar.bg_54105310/0002_afedac9c.jpg, data/media/Bazar.bg_54105310/0003_2978b0fa.jpg, data/media/Bazar.bg_54105310/0004_84ca4ddb.jpg
- Sample completeness: description=True, price=True, area=True, rooms=True, floor=False, phones=True, city=True, address=True
- Source description status: captured
- Structured fields count: 3
- Source attributes count: 0

## Domaza (Tier 2)

- Pattern status: `Patterned`
- Pattern issue: Code pattern exists and the best saved sample proves full local image-file capture plus core and structured detail-page fields.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 22000 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: Varna sale/rent listing pages + Domaza detail parser for property content, features, rooms/area/price, and full `cdn.domaza.biz` gallery.
- Code paths: scripts/live_scraper.py::generic, scripts/live_scraper.py::_parse_domaza
- DB status: `without_database_target`
- Source listing root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/domaza/listings
- Source raw root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/domaza/raw
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/domaza/listings/Domaza_8636166.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/domaza/raw/Domaza_8636166.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/Domaza_8636166
- Sample listing URL: https://www.domaza.bg/%D0%B0%D0%BF%D0%B0%D1%80%D1%82%D0%B0%D0%BC%D0%B5%D0%BD%D1%82_%D0%B7%D0%BA_%D1%82%D1%80%D0%B0%D0%BA%D0%B8%D1%8F_%D0%B3%D1%80_%D0%B2%D0%B0%D1%80%D0%BD%D0%B0_%D0%B2%D0%B0%D1%80%D0%BD%D0%B0_%D0%B1%D1%8A%D0%BB%D0%B3%D0%B0%D1%80%D0%B8%D1%8F-16-8636166-p/
- Sample title: Апартамент, ЗК Тракия, гр. Варна, Варна, България
- Sample gallery: 32/32 saved locally (100.0%)
- Local image files saved: 32
- Local image file preview: data/media/Domaza_8636166/0000_d8e37377.jpg, data/media/Domaza_8636166/0001_f90c0788.jpg, data/media/Domaza_8636166/0002_3f02112a.jpg, data/media/Domaza_8636166/0003_d52ad108.jpg, data/media/Domaza_8636166/0004_20cbfed4.jpg
- Sample completeness: description=True, price=True, area=True, rooms=True, floor=False, phones=True, city=True, address=True
- Source description status: captured
- Structured fields count: 3
- Source attributes count: 5

## Holding Group Real Estate (Tier 2)

- Pattern status: `without_sample_product_capture`
- Pattern issue: No saved full product sample exists yet for this source.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 3000 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: crawl direct site plus dedupe against portal syndication
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Sample evidence: none saved yet

## Home2U (Tier 2)

- Pattern status: `Patterned`
- Pattern issue: Code pattern exists and the best saved sample proves full local image-file capture plus core and structured detail-page fields.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 6000 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: Home2U property archive pages + detail parser for secondary info blocks, gallery images, source description status, and local media proof.
- Code paths: scripts/live_scraper.py::generic, scripts/live_scraper.py::_parse_home2u
- DB status: `without_database_target`
- Source listing root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/home2u/listings
- Source raw root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/home2u/raw
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/home2u/listings/Home2U_9e265a1748ab.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/home2u/raw/Home2U_9e265a1748ab.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/Home2U_9e265a1748ab
- Sample listing URL: https://home2u.bg/property/targovsko-pomesthenie-pod-naem-v-rajona-na-avtogara-varna/
- Sample title: ТЪРГОВСКО ПОМЕЩЕНИЕ ПОД НАЕМ В РАЙОНА НА АВТОГАРА ВАРНА
- Sample gallery: 1/1 saved locally (100.0%)
- Local image files saved: 1
- Local image file preview: data/media/Home2U_9e265a1748ab/0000_4faca56f.jpg
- Sample completeness: description=True, price=True, area=True, rooms=True, floor=True, phones=True, city=True, address=True
- Source description status: captured
- Structured fields count: 4
- Source attributes count: 3

## Imoteka.bg (Tier 2)

- Pattern status: `without_authorized_pattern`
- Pattern issue: Source needs legal review before a live pattern can be promoted.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 14000 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: partnership/licensed feed preferred; headless only after legal clearance
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Sample evidence: none saved yet

## Imoti.info (Tier 2)

- Pattern status: `without_authorized_pattern`
- Pattern issue: Source is licensing-gated; no public scraping pattern should be marked complete.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 25000 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: licensing or partnership first; fixture-only parser research until approved
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Sample evidence: none saved yet

## Indomio.bg (Tier 2)

- Pattern status: `without_sample_product_capture`
- Pattern issue: No saved full product sample exists yet for this source.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 7000 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: hybrid HTML/headless crawler
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Sample evidence: none saved yet

## Lions Group (Tier 2)

- Pattern status: `without_sample_product_capture`
- Pattern issue: No saved full product sample exists yet for this source.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 2500 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: server-rendered listing crawl
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Sample evidence: none saved yet

## Pochivka.bg (Tier 2)

- Pattern status: `without_sample_product_capture`
- Pattern issue: No saved full product sample exists yet for this source.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 5000 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: partnership or limited travel-catalog crawl
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Sample evidence: none saved yet

## realestates.bg (Tier 2)

- Pattern status: `without_sample_product_capture`
- Pattern issue: No saved full product sample exists yet for this source.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 6000 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: scope-limited HTML crawl and dedupe against alo.bg
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Sample evidence: none saved yet

## Realistimo (Tier 2)

- Pattern status: `without_sample_product_capture`
- Pattern issue: No saved full product sample exists yet for this source.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 4500 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: HTML crawl with map-filter fallback
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Sample evidence: none saved yet

## Rentica.bg (Tier 2)

- Pattern status: `without_sample_product_capture`
- Pattern issue: No saved full product sample exists yet for this source.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 1200 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: rent-only HTML parser
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Sample evidence: none saved yet

## Svobodni-kvartiri.com (Tier 2)

- Pattern status: `without_sample_product_capture`
- Pattern issue: No saved full product sample exists yet for this source.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 3500 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: deep pagination crawl by city scope
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Sample evidence: none saved yet

## Unique Estates (Tier 2)

- Pattern status: `without_sample_product_capture`
- Pattern issue: No saved full product sample exists yet for this source.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 2000 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: luxury listing crawler
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Sample evidence: none saved yet

## Vila.bg (Tier 2)

- Pattern status: `without_sample_product_capture`
- Pattern issue: No saved full product sample exists yet for this source.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 4000 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: partnership or limited catalog crawl
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Sample evidence: none saved yet

## Yavlena (Tier 2)

- Pattern status: `Patterned`
- Pattern issue: Code pattern exists and the best saved sample proves full local image-file capture plus core and structured detail-page fields.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 9000 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: incremental crawl with ID-based URLs
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Source listing root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/yavlena/listings
- Source raw root: /Users/getapple/Documents/Real Estate Bulg/data/scraped/yavlena/raw
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/yavlena/listings/Yavlena_674a3a1d4ee3.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/yavlena/raw/Yavlena_674a3a1d4ee3.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/Yavlena_674a3a1d4ee3
- Sample listing URL: https://www.yavlena.com/bg/168889
- Sample title: Тристаен апартамент в София 108 кв.м. ID 168889  | Явлена
- Sample gallery: 1/1 saved locally (100.0%)
- Local image files saved: 1
- Local image file preview: data/media/Yavlena_674a3a1d4ee3/0000_fcc7ddc5.jpg
- Sample completeness: description=True, price=True, area=True, rooms=True, floor=False, phones=True, city=True, address=True
- Source description status: captured
- Structured fields count: 3
- Source attributes count: 3
