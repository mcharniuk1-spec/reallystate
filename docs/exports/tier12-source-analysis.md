# Tier 1-2 source analysis

Generated: 2026-04-14T13:46:10.524023+00:00

## Tier summary

- Tier 1 sources analyzed: 10
- Tier 2 sources analyzed: 17
- Primary interpretation: the repo already has strong category-entrypoint knowledge for implemented sources, but the remaining gap is detail-page recovery and DB-backed proof, not source inventory.

## Source table

| Tier | Source | Primary URL | Apartment entrypoint | Saved listings | Descriptions | Readable photo sets | Full-list strategy |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| 1 | Address.bg | https://address.bg/ | - | 43 | 43 | 0 | Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media. |
| 1 | alo.bg | https://www.alo.bg/ | https://www.alo.bg/obiavi/imoti-prodajbi/apartamenti-stai/ | 0 | 0 | 0 | Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media. |
| 1 | BulgarianProperties | https://www.bulgarianproperties.bg/ | https://www.bulgarianproperties.com/1-bedroom_apartments_in_Bulgaria/index.html | 249 | 249 | 0 | Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media. |
| 1 | Homes.bg | https://www.homes.bg/ | - | 37 | 37 | 0 | Loop `offerType` sale/rent and city scopes, paginate API responses until empty, collect `viewHref`, then fetch each detail page for full text, photos, and structured data. |
| 1 | imot.bg | https://www.imot.bg/ | - | 261 | 261 | 0 | Walk city and intent search pages, increment `/p-{page}` until no new URLs, normalize `obiava-*` detail URLs, then parse each detail page. |
| 1 | imoti.net | https://www.imoti.net/ | - | 0 | 0 | 0 | Trace entry pages and XHR calls first, then decide between browser automation and lower-level API extraction. |
| 1 | LUXIMMO | https://www.luximmo.bg/ | https://www.luximmo.bg/apartamenti/ | 15 | 13 | 0 | Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media. |
| 1 | OLX.bg | https://www.olx.bg/ | - | 249 | 249 | 0 | Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media. |
| 1 | property.bg | https://www.property.bg/ | https://www.property.bg/bulgaria/apartments/ | 15 | 15 | 0 | Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media. |
| 1 | SUPRIMMO | https://www.suprimmo.bg/ | https://www.suprimmo.bg/bulgaria/apartamenti/ | 12 | 12 | 0 | Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media. |
| 2 | ApartmentsBulgaria.com | https://www.apartmentsbulgaria.bg/ | - | 0 | 0 | 0 | Map resort/category pages first, then enumerate property cards and fetch each item page for room mix, amenities, and gallery. |
| 2 | Bazar.bg | https://bazar.bg/ | https://bazar.bg/obiavi/apartamenti | 250 | 250 | 0 | Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media. |
| 2 | Domaza | https://www.domaza.bg/ | - | 0 | 0 | 0 | Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media. |
| 2 | Holding Group Real Estate | https://holdinggroup.bg/ | - | 0 | 0 | 0 | Start from city/project category pages, dedupe against syndication, then fetch each offer detail page. |
| 2 | Home2U | https://home2u.bg/ | https://home2u.bg/nedvizhimi-imoti-sofia/ | 0 | 0 | 0 | Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media. |
| 2 | Imoteka.bg | https://imoteka.bg/ | - | 0 | 0 | 0 | Legal review first, then browser trace category/XHR flows before parser work. |
| 2 | Imoti.info | https://imoti.info/ | - | 0 | 0 | 0 | Do not crawl broadly. Seek licensing or partner export before item recovery. |
| 2 | Indomio.bg | https://www.indomio.bg/ | - | 0 | 0 | 0 | Map category/city entry pages, inspect XHR if present, then reconcile to detail pages. |
| 2 | Lions Group | https://lionsgroup.bg/ | - | 0 | 0 | 0 | Enumerate listing archives and project buckets, then fetch each listing page. |
| 2 | Pochivka.bg | https://pochivka.bg/ | - | 0 | 0 | 0 | Treat as STR intelligence. Traverse resort/location catalogs to item pages. |
| 2 | realestates.bg | https://en.realestates.bg/ | - | 0 | 0 | 0 | Scope crawl carefully and dedupe aggressively against alo.bg by URL/title/price/media hash. |
| 2 | Realistimo | https://realistimo.com/ | - | 0 | 0 | 0 | Map initial browse endpoints, discover backing XHR or map payloads, then fetch detail pages. |
| 2 | Rentica.bg | https://rentica.bg/ | - | 0 | 0 | 0 | Target city rental pages, paginate deeply, then fetch item pages. |
| 2 | Svobodni-kvartiri.com | https://svobodni-kvartiri.com/ | - | 0 | 0 | 0 | Paginate per city and rental type, then fetch each item page. |
| 2 | Unique Estates | https://ues.bg/ | - | 0 | 0 | 0 | Enumerate category archives and project/luxury pages, then item pages. |
| 2 | Vila.bg | https://vila.bg/ | - | 0 | 0 | 0 | Treat as resort/vacation inventory; traverse destination pages to item pages. |
| 2 | Yavlena | https://www.yavlena.com/ | - | 250 | 0 | 0 | Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media. |

