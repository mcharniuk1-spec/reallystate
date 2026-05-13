# Scrape taxonomy: Action1 vs A1 vs A12 (consistency contract)

**Purpose:** Align operator language (**Action1** / **Action2**), scraper **code buckets** (**A1** / **A12** / **other**), and **`tier12-pattern-status.json`** so OpenClaw and humans do not confuse scopes.

**Authoritative code:** `src/bgrealestate/scraping/source_class.py` (`A1_SOURCE_KEYS`, `source_bucket_for_key`, `detail_concurrency_for_source`).

**Pattern file:** `docs/exports/tier12-pattern-status.json` — `pattern_status == "Patterned"` drives **A12** classification (when the source is not already **A1**).

---

## Definitions

| Term | Meaning |
|------|---------|
| **Action1** | Operator / OpenClaw **task scope** `S1-22B`: live scrape **only** the **seven** priority all-Bulgaria portals, × four buckets. Does **not** mean “every patterned source”. |
| **A1** | **Same seven sources** in code: bounded detail concurrency `SCRAPER_CONCURRENCY_A1` (default **4**). Keys: `address_bg`, `bulgarianproperties`, `homes_bg`, `imot_bg`, `luximmo`, `property_bg`, `suprimmo`. |
| **A12** | Sources that are **Patterned** in `tier12-pattern-status.json` **and** whose `live_scraper.SOURCE_CONFIGS` key is **not** in **A1**. Use bounded concurrency `SCRAPER_CONCURRENCY_A12` (default **3**). Typical home: **Action2** expansion, not Action1. |
| **other** | Every other configured source in `scripts/live_scraper.py`: concurrency **1** by default (`SCRAPER_CONCURRENCY_OTHER`). |

**FACT:** Action1 scope **equals** the **A1** key set — seven portals, one naming convention difference only (**Action1** = task name, **A1** = engineering bucket).

---

## Seven Action1 sources = seven A1 keys (canonical)

| Order | Registry `source_name` | `SOURCE_CONFIGS` key | Scraped listing JSON root |
|------|-------------------------|----------------------|---------------------------|
| 1 | Address.bg | `address_bg` | `data/scraped/address_bg/listings/` |
| 2 | BulgarianProperties | `bulgarianproperties` | `data/scraped/bulgarianproperties/listings/` |
| 3 | Homes.bg | `homes_bg` | `data/scraped/homes_bg/listings/` |
| 4 | imot.bg | `imot_bg` | `data/scraped/imot_bg/listings/` |
| 5 | LUXIMMO | `luximmo` | `data/scraped/luximmo/listings/` |
| 6 | property.bg | `property_bg` | `data/scraped/property_bg/listings/` |
| 7 | SUPRIMMO | `suprimmo` | `data/scraped/suprimmo/listings/` |

**Registry vs scraper URL (BulgarianProperties):** `data/source_registry.json` lists `primary_url` **https://www.bulgarianproperties.bg/** (and mirrors **.com**). The live scraper entry points use **https://www.bulgarianproperties.com** — do not treat this as a scope mismatch; both are the same brand scope.

---

## A12 sources (Patterned, not Action1) — as of tier12 export

These six appear as **Patterned** in `tier12-pattern-status.json` and classify as **A12** in code (not in `A1_SOURCE_KEYS`):

| `source_name` | `SOURCE_CONFIGS` key |
|---------------|----------------------|
| alo.bg | `alo_bg` |
| Bazar.bg | `bazar_bg` |
| Domaza | `domaza` |
| Home2U | `home2u` |
| OLX.bg | `olx_bg` |
| Yavlena | `yavlena` |

**Interpretation:** OpenClaw **Action2** may include these when the operator expands tier-1/2 scraping after Action1 QA — they are **not** part of **Action1**.

If `tier12-pattern-status.json` is regenerated and Patterned membership changes, re-run classification:

```bash
PYTHONPATH=src python3 -c "
import json
from pathlib import Path
from bgrealestate.scraping.source_class import A1_SOURCE_KEYS, source_bucket_for_key
import runpy
cfg = runpy.run_path('scripts/live_scraper.py')['SOURCE_CONFIGS']
data = json.loads(Path('docs/exports/tier12-pattern-status.json').read_text())
for r in data.get('sources', []):
    if r.get('pattern_status') != 'Patterned':
        continue
    name = r.get('source_name')
    sk = (r.get('sample') or {}).get('source_key')
    if not sk:
        sk = next((k for k,c in cfg.items() if c.get('name')==name), None)
    b = source_bucket_for_key(sk or 'x', source_display_name=name or '')
    print(b, sk, name)
"
```

---

## Bounded concurrency + metrics (operator-visible)

- Per-source detail phase uses **ThreadPoolExecutor** workers from **A1 / A12 / other** (see `scripts/live_scraper.py`).
- Environment (optional overrides): `SCRAPER_CONCURRENCY_A1`, `SCRAPER_CONCURRENCY_A12`, `SCRAPER_CONCURRENCY_OTHER`.
- Each finished source appends one JSON line to **`data/runs/scrape_metrics.jsonl`** and updates **`data/runs/scrape_metrics_latest.json`** (`source_bucket`, `detail_concurrency_used`, counts, duration).

---

## Database alignment (post-scrape)

- File corpus is under **`data/scraped/<source_key>/listings/*.json`** and **`data/media/<reference_id>/`**.
- PostgreSQL ingest (when used): **`make import-scraped`** (`scripts/import_scraped_listings.py`) — requires **`DATABASE_URL`** and registry-aligned source keys.
- **Consistency check:** disk counts per `source_key` vs `canonical_listing` (or importer dry-run) after large runs; never assume Telegram counts match DB without import.

---

## OpenClaw behavioral summary

1. **Action1:** only the **seven** rows in the first table — same as **A1**.
2. **Action2:** remaining legal tier-1/2 from **`data/source_registry.json`**; **A12** Patterned sources are the usual **next** high-trust batch after Action1 but still require **`Action2 now`**.
3. Do **not** widen Action1 to alo.bg / Bazar / OLX / etc. without operator explicitly changing scope (that would be Action2 or a new operator directive).
