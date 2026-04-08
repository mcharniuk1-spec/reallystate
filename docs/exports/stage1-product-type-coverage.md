# Stage-1 Product Type Coverage (Tier 1-2)

Generated from fixture `expected.json` files for tier-1/2 marketplace sources.

## Required product types

| Product type | Covered | Fixture count | Example fixtures |
|---|---:|---:|---|
| sale | yes | 15 | Address.bg::fixtures/address_bg/basic_listing/expected.json, alo.bg::fixtures/alo_bg/basic_listing/expected.json, Bazar.bg::fixtures/bazar_bg/basic_listing/expected.json |
| long_term_rent | yes | 1 | Yavlena::fixtures/yavlena/long_term_rent/expected.json |
| short_term_rent | yes | 1 | Domaza::fixtures/domaza/short_term_rent/expected.json |
| land | yes | 2 | Bazar.bg::fixtures/bazar_bg/land_listing/expected.json, OLX.bg::fixtures/olx_bg/missing_price/expected.json |
| new_build | yes | 1 | Home2U::fixtures/home2u/new_build/expected.json |

## Fixture inventory used

| Source | Tier | listing_intent | property_category | Fixture |
|---|---:|---|---|---|
| Address.bg | 1 | sale | apartment | fixtures/address_bg/basic_listing/expected.json |
| Address.bg | 1 | mixed | unknown | fixtures/address_bg/blocked_page/expected.json |
| BulgarianProperties | 1 | sale | apartment | fixtures/bulgarianproperties/basic_listing/expected.json |
| BulgarianProperties | 1 | mixed | unknown | fixtures/bulgarianproperties/blocked_page/expected.json |
| Homes.bg | 1 | mixed | apartment | fixtures/homes_bg/basic_listing/expected.json |
| Homes.bg | 1 | mixed | unknown | fixtures/homes_bg/blocked_page/expected.json |
| Homes.bg | 1 | mixed | apartment | fixtures/homes_bg/missing_geo/expected.json |
| Homes.bg | 1 | mixed | house | fixtures/homes_bg/missing_price/expected.json |
| Homes.bg | 1 | mixed | unknown | fixtures/homes_bg/removed_404/expected.json |
| LUXIMMO | 1 | sale | apartment | fixtures/luximmo/basic_listing/expected.json |
| LUXIMMO | 1 | mixed | unknown | fixtures/luximmo/blocked_page/expected.json |
| OLX.bg | 1 | sale | apartment | fixtures/olx_bg/basic_listing/expected.json |
| OLX.bg | 1 | mixed | unknown | fixtures/olx_bg/blocked_page/expected.json |
| OLX.bg | 1 | sale | land | fixtures/olx_bg/missing_price/expected.json |
| SUPRIMMO | 1 | sale | apartment | fixtures/suprimmo/basic_listing/expected.json |
| SUPRIMMO | 1 | mixed | unknown | fixtures/suprimmo/blocked_page/expected.json |
| alo.bg | 1 | sale | apartment | fixtures/alo_bg/basic_listing/expected.json |
| alo.bg | 1 | mixed | unknown | fixtures/alo_bg/blocked_page/expected.json |
| imot.bg | 1 | sale | apartment | fixtures/imot_bg/basic_listing/expected.json |
| imot.bg | 1 | mixed | unknown | fixtures/imot_bg/blocked_page/expected.json |
| imoti.net | 1 | mixed | apartment | fixtures/imoti_net/basic_listing/expected.json |
| imoti.net | 1 | mixed | unknown | fixtures/imoti_net/blocked_page/expected.json |
| property.bg | 1 | sale | apartment | fixtures/property_bg/basic_listing/expected.json |
| property.bg | 1 | mixed | unknown | fixtures/property_bg/blocked_page/expected.json |
| Bazar.bg | 2 | sale | apartment | fixtures/bazar_bg/basic_listing/expected.json |
| Bazar.bg | 2 | sale | land | fixtures/bazar_bg/land_listing/expected.json |
| Domaza | 2 | sale | apartment | fixtures/domaza/basic_listing/expected.json |
| Domaza | 2 | short_term_rent | apartment | fixtures/domaza/short_term_rent/expected.json |
| Home2U | 2 | sale | house | fixtures/home2u/basic_listing/expected.json |
| Home2U | 2 | sale | project | fixtures/home2u/new_build/expected.json |
| Yavlena | 2 | sale | apartment | fixtures/yavlena/basic_listing/expected.json |
| Yavlena | 2 | long_term_rent | apartment | fixtures/yavlena/long_term_rent/expected.json |