## Detailed source notes

### Address.bg

- Links: `https://address.bg/`
- Access/legal: `html` / `medium` / `public_crawl_with_review`
- Declared services: `sale, long_term_rent, land, new_build`
- Scraped services: `sale=43`
- Scraped categories: `apartment=29, house=8, land=3, office=2, unknown=1`
- Apartment list organization: Listings are organized by product/category buckets or broad sale/rent archives; apartment recovery is best from category pages instead of the home page.
- Discovery entrypoints: https://address.bg/sale; https://address.bg/rent; https://address.bg/sale/sofia/l4451; https://address.bg/sale/varna/l4694; https://address.bg/rent/sofia/l4451
- Apartment-focused entrypoints: not yet captured in repo
- Pagination: server-rendered pagination using suffix `?page={}`
- Detail URL pattern: `address\.bg/.+-offer\d{5,}(?:[/?#].*)?$`
- Full-list approach: Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media.
- Item-page requirement: detail page required
- Current blocker: none in current config

### alo.bg

- Links: `https://www.alo.bg/`
- Access/legal: `html` / `medium` / `public_crawl_with_review`
- Declared services: `sale, long_term_rent, short_term_rent, land, new_build`
- Scraped services: `none saved yet`
- Scraped categories: `none saved yet`
- Apartment list organization: Listings are organized by product/category buckets or broad sale/rent archives; apartment recovery is best from category pages instead of the home page.
- Discovery entrypoints: https://www.alo.bg/obiavi/imoti-prodajbi/apartamenti-stai/; https://www.alo.bg/obiavi/imoti-prodajbi/kashti-vili/; https://www.alo.bg/obiavi/imoti-prodajbi/parzeli-za-zastroiavane-investicionni-proekti/; https://www.alo.bg/obiavi/imoti-prodajbi/zemedelska-zemia-gradini-lozia-gora/; https://www.alo.bg/obiavi/imoti-naemi/apartamenti-stai/
- Apartment-focused entrypoints: https://www.alo.bg/obiavi/imoti-prodajbi/apartamenti-stai/; https://www.alo.bg/obiavi/imoti-naemi/apartamenti-stai/
- Pagination: server-rendered pagination using suffix `?page={}`
- Detail URL pattern: `alo\.bg/.+-\d{5,}(?:[/?#].*)?$`
- Full-list approach: Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media.
- Item-page requirement: detail page required
- Current blocker: connector planning exists but saved corpus is still zero

### BulgarianProperties

- Links: `https://www.bulgarianproperties.bg/`; related: `https://www.bulgarianproperties.com/`
- Access/legal: `html` / `medium` / `public_crawl_with_review`
- Declared services: `sale, long_term_rent, land, new_build`
- Scraped services: `long_term_rent=3, sale=246`
- Scraped categories: `apartment=93, house=34, land=10, office=4, unknown=108`
- Apartment list organization: Listings are organized by product/category buckets or broad sale/rent archives; apartment recovery is best from category pages instead of the home page.
- Discovery entrypoints: https://www.bulgarianproperties.com/properties_for_sale_in_Bulgaria/index.html; https://www.bulgarianproperties.com/properties_for_rent_in_Bulgaria/index.html; https://www.bulgarianproperties.com/land_for_sale_in_Bulgaria/index.html; https://www.bulgarianproperties.com/1-bedroom_apartments_in_Bulgaria/index.html; https://www.bulgarianproperties.com/2-bedroom_apartments_in_Bulgaria/index.html; https://www.bulgarianproperties.com/3-bedroom_apartments_in_Bulgaria/index.html; https://www.bulgarianproperties.com/houses_in_Bulgaria/index.html
- Apartment-focused entrypoints: https://www.bulgarianproperties.com/1-bedroom_apartments_in_Bulgaria/index.html; https://www.bulgarianproperties.com/2-bedroom_apartments_in_Bulgaria/index.html; https://www.bulgarianproperties.com/3-bedroom_apartments_in_Bulgaria/index.html
- Pagination: server-rendered pagination using suffix `?page={}`
- Detail URL pattern: `bulgarianproperties\.com/.+AD\d+BG`
- Full-list approach: Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media.
- Item-page requirement: detail page required
- Current blocker: none in current config

