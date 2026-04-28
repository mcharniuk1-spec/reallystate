# Gemma4 / OpenClaw Run Analysis

Generated: 2026-04-27

## Summary

The current repository state shows that the OpenClaw/Gemma4 run materially expanded or preserved the file-backed tier-1/2 scrape corpus, but it did not complete the apartment image-description report requirement.

## Observed Outputs

FACT: `data/scraped/` contains 1,549 saved tier-1/2 listing JSON files across 10 sources.

FACT: Saved listing rows contain 18,707 remote photo references and 5,376 local downloaded image files.

FACT: Four sources currently have at least 100 listings marked as full-gallery complete in file-backed data: `address_bg`, `bazar_bg`, `olx_bg`, and `yavlena`.

FACT: Three sources currently have at least 100 basic-complete saved rows by file-backed criteria: `bazar_bg`, `bulgarianproperties`, and `olx_bg`.

FACT: No completed apartment visual-report directory was found under `docs/exports/apartment-image-reports/` or a similarly named path.

## Source Snapshot

| Source | Items | Remote photos | Local photos | Full-gallery items | Basic-complete rows | Main gap |
|---|---:|---:|---:|---:|---:|---|
| address_bg | 140 | 140 | 141 | 140 | 98 | city missing on 42 rows |
| bazar_bg | 250 | 2607 | 2487 | 192 | 233 | partial gallery on 58 rows |
| bulgarianproperties | 249 | 8114 | 286 | 1 | 248 | remote gallery backfill incomplete |
| homes_bg | 97 | 489 | 304 | 32 | 59 | below 100 rows, partial local gallery |
| imot_bg | 271 | 3191 | 148 | 14 | 9 | price/area extraction and media backfill |
| luximmo | 15 | 114 | 128 | 13 | 12 | low row volume |
| olx_bg | 249 | 1365 | 1365 | 249 | 208 | area missing on many rows |
| property_bg | 15 | 1341 | 101 | 1 | 12 | low row volume and media backfill |
| suprimmo | 12 | 1095 | 166 | 1 | 9 | low row volume and media backfill |
| yavlena | 251 | 251 | 250 | 250 | 58 | description extraction is thin/missing |

## Interpretation

The next Codex tier1-2 run should be a quality-assurance and pattern-repair pass, not a broad discovery pass. The crawler already lands volume for several sources, but quality gaps are uneven:

- `imot_bg`: strong text volume, weak price/area extraction in saved JSON.
- `yavlena`: strong listing/photo count, weak description capture.
- `bulgarianproperties`, `property_bg`, `suprimmo`: high remote-gallery counts, weak local full-gallery completion.
- `address_bg`: good media/full-gallery status, but city extraction needs repair.
- `homes_bg`: close to threshold but still below 100 saved items and partial local gallery.

## Missing Gemma Requirement

Gemma/OpenClaw was expected to create one grouped apartment visual report per apartment and one ordered description per local image. That output is not present. The next Gemma run should start after Codex repairs scraper patterns and should consume complete local galleries only.

## Relevant Agents

- `scraper_1`: next owner for quality audit, pattern repair, image-count validation, and dashboard evidence.
- `debugger`: verifier for generated reports, dashboard consistency, and fixture-backed parser regressions.
- `ux_ui_designer`: relevant only because the website now displays scraped item evidence and media completeness.
- `backend_developer`: relevant only for later DB import/proof; not the immediate next run unless Postgres is available.
- `scraper_t3` and `scraper_sm`: not relevant to this specific next run.

