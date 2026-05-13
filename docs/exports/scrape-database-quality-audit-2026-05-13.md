# Scrape Database And Corpus Quality Audit

Generated: 2026-05-13T13:45:33.447933+00:00

## Executive Findings

- FACT: PostgreSQL was not available in this environment; this audit is file-backed plus static schema/model analysis.
- FACT: Current scraped JSON corpus contains `30334` rows across `13` source directories; Action1 seven-source rows total `29397`.
- FACT: Stored QA state is stale/incomplete: `26231` rows have `PENDING_QA`, missing, or unknown `scrape_status`.
- FACT: Offline Action1 QA estimate: `20811` accepted single-unit candidates, `7133` LOST rows, `1453` grouped/development publications.
- INTERPRETATION: The corpus is large enough for product testing, but not safe for default canonical import until QA state, source-publication identity, contact normalization, and first-class DB fields are fixed.
- GAP: Live URL existence, PostgreSQL row counts, and image semantic descriptions were not verified here.

## Source Summary

| Source key | Rows | Stored status top | Estimated OK | Estimated LOST | Estimated grouped | Pending/missing QA | Import candidates by current importer | Top reasons |
|---|---:|---|---:|---:|---:|---:|---:|---|
| `address_bg` | 6473 | PENDING_QA:5582, LOST:891 | 3330 | 3143 | 0 | 5582 | 0 | one_remote_photo_gallery_suspect:1677, missing_city_or_address:1262, suspicious_unit_area_too_large:306, partial_local_gallery:197, suspicious_house_area_too_large:156 |
| `alo_bg` | 29 | MISSING:29 | 29 | 0 | 0 | 29 | 0 |  |
| `bazar_bg` | 250 | MISSING:250 | 177 | 73 | 0 | 250 | 0 | partial_local_gallery:58, missing_city_or_address:17, zero_price_invalid:3, suspicious_unit_area_too_large:2, description_too_short:1 |
| `bulgarianproperties` | 2289 | PENDING_QA:1888, GROUPED_PUBLICATION:284, LOST:117 | 12 | 2277 | 0 | 1888 | 0 | partial_local_gallery:2271, missing_area:510, suspicious_unit_area_too_large:116, suspicious_house_area_too_large:112, thin_title:1 |
| `domaza` | 40 | MISSING:40 | 25 | 13 | 2 | 40 | 0 | missing_area:13 |
| `home2u` | 24 | MISSING:24 | 10 | 14 | 0 | 24 | 0 | thin_title:13, missing_area:3, missing_city_or_address:1, missing_description:1 |
| `homes_bg` | 144 | LOST:62, SCRAPED_OK:60, PENDING_QA:20 | 79 | 62 | 3 | 20 | 60 | partial_local_gallery:55, one_remote_photo_gallery_suspect:13, missing_remote_gallery:3, missing_description:1 |
| `imot_bg` | 9937 | PENDING_QA:8124, SCRAPED_OK:1535, LOST:189 | 8986 | 264 | 687 | 8124 | 1535 | partial_local_gallery:209, missing_area:176, description_too_short:25, one_remote_photo_gallery_suspect:9, suspicious_unit_area_too_large:8 |
| `luximmo` | 2512 | PENDING_QA:2356, GROUPED_PUBLICATION:138, SCRAPED_OK:11 | 1788 | 607 | 117 | 2356 | 5 | missing_area:518, suspicious_unit_area_too_large:84, partial_local_gallery:4, one_remote_photo_gallery_suspect:1, suspicious_area_below_2sqm:1 |
| `olx_bg` | 249 | MISSING:249 | 111 | 131 | 7 | 249 | 0 | missing_area:107, missing_city_or_address:41, suspicious_unit_area_too_large:1 |
| `property_bg` | 3094 | PENDING_QA:3089, SCRAPED_OK:5 | 3053 | 41 | 0 | 3089 | 5 | suspicious_unit_area_too_large:25, description_too_short:9, suspicious_house_area_too_large:4, partial_local_gallery:3, missing_area:1 |
| `suprimmo` | 4948 | PENDING_QA:4235, GROUPED_PUBLICATION:712, SCRAPED_OK:1 | 3563 | 739 | 646 | 4235 | 1 | missing_area:684, suspicious_unit_area_too_large:36, suspicious_house_area_too_large:15, partial_local_gallery:5, suspicious_area_below_2sqm:1 |
| `yavlena` | 345 | MISSING:345 | 144 | 194 | 7 | 345 | 0 | missing_description:166, description_too_short:22, zero_price_invalid:9, suspicious_unit_area_too_large:3, partial_local_gallery:1 |

## Action1 Bucket Quality Matrix

