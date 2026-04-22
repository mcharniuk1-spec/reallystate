# Tier 1-2 source metrics deep dive

Generated from `data/source_registry.json`, `docs/exports/tier12-source-analysis.json`, and `docs/exports/scrape-status-dashboard.json`.

## Method

FACT:
- `estimated_total_listings` is the saved site-scale estimate from the project source analysis snapshot, not a fresh live recount from today.
- `saved_listings` is the currently landed on-disk corpus from `data/scraped/*/listings/*.json`.
- `with_description`, `with_photo_urls`, and `with_readable_local_photos` are evidence-backed completeness counters from the saved corpus.

INTERPRETATION:
- This report separates website scale from landed scraper output, so we do not confuse source potential with confirmed capture.

GAP:
- PostgreSQL `canonical_listing` proof is still pending for the live volume gate.
- Some sites expose additional property categories beyond what is currently landed in the corpus.

## Tier summary

- Tier 1: 10 sources, landed corpus 881, estimated site scale 549000, landed-vs-estimated 0.2%
- Tier 2: 17 sources, landed corpus 500, estimated site scale 124500, landed-vs-estimated 0.4%

## Source summary table

| Tier | Source | Declared offers | Estimated active items | Landed items | Landed vs estimated | 100-item benchmark | Description % | Photo URL % | Readable photo % | Declared intent coverage |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Address.bg | sale, long_term_rent, land, new_build | 18000 | 43 | 0.2% | 43.0% | 100.0% | 100.0% | 100.0% | 50.0% |
| 1 | alo.bg | sale, long_term_rent, short_term_rent, land, new_build | 35000 | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 1 | BulgarianProperties | sale, long_term_rent, land, new_build | 12000 | 249 | 2.1% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |
| 1 | Homes.bg | sale, long_term_rent, land | 120000 | 37 | 0.0% | 37.0% | 100.0% | 97.3% | 54.1% | 50.0% |
| 1 | imot.bg | sale, long_term_rent, land, new_build | 200000 | 261 | 0.1% | 100.0% | 100.0% | 100.0% | 0.4% | 50.0% |
| 1 | imoti.net | sale, long_term_rent, land, new_build | 90000 | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 1 | LUXIMMO | sale, long_term_rent, land, new_build | 4000 | 15 | 0.4% | 15.0% | 86.7% | 100.0% | 100.0% | 50.0% |
| 1 | OLX.bg | sale, long_term_rent, land, new_build | 45000 | 249 | 0.6% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |
| 1 | property.bg | sale, long_term_rent, land, new_build | 10000 | 15 | 0.1% | 15.0% | 100.0% | 100.0% | 100.0% | 50.0% |
| 1 | SUPRIMMO | sale, long_term_rent, land, new_build | 15000 | 12 | 0.1% | 12.0% | 100.0% | 100.0% | 100.0% | 50.0% |
| 2 | ApartmentsBulgaria.com | short_term_rent | 1800 | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2 | Bazar.bg | sale, long_term_rent, land | 8000 | 250 | 3.1% | 100.0% | 100.0% | 100.0% | 99.6% | 100.0% |
| 2 | Domaza | sale, long_term_rent, short_term_rent, land, new_build | 22000 | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2 | Holding Group Real Estate | sale, long_term_rent, land, new_build | 3000 | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2 | Home2U | sale, long_term_rent, land, new_build | 6000 | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2 | Imoteka.bg | sale, long_term_rent, land, new_build | 14000 | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2 | Imoti.info | sale, long_term_rent, land, new_build | 25000 | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2 | Indomio.bg | sale, long_term_rent, land | 7000 | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2 | Lions Group | sale, long_term_rent, land, new_build | 2500 | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2 | Pochivka.bg | short_term_rent | 5000 | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2 | realestates.bg | sale, long_term_rent, land | 6000 | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2 | Realistimo | sale, long_term_rent, land, new_build | 4500 | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2 | Rentica.bg | long_term_rent | 1200 | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2 | Svobodni-kvartiri.com | long_term_rent, short_term_rent | 3500 | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2 | Unique Estates | sale, long_term_rent, new_build | 2000 | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2 | Vila.bg | short_term_rent | 4000 | 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2 | Yavlena | sale, long_term_rent | 9000 | 250 | 2.8% | 100.0% | 0.0% | 100.0% | 99.6% | 50.0% |

## Per-source details

### Address.bg

- Tier: `1`
- URL: https://address.bg/
- Access/legal: `html` / `public_crawl_with_review`
- Declared website offering: `sale, long_term_rent, land, new_build`
- Estimated active items on website: `18000`
- Confirmed landed active items in current corpus: `43`
- Progress vs estimated site scale: `0.2%`
- Progress vs 100-item benchmark: `43.0%`
- Completeness: description `43/43` (100.0%), photo URLs `43/43` (100.0%), readable local photos `43/43` (100.0%)
- Declared intent coverage: `1/2` (50.0%) from `sale`
- Services landed: sale=43
- Property categories landed: apartment=29, house=8, land=3, office=2, unknown=1
- Fields captured most often: description 43/43, image_urls 43/43, readable_photos 43/43
- Current state: Partial corpus on disk
- Method used now: crawl listings with ref-id normalization
- How the list is organized: Listings are organized by product/category buckets or broad sale/rent archives; apartment recovery is best from category pages instead of the home page.
- Full-list strategy: Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media.
- Detail-page requirement: detail page required
- Detail URL pattern: `address\.bg/.+-offer\d{5,}(?:[/?#].*)?$`
- Discovery entrypoints: `https://address.bg/sale; https://address.bg/rent; https://address.bg/sale/sofia/l4451; https://address.bg/sale/varna/l4694; https://address.bg/rent/sofia/l4451`
- Next step already recorded: Continue category-by-category refreshes and push the file-backed corpus into PostgreSQL for `S1-18` evidence.
- What to automate better:
  - Keep category-first discovery and push every card into a detail-page queue; do not rely on homepage sampling.
  - Expand intent coverage by crawling explicit sale and rent bucket pages separately and tracking them as independent queues.
  - Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.