### Homes.bg

- Links: `https://www.homes.bg/`
- Access/legal: `html` / `medium` / `public_crawl_with_review`
- Declared services: `sale, long_term_rent, land`
- Scraped services: `sale=37`
- Scraped categories: `apartment=37`
- Apartment list organization: Apartment feed is discovered from Homes.bg JSON API result pages, then each card points to an HTML detail page.
- Discovery entrypoints: https://www.homes.bg/
- Apartment-focused entrypoints: not yet captured in repo
- Pagination: JSON API pages by `currPage`, `offerType`, and optional `city`
- Detail URL pattern: `not yet mapped`
- Full-list approach: Loop `offerType` sale/rent and city scopes, paginate API responses until empty, collect `viewHref`, then fetch each detail page for full text, photos, and structured data.
- Item-page requirement: detail page required
- Current blocker: none in current config

### imot.bg

- Links: `https://www.imot.bg/`
- Access/legal: `html` / `medium` / `public_crawl_with_review`
- Declared services: `sale, long_term_rent, land, new_build`
- Scraped services: `sale=261`
- Scraped categories: `unknown=261`
- Apartment list organization: Apartment and other property grids live on city+intent listing pages; detail pages are `obiava-*` URLs.
- Discovery entrypoints: https://www.imot.bg/
- Apartment-focused entrypoints: not yet captured in repo
- Pagination: server-rendered `/p-{page}` search pagination
- Detail URL pattern: `not yet mapped`
- Full-list approach: Walk city and intent search pages, increment `/p-{page}` until no new URLs, normalize `obiava-*` detail URLs, then parse each detail page.
- Item-page requirement: detail page required
- Current blocker: none in current config

### imoti.net

- Links: `https://www.imoti.net/`
- Access/legal: `headless` / `high` / `legal_review_required`
- Declared services: `sale, long_term_rent, land, new_build`
- Scraped services: `none saved yet`
- Scraped categories: `none saved yet`
- Apartment list organization: Likely JS-heavy result grid or map-first browse flow.
- Discovery entrypoints: https://www.imoti.net/
- Apartment-focused entrypoints: not yet captured in repo
- Pagination: browser/XHR mapping required
- Detail URL pattern: `not yet mapped`
- Full-list approach: Trace entry pages and XHR calls first, then decide between browser automation and lower-level API extraction.
- Item-page requirement: detail page required
- Current blocker: connector not yet captured in repo

### LUXIMMO

- Links: `https://www.luximmo.bg/`
- Access/legal: `html` / `medium` / `public_crawl_with_review`
- Declared services: `sale, long_term_rent, land, new_build`
- Scraped services: `sale=15`
- Scraped categories: `apartment=10, unknown=5`
- Apartment list organization: Listings are organized by product/category buckets or broad sale/rent archives; apartment recovery is best from category pages instead of the home page.
- Discovery entrypoints: https://www.luximmo.bg/apartamenti/
- Apartment-focused entrypoints: https://www.luximmo.bg/apartamenti/
- Pagination: server-rendered pagination using suffix `index{}.html`
- Detail URL pattern: `luximmo\.bg/.+-\d{5,}-[^\"'<> ]+\.html(?:[?#][^\"'<> ]*)?$`
- Full-list approach: Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media.
- Item-page requirement: detail page required
- Current blocker: none in current config

### OLX.bg

