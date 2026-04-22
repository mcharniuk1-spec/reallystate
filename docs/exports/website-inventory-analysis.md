# Website Inventory Analysis

Generated at: `2026-04-21T15:22:11.425853+00:00`

This artifact separates website-side inventory evidence from landed scraper corpus counts.

## Address.bg

- Tier: `1`
- Website total: `18701` (Exact)
- Coverage vs landed corpus: `43` saved / `0.2%`
- Total basis: `live_embedded_json`
- Total notes: Computed as sale total 16935 plus rent total 1766 from live `offers-object` payloads.
- Counting method: Read the live search page and extract `offers-object.total` from the embedded JSON payload.
- Counting gap: Property-type split still needs category-specific entry pages or in-payload estate-type aggregation.
- Estimate conflict: Saved analysis estimate 18000 is below the confirmed/lower-bound live count 18701.

| Service | Property | Count | Kind | Basis | URL | Notes |
| --- | --- | ---: | --- | --- | --- | --- |
| sale | all | 16935 | Exact | live_embedded_json | https://address.bg/sale | Page payload exposes `total=16935`. |
| long_term_rent | all | 1766 | Exact | live_embedded_json | https://address.bg/rent | Page payload exposes `total=1766`. |

## alo.bg

- Tier: `1`
- Website total: `75961` (Lower bound)
- Coverage vs landed corpus: `0` saved / `0.0%`
- Total basis: `largest_live_category_count`
- Total notes: Sale apartments alone already exceed the older source estimate, so current total must be at least this large.
- Counting method: Extract counts from the live category page meta description on mapped product pages.
- Counting gap: Land and rent routes need refreshed discovery URLs before the source can have a trustworthy total.
- Estimate conflict: Saved analysis estimate 35000 is below the confirmed/lower-bound live count 75961.

| Service | Property | Count | Kind | Basis | URL | Notes |
| --- | --- | ---: | --- | --- | --- | --- |
| sale | apartment | 75961 | Exact | live_meta_description | https://www.alo.bg/obiavi/imoti-prodajbi/apartamenti-stai/ | Meta description says `75961 обяви`. |
| sale | house | 24695 | Exact | live_meta_description | https://www.alo.bg/obiavi/imoti-prodajbi/kashti-vili/ | Meta description says `24695 обяви`. |
| sale | land | n/a | Unavailable | configured_url_404 | https://www.alo.bg/obiavi/imoti-prodajbi/parzeli-za-zastroiavane-investicionni-proekti/ | Configured land URL returned 404 during this run and needs remapping. |
| long_term_rent | apartment | n/a | Unavailable | configured_url_404 | https://www.alo.bg/obiavi/imoti-naemi/apartamenti-stai/ | Configured rent URL returned 404 during this run and needs remapping. |

## BulgarianProperties

- Tier: `1`
- Website total: `12000` (Estimate)
- Coverage vs landed corpus: `249` saved / `2.1%`
- Total basis: `analysis_estimate`
- Total notes: Fallback to the saved tier-1/2 source analysis estimate because no live category count was confirmed in this run.
- Counting method: Use the configured category entry pages first, then extract visible counts, embedded JSON totals, or traced XHR payloads.
- Counting gap: Website-side category totals are not yet confirmed and still depend on a source-specific live counting pass.

No category-level website counts are saved yet for this source.

## Homes.bg

- Tier: `1`
- Website total: `120000` (Estimate)
- Coverage vs landed corpus: `49` saved / `0.0%`
- Total basis: `analysis_estimate`
- Total notes: Fallback to the saved tier-1/2 source analysis estimate because no live category count was confirmed in this run.
- Counting method: Use the configured category entry pages first, then extract visible counts, embedded JSON totals, or traced XHR payloads.
- Counting gap: Website-side category totals are not yet confirmed and still depend on a source-specific live counting pass.

No category-level website counts are saved yet for this source.

## imot.bg

- Tier: `1`
- Website total: `200000` (Estimate)
- Coverage vs landed corpus: `271` saved / `0.1%`
- Total basis: `analysis_estimate`
- Total notes: Fallback to the saved tier-1/2 source analysis estimate because no live category count was confirmed in this run.
- Counting method: Use the configured category entry pages first, then extract visible counts, embedded JSON totals, or traced XHR payloads.
- Counting gap: Website-side category totals are not yet confirmed and still depend on a source-specific live counting pass.

No category-level website counts are saved yet for this source.

## imoti.net