### alo.bg

- Tier: `1`
- URL: https://www.alo.bg/
- Access/legal: `html` / `public_crawl_with_review`
- Declared website offering: `sale, long_term_rent, short_term_rent, land, new_build`
- Estimated active items on website: `35000`
- Confirmed landed active items in current corpus: `0`
- Progress vs estimated site scale: `0.0%`
- Progress vs 100-item benchmark: `0.0%`
- Completeness: description `0/0` (0.0%), photo URLs `0/0` (0.0%), readable local photos `0/0` (0.0%)
- Declared intent coverage: `0/3` (0.0%) from `none landed yet`
- Services landed: none
- Property categories landed: none
- Fields captured most often: none captured yet
- Current state: Configured, zero landed corpus
- Method used now: scoped HTML crawl with category filtering
- How the list is organized: Listings are organized by product/category buckets or broad sale/rent archives; apartment recovery is best from category pages instead of the home page.
- Full-list strategy: Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media.
- Detail-page requirement: detail page required
- Detail URL pattern: `alo\.bg/.+-\d{5,}(?:[/?#].*)?$`
- Discovery entrypoints: `https://www.alo.bg/obiavi/imoti-prodajbi/apartamenti-stai/; https://www.alo.bg/obiavi/imoti-prodajbi/kashti-vili/; https://www.alo.bg/obiavi/imoti-prodajbi/parzeli-za-zastroiavane-investicionni-proekti/; https://www.alo.bg/obiavi/imoti-prodajbi/zemedelska-zemia-gradini-lozia-gora/; https://www.alo.bg/obiavi/imoti-naemi/apartamenti-stai/`
- Apartment entrypoints: `https://www.alo.bg/obiavi/imoti-prodajbi/apartamenti-stai/; https://www.alo.bg/obiavi/imoti-naemi/apartamenti-stai/`
- Next step already recorded: Run the stalled category-targeted continuation and confirm apartment sale/rent detail capture from `alo.bg/obiavi/...` pages.
- What to automate better:
  - Repair category entrypoints first, then validate one stable detail-URL family before broad pagination.
  - Run product-by-product detail fetch with full-gallery download enabled from the first successful item.
  - Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.

### BulgarianProperties

- Tier: `1`
- URL: https://www.bulgarianproperties.bg/
- Access/legal: `html` / `public_crawl_with_review`
- Declared website offering: `sale, long_term_rent, land, new_build`
- Estimated active items on website: `12000`
- Confirmed landed active items in current corpus: `249`
- Progress vs estimated site scale: `2.1%`
- Progress vs 100-item benchmark: `100.0%`
- Completeness: description `249/249` (100.0%), photo URLs `249/249` (100.0%), readable local photos `249/249` (100.0%)
- Declared intent coverage: `2/2` (100.0%) from `long_term_rent, sale`
- Services landed: long_term_rent=3, sale=246
- Property categories landed: apartment=93, house=34, land=10, office=4, unknown=108
- Fields captured most often: description 249/249, image_urls 249/249, readable_photos 249/249
- Current state: High-volume corpus on disk
- Method used now: conservative crawl using stable reference IDs
- How the list is organized: Listings are organized by product/category buckets or broad sale/rent archives; apartment recovery is best from category pages instead of the home page.
- Full-list strategy: Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media.
- Detail-page requirement: detail page required
- Detail URL pattern: `bulgarianproperties\.com/.+AD\d+BG`
- Discovery entrypoints: `https://www.bulgarianproperties.com/properties_for_sale_in_Bulgaria/index.html; https://www.bulgarianproperties.com/properties_for_rent_in_Bulgaria/index.html; https://www.bulgarianproperties.com/land_for_sale_in_Bulgaria/index.html; https://www.bulgarianproperties.com/1-bedroom_apartments_in_Bulgaria/index.html; https://www.bulgarianproperties.com/2-bedroom_apartments_in_Bulgaria/index.html; https://www.bulgarianproperties.com/3-bedroom_apartments_in_Bulgaria/index.html; https://www.bulgarianproperties.com/houses_in_Bulgaria/index.html`
- Apartment entrypoints: `https://www.bulgarianproperties.com/1-bedroom_apartments_in_Bulgaria/index.html; https://www.bulgarianproperties.com/2-bedroom_apartments_in_Bulgaria/index.html; https://www.bulgarianproperties.com/3-bedroom_apartments_in_Bulgaria/index.html`
- Next step already recorded: Continue category-by-category refreshes and push the file-backed corpus into PostgreSQL for `S1-18` evidence.
- What to automate better:
  - Keep category-first discovery and push every card into a detail-page queue; do not rely on homepage sampling.
  - Improve item classification with title heuristics, structured-data parsing, and URL-path category mapping.

### Homes.bg

- Tier: `1`
- URL: https://www.homes.bg/
- Access/legal: `html` / `public_crawl_with_review`
- Declared website offering: `sale, long_term_rent, land`
- Estimated active items on website: `120000`
- Confirmed landed active items in current corpus: `37`
- Progress vs estimated site scale: `0.0%`
- Progress vs 100-item benchmark: `37.0%`
- Completeness: description `37/37` (100.0%), photo URLs `36/37` (97.3%), readable local photos `20/37` (54.1%)
- Declared intent coverage: `1/2` (50.0%) from `sale`
- Services landed: sale=37
- Property categories landed: apartment=37
- Fields captured most often: description 37/37, image_urls 36/37, readable_photos 20/37
- Current state: Partial corpus on disk
- Method used now: server-rendered HTML crawl
- How the list is organized: Apartment feed is discovered from Homes.bg JSON API result pages, then each card points to an HTML detail page.
- Full-list strategy: Loop `offerType` sale/rent and city scopes, paginate API responses until empty, collect `viewHref`, then fetch each detail page for full text, photos, and structured data.
- Detail-page requirement: detail page required
- Detail URL pattern: `not mapped yet`
- Discovery entrypoints: `https://www.homes.bg/`
- Next step already recorded: Expand beyond the current apartment-heavy subset by widening the API scopes and continuing city pagination.
- What to automate better:
  - Keep category-first discovery and push every card into a detail-page queue; do not rely on homepage sampling.
  - Normalize gallery extraction so each item attempts the full reachable photo set, not only the lead image.
  - Add image URL normalization, decode validation, and re-download retries for unreadable or lazy-loaded media.
  - Expand intent coverage by crawling explicit sale and rent bucket pages separately and tracking them as independent queues.
  - Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.

