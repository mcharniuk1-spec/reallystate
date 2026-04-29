# Tier 1-2 Pattern Status

Generated: 2026-04-29 03:47 UTC

Media storage mode: image binaries are stored as local files under `data/media/<reference_id>/...`; remote `image_urls` remain only as source traceability, while listing JSON artifacts now also store `local_image_files` and `local_image_storage_keys`.

This report separates four questions for each source:
- Can we count the live active site inventory?
- Can we count posted-within-2-months inventory?
- Can we split Varna city vs Varna region at website level?
- Do we have a saved code pattern that lands one full product item with full gallery evidence and local image files?

Strict patterned sources: Address.bg, BulgarianProperties, Homes.bg, imot.bg, LUXIMMO, OLX.bg, property.bg, SUPRIMMO, Bazar.bg, Yavlena

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
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/address_bg/listings/Address.bg_46c9d4cb568d.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/address_bg/raw/Address.bg_46c9d4cb568d.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/Address.bg_46c9d4cb568d
- Sample listing URL: https://address.bg/varna-m-st-zelenika-parcel-teren-offer686997
- Sample title: Парцел/Терен във Варна, м-ст Зеленика - код на имота: 686997
- Sample gallery: 1/1 saved locally (100.0%)
- Local image files saved: 1
- Local image file preview: data/media/Address.bg_46c9d4cb568d/0000_f6185c81.jpg
- Sample completeness: description=True, price=True, area=True, rooms=False, floor=False, phones=True, city=True, address=True
- Structured fields count: 2
- Source attributes count: 1

## alo.bg (Tier 1)