| Source key | Bucket | Estimated OK | Estimated LOST | Estimated grouped | Top bucket reasons |
|---|---|---:|---:|---:|---|
| `address_bg` | `buy_personal` | 1798 | 1611 | 0 | one_remote_photo_gallery_suspect:742, missing_city_or_address:720, suspicious_unit_area_too_large:157, suspicious_house_area_too_large:153 |
| `address_bg` | `buy_commercial` | 445 | 869 | 0 | one_remote_photo_gallery_suspect:775, missing_city_or_address:82, suspicious_unit_area_too_large:53, partial_local_gallery:51 |
| `address_bg` | `rent_personal` | 720 | 440 | 0 | missing_city_or_address:359, one_remote_photo_gallery_suspect:71, suspicious_unit_area_too_large:22, partial_local_gallery:14 |
| `address_bg` | `rent_commercial` | 367 | 223 | 0 | missing_city_or_address:101, one_remote_photo_gallery_suspect:89, suspicious_unit_area_too_large:74, partial_local_gallery:16 |
| `bulgarianproperties` | `buy_personal` | 7 | 1759 | 0 | partial_local_gallery:1755, missing_area:422, suspicious_house_area_too_large:111, suspicious_unit_area_too_large:96 |
| `bulgarianproperties` | `buy_commercial` | 1 | 273 | 0 | partial_local_gallery:273, missing_area:39, suspicious_unit_area_too_large:6 |
| `bulgarianproperties` | `rent_personal` | 3 | 177 | 0 | partial_local_gallery:175, missing_area:35, suspicious_unit_area_too_large:8, thin_title:1 |
| `bulgarianproperties` | `rent_commercial` | 1 | 68 | 0 | partial_local_gallery:68, missing_area:14, suspicious_unit_area_too_large:6 |
| `homes_bg` | `buy_personal` | 79 | 62 | 3 | partial_local_gallery:55, one_remote_photo_gallery_suspect:13, missing_remote_gallery:3, missing_description:1 |
| `imot_bg` | `buy_personal` | 6751 | 225 | 614 | partial_local_gallery:184, missing_area:175, description_too_short:21, one_remote_photo_gallery_suspect:8 |
| `imot_bg` | `buy_commercial` | 218 | 16 | 8 | partial_local_gallery:11, suspicious_unit_area_too_large:3, missing_area:1, one_remote_photo_gallery_suspect:1 |
| `imot_bg` | `rent_personal` | 1895 | 15 | 60 | partial_local_gallery:11, description_too_short:4 |
| `imot_bg` | `rent_commercial` | 122 | 8 | 5 | suspicious_unit_area_too_large:5, partial_local_gallery:3 |
| `luximmo` | `buy_personal` | 1583 | 424 | 107 | missing_area:339, suspicious_unit_area_too_large:80, partial_local_gallery:4, one_remote_photo_gallery_suspect:1 |
| `luximmo` | `rent_personal` | 204 | 183 | 10 | missing_area:179, suspicious_unit_area_too_large:4 |
| `luximmo` | `rent_commercial` | 1 | 0 | 0 |  |
| `property_bg` | `buy_personal` | 1969 | 14 | 0 | suspicious_unit_area_too_large:6, suspicious_house_area_too_large:3, description_too_short:3, partial_local_gallery:1 |
| `property_bg` | `buy_commercial` | 174 | 3 | 0 | description_too_short:2, suspicious_unit_area_too_large:1 |
| `property_bg` | `rent_personal` | 666 | 4 | 0 | description_too_short:2, suspicious_house_area_too_large:1, partial_local_gallery:1 |
| `property_bg` | `rent_commercial` | 244 | 20 | 0 | suspicious_unit_area_too_large:18, description_too_short:2, partial_local_gallery:1 |
| `suprimmo` | `buy_personal` | 2175 | 323 | 414 | missing_area:297, suspicious_house_area_too_large:15, suspicious_unit_area_too_large:10, partial_local_gallery:2 |
| `suprimmo` | `buy_commercial` | 836 | 109 | 187 | missing_area:107, suspicious_area_below_2sqm:1, partial_local_gallery:1 |
| `suprimmo` | `rent_personal` | 350 | 231 | 31 | missing_area:227, suspicious_unit_area_too_large:3, partial_local_gallery:1 |
| `suprimmo` | `rent_commercial` | 202 | 76 | 14 | missing_area:53, suspicious_unit_area_too_large:23, partial_local_gallery:1 |

## Cross-Source Issues For Scraper Agent