- Tier: `1`
- Website total: `90000` (Estimate)
- Coverage vs landed corpus: `0` saved / `0.0%`
- Total basis: `analysis_estimate`
- Total notes: Fallback to the saved tier-1/2 source analysis estimate because no live category count was confirmed in this run.
- Counting method: Use the configured category entry pages first, then extract visible counts, embedded JSON totals, or traced XHR payloads.
- Counting gap: Website-side category totals are not yet confirmed and still depend on a source-specific live counting pass.

No category-level website counts are saved yet for this source.

## LUXIMMO

- Tier: `1`
- Website total: `4000` (Estimate)
- Coverage vs landed corpus: `15` saved / `0.4%`
- Total basis: `analysis_estimate`
- Total notes: Fallback to the saved tier-1/2 source analysis estimate because no live category count was confirmed in this run.
- Counting method: Use the configured category entry pages first, then extract visible counts, embedded JSON totals, or traced XHR payloads.
- Counting gap: Website-side category totals are not yet confirmed and still depend on a source-specific live counting pass.

No category-level website counts are saved yet for this source.

## OLX.bg

- Tier: `1`
- Website total: `1000` (Lower bound)
- Coverage vs landed corpus: `249` saved / `24.9%`
- Total basis: `live_listing_count_banner`
- Total notes: The live banner says `повече от 1000 обяви`, so this is only a floor.
- Counting method: Read the search results banner rendered on the listing page.
- Counting gap: The page only exposes a lower bound; precise per-category totals require client-side API/XHR tracing.

| Service | Property | Count | Kind | Basis | URL | Notes |
| --- | --- | ---: | --- | --- | --- | --- |
| all | all | 1000 | Lower bound | live_listing_count_banner | https://www.olx.bg/nedvizhimi-imoti/ | Banner text: `Открихме повече от 1000 обяви`. |

## property.bg

- Tier: `1`
- Website total: `4229` (Lower bound)
- Coverage vs landed corpus: `15` saved / `0.4%`
- Total basis: `live_meta_description`
- Total notes: The apartments page meta description says `Over 4229 properties`; wording is category-oriented but still needs one confirmation pass.
- Counting method: Extract category counts from live page metadata.
- Counting gap: Sale-selection and rent-selection pages still need their own counts to separate apartments from broader portal inventory.

| Service | Property | Count | Kind | Basis | URL | Notes |
| --- | --- | ---: | --- | --- | --- | --- |
| sale | apartment | 4229 | Lower bound | live_meta_description | https://www.property.bg/bulgaria/apartments/ | Meta description says `Over 4229 properties` on the apartments page. |

## SUPRIMMO

- Tier: `1`
- Website total: `4628` (Lower bound)
- Coverage vs landed corpus: `12` saved / `0.3%`
- Total basis: `live_meta_description`
- Total notes: The apartments page meta description says `Over 4628 ...`, which is a category lower bound rather than a whole-site total.
- Counting method: Extract category counts from live page metadata on the canonical product page.
- Counting gap: Houses, land, sale-selection, and rent-selection still need separate count captures.

| Service | Property | Count | Kind | Basis | URL | Notes |
| --- | --- | ---: | --- | --- | --- | --- |
| sale | apartment | 4628 | Lower bound | live_meta_description | https://www.suprimmo.bg/bulgaria/apartamenti/ | Meta description exposes `4628` as the visible apartment count floor. |

## ApartmentsBulgaria.com

- Tier: `2`
- Website total: `1800` (Estimate)
- Coverage vs landed corpus: `0` saved / `0.0%`
- Total basis: `analysis_estimate`
- Total notes: Fallback to the saved tier-1/2 source analysis estimate because no live category count was confirmed in this run.
- Counting method: Use the configured category entry pages first, then extract visible counts, embedded JSON totals, or traced XHR payloads.
- Counting gap: Website-side category totals are not yet confirmed and still depend on a source-specific live counting pass.

No category-level website counts are saved yet for this source.

## Bazar.bg

- Tier: `2`
- Website total: `221272` (Exact)
- Coverage vs landed corpus: `250` saved / `0.1%`
- Total basis: `live_category_switcher`
- Total notes: The page header exposes `Имоти 221 272 обяви`.
- Counting method: Read the visible category switcher for portal total, then mine shortcut blocks for subtype/city slices.
- Counting gap: A clean apartment/house/land total still needs either a dedicated count endpoint or a DOM/XHR trace.
- Estimate conflict: Saved analysis estimate 8000 is below the confirmed/lower-bound live count 221272.