### imot.bg

- Tier: `1`
- URL: https://www.imot.bg/
- Access/legal: `html` / `public_crawl_with_review`
- Declared website offering: `sale, long_term_rent, land, new_build`
- Estimated active items on website: `200000`
- Confirmed landed active items in current corpus: `261`
- Progress vs estimated site scale: `0.1%`
- Progress vs 100-item benchmark: `100.0%`
- Completeness: description `261/261` (100.0%), photo URLs `261/261` (100.0%), readable local photos `1/261` (0.4%)
- Declared intent coverage: `1/2` (50.0%) from `sale`
- Services landed: sale=261
- Property categories landed: unknown=261
- Fields captured most often: city 261/261, description 261/261, image_urls 261/261, readable_photos 1/261
- Current state: High-volume corpus on disk
- Method used now: respectful crawl or partnership feed
- How the list is organized: Apartment and other property grids live on city+intent listing pages; detail pages are `obiava-*` URLs.
- Full-list strategy: Walk city and intent search pages, increment `/p-{page}` until no new URLs, normalize `obiava-*` detail URLs, then parse each detail page.
- Detail-page requirement: detail page required
- Detail URL pattern: `not mapped yet`
- Discovery entrypoints: `https://www.imot.bg/`
- Next step already recorded: Improve item classification and image download completeness; the volume is present but category precision is weak.
- What to automate better:
  - Keep category-first discovery and push every card into a detail-page queue; do not rely on homepage sampling.
  - Add image URL normalization, decode validation, and re-download retries for unreadable or lazy-loaded media.
  - Improve item classification with title heuristics, structured-data parsing, and URL-path category mapping.
  - Expand intent coverage by crawling explicit sale and rent bucket pages separately and tracking them as independent queues.

### imoti.net

- Tier: `1`
- URL: https://www.imoti.net/
- Access/legal: `headless` / `legal_review_required`
- Declared website offering: `sale, long_term_rent, land, new_build`
- Estimated active items on website: `90000`
- Confirmed landed active items in current corpus: `0`
- Progress vs estimated site scale: `0.0%`
- Progress vs 100-item benchmark: `0.0%`
- Completeness: description `0/0` (0.0%), photo URLs `0/0` (0.0%), readable local photos `0/0` (0.0%)
- Declared intent coverage: `0/2` (0.0%) from `none landed yet`
- Services landed: none
- Property categories landed: none
- Fields captured most often: none captured yet
- Current state: Legal review required
- Method used now: partnership first, headless as fallback
- How the list is organized: Likely JS-heavy result grid or map-first browse flow.
- Full-list strategy: Trace entry pages and XHR calls first, then decide between browser automation and lower-level API extraction.
- Detail-page requirement: detail page required
- Detail URL pattern: `not mapped yet`
- Discovery entrypoints: `https://www.imoti.net/`
- Next step already recorded: Run a legal/access review before new live work, then choose headless tracing or partner route.
- What to automate better:
  - Repair category entrypoints first, then validate one stable detail-URL family before broad pagination.
  - Run product-by-product detail fetch with full-gallery download enabled from the first successful item.
  - Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.

### LUXIMMO

- Tier: `1`
- URL: https://www.luximmo.bg/
- Access/legal: `html` / `public_crawl_with_review`
- Declared website offering: `sale, long_term_rent, land, new_build`
- Estimated active items on website: `4000`
- Confirmed landed active items in current corpus: `15`
- Progress vs estimated site scale: `0.4%`
- Progress vs 100-item benchmark: `15.0%`
- Completeness: description `13/15` (86.7%), photo URLs `15/15` (100.0%), readable local photos `15/15` (100.0%)
- Declared intent coverage: `1/2` (50.0%) from `sale`
- Services landed: sale=15
- Property categories landed: apartment=10, unknown=5
- Fields captured most often: image_urls 15/15, readable_photos 15/15, description 13/15, price 2/15
- Current state: Partial corpus on disk
- Method used now: careful crawl using stable luxury listing reference IDs
- How the list is organized: Listings are organized by product/category buckets or broad sale/rent archives; apartment recovery is best from category pages instead of the home page.
- Full-list strategy: Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media.
- Detail-page requirement: detail page required
- Detail URL pattern: `luximmo\.bg/.+-\d{5,}-[^\"'<> ]+\.html(?:[?#][^\"'<> ]*)?$`
- Discovery entrypoints: `https://www.luximmo.bg/apartamenti/`
- Apartment entrypoints: `https://www.luximmo.bg/apartamenti/`
- Next step already recorded: Close the text gap on detail pages before widening source coverage.
- What to automate better:
  - Keep category-first discovery and push every card into a detail-page queue; do not rely on homepage sampling.
  - Add detail-page fallback extraction for missing descriptions and keep raw HTML for retries.
  - Improve item classification with title heuristics, structured-data parsing, and URL-path category mapping.
  - Expand intent coverage by crawling explicit sale and rent bucket pages separately and tracking them as independent queues.
  - Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.

### OLX.bg

