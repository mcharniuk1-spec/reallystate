# Tier 1-2 Pattern Status

Generated: 2026-04-21 15:22 UTC

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
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/address_bg/listings/Address.bg_45556d0cad2d.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/address_bg/raw/Address.bg_45556d0cad2d.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/Address.bg_45556d0cad2d
- Sample listing URL: https://address.bg/sofia-bistrica-parcel-teren-offer626861
- Sample title: Парцел/Терен в София, Бистрица - код на имота: 626861
- Sample gallery: 1/1 saved locally (100.0%)
- Local image files saved: 1
- Local image file preview: data/media/Address.bg_45556d0cad2d/0000_6ae4210c.jpg
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
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/homes_bg/listings/Homes.bg_1680493.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/homes_bg/raw/Homes.bg_1680493.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/Homes.bg_1680493
- Sample listing URL: https://www.homes.bg/offer/apartament-za-prodazhba/dvustaen-57m2-sofiya-zhk.-suhata-reka/as1680493
- Sample title: Двустаен, 57m² - жк. Сухата Река, София
- Sample gallery: 10/10 saved locally (100.0%)
- Local image files saved: 10
- Local image file preview: data/media/Homes.bg_1680493/0000_69f4c0fe.jpg, data/media/Homes.bg_1680493/0001_007b8f52.jpg, data/media/Homes.bg_1680493/0002_accd0edf.jpg, data/media/Homes.bg_1680493/0003_f7b19633.jpg, data/media/Homes.bg_1680493/0004_3cd7c7c8.jpg
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
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/imot_bg/listings/imot.bg_e42f7bff1005.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/imot_bg/raw/imot.bg_e42f7bff1005.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/imot.bg_e42f7bff1005
- Sample listing URL: https://www.imot.bg/obiava-1b177261786459012-prodava-dvustaen-apartament-grad-sofiya-levski-g
- Sample title: Продава 2-СТАЕН град София, Левски Г Обява: 1b177261786459012
- Sample gallery: 17/17 saved locally (100.0%)
- Local image files saved: 17
- Local image file preview: data/media/imot.bg_e42f7bff1005/0000_6c35fb32.jpg, data/media/imot.bg_e42f7bff1005/0001_64b2cc01.jpg, data/media/imot.bg_e42f7bff1005/0002_e84e83dd.jpg, data/media/imot.bg_e42f7bff1005/0003_981cf594.jpg, data/media/imot.bg_e42f7bff1005/0004_bae4aa5b.jpg
- Sample completeness: description=True, price=True, area=True, rooms=True, floor=True, phones=True, city=True, address=True
- Structured fields count: 4
- Source attributes count: 4

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
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/luximmo/listings/LUXIMMO_0c9fd22cfdbb.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/luximmo/raw/LUXIMMO_0c9fd22cfdbb.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/LUXIMMO_0c9fd22cfdbb
- Sample listing URL: https://www.luximmo.bg/bulgaria/oblast-sofia/borovets/luksozni-imoti-dvustayni-apartamenti/luksozen-imot-40091-dvustaen-apartament-za-prodajba-v-borovets.html
- Sample title: Двустаен апартамент "до ключ" в престижния комплекс 7 Angels
- Sample gallery: 30/30 saved locally (100.0%)
- Local image files saved: 30
- Local image file preview: data/media/LUXIMMO_0c9fd22cfdbb/0000_02293170.jpg, data/media/LUXIMMO_0c9fd22cfdbb/0001_02293170.jpg, data/media/LUXIMMO_0c9fd22cfdbb/0002_196babe3.jpg, data/media/LUXIMMO_0c9fd22cfdbb/0003_dc0063d4.jpg, data/media/LUXIMMO_0c9fd22cfdbb/0004_a719601f.jpg
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
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/olx_bg/listings/OLX.bg_147540772.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/olx_bg/raw/OLX.bg_147540772.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/OLX.bg_147540772
- Sample listing URL: https://www.olx.bg/d/ad/dvustaen-ap-pod-naem-v-kv-lyulin-5-CID368-ID9Z45S.html
- Sample title: Двустаен ап. под наем в кв. Люлин 5
- Sample gallery: 6/6 saved locally (100.0%)
- Local image files saved: 6
- Local image file preview: data/media/OLX.bg_147540772/0000_9dfd850b.webp, data/media/OLX.bg_147540772/0001_708b71ff.webp, data/media/OLX.bg_147540772/0002_fc2c1682.webp, data/media/OLX.bg_147540772/0003_7553e5a4.webp, data/media/OLX.bg_147540772/0004_e49a3bae.webp
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
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/bazar_bg/listings/Bazar.bg_53706749.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/bazar_bg/raw/Bazar.bg_53706749.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/Bazar.bg_53706749
- Sample listing URL: https://bazar.bg/obiava-53706749/prodava-4-staen-gr-sofiya-krastova-vada
- Sample title: Продава 4-СТАЕН, гр. София, Кръстова вада → Обява 53706749
- Sample gallery: 15/15 saved locally (100.0%)
- Local image files saved: 15
- Local image file preview: data/media/Bazar.bg_53706749/0000_de4ef8a5.jpg, data/media/Bazar.bg_53706749/0001_b614c18e.jpg, data/media/Bazar.bg_53706749/0002_5b16c2c8.jpg, data/media/Bazar.bg_53706749/0003_3276c5ee.jpg, data/media/Bazar.bg_53706749/0004_eb4e6ab9.jpg
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
- Sample listing JSON: /Users/getapple/Documents/Real Estate Bulg/data/scraped/yavlena/listings/Yavlena_acbef70866cf.json
- Sample raw HTML: /Users/getapple/Documents/Real Estate Bulg/data/scraped/yavlena/raw/Yavlena_acbef70866cf.html
- Sample media dir: /Users/getapple/Documents/Real Estate Bulg/data/media/Yavlena_acbef70866cf
- Sample listing URL: https://www.yavlena.com/bg/168366
- Sample title: Тристаен апартамент в София 124 кв.м. ID 168366  | Явлена
- Sample gallery: 1/1 saved locally (100.0%)
- Local image files saved: 1
- Local image file preview: data/media/Yavlena_acbef70866cf/0000_3f8b072f.jpg
- Sample completeness: description=True, price=True, area=True, rooms=True, floor=False, phones=True, city=True, address=True
- Structured fields count: 3
- Source attributes count: 3