- Pattern status: `without_sample_product_capture`
- Pattern issue: No saved full product sample exists yet for this source.
- Count status: `recounted_live`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 75961 (lower_bound)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: scoped HTML crawl with category filtering
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Sample evidence: none saved yet

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
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/bulgarianproperties/listings/BulgarianProperties_ec4b0ae64e6c.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/bulgarianproperties/raw/BulgarianProperties_ec4b0ae64e6c.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/BulgarianProperties_ec4b0ae64e6c
- Sample listing URL: https://www.bulgarianproperties.com/1-bedroom_apartments_in_Bulgaria/AD86759BG_1-bedroom_apartment_for_sale_in_Sozopol.html
- Sample title: One bedroom turnkey apartment in Sozopol
- Sample gallery: 38/16 saved locally (237.5%)
- Local image files saved: 38
- Local image file preview: data/media/BulgarianProperties_ec4b0ae64e6c/0000_30b1485f.jpg, data/media/BulgarianProperties_ec4b0ae64e6c/0001_30b1485f.jpg, data/media/BulgarianProperties_ec4b0ae64e6c/0002_21d91181.jpg, data/media/BulgarianProperties_ec4b0ae64e6c/0003_1b0c98f9.jpg, data/media/BulgarianProperties_ec4b0ae64e6c/0004_23e343be.jpg
- Sample completeness: description=True, price=True, area=False, rooms=True, floor=False, phones=True, city=True, address=True
- Structured fields count: 2
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
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/homes_bg/listings/Homes.bg_1681133.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/homes_bg/raw/Homes.bg_1681133.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/Homes.bg_1681133
- Sample listing URL: https://www.homes.bg/offer/apartament-za-prodazhba/dvustaen-68m2-sofiya-centyr/as1681133
- Sample title: Двустаен, 68m² - Център, София
- Sample gallery: 10/10 saved locally (100.0%)
- Local image files saved: 10
- Local image file preview: data/media/Homes.bg_1681133/0000_cfd05ac9.jpg, data/media/Homes.bg_1681133/0001_82a16b1e.jpg, data/media/Homes.bg_1681133/0002_a8ddfae7.jpg, data/media/Homes.bg_1681133/0003_159b1b96.jpg, data/media/Homes.bg_1681133/0004_29c16c6d.jpg
- Sample completeness: description=True, price=True, area=True, rooms=True, floor=True, phones=True, city=True, address=True
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
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/imot_bg/listings/imot.bg_3f93a31d3f1b.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/imot_bg/raw/imot.bg_3f93a31d3f1b.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/imot.bg_3f93a31d3f1b
- Sample listing URL: https://www.imot.bg/obiava-1a176959443896121-prodava-ednostaen-apartament-grad-sofiya-boyana
- Sample title: Продава 1-СТАЕН град София, Бояна Обява: 1a176959443896121
- Sample gallery: 15/15 saved locally (100.0%)
- Local image files saved: 15
- Local image file preview: data/media/imot.bg_3f93a31d3f1b/0000_147f45d8.jpg, data/media/imot.bg_3f93a31d3f1b/0001_27706677.jpg, data/media/imot.bg_3f93a31d3f1b/0002_5755e343.jpg, data/media/imot.bg_3f93a31d3f1b/0003_4cf28098.jpg, data/media/imot.bg_3f93a31d3f1b/0004_7ad69903.jpg
- Sample completeness: description=True, price=True, area=True, rooms=True, floor=True, phones=True, city=True, address=True
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
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/luximmo/listings/LUXIMMO_50928a486328.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/luximmo/raw/LUXIMMO_50928a486328.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/LUXIMMO_50928a486328
- Sample listing URL: https://www.luximmo.bg/bulgaria/oblast-sofia/borovets/luksozni-imoti-tristayni-apartamenti/luksozen-imot-40084-tristaen-apartament-za-prodajba-v-borovets.html
- Sample title: Тристаен мезонет "до ключ" в престижния комплекс 7 Angels
- Sample gallery: 6/6 saved locally (100.0%)
- Local image files saved: 6
- Local image file preview: data/media/LUXIMMO_50928a486328/0000_46fe386d.jpg, data/media/LUXIMMO_50928a486328/0001_46fe386d.jpg, data/media/LUXIMMO_50928a486328/0002_890b9c0d.jpg, data/media/LUXIMMO_50928a486328/0003_196babe3.jpg, data/media/LUXIMMO_50928a486328/0004_dc0063d4.jpg
- Sample completeness: description=True, price=True, area=True, rooms=True, floor=False, phones=True, city=True, address=True
- Structured fields count: 3
- Source attributes count: 3

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
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/property_bg/listings/property.bg_c6be6a6838ca.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/property_bg/raw/property.bg_c6be6a6838ca.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/property.bg_c6be6a6838ca
- Sample listing URL: https://www.property.bg/property-117962-two-room-maisonette-quotturnkeyquot-in-the-luxury-complex-7-angels/
- Sample title: Two-room maisonette "turnkey" in the luxury complex 7 Angels
- Sample gallery: 87/87 saved locally (100.0%)
- Local image files saved: 87
- Local image file preview: data/media/property.bg_c6be6a6838ca/0000_b1d8f58f.jpg, data/media/property.bg_c6be6a6838ca/0001_5e2b4b85.jpg, data/media/property.bg_c6be6a6838ca/0002_a0b2db92.jpg, data/media/property.bg_c6be6a6838ca/0003_e1384009.jpg, data/media/property.bg_c6be6a6838ca/0004_8ba2135b.jpg
- Sample completeness: description=True, price=True, area=True, rooms=True, floor=False, phones=True, city=True, address=True
- Structured fields count: 3
- Source attributes count: 3

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
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/suprimmo/listings/SUPRIMMO_STO-132154.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/suprimmo/raw/SUPRIMMO_STO-132154.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/SUPRIMMO_STO-132154
- Sample listing URL: https://www.suprimmo.bg/imot-132154-yujen-dvustaen-apartament-s-otdelna-kuhnya-v-spokoen-i-zelen-rayon/
- Sample title: Южен двустаен апартамент с отделна кухня, в спокоен и зелен район
- Sample gallery: 43/43 saved locally (100.0%)
- Local image files saved: 43
- Local image file preview: data/media/SUPRIMMO_STO-132154/0000_6d93e91f.jpg, data/media/SUPRIMMO_STO-132154/0001_c7298b7d.jpg, data/media/SUPRIMMO_STO-132154/0002_a9bae48c.jpg, data/media/SUPRIMMO_STO-132154/0003_dc2e39d6.jpg, data/media/SUPRIMMO_STO-132154/0004_50cd4fd2.jpg
- Sample completeness: description=True, price=True, area=True, rooms=True, floor=False, phones=True, city=True, address=True
- Structured fields count: 3
- Source attributes count: 3

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
- Structured fields count: 3
- Source attributes count: 0

## Domaza (Tier 2)

- Pattern status: `without_sample_product_capture`
- Pattern issue: No saved full product sample exists yet for this source.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 22000 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: crawl with language canonicalization
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Sample evidence: none saved yet

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

- Pattern status: `without_sample_product_capture`
- Pattern issue: No saved full product sample exists yet for this source.
- Count status: `without_live_count_method`
- Recent status: `without_recent_count_method`
- Varna status: `without_varna_count_method`
- Website total active: 6000 (estimate)
- Recent under 2 months: n/a
- Varna split: n/a+n/a
- Code method: templated HTML parser
- Code paths: scripts/live_scraper.py::generic
- DB status: `without_database_target`
- Sample evidence: none saved yet

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
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/yavlena/listings/Yavlena_f7a1a1631995.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/yavlena/raw/Yavlena_f7a1a1631995.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/Yavlena_f7a1a1631995
- Sample listing URL: https://www.yavlena.com/bg/168194
- Sample title: Тристаен апартамент във Варна 102 кв.м. ID 168194  | Явлена
- Sample gallery: 1/1 saved locally (100.0%)
- Local image files saved: 1
- Local image file preview: data/media/Yavlena_f7a1a1631995/0000_3d2c6df2.jpg
- Sample completeness: description=True, price=True, area=True, rooms=True, floor=False, phones=True, city=True, address=True
- Structured fields count: 3
- Source attributes count: 3