- Tier: `1`
- URL: https://www.olx.bg/
- Access/legal: `official_api` / `official_api_allowed`
- Declared website offering: `sale, long_term_rent, land, new_build`
- Estimated active items on website: `45000`
- Confirmed landed active items in current corpus: `249`
- Progress vs estimated site scale: `0.6%`
- Progress vs 100-item benchmark: `100.0%`
- Completeness: description `249/249` (100.0%), photo URLs `249/249` (100.0%), readable local photos `249/249` (100.0%)
- Declared intent coverage: `2/2` (100.0%) from `long_term_rent, sale`
- Services landed: long_term_rent=117, sale=132
- Property categories landed: apartment=170, house=25, land=24, office=13, unknown=17
- Fields captured most often: description 249/249, image_urls 249/249, price 249/249, readable_photos 249/249
- Current state: High-volume corpus on disk
- Method used now: official developer API first
- How the list is organized: Listings are organized by product/category buckets or broad sale/rent archives; apartment recovery is best from category pages instead of the home page.
- Full-list strategy: Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media.
- Detail-page requirement: detail page required
- Detail URL pattern: `olx\.bg/d/ad/`
- Discovery entrypoints: `https://www.olx.bg/nedvizhimi-imoti/`
- Next step already recorded: Continue category-by-category refreshes and push the file-backed corpus into PostgreSQL for `S1-18` evidence.
- What to automate better:
  - Keep category-first discovery and push every card into a detail-page queue; do not rely on homepage sampling.

### property.bg

- Tier: `1`
- URL: https://www.property.bg/
- Access/legal: `html` / `public_crawl_with_review`
- Declared website offering: `sale, long_term_rent, land, new_build`
- Estimated active items on website: `10000`
- Confirmed landed active items in current corpus: `15`
- Progress vs estimated site scale: `0.1%`
- Progress vs 100-item benchmark: `15.0%`
- Completeness: description `15/15` (100.0%), photo URLs `15/15` (100.0%), readable local photos `15/15` (100.0%)
- Declared intent coverage: `1/2` (50.0%) from `sale`
- Services landed: sale=15
- Property categories landed: apartment=12, unknown=3
- Fields captured most often: description 15/15, image_urls 15/15, readable_photos 15/15
- Current state: Partial corpus on disk
- Method used now: targeted listing-page crawl
- How the list is organized: Listings are organized by product/category buckets or broad sale/rent archives; apartment recovery is best from category pages instead of the home page.
- Full-list strategy: Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media.
- Detail-page requirement: detail page required
- Detail URL pattern: `property\.bg/property-\d{5,}(?:[-/][^\"'<> ]*)?`
- Discovery entrypoints: `https://www.property.bg/bulgaria/apartments/; https://www.property.bg/sales/bulgaria/selection/; https://www.property.bg/rentals/bulgaria/selection/`
- Apartment entrypoints: `https://www.property.bg/bulgaria/apartments/`
- Next step already recorded: Continue category-by-category refreshes and push the file-backed corpus into PostgreSQL for `S1-18` evidence.
- What to automate better:
  - Keep category-first discovery and push every card into a detail-page queue; do not rely on homepage sampling.
  - Expand intent coverage by crawling explicit sale and rent bucket pages separately and tracking them as independent queues.
  - Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.

### SUPRIMMO

- Tier: `1`
- URL: https://www.suprimmo.bg/
- Access/legal: `html` / `public_crawl_with_review`
- Declared website offering: `sale, long_term_rent, land, new_build`
- Estimated active items on website: `15000`
- Confirmed landed active items in current corpus: `12`
- Progress vs estimated site scale: `0.1%`
- Progress vs 100-item benchmark: `12.0%`
- Completeness: description `12/12` (100.0%), photo URLs `12/12` (100.0%), readable local photos `12/12` (100.0%)
- Declared intent coverage: `1/2` (50.0%) from `sale`
- Services landed: sale=12
- Property categories landed: apartment=10, unknown=2
- Fields captured most often: description 12/12, image_urls 12/12, readable_photos 12/12, price 9/12
- Current state: Partial corpus on disk
- Method used now: crawl listings and unify group reference IDs
- How the list is organized: Listings are organized by product/category buckets or broad sale/rent archives; apartment recovery is best from category pages instead of the home page.
- Full-list strategy: Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media.
- Detail-page requirement: detail page required
- Detail URL pattern: `suprimmo\.bg/imot-\d{5,}(?:[-/][^\"'<> ]*)?`
- Discovery entrypoints: `https://www.suprimmo.bg/bulgaria/apartamenti/; https://www.suprimmo.bg/bulgaria/kushti-vili/; https://www.suprimmo.bg/bulgaria/partseli/; https://www.suprimmo.bg/prodajba/bulgaria/selectsya/; https://www.suprimmo.bg/naem/bulgaria/selectsya/`
- Apartment entrypoints: `https://www.suprimmo.bg/bulgaria/apartamenti/`
- Next step already recorded: Continue category-by-category refreshes and push the file-backed corpus into PostgreSQL for `S1-18` evidence.
- What to automate better:
  - Keep category-first discovery and push every card into a detail-page queue; do not rely on homepage sampling.
  - Expand intent coverage by crawling explicit sale and rent bucket pages separately and tracking them as independent queues.
  - Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.

### ApartmentsBulgaria.com

- Tier: `2`
- URL: https://www.apartmentsbulgaria.bg/
- Access/legal: `headless` / `public_crawl_with_review`
- Declared website offering: `short_term_rent`
- Estimated active items on website: `1800`
- Confirmed landed active items in current corpus: `0`
- Progress vs estimated site scale: `0.0%`
- Progress vs 100-item benchmark: `0.0%`
- Completeness: description `0/0` (0.0%), photo URLs `0/0` (0.0%), readable local photos `0/0` (0.0%)
- Declared intent coverage: `0/1` (0.0%) from `none landed yet`
- Services landed: none
- Property categories landed: none
- Fields captured most often: none captured yet
- Current state: Planned / no landed corpus
- Method used now: direct booking integration or careful crawl
- How the list is organized: Short-term-rent catalog; likely property-type and resort pages rather than one national apartment feed.
- Full-list strategy: Map resort/category pages first, then enumerate property cards and fetch each item page for room mix, amenities, and gallery.
- Detail-page requirement: Detail page required for photos, amenities, and availability-style metadata.
- Detail URL pattern: `not mapped yet`
- Discovery entrypoints: `https://www.apartmentsbulgaria.bg/`
- Next step already recorded: Map apartment/category entry pages first, capture fixtures, then build detail-page recovery.
- What to automate better:
  - Repair category entrypoints first, then validate one stable detail-URL family before broad pagination.
  - Run product-by-product detail fetch with full-gallery download enabled from the first successful item.
  - Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.