| Service | Property | Count | Kind | Basis | URL | Notes |
| --- | --- | ---: | --- | --- | --- | --- |
| all | all | 221272 | Exact | live_category_switcher | https://bazar.bg/obiavi/kashti-i-vili | Real-estate umbrella count exposed in the top category switcher. |
| sale | apartment | n/a | Partial visible breakdown | live_city_shortcuts | https://bazar.bg/obiavi/apartamenti | Apartment page exposes visible city/subtype slices such as `2-стаен София 12 376` and `3-стаен София 13 540`, but not a single clean apartment total. |

## Domaza

- Tier: `2`
- Website total: `22000` (Estimate)
- Coverage vs landed corpus: `0` saved / `0.0%`
- Total basis: `analysis_estimate`
- Total notes: Fallback to the saved tier-1/2 source analysis estimate because no live category count was confirmed in this run.
- Counting method: Use the configured category entry pages first, then extract visible counts, embedded JSON totals, or traced XHR payloads.
- Counting gap: Website-side category totals are not yet confirmed and still depend on a source-specific live counting pass.

No category-level website counts are saved yet for this source.

## Holding Group Real Estate

- Tier: `2`
- Website total: `3000` (Estimate)
- Coverage vs landed corpus: `0` saved / `0.0%`
- Total basis: `analysis_estimate`
- Total notes: Fallback to the saved tier-1/2 source analysis estimate because no live category count was confirmed in this run.
- Counting method: Use the configured category entry pages first, then extract visible counts, embedded JSON totals, or traced XHR payloads.
- Counting gap: Website-side category totals are not yet confirmed and still depend on a source-specific live counting pass.

No category-level website counts are saved yet for this source.

## Home2U

- Tier: `2`
- Website total: `6000` (Estimate)
- Coverage vs landed corpus: `0` saved / `0.0%`
- Total basis: `analysis_estimate`
- Total notes: Fallback to the saved tier-1/2 source analysis estimate because no live category count was confirmed in this run.
- Counting method: Use the configured category entry pages first, then extract visible counts, embedded JSON totals, or traced XHR payloads.
- Counting gap: Website-side category totals are not yet confirmed and still depend on a source-specific live counting pass.

No category-level website counts are saved yet for this source.

## Imoteka.bg

- Tier: `2`
- Website total: `14000` (Estimate)
- Coverage vs landed corpus: `0` saved / `0.0%`
- Total basis: `analysis_estimate`
- Total notes: Fallback to the saved tier-1/2 source analysis estimate because no live category count was confirmed in this run.
- Counting method: Use the configured category entry pages first, then extract visible counts, embedded JSON totals, or traced XHR payloads.
- Counting gap: Website-side category totals are not yet confirmed and still depend on a source-specific live counting pass.

No category-level website counts are saved yet for this source.

## Imoti.info

- Tier: `2`
- Website total: `25000` (Estimate)
- Coverage vs landed corpus: `0` saved / `0.0%`
- Total basis: `analysis_estimate`
- Total notes: Fallback to the saved tier-1/2 source analysis estimate because no live category count was confirmed in this run.
- Counting method: Use the configured category entry pages first, then extract visible counts, embedded JSON totals, or traced XHR payloads.
- Counting gap: Website-side category totals are not yet confirmed and still depend on a source-specific live counting pass.

No category-level website counts are saved yet for this source.

## Indomio.bg

- Tier: `2`
- Website total: `7000` (Estimate)
- Coverage vs landed corpus: `0` saved / `0.0%`
- Total basis: `analysis_estimate`
- Total notes: Fallback to the saved tier-1/2 source analysis estimate because no live category count was confirmed in this run.
- Counting method: Use the configured category entry pages first, then extract visible counts, embedded JSON totals, or traced XHR payloads.
- Counting gap: Website-side category totals are not yet confirmed and still depend on a source-specific live counting pass.

No category-level website counts are saved yet for this source.

## Lions Group

- Tier: `2`
- Website total: `2500` (Estimate)
- Coverage vs landed corpus: `0` saved / `0.0%`
- Total basis: `analysis_estimate`
- Total notes: Fallback to the saved tier-1/2 source analysis estimate because no live category count was confirmed in this run.
- Counting method: Use the configured category entry pages first, then extract visible counts, embedded JSON totals, or traced XHR payloads.
- Counting gap: Website-side category totals are not yet confirmed and still depend on a source-specific live counting pass.