- Links: `https://www.olx.bg/`; related: `https://developer.olx.bg/`
- Access/legal: `official_api` / `low` / `official_api_allowed`
- Declared services: `sale, long_term_rent, land, new_build`
- Scraped services: `long_term_rent=117, sale=132`
- Scraped categories: `apartment=170, house=25, land=24, office=13, unknown=17`
- Apartment list organization: Listings are organized by product/category buckets or broad sale/rent archives; apartment recovery is best from category pages instead of the home page.
- Discovery entrypoints: https://www.olx.bg/nedvizhimi-imoti/
- Apartment-focused entrypoints: not yet captured in repo
- Pagination: server-rendered pagination using suffix `?page={}`
- Detail URL pattern: `olx\.bg/d/ad/`
- Full-list approach: Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media.
- Item-page requirement: detail page required
- Current blocker: none in current config

### property.bg

- Links: `https://www.property.bg/`
- Access/legal: `html` / `medium` / `public_crawl_with_review`
- Declared services: `sale, long_term_rent, land, new_build`
- Scraped services: `sale=15`
- Scraped categories: `apartment=12, unknown=3`
- Apartment list organization: Listings are organized by product/category buckets or broad sale/rent archives; apartment recovery is best from category pages instead of the home page.
- Discovery entrypoints: https://www.property.bg/bulgaria/apartments/; https://www.property.bg/sales/bulgaria/selection/; https://www.property.bg/rentals/bulgaria/selection/
- Apartment-focused entrypoints: https://www.property.bg/bulgaria/apartments/
- Pagination: server-rendered pagination using suffix `/page/{}/`
- Detail URL pattern: `property\.bg/property-\d{5,}(?:[-/][^\"'<> ]*)?`
- Full-list approach: Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media.
- Item-page requirement: detail page required
- Current blocker: none in current config

### SUPRIMMO

- Links: `https://www.suprimmo.bg/`
- Access/legal: `html` / `medium` / `public_crawl_with_review`
- Declared services: `sale, long_term_rent, land, new_build`
- Scraped services: `sale=12`
- Scraped categories: `apartment=10, unknown=2`
- Apartment list organization: Listings are organized by product/category buckets or broad sale/rent archives; apartment recovery is best from category pages instead of the home page.
- Discovery entrypoints: https://www.suprimmo.bg/bulgaria/apartamenti/; https://www.suprimmo.bg/bulgaria/kushti-vili/; https://www.suprimmo.bg/bulgaria/partseli/; https://www.suprimmo.bg/prodajba/bulgaria/selectsya/; https://www.suprimmo.bg/naem/bulgaria/selectsya/
- Apartment-focused entrypoints: https://www.suprimmo.bg/bulgaria/apartamenti/
- Pagination: server-rendered pagination using suffix `/page/{}/`
- Detail URL pattern: `suprimmo\.bg/imot-\d{5,}(?:[-/][^\"'<> ]*)?`
- Full-list approach: Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media.
- Item-page requirement: detail page required
- Current blocker: none in current config

### ApartmentsBulgaria.com

- Links: `https://www.apartmentsbulgaria.bg/`
- Access/legal: `headless` / `medium` / `public_crawl_with_review`
- Declared services: `short_term_rent`
- Scraped services: `none saved yet`
- Scraped categories: `none saved yet`
- Apartment list organization: Short-term-rent catalog; likely property-type and resort pages rather than one national apartment feed.
- Discovery entrypoints: https://www.apartmentsbulgaria.bg/
- Apartment-focused entrypoints: not yet captured in repo
- Pagination: browser/XHR mapping required
- Detail URL pattern: `not yet mapped`
- Full-list approach: Map resort/category pages first, then enumerate property cards and fetch each item page for room mix, amenities, and gallery.
- Item-page requirement: Detail page required for photos, amenities, and availability-style metadata.
- Current blocker: Headless access expected; current repo has no connector yet.

### Bazar.bg

- Links: `https://bazar.bg/`
- Access/legal: `html` / `medium` / `public_crawl_with_review`
- Declared services: `sale, long_term_rent, land`
- Scraped services: `long_term_rent=25, sale=225`
- Scraped categories: `apartment=204, office=1, unknown=45`
- Apartment list organization: Listings are organized by product/category buckets or broad sale/rent archives; apartment recovery is best from category pages instead of the home page.
- Discovery entrypoints: https://bazar.bg/obiavi/apartamenti; https://bazar.bg/obiavi/kashti-i-vili; https://bazar.bg/obiavi/zemya; https://bazar.bg/obiavi/garazhi-i-parkoingi
- Apartment-focused entrypoints: https://bazar.bg/obiavi/apartamenti
- Pagination: server-rendered pagination using suffix `?page={}`
- Detail URL pattern: `bazar\.bg/obiava-\d{5,}`
- Full-list approach: Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media.
- Item-page requirement: detail page required
- Current blocker: none in current config