1. Re-run or apply the quality gate after every Action1 continuation before import/export. Current JSON has many `PENDING_QA` rows, so importer dry-run logic cannot distinguish accepted rows from unreviewed rows.
2. Treat `source_publication_type` as mandatory. Grouped/development pages must remain source publications until unit-level URL, price/price-status, area, and media are present.
3. Normalize and validate contacts. Phone extraction is polluted by dates, IDs, UI counters, and JavaScript numbers on several sources.
4. Deduplicate remote gallery variants before comparing remote vs local counts; property-family sources often count `big`, `medium`, and `small1` versions of the same photo.
5. Preserve image binaries as local files, but add semantic image-report coverage before using photo content for smart search.
6. Capture bucket/segment provenance in a DB-safe way. Current `source_section_id` strings are useful in JSON but are not aligned with the Varna-only DB control plane.
7. Do not import rows with `PENDING_QA`, missing `scrape_status`, `LOST`, grouped/development, or inactive markers by default.

## Source Instructions

### address_bg

Backfill full high-resolution gallery and fix missing city/address extraction. Many rows are one-photo suspects or have oversized unit/house areas.

- FACT: rows=6473; estimated_quality={'SCRAPED_OK': 3330, 'LOST': 3143}.
- FACT: field_gaps={'missing_city_or_address': 1262, 'unknown_property_category': 649, 'thin_description': 28, 'missing_area': 3}.
- FACT: phones total/valid/invalid=100325/50660/49665; remote/local photos=47367/50748.
- Example `missing_city_or_address`: `Address.bg:001f2a6df8f5` — Тристаен апартамент във Варна, Аспарухово - код на имота: 688648

### alo_bg

Add formal QA fields and contact cleanup; current rows are small but unreviewed.

- FACT: rows=29; estimated_quality={'SCRAPED_OK': 29}.
- FACT: field_gaps={'thin_description': 1}.
- FACT: phones total/valid/invalid=139/3/136; remote/local photos=322/322.

### bazar_bg

Add bucket keys, QA fields, contact cleanup, and remote gallery de-duplication.

- FACT: rows=250; estimated_quality={'SCRAPED_OK': 177, 'LOST': 73}.
- FACT: field_gaps={'thin_description': 50, 'unknown_property_category': 44, 'missing_city_or_address': 17, 'zero_price': 3}.
- FACT: phones total/valid/invalid=4238/1744/2494; remote/local photos=2607/2487.
- Example `missing_city_or_address`: `Bazar.bg:40857836` — Продава 2-СТАЕН без комисионна за купувача, не се начислява ДДС  → Обява 40857836

### bulgarianproperties

Prioritize local-gallery completeness and area semantics; development pages must be grouped unless unit-level evidence exists.

- FACT: rows=2289; estimated_quality={'LOST': 2277, 'SCRAPED_OK': 12}.
- FACT: field_gaps={'missing_area': 510, 'unknown_property_category': 24, 'thin_title': 1, 'missing_city_or_address': 1}.
- FACT: phones total/valid/invalid=74127/60895/13232; remote/local photos=61878/55247.
- Example `partial_local_gallery`: `BulgarianProperties:0023d0450186` — Renovated 1-storey house with garden in Sokolovo village near Karnobat

### domaza

Resolve missing area and add QA status before any import.

- FACT: rows=40; estimated_quality={'SCRAPED_OK': 25, 'LOST': 13, 'GROUPED_PUBLICATION': 2}.
- FACT: field_gaps={'missing_area': 13}.
- FACT: phones total/valid/invalid=12/12/0; remote/local photos=777/777.
- Example `missing_area`: `Domaza:22334` — Жилищен Комплекс, гр. Бяла, Варна, България

### home2u

Fix thin titles and missing areas; add QA status.

- FACT: rows=24; estimated_quality={'LOST': 14, 'SCRAPED_OK': 10}.
- FACT: field_gaps={'thin_title': 13, 'missing_area': 3, 'thin_description': 1, 'missing_city_or_address': 1, 'missing_description': 1}.
- FACT: phones total/valid/invalid=4/4/0; remote/local photos=133/133.
- Example `thin_title`: `Home2U:0ed15363bab8` — 2-стаен

### homes_bg

Expand beyond sale apartments, remove duplicate URL rows, use offer JSON/API for active status and all gallery images.

- FACT: rows=144; estimated_quality={'SCRAPED_OK': 79, 'LOST': 62, 'GROUPED_PUBLICATION': 3}.
- FACT: field_gaps={'missing_description': 1}.
- FACT: phones total/valid/invalid=201/159/42; remote/local photos=1077/740.
- Example `partial_local_gallery`: `Homes.bg:01bf996371bd` — Едностаен, 50m² - жк. Лозенец, София

### imot_bg

Keep as strongest corpus, but repair partial gallery, missing area, grouped development separation, and category precision.

