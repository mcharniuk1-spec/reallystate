# Scraper 1 tier-1/2 live status

Updated from saved `data/scraped/*/listings/*.json` files and local `data/media/*` directories after the 2026-04-09 continuation wave.

## Tier 1

| source | listings | with description | with photo URLs | readable local photos | services scraped | categories scraped |
|---|---:|---:|---:|---:|---|---|
| Address.bg | 43 | 43 | 43 | 43 | `sale=43` | `apartment=29`, `house=8`, `land=3`, `office=2`, `unknown=1` |
| BulgarianProperties | 249 | 249 | 249 | 249 | `sale=246`, `long_term_rent=3` | `apartment=93`, `house=34`, `land=10`, `office=4`, `unknown=108` |
| Homes.bg | 37 | 37 | 36 | 20 | `sale=37` | `apartment=37` |
| imot.bg | 261 | 261 | 261 | 1 | `sale=261` | `unknown=261` |
| LUXIMMO | 15 | 13 | 15 | 15 | `sale=15` | `apartment=10`, `unknown=5` |
| OLX.bg | 249 | 249 | 249 | 249 | `sale=132`, `long_term_rent=117` | `apartment=170`, `house=25`, `land=24`, `office=13`, `unknown=17` |
| property.bg | 15 | 15 | 15 | 15 | `sale=15` | `apartment=12`, `unknown=3` |
| SUPRIMMO | 12 | 12 | 12 | 12 | `sale=12` | `apartment=10`, `unknown=2` |

## Tier 2

| source | listings | with description | with photo URLs | readable local photos | services scraped | categories scraped |
|---|---:|---:|---:|---:|---|---|
| Bazar.bg | 250 | 250 | 250 | 249 | `sale=225`, `long_term_rent=25` | `apartment=204`, `office=1`, `unknown=45` |
| Yavlena | 250 | 0 | 250 | 249 | `sale=250` | `apartment=145`, `house=40`, `land=36`, `office=7`, `unknown=22` |

## Service x category breakdown

### Tier 1

- Address.bg: `sale|apartment=29`, `sale|house=8`, `sale|land=3`, `sale|office=2`, `sale|unknown=1`
- BulgarianProperties: `sale|apartment=92`, `sale|house=34`, `sale|land=10`, `sale|office=4`, `sale|unknown=106`, `long_term_rent|apartment=1`, `long_term_rent|unknown=2`
- Homes.bg: `sale|apartment=37`
- imot.bg: `sale|unknown=261`
- LUXIMMO: `sale|apartment=10`, `sale|unknown=5`
- OLX.bg: `sale|apartment=80`, `sale|house=23`, `sale|land=18`, `sale|office=5`, `sale|unknown=6`, `long_term_rent|apartment=90`, `long_term_rent|house=2`, `long_term_rent|land=6`, `long_term_rent|office=8`, `long_term_rent|unknown=11`
- property.bg: `sale|apartment=12`, `sale|unknown=3`
- SUPRIMMO: `sale|apartment=10`, `sale|unknown=2`

### Tier 2

- Bazar.bg: `sale|apartment=182`, `sale|office=1`, `sale|unknown=42`, `long_term_rent|apartment=22`, `long_term_rent|unknown=3`
- Yavlena: `sale|apartment=145`, `sale|house=40`, `sale|land=36`, `sale|office=7`, `sale|unknown=22`

## Readability assessment

- Fully readable local photo sets in this continuation wave: `Address.bg`, `SUPRIMMO`, `LUXIMMO`, `property.bg`
- Strong readable coverage from earlier waves: `BulgarianProperties`, `OLX.bg`, `Bazar.bg`, `Yavlena`
- Partial readable coverage: `Homes.bg` (`20/36` with local readable photos)
- Weak readable coverage: `imot.bg` (`1/261` locally readable; image URLs exist but were mostly not downloaded in the older batch)
- Description gap: `Yavlena` listings currently have photo coverage but `0/250` saved descriptions in the harvested corpus

## Still pending / zero-yield in `data/scraped`

- Tier 1: `alo.bg`
- Tier 2: `Domaza`, `Home2U`

These sources still need a separate live continuation pass; they were not successfully landed into the saved corpus during this run.