### Domaza

- Links: `https://www.domaza.bg/`
- Access/legal: `html` / `medium` / `public_crawl_with_review`
- Declared services: `sale, long_term_rent, short_term_rent, land, new_build`
- Scraped services: `none saved yet`
- Scraped categories: `none saved yet`
- Apartment list organization: Listings are organized by product/category buckets or broad sale/rent archives; apartment recovery is best from category pages instead of the home page.
- Discovery entrypoints: https://www.domaza.bg/property/index/search/1/s/572da6146f10beb4bf6333d75039731a4d2b9902; https://www.domaza.bg/property/index/search/1/s/c8a3ad4db8f37d4e8b31fe9db66bc4d1f537ba5a; https://www.domaza.bg/property/index/search/1/s/e8780bcda8fa201940f1ce87e404f870d0c5c3fc
- Apartment-focused entrypoints: not yet captured in repo
- Pagination: server-rendered pagination using suffix `?page={}`
- Detail URL pattern: `domaza\.(bg|biz)/.+ID\d+`
- Full-list approach: Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media.
- Item-page requirement: detail page required
- Current blocker: connector planning exists but saved corpus is still zero

### Holding Group Real Estate

- Links: `https://holdinggroup.bg/`
- Access/legal: `html` / `medium` / `public_crawl_with_review`
- Declared services: `sale, long_term_rent, land, new_build`
- Scraped services: `none saved yet`
- Scraped categories: `none saved yet`
- Apartment list organization: Agency inventory organized around direct sale/project pages, likely city and project buckets.
- Discovery entrypoints: https://holdinggroup.bg/
- Apartment-focused entrypoints: not yet captured in repo
- Pagination: server-rendered pagination expected
- Detail URL pattern: `not yet mapped`
- Full-list approach: Start from city/project category pages, dedupe against syndication, then fetch each offer detail page.
- Item-page requirement: Detail page required.
- Current blocker: No live connector or fixture capture yet.

### Home2U

- Links: `https://home2u.bg/`
- Access/legal: `html` / `medium` / `public_crawl_with_review`
- Declared services: `sale, long_term_rent, land, new_build`
- Scraped services: `none saved yet`
- Scraped categories: `none saved yet`
- Apartment list organization: Listings are organized by product/category buckets or broad sale/rent archives; apartment recovery is best from category pages instead of the home page.
- Discovery entrypoints: https://home2u.bg/nedvizhimi-imoti-sofia/; https://home2u.bg/nedvizhimi-imoti-varna/; https://home2u.bg/nedvizhimi-imoti-burgas/; https://home2u.bg/nedvizhimi-imoti-plovdiv/; https://home2u.bg/apartamenti-pod-naem-sofia/; https://home2u.bg/apartamenti-pod-naem-varna/
- Apartment-focused entrypoints: https://home2u.bg/nedvizhimi-imoti-sofia/; https://home2u.bg/nedvizhimi-imoti-varna/; https://home2u.bg/nedvizhimi-imoti-burgas/; https://home2u.bg/nedvizhimi-imoti-plovdiv/; https://home2u.bg/apartamenti-pod-naem-sofia/; https://home2u.bg/apartamenti-pod-naem-varna/
- Pagination: server-rendered pagination using suffix `?page={}`
- Detail URL pattern: `home2u\.bg/.+-[a-z0-9]{5,}`
- Full-list approach: Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media.
- Item-page requirement: detail page required
- Current blocker: connector planning exists but saved corpus is still zero

### Imoteka.bg

- Links: `https://imoteka.bg/`
- Access/legal: `headless` / `high` / `legal_review_required`
- Declared services: `sale, long_term_rent, land, new_build`
- Scraped services: `none saved yet`
- Scraped categories: `none saved yet`
- Apartment list organization: Likely JS-heavy agency portal with filtered grids and campaign/new-build emphasis.
- Discovery entrypoints: https://imoteka.bg/
- Apartment-focused entrypoints: not yet captured in repo
- Pagination: browser/XHR mapping required
- Detail URL pattern: `not yet mapped`
- Full-list approach: Legal review first, then browser trace category/XHR flows before parser work.
- Item-page requirement: Detail page required.
- Current blocker: High risk + headless + legal review required.