### Bazar.bg

- Tier: `2`
- URL: https://bazar.bg/
- Access/legal: `html` / `public_crawl_with_review`
- Declared website offering: `sale, long_term_rent, land`
- Estimated active items on website: `8000`
- Confirmed landed active items in current corpus: `250`
- Progress vs estimated site scale: `3.1%`
- Progress vs 100-item benchmark: `100.0%`
- Completeness: description `250/250` (100.0%), photo URLs `250/250` (100.0%), readable local photos `249/250` (99.6%)
- Declared intent coverage: `2/2` (100.0%) from `long_term_rent, sale`
- Services landed: long_term_rent=25, sale=225
- Property categories landed: apartment=204, office=1, unknown=45
- Fields captured most often: description 250/250, image_urls 250/250, price 250/250, readable_photos 249/250
- Current state: High-volume corpus on disk
- Method used now: limited HTML crawl
- How the list is organized: Listings are organized by product/category buckets or broad sale/rent archives; apartment recovery is best from category pages instead of the home page.
- Full-list strategy: Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media.
- Detail-page requirement: detail page required
- Detail URL pattern: `bazar\.bg/obiava-\d{5,}`
- Discovery entrypoints: `https://bazar.bg/obiavi/apartamenti; https://bazar.bg/obiavi/kashti-i-vili; https://bazar.bg/obiavi/zemya; https://bazar.bg/obiavi/garazhi-i-parkoingi`
- Apartment entrypoints: `https://bazar.bg/obiavi/apartamenti`
- Next step already recorded: Improve local media downloads and readability before the next large batch.
- What to automate better:
  - Keep category-first discovery and push every card into a detail-page queue; do not rely on homepage sampling.
  - Add image URL normalization, decode validation, and re-download retries for unreadable or lazy-loaded media.

### Domaza

- Tier: `2`
- URL: https://www.domaza.bg/
- Access/legal: `html` / `public_crawl_with_review`
- Declared website offering: `sale, long_term_rent, short_term_rent, land, new_build`
- Estimated active items on website: `22000`
- Confirmed landed active items in current corpus: `0`
- Progress vs estimated site scale: `0.0%`
- Progress vs 100-item benchmark: `0.0%`
- Completeness: description `0/0` (0.0%), photo URLs `0/0` (0.0%), readable local photos `0/0` (0.0%)
- Declared intent coverage: `0/3` (0.0%) from `none landed yet`
- Services landed: none
- Property categories landed: none
- Fields captured most often: none captured yet
- Current state: Configured, zero landed corpus
- Method used now: crawl with language canonicalization
- How the list is organized: Listings are organized by product/category buckets or broad sale/rent archives; apartment recovery is best from category pages instead of the home page.
- Full-list strategy: Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media.
- Detail-page requirement: detail page required
- Detail URL pattern: `domaza\.(bg|biz)/.+ID\d+`
- Discovery entrypoints: `https://www.domaza.bg/property/index/search/1/s/572da6146f10beb4bf6333d75039731a4d2b9902; https://www.domaza.bg/property/index/search/1/s/c8a3ad4db8f37d4e8b31fe9db66bc4d1f537ba5a; https://www.domaza.bg/property/index/search/1/s/e8780bcda8fa201940f1ce87e404f870d0c5c3fc`
- Next step already recorded: Map the language-canonical search entrypoints and recover the first working detail URL family before broad pagination.
- What to automate better:
  - Repair category entrypoints first, then validate one stable detail-URL family before broad pagination.
  - Run product-by-product detail fetch with full-gallery download enabled from the first successful item.
  - Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.

### Holding Group Real Estate

- Tier: `2`
- URL: https://holdinggroup.bg/
- Access/legal: `html` / `public_crawl_with_review`
- Declared website offering: `sale, long_term_rent, land, new_build`
- Estimated active items on website: `3000`
- Confirmed landed active items in current corpus: `0`
- Progress vs estimated site scale: `0.0%`
- Progress vs 100-item benchmark: `0.0%`
- Completeness: description `0/0` (0.0%), photo URLs `0/0` (0.0%), readable local photos `0/0` (0.0%)
- Declared intent coverage: `0/2` (0.0%) from `none landed yet`
- Services landed: none
- Property categories landed: none
- Fields captured most often: none captured yet
- Current state: Planned / no landed corpus
- Method used now: crawl direct site plus dedupe against portal syndication
- How the list is organized: Agency inventory organized around direct sale/project pages, likely city and project buckets.
- Full-list strategy: Start from city/project category pages, dedupe against syndication, then fetch each offer detail page.
- Detail-page requirement: Detail page required.
- Detail URL pattern: `not mapped yet`
- Discovery entrypoints: `https://holdinggroup.bg/`
- Next step already recorded: Map apartment/category entry pages first, capture fixtures, then build detail-page recovery.
- What to automate better:
  - Repair category entrypoints first, then validate one stable detail-URL family before broad pagination.
  - Run product-by-product detail fetch with full-gallery download enabled from the first successful item.
  - Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.

### Home2U