No category-level website counts are saved yet for this source.

## Pochivka.bg

- Tier: `2`
- Website total: `5000` (Estimate)
- Coverage vs landed corpus: `0` saved / `0.0%`
- Total basis: `analysis_estimate`
- Total notes: Fallback to the saved tier-1/2 source analysis estimate because no live category count was confirmed in this run.
- Counting method: Use the configured category entry pages first, then extract visible counts, embedded JSON totals, or traced XHR payloads.
- Counting gap: Website-side category totals are not yet confirmed and still depend on a source-specific live counting pass.

No category-level website counts are saved yet for this source.

## realestates.bg

- Tier: `2`
- Website total: `6000` (Estimate)
- Coverage vs landed corpus: `0` saved / `0.0%`
- Total basis: `analysis_estimate`
- Total notes: Fallback to the saved tier-1/2 source analysis estimate because no live category count was confirmed in this run.
- Counting method: Use the configured category entry pages first, then extract visible counts, embedded JSON totals, or traced XHR payloads.
- Counting gap: Website-side category totals are not yet confirmed and still depend on a source-specific live counting pass.

No category-level website counts are saved yet for this source.

## Realistimo

- Tier: `2`
- Website total: `4500` (Estimate)
- Coverage vs landed corpus: `0` saved / `0.0%`
- Total basis: `analysis_estimate`
- Total notes: Fallback to the saved tier-1/2 source analysis estimate because no live category count was confirmed in this run.
- Counting method: Use the configured category entry pages first, then extract visible counts, embedded JSON totals, or traced XHR payloads.
- Counting gap: Website-side category totals are not yet confirmed and still depend on a source-specific live counting pass.

No category-level website counts are saved yet for this source.

## Rentica.bg

- Tier: `2`
- Website total: `1200` (Estimate)
- Coverage vs landed corpus: `0` saved / `0.0%`
- Total basis: `analysis_estimate`
- Total notes: Fallback to the saved tier-1/2 source analysis estimate because no live category count was confirmed in this run.
- Counting method: Use the configured category entry pages first, then extract visible counts, embedded JSON totals, or traced XHR payloads.
- Counting gap: Website-side category totals are not yet confirmed and still depend on a source-specific live counting pass.

No category-level website counts are saved yet for this source.

## Svobodni-kvartiri.com

- Tier: `2`
- Website total: `3500` (Estimate)
- Coverage vs landed corpus: `0` saved / `0.0%`
- Total basis: `analysis_estimate`
- Total notes: Fallback to the saved tier-1/2 source analysis estimate because no live category count was confirmed in this run.
- Counting method: Use the configured category entry pages first, then extract visible counts, embedded JSON totals, or traced XHR payloads.
- Counting gap: Website-side category totals are not yet confirmed and still depend on a source-specific live counting pass.

No category-level website counts are saved yet for this source.

## Unique Estates

- Tier: `2`
- Website total: `2000` (Estimate)
- Coverage vs landed corpus: `0` saved / `0.0%`
- Total basis: `analysis_estimate`
- Total notes: Fallback to the saved tier-1/2 source analysis estimate because no live category count was confirmed in this run.
- Counting method: Use the configured category entry pages first, then extract visible counts, embedded JSON totals, or traced XHR payloads.
- Counting gap: Website-side category totals are not yet confirmed and still depend on a source-specific live counting pass.

No category-level website counts are saved yet for this source.

## Vila.bg

- Tier: `2`
- Website total: `4000` (Estimate)
- Coverage vs landed corpus: `0` saved / `0.0%`
- Total basis: `analysis_estimate`
- Total notes: Fallback to the saved tier-1/2 source analysis estimate because no live category count was confirmed in this run.
- Counting method: Use the configured category entry pages first, then extract visible counts, embedded JSON totals, or traced XHR payloads.
- Counting gap: Website-side category totals are not yet confirmed and still depend on a source-specific live counting pass.

No category-level website counts are saved yet for this source.

## Yavlena

- Tier: `2`
- Website total: `9000` (Estimate)
- Coverage vs landed corpus: `251` saved / `2.8%`
- Total basis: `analysis_estimate`
- Total notes: Fallback to the saved tier-1/2 source analysis estimate because no live category count was confirmed in this run.
- Counting method: Use the configured category entry pages first, then extract visible counts, embedded JSON totals, or traced XHR payloads.
- Counting gap: Website-side category totals are not yet confirmed and still depend on a source-specific live counting pass.

No category-level website counts are saved yet for this source.