### Imoti.info

- Links: `https://imoti.info/`
- Access/legal: `partner_feed` / `high` / `licensing_required`
- Declared services: `sale, long_term_rent, land, new_build`
- Scraped services: `none saved yet`
- Scraped categories: `none saved yet`
- Apartment list organization: Partner-feed style marketplace; browsing exists but licensing governs commercial extraction.
- Discovery entrypoints: https://imoti.info/
- Apartment-focused entrypoints: not yet captured in repo
- Pagination: partner export or licensed feed
- Detail URL pattern: `not yet mapped`
- Full-list approach: Do not crawl broadly. Seek licensing or partner export before item recovery.
- Item-page requirement: Would require detail pages or feed payloads, but licensing is the first gate.
- Current blocker: Licensing required.

### Indomio.bg

- Links: `https://www.indomio.bg/`
- Access/legal: `headless` / `medium` / `public_crawl_with_review`
- Declared services: `sale, long_term_rent, land`
- Scraped services: `none saved yet`
- Scraped categories: `none saved yet`
- Apartment list organization: Portal-style result grids with filterable categories and likely JS-assisted navigation.
- Discovery entrypoints: https://www.indomio.bg/
- Apartment-focused entrypoints: not yet captured in repo
- Pagination: browser/XHR mapping required
- Detail URL pattern: `not yet mapped`
- Full-list approach: Map category/city entry pages, inspect XHR if present, then reconcile to detail pages.
- Item-page requirement: Detail page required.
- Current blocker: No connector yet; likely headless fallback needed.

### Lions Group

- Links: `https://lionsgroup.bg/`
- Access/legal: `html` / `medium` / `public_crawl_with_review`
- Declared services: `sale, long_term_rent, land, new_build`
- Scraped services: `none saved yet`
- Scraped categories: `none saved yet`
- Apartment list organization: Agency site with city/project-driven inventory sections.
- Discovery entrypoints: https://lionsgroup.bg/
- Apartment-focused entrypoints: not yet captured in repo
- Pagination: server-rendered pagination expected
- Detail URL pattern: `not yet mapped`
- Full-list approach: Enumerate listing archives and project buckets, then fetch each listing page.
- Item-page requirement: Detail page required.
- Current blocker: No fixture or live recovery yet.

### Pochivka.bg

- Links: `https://pochivka.bg/`
- Access/legal: `html` / `medium` / `public_crawl_with_review`
- Declared services: `short_term_rent`
- Scraped services: `none saved yet`
- Scraped categories: `none saved yet`
- Apartment list organization: Travel catalog rather than classic sale feed; apartment inventory is hospitality-oriented.
- Discovery entrypoints: https://pochivka.bg/
- Apartment-focused entrypoints: not yet captured in repo
- Pagination: server-rendered pagination expected
- Detail URL pattern: `not yet mapped`
- Full-list approach: Treat as STR intelligence. Traverse resort/location catalogs to item pages.
- Item-page requirement: Detail page required.
- Current blocker: Not a core sale/rent apartment source.

### realestates.bg

- Links: `https://en.realestates.bg/`
- Access/legal: `html` / `medium` / `public_crawl_with_review`
- Declared services: `sale, long_term_rent, land`
- Scraped services: `none saved yet`
- Scraped categories: `none saved yet`
- Apartment list organization: Foreign-facing portal layer related to alo.bg; likely mirrored listing pages and translated categories.
- Discovery entrypoints: https://en.realestates.bg/
- Apartment-focused entrypoints: not yet captured in repo
- Pagination: server-rendered pagination expected
- Detail URL pattern: `not yet mapped`
- Full-list approach: Scope crawl carefully and dedupe aggressively against alo.bg by URL/title/price/media hash.
- Item-page requirement: Detail page required.
- Current blocker: Cross-network duplication risk.

### Realistimo

