# Tier-1/2 live volume report

**Template for `scraper_1`:** append a new section after each major harvest batch. This file is the acceptance artifact for **`S1-18`** in `docs/agents/TASKS.md`.

## Gate (must be true to mark S1-18 DONE_AWAITING_VERIFY)

- At least **5** distinct marketplace sources (tier **1** or **2** per `data/source_registry.json`) that allow live fetch under their `legal_mode` / `access_mode`.
- Each of those sources has **≥100** rows in **`canonical_listing`** in PostgreSQL, counted by distinct `reference_id` (or the project’s agreed unique key), with `source_name` matching the registry.

If the gate is not met, document **BLOCKED** reasons in `docs/agents/scraper_1/JOURNEY.md` (e.g. legal gate, 403, CAPTCHA).

## Suggested default “first five” sources

Homes.bg, OLX.bg, imot.bg, alo.bg, property.bg — substitute if the registry or legal gate forbids live HTTP for any of them.

---

## Run log (append below)

### 2026-04-09 09:55 UTC — interim corpus reconciliation

| source_name | tier | new_this_run | total_in_db | notes |
|-------------|-----:|-------------:|------------:|-------|
| Bazar.bg | 2 | 250 | 0 | `data/scraped/bazar_bg` contains 250 parsed listings across category-targeted pages; DB import still pending because `DATABASE_URL` is unset in this shell. |
| BulgarianProperties | 1 | 249 | 0 | `data/scraped/bulgarianproperties` contains 249 parsed listings from product-specific sale/rent/land/apartment/house pages. |
| imot.bg | 1 | 250 | 0 | `data/scraped/imot_bg` contains 250 parsed listings from city + intent search pages. |
| OLX.bg | 1 | 249 | 0 | `data/scraped/olx_bg` contains 249 parsed listings from the real-estate feed. |
| Yavlena | 2 | 250 | 0 | `data/scraped/yavlena` contains 250 parsed listings from sale/rent search pages. |

**Commands / scripts:**

- `python3 - <<'PY' ...` tally from `data/scraped/*/scrape_stats.json`
- `find data/scraped -path '*/listings/*.json' | awk ...` per-source file counts
- `make scraping-inventory`

**Git revision:**

- local working tree with scraper/import/reporting updates in progress

**Operator:**

- Interim gate evidence only. The numeric benchmark is met in `data/scraped/`, but **`S1-18` remains NOT MET** until these rows are imported into PostgreSQL `canonical_listing` and verified there.

### 2026-04-09 — repaired-source continuation (file-backed corpus)

| source_name | tier | new_this_run | total_in_db | notes |
|-------------|-----:|-------------:|------------:|-------|
| Address.bg | 1 | 43 | 0 | Live discovery regex repaired from broken `p####` assumption to real `...offer688672` detail URLs; 43 listing JSON files and 43 readable local photo sets saved on disk. |
| LUXIMMO | 1 | 15 | 0 | Category-page discovery repaired to real luxury detail URLs ending in `-<id>-...html`; 15 listings + readable photo downloads saved on disk. |
| property.bg | 1 | 15 | 0 | Discovery repaired to real `property-<id>-.../` detail URLs; full completed sample run wrote 15 listings + 15 readable local photo sets. |
| SUPRIMMO | 1 | 12 | 0 | Discovery repaired to real `/imot-<id>-.../` detail URLs from category pages; checkpointed batch saved 12 listings + readable photo downloads on disk. |

**Commands / scripts:**

- `python3 -m py_compile scripts/live_scraper.py`
- `python3 scripts/live_scraper.py --sources address_bg,suprimmo,luximmo,property_bg --max-pages 3 --max-listings 120 --download-photos` (checkpointed after Address.bg landed cleanly)
- `python3 scripts/live_scraper.py --sources suprimmo,luximmo,property_bg --max-pages 2 --max-listings 60 --download-photos` (checkpointed after SUPRIMMO landed cleanly)
- `python3 scripts/live_scraper.py --sources luximmo,property_bg --max-pages 2 --max-listings 20 --download-photos` (checkpointed after LUXIMMO landed cleanly)
- `python3 scripts/live_scraper.py --sources property_bg --max-pages 2 --max-listings 15 --download-photos`
- file-backed reconciliation from `data/scraped/*/listings/*.json` + `data/media/*`

**Operator:**

- This continuation expanded the on-disk tier-1/2 corpus, but **`S1-18` remains NOT MET** because PostgreSQL import is still blocked by missing `DATABASE_URL`.
- Interrupted runs wrote listing JSON and media files before final `scrape_stats.json`, so the authoritative counts for this section come from saved listing/media files, not only `scrape_stats.json`.

### YYYY-MM-DD HH:MM UTC — batch label

| source_name | tier | new_this_run | total_in_db | notes |
|-------------|-----:|-------------:|------------:|-------|
| (example) Homes.bg | 1 | 0 | 0 | initial template |

**Commands / scripts:**

**Git revision:**

**Operator:**