- Tier: `2`
- URL: https://home2u.bg/
- Access/legal: `html` / `public_crawl_with_review`
- Declared website offering: `sale, long_term_rent, land, new_build`
- Estimated active items on website: `6000`
- Confirmed landed active items in current corpus: `0`
- Progress vs estimated site scale: `0.0%`
- Progress vs 100-item benchmark: `0.0%`
- Completeness: description `0/0` (0.0%), photo URLs `0/0` (0.0%), readable local photos `0/0` (0.0%)
- Declared intent coverage: `0/2` (0.0%) from `none landed yet`
- Services landed: none
- Property categories landed: none
- Fields captured most often: none captured yet
- Current state: Configured, zero landed corpus
- Method used now: templated HTML parser
- How the list is organized: Listings are organized by product/category buckets or broad sale/rent archives; apartment recovery is best from category pages instead of the home page.
- Full-list strategy: Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media.
- Detail-page requirement: detail page required
- Detail URL pattern: `home2u\.bg/.+-[a-z0-9]{5,}`
- Discovery entrypoints: `https://home2u.bg/nedvizhimi-imoti-sofia/; https://home2u.bg/nedvizhimi-imoti-varna/; https://home2u.bg/nedvizhimi-imoti-burgas/; https://home2u.bg/nedvizhimi-imoti-plovdiv/; https://home2u.bg/apartamenti-pod-naem-sofia/; https://home2u.bg/apartamenti-pod-naem-varna/`
- Apartment entrypoints: `https://home2u.bg/nedvizhimi-imoti-sofia/; https://home2u.bg/nedvizhimi-imoti-varna/; https://home2u.bg/nedvizhimi-imoti-burgas/; https://home2u.bg/nedvizhimi-imoti-plovdiv/; https://home2u.bg/apartamenti-pod-naem-sofia/; https://home2u.bg/apartamenti-pod-naem-varna/`
- Next step already recorded: Repair the city landing pages into stable listing archives, then fetch detail pages product by product.
- What to automate better:
  - Repair category entrypoints first, then validate one stable detail-URL family before broad pagination.
  - Run product-by-product detail fetch with full-gallery download enabled from the first successful item.
  - Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.

### Imoteka.bg

- Tier: `2`
- URL: https://imoteka.bg/
- Access/legal: `headless` / `legal_review_required`
- Declared website offering: `sale, long_term_rent, land, new_build`
- Estimated active items on website: `14000`
- Confirmed landed active items in current corpus: `0`
- Progress vs estimated site scale: `0.0%`
- Progress vs 100-item benchmark: `0.0%`
- Completeness: description `0/0` (0.0%), photo URLs `0/0` (0.0%), readable local photos `0/0` (0.0%)
- Declared intent coverage: `0/2` (0.0%) from `none landed yet`
- Services landed: none
- Property categories landed: none
- Fields captured most often: none captured yet
- Current state: Legal review required
- Method used now: partnership/licensed feed preferred; headless only after legal clearance
- How the list is organized: Likely JS-heavy agency portal with filtered grids and campaign/new-build emphasis.
- Full-list strategy: Legal review first, then browser trace category/XHR flows before parser work.
- Detail-page requirement: Detail page required.
- Detail URL pattern: `not mapped yet`
- Discovery entrypoints: `https://imoteka.bg/`
- Next step already recorded: Run a legal/access review before new live work, then choose headless tracing or partner route.
- What to automate better:
  - Repair category entrypoints first, then validate one stable detail-URL family before broad pagination.
  - Run product-by-product detail fetch with full-gallery download enabled from the first successful item.
  - Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.

### Imoti.info

- Tier: `2`
- URL: https://imoti.info/
- Access/legal: `partner_feed` / `licensing_required`
- Declared website offering: `sale, long_term_rent, land, new_build`
- Estimated active items on website: `25000`
- Confirmed landed active items in current corpus: `0`
- Progress vs estimated site scale: `0.0%`
- Progress vs 100-item benchmark: `0.0%`
- Completeness: description `0/0` (0.0%), photo URLs `0/0` (0.0%), readable local photos `0/0` (0.0%)
- Declared intent coverage: `0/2` (0.0%) from `none landed yet`
- Services landed: none
- Property categories landed: none
- Fields captured most often: none captured yet
- Current state: Licensing required
- Method used now: licensing or partnership first; fixture-only parser research until approved
- How the list is organized: Partner-feed style marketplace; browsing exists but licensing governs commercial extraction.
- Full-list strategy: Do not crawl broadly. Seek licensing or partner export before item recovery.
- Detail-page requirement: Would require detail pages or feed payloads, but licensing is the first gate.
- Detail URL pattern: `not mapped yet`
- Discovery entrypoints: `https://imoti.info/`
- Next step already recorded: Do not broaden crawling. Move this source through licensing or partner-feed negotiation first.
- What to automate better:
  - Repair category entrypoints first, then validate one stable detail-URL family before broad pagination.
  - Run product-by-product detail fetch with full-gallery download enabled from the first successful item.
  - Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.

### Indomio.bg

- Tier: `2`
- URL: https://www.indomio.bg/
- Access/legal: `headless` / `public_crawl_with_review`
- Declared website offering: `sale, long_term_rent, land`
- Estimated active items on website: `7000`
- Confirmed landed active items in current corpus: `0`
- Progress vs estimated site scale: `0.0%`
- Progress vs 100-item benchmark: `0.0%`
- Completeness: description `0/0` (0.0%), photo URLs `0/0` (0.0%), readable local photos `0/0` (0.0%)
- Declared intent coverage: `0/2` (0.0%) from `none landed yet`
- Services landed: none
- Property categories landed: none
- Fields captured most often: none captured yet
- Current state: Planned / no landed corpus
- Method used now: hybrid HTML/headless crawler
- How the list is organized: Portal-style result grids with filterable categories and likely JS-assisted navigation.
- Full-list strategy: Map category/city entry pages, inspect XHR if present, then reconcile to detail pages.
- Detail-page requirement: Detail page required.
- Detail URL pattern: `not mapped yet`
- Discovery entrypoints: `https://www.indomio.bg/`
- Next step already recorded: Map apartment/category entry pages first, capture fixtures, then build detail-page recovery.
- What to automate better:
  - Repair category entrypoints first, then validate one stable detail-URL family before broad pagination.
  - Run product-by-product detail fetch with full-gallery download enabled from the first successful item.
  - Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.

### Lions Group

- Tier: `2`
- URL: https://lionsgroup.bg/
- Access/legal: `html` / `public_crawl_with_review`
- Declared website offering: `sale, long_term_rent, land, new_build`
- Estimated active items on website: `2500`
- Confirmed landed active items in current corpus: `0`
- Progress vs estimated site scale: `0.0%`
- Progress vs 100-item benchmark: `0.0%`
- Completeness: description `0/0` (0.0%), photo URLs `0/0` (0.0%), readable local photos `0/0` (0.0%)
- Declared intent coverage: `0/2` (0.0%) from `none landed yet`
- Services landed: none
- Property categories landed: none
- Fields captured most often: none captured yet
- Current state: Planned / no landed corpus
- Method used now: server-rendered listing crawl
- How the list is organized: Agency site with city/project-driven inventory sections.
- Full-list strategy: Enumerate listing archives and project buckets, then fetch each listing page.
- Detail-page requirement: Detail page required.
- Detail URL pattern: `not mapped yet`
- Discovery entrypoints: `https://lionsgroup.bg/`
- Next step already recorded: Map apartment/category entry pages first, capture fixtures, then build detail-page recovery.
- What to automate better:
  - Repair category entrypoints first, then validate one stable detail-URL family before broad pagination.
  - Run product-by-product detail fetch with full-gallery download enabled from the first successful item.
  - Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.