- Links: `https://realistimo.com/`
- Access/legal: `headless` / `medium` / `public_crawl_with_review`
- Declared services: `sale, long_term_rent, land, new_build`
- Scraped services: `none saved yet`
- Scraped categories: `none saved yet`
- Apartment list organization: Map-led browsing with geo filters and listing cards.
- Discovery entrypoints: https://realistimo.com/
- Apartment-focused entrypoints: not yet captured in repo
- Pagination: browser/XHR mapping required
- Detail URL pattern: `not yet mapped`
- Full-list approach: Map initial browse endpoints, discover backing XHR or map payloads, then fetch detail pages.
- Item-page requirement: Detail page required.
- Current blocker: Likely headless or API trace needed.

### Rentica.bg

- Links: `https://rentica.bg/`
- Access/legal: `html` / `medium` / `public_crawl_with_review`
- Declared services: `long_term_rent`
- Scraped services: `none saved yet`
- Scraped categories: `none saved yet`
- Apartment list organization: Rent-specialist listing grid, probably city-first and apartment-heavy.
- Discovery entrypoints: https://rentica.bg/
- Apartment-focused entrypoints: not yet captured in repo
- Pagination: server-rendered pagination expected
- Detail URL pattern: `not yet mapped`
- Full-list approach: Target city rental pages, paginate deeply, then fetch item pages.
- Item-page requirement: Detail page required.
- Current blocker: No connector yet.

### Svobodni-kvartiri.com

- Links: `https://svobodni-kvartiri.com/`
- Access/legal: `html` / `medium` / `public_crawl_with_review`
- Declared services: `long_term_rent, short_term_rent`
- Scraped services: `none saved yet`
- Scraped categories: `none saved yet`
- Apartment list organization: Deep city pagination focused on rentals, rooms, and worker/student supply.
- Discovery entrypoints: https://svobodni-kvartiri.com/
- Apartment-focused entrypoints: not yet captured in repo
- Pagination: server-rendered pagination expected
- Detail URL pattern: `not yet mapped`
- Full-list approach: Paginate per city and rental type, then fetch each item page.
- Item-page requirement: Detail page required.
- Current blocker: No connector yet.

### Unique Estates

- Links: `https://ues.bg/`
- Access/legal: `html` / `medium` / `public_crawl_with_review`
- Declared services: `sale, long_term_rent, new_build`
- Scraped services: `none saved yet`
- Scraped categories: `none saved yet`
- Apartment list organization: Luxury agency catalog with sale/rent/new-build buckets.
- Discovery entrypoints: https://ues.bg/
- Apartment-focused entrypoints: not yet captured in repo
- Pagination: server-rendered pagination expected
- Detail URL pattern: `not yet mapped`
- Full-list approach: Enumerate category archives and project/luxury pages, then item pages.
- Item-page requirement: Detail page required.
- Current blocker: No connector yet.

### Vila.bg

- Links: `https://vila.bg/`
- Access/legal: `html` / `medium` / `public_crawl_with_review`
- Declared services: `short_term_rent`
- Scraped services: `none saved yet`
- Scraped categories: `none saved yet`
- Apartment list organization: Vacation and villa catalog, likely organized by destination rather than strict apartment taxonomy.
- Discovery entrypoints: https://vila.bg/
- Apartment-focused entrypoints: not yet captured in repo
- Pagination: server-rendered pagination expected
- Detail URL pattern: `not yet mapped`
- Full-list approach: Treat as resort/vacation inventory; traverse destination pages to item pages.
- Item-page requirement: Detail page required.
- Current blocker: Not a core apartment-sale feed.

### Yavlena

- Links: `https://www.yavlena.com/`
- Access/legal: `html` / `medium` / `public_crawl_with_review`
- Declared services: `sale, long_term_rent`
- Scraped services: `sale=250`
- Scraped categories: `apartment=145, house=40, land=36, office=7, unknown=22`
- Apartment list organization: Listings are organized by product/category buckets or broad sale/rent archives; apartment recovery is best from category pages instead of the home page.
- Discovery entrypoints: https://www.yavlena.com/bg/sales; https://www.yavlena.com/bg/rentals
- Apartment-focused entrypoints: not yet captured in repo
- Pagination: server-rendered pagination using suffix `?page={}`
- Detail URL pattern: `yavlena\.com/bg/\d{5,}`
- Full-list approach: Start from bucket entrypoints, paginate each bucket until no new URLs, regex-match detail URLs, then fetch every detail page for full text and media.
- Item-page requirement: detail page required
- Current blocker: none in current config