- FACT: rows=9937; estimated_quality={'SCRAPED_OK': 8986, 'GROUPED_PUBLICATION': 687, 'LOST': 264}.
- FACT: field_gaps={'thin_description': 234, 'unknown_property_category': 211, 'missing_area': 176, 'missing_description': 1}.
- FACT: phones total/valid/invalid=14498/13871/627; remote/local photos=102804/102046.
- Example `missing_area`: `imot.bg:00a2fadab024` — ������� ������ � ���� ����� ����������� ������ ����� 7898

### luximmo

Fix missing area and oversized unit area; de-duplicate gallery size variants; keep development pages grouped.

- FACT: rows=2512; estimated_quality={'SCRAPED_OK': 1788, 'LOST': 607, 'GROUPED_PUBLICATION': 117}.
- FACT: field_gaps={'missing_area': 518, 'thin_description': 113}.
- FACT: phones total/valid/invalid=60338/26709/33629; remote/local photos=17947/28601.
- Example `missing_area`: `LUXIMMO:000386d2645f` — Просторен апартамент с три спални под наем до Мол "България"

### olx_bg

Add bucket keys, QA status, area extraction, location extraction, and contact cleanup.

- FACT: rows=249; estimated_quality={'LOST': 131, 'SCRAPED_OK': 111, 'GROUPED_PUBLICATION': 7}.
- FACT: field_gaps={'missing_area': 107, 'missing_city_or_address': 41, 'unknown_property_category': 17, 'thin_description': 5}.
- FACT: phones total/valid/invalid=28762/15691/13071; remote/local photos=1365/1365.
- Example `missing_area`: `OLX.bg:125403576` — Къща под наем 3 спални 2 бани с планинска гледка, 2 паркоместа, на 13км до Слънчев Бряг (с. Гюльовца). Затворен и охраняем квартал.

### property_bg

Stored QA is almost entirely pending even though offline estimate is strong; apply QA and reduce thin descriptions/low sale price warnings.

- FACT: rows=3094; estimated_quality={'SCRAPED_OK': 3053, 'LOST': 41}.
- FACT: field_gaps={'thin_description': 2075, 'unknown_property_category': 118, 'missing_area': 1}.
- FACT: phones total/valid/invalid=24330/10451/13879; remote/local photos=138662/138764.
- Example `suspicious_unit_area_too_large`: `property.bg:0123d7e45c40` — Elite class A building - OKINAWA Office Center next to Simeonovsko Shose Blvd.

### suprimmo

Fix missing area, low sale price warnings, grouped development classification, and gallery variant duplication.

- FACT: rows=4948; estimated_quality={'SCRAPED_OK': 3563, 'LOST': 739, 'GROUPED_PUBLICATION': 646}.
- FACT: field_gaps={'missing_area': 684, 'unknown_property_category': 66, 'thin_description': 47}.
- FACT: phones total/valid/invalid=89246/25052/64194; remote/local photos=229204/229556.
- Example `missing_area`: `SUPRIMMO:0405d137ade6` — Обзаведено студио под наем в елитен комплекс в Черноморец

### yavlena

Do not import until description and zero-price issues are resolved; add QA status and price-status provenance.

- FACT: rows=345; estimated_quality={'LOST': 194, 'SCRAPED_OK': 144, 'GROUPED_PUBLICATION': 7}.
- FACT: field_gaps={'missing_description': 166, 'thin_description': 151, 'unknown_property_category': 28, 'zero_price': 9}.
- FACT: phones total/valid/invalid=646/646/0; remote/local photos=345/345.
- Example `missing_description`: `Yavlena:0381ae4d9137` — Двустаен апартамент в Поморие 97 кв.м. ID 168399  | Явлена

## Database Structure Issues

- FACT: `CanonicalListing` domain fields missing from `CanonicalListingModel`: 
- FACT: Recommended first-class QA/media fields absent from SQL: `full_gallery_downloaded`, `image_description_coverage`, `image_report_status`, `listing_status`, `local_image_storage_keys`, `photo_count_local`, `photo_count_remote`, `price_status`, `scrape_acceptance_status`, `scrape_status`, `single_entity_candidate`, `source_publication_type`
- FACT: `source_section` / `crawl_run` are still constrained to `region_key = 'varna'`, while Action1 is all-Bulgaria.
- INTERPRETATION: DB import can lose QA/media/segment evidence or fail when model/schema alignment is exercised with a real SQLAlchemy/PostgreSQL runtime.

## Required Acceptance Gate

- `python3 scripts/audit_scrape_database_quality.py` regenerates this report.
- Action1 quality gate is run and applied or importer blocks unreviewed `PENDING_QA` rows.
- Import dry-run works without requiring DB-only dependencies, or reports dependency failure as a blocker.
- DB model, SQL schema, and import payload agree on canonical listing fields.
- Scraper fixes are verified with fixture/parser regression tests and no live-network test dependencies.