### Pochivka.bg

- Tier: `2`
- URL: https://pochivka.bg/
- Access/legal: `html` / `public_crawl_with_review`
- Declared website offering: `short_term_rent`
- Estimated active items on website: `5000`
- Confirmed landed active items in current corpus: `0`
- Progress vs estimated site scale: `0.0%`
- Progress vs 100-item benchmark: `0.0%`
- Completeness: description `0/0` (0.0%), photo URLs `0/0` (0.0%), readable local photos `0/0` (0.0%)
- Declared intent coverage: `0/1` (0.0%) from `none landed yet`
- Services landed: none
- Property categories landed: none
- Fields captured most often: none captured yet
- Current state: Planned / no landed corpus
- Method used now: partnership or limited travel-catalog crawl
- How the list is organized: Travel catalog rather than classic sale feed; apartment inventory is hospitality-oriented.
- Full-list strategy: Treat as STR intelligence. Traverse resort/location catalogs to item pages.
- Detail-page requirement: Detail page required.
- Detail URL pattern: `not mapped yet`
- Discovery entrypoints: `https://pochivka.bg/`
- Next step already recorded: Map apartment/category entry pages first, capture fixtures, then build detail-page recovery.
- What to automate better:
  - Repair category entrypoints first, then validate one stable detail-URL family before broad pagination.
  - Run product-by-product detail fetch with full-gallery download enabled from the first successful item.
  - Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.

### realestates.bg

- Tier: `2`
- URL: https://en.realestates.bg/
- Access/legal: `html` / `public_crawl_with_review`
- Declared website offering: `sale, long_term_rent, land`
- Estimated active items on website: `6000`
- Confirmed landed active items in current corpus: `0`
- Progress vs estimated site scale: `0.0%`
- Progress vs 100-item benchmark: `0.0%`
- Completeness: description `0/0` (0.0%), photo URLs `0/0` (0.0%), readable local photos `0/0` (0.0%)
- Declared intent coverage: `0/2` (0.0%) from `none landed yet`
- Services landed: none
- Property categories landed: none
- Fields captured most often: none captured yet
- Current state: Planned / no landed corpus
- Method used now: scope-limited HTML crawl and dedupe against alo.bg
- How the list is organized: Foreign-facing portal layer related to alo.bg; likely mirrored listing pages and translated categories.
- Full-list strategy: Scope crawl carefully and dedupe aggressively against alo.bg by URL/title/price/media hash.
- Detail-page requirement: Detail page required.
- Detail URL pattern: `not mapped yet`
- Discovery entrypoints: `https://en.realestates.bg/`
- Next step already recorded: Map apartment/category entry pages first, capture fixtures, then build detail-page recovery.
- What to automate better:
  - Repair category entrypoints first, then validate one stable detail-URL family before broad pagination.
  - Run product-by-product detail fetch with full-gallery download enabled from the first successful item.
  - Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.

### Realistimo

- Tier: `2`
- URL: https://realistimo.com/
- Access/legal: `headless` / `public_crawl_with_review`
- Declared website offering: `sale, long_term_rent, land, new_build`
- Estimated active items on website: `4500`
- Confirmed landed active items in current corpus: `0`
- Progress vs estimated site scale: `0.0%`
- Progress vs 100-item benchmark: `0.0%`
- Completeness: description `0/0` (0.0%), photo URLs `0/0` (0.0%), readable local photos `0/0` (0.0%)
- Declared intent coverage: `0/2` (0.0%) from `none landed yet`
- Services landed: none
- Property categories landed: none
- Fields captured most often: none captured yet
- Current state: Planned / no landed corpus
- Method used now: HTML crawl with map-filter fallback
- How the list is organized: Map-led browsing with geo filters and listing cards.
- Full-list strategy: Map initial browse endpoints, discover backing XHR or map payloads, then fetch detail pages.
- Detail-page requirement: Detail page required.
- Detail URL pattern: `not mapped yet`
- Discovery entrypoints: `https://realistimo.com/`
- Next step already recorded: Map apartment/category entry pages first, capture fixtures, then build detail-page recovery.
- What to automate better:
  - Repair category entrypoints first, then validate one stable detail-URL family before broad pagination.
  - Run product-by-product detail fetch with full-gallery download enabled from the first successful item.
  - Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.

### Rentica.bg

- Tier: `2`
- URL: https://rentica.bg/
- Access/legal: `html` / `public_crawl_with_review`
- Declared website offering: `long_term_rent`
- Estimated active items on website: `1200`
- Confirmed landed active items in current corpus: `0`
- Progress vs estimated site scale: `0.0%`
- Progress vs 100-item benchmark: `0.0%`
- Completeness: description `0/0` (0.0%), photo URLs `0/0` (0.0%), readable local photos `0/0` (0.0%)
- Declared intent coverage: `0/1` (0.0%) from `none landed yet`
- Services landed: none
- Property categories landed: none
- Fields captured most often: none captured yet
- Current state: Planned / no landed corpus
- Method used now: rent-only HTML parser
- How the list is organized: Rent-specialist listing grid, probably city-first and apartment-heavy.
- Full-list strategy: Target city rental pages, paginate deeply, then fetch item pages.
- Detail-page requirement: Detail page required.
- Detail URL pattern: `not mapped yet`
- Discovery entrypoints: `https://rentica.bg/`
- Next step already recorded: Map apartment/category entry pages first, capture fixtures, then build detail-page recovery.
- What to automate better:
  - Repair category entrypoints first, then validate one stable detail-URL family before broad pagination.
  - Run product-by-product detail fetch with full-gallery download enabled from the first successful item.
  - Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.

### Svobodni-kvartiri.com

- Tier: `2`
- URL: https://svobodni-kvartiri.com/
- Access/legal: `html` / `public_crawl_with_review`
- Declared website offering: `long_term_rent, short_term_rent`
- Estimated active items on website: `3500`
- Confirmed landed active items in current corpus: `0`
- Progress vs estimated site scale: `0.0%`
- Progress vs 100-item benchmark: `0.0%`
- Completeness: description `0/0` (0.0%), photo URLs `0/0` (0.0%), readable local photos `0/0` (0.0%)
- Declared intent coverage: `0/2` (0.0%) from `none landed yet`
- Services landed: none
- Property categories landed: none
- Fields captured most often: none captured yet
- Current state: Planned / no landed corpus
- Method used now: deep pagination crawl by city scope
- How the list is organized: Deep city pagination focused on rentals, rooms, and worker/student supply.
- Full-list strategy: Paginate per city and rental type, then fetch each item page.
- Detail-page requirement: Detail page required.
- Detail URL pattern: `not mapped yet`
- Discovery entrypoints: `https://svobodni-kvartiri.com/`
- Next step already recorded: Map apartment/category entry pages first, capture fixtures, then build detail-page recovery.
- What to automate better:
  - Repair category entrypoints first, then validate one stable detail-URL family before broad pagination.
  - Run product-by-product detail fetch with full-gallery download enabled from the first successful item.
  - Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.

### Unique Estates

- Tier: `2`
- URL: https://ues.bg/
- Access/legal: `html` / `public_crawl_with_review`
- Declared website offering: `sale, long_term_rent, new_build`
- Estimated active items on website: `2000`
- Confirmed landed active items in current corpus: `0`
- Progress vs estimated site scale: `0.0%`
- Progress vs 100-item benchmark: `0.0%`
- Completeness: description `0/0` (0.0%), photo URLs `0/0` (0.0%), readable local photos `0/0` (0.0%)
- Declared intent coverage: `0/2` (0.0%) from `none landed yet`
- Services landed: none
- Property categories landed: none
- Fields captured most often: none captured yet
- Current state: Planned / no landed corpus
- Method used now: luxury listing crawler
- How the list is organized: Luxury agency catalog with sale/rent/new-build buckets.
- Full-list strategy: Enumerate category archives and project/luxury pages, then item pages.
- Detail-page requirement: Detail page required.
- Detail URL pattern: `not mapped yet`
- Discovery entrypoints: `https://ues.bg/`
- Next step already recorded: Map apartment/category entry pages first, capture fixtures, then build detail-page recovery.
- What to automate better:
  - Repair category entrypoints first, then validate one stable detail-URL family before broad pagination.
  - Run product-by-product detail fetch with full-gallery download enabled from the first successful item.
  - Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.

### Vila.bg

- Tier: `2`
- URL: https://vila.bg/
- Access/legal: `html` / `public_crawl_with_review`
- Declared website offering: `short_term_rent`
- Estimated active items on website: `4000`
- Confirmed landed active items in current corpus: `0`
- Progress vs estimated site scale: `0.0%`
- Progress vs 100-item benchmark: `0.0%`
- Completeness: description `0/0` (0.0%), photo URLs `0/0` (0.0%), readable local photos `0/0` (0.0%)
- Declared intent coverage: `0/1` (0.0%) from `none landed yet`
- Services landed: none
- Property categories landed: none
- Fields captured most often: none captured yet
- Current state: Planned / no landed corpus
- Method used now: partnership or limited catalog crawl
- How the list is organized: Vacation and villa catalog, likely organized by destination rather than strict apartment taxonomy.
- Full-list strategy: Treat as resort/vacation inventory; traverse destination pages to item pages.
- Detail-page requirement: Detail page required.
- Detail URL pattern: `not mapped yet`
- Discovery entrypoints: `https://vila.bg/`
- Next step already recorded: Map apartment/category entry pages first, capture fixtures, then build detail-page recovery.
- What to automate better:
  - Repair category entrypoints first, then validate one stable detail-URL family before broad pagination.
  - Run product-by-product detail fetch with full-gallery download enabled from the first successful item.
  - Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.

### Yavlena

- Tier: `2`
- URL: https://www.yavlena.com/
- Access/legal: `html` / `public_crawl_with_review`
- Declared website offering: `sale, long_term_rent`
- Estimated active items on website: `9000`
- Confirmed landed active items in current corpus: `250`
- Progress vs estimated site scale: `2.8%`
- Progress vs 100-item benchmark: `100.0%`
- Completeness: description `0/250` (0.0%), photo URLs `250/250` (100.0%), readable local photos `249/250` (99.6%)
- Declared intent coverage: `1/2` (50.0%) from `sale`
- Services landed: sale=250
- Property categories landed: apartment=145, house=40, land=36, office=7, unknown=22
- Fields captured most often: image_urls 250/250, readable_photos 249/250
- Current state: High-volume corpus, description gap
- Method used now: incremental crawl with ID-based URLs
- How the list is organized: Listings are organized by product/category buckets or broad sale/rent archives; apartment recovery is best from category pages instead of the home page.
- Full-list strategy: Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media.
- Detail-page requirement: detail page required
- Detail URL pattern: `yavlena\.com/bg/\d{5,}`
- Discovery entrypoints: `https://www.yavlena.com/bg/sales; https://www.yavlena.com/bg/rentals`
- Next step already recorded: Recover detail-page descriptions for the already large on-disk corpus and keep sale buckets fresh.
- What to automate better:
  - Keep category-first discovery and push every card into a detail-page queue; do not rely on homepage sampling.
  - Add detail-page fallback extraction for missing descriptions and keep raw HTML for retries.
  - Add image URL normalization, decode validation, and re-download retries for unreadable or lazy-loaded media.
  - Expand intent coverage by crawling explicit sale and rent bucket pages separately and tracking them as independent queues.

