# Property Link Comparable Search

## Goal

When the operator gives one property detail URL, the system should:

1. infer the source from `data/source_registry.json`;
2. enforce the source legal/access gate before any live fetch;
3. fetch only that detail page, or parse a saved fixture;
4. extract a property fingerprint from source-specific parser evidence;
5. classify the page as a single-unit candidate or source-publication-only page;
6. search saved tier 1/2/3 source-publications from all other sources;
7. return explicit same-property candidates, comparable properties, weak candidates, score components, evidence, and conflicts.

No discovery crawl, queue unpause, partner-feed access, private-channel access, or public property promotion is implied by this workflow.

## Current State

FACT: The repo already has source-first scraping, source registry gates, source-publication QA fields, accepted-only import defaults, canonical listing import, property entity unification, and DB/API search contracts.

FACT: `reallystate` and `reallystate1` point at the same local commit. `origin/main` is behind the current branch by eleven commits, and `origin/reallystate` is behind by two commits.

FACT: Existing entity resolution is conservative and DB proof is still blocked by missing runtime credentials. File-backed accepted rows remain the safest comparable-search corpus until `BD-18`/`BD-19` are verified.

INTERPRETATION: The missing product layer was not another broad scraper. It was a bounded source-link intake and comparable-search path that uses the existing parser, QA, and identity rules without bypassing Action1/Action2 gates.

GAP: The new script searches saved file-backed rows. A DB-backed endpoint and reviewed candidate persistence still need `BD-24`/`ER-09`/`DBG-33`.

## Property Definition From One Page

A page is treated as a source publication first. It becomes a single-unit candidate only when:

- the page has a stable detail URL;
- it is not marked grouped/development/multi-unit;
- it has one numeric price or explicit `price_status` such as `on_request` or `undefined`;
- it has enough area or location evidence to compare it safely;
- it is not inactive, removed, expired, `LOST`, or rejected by QA.

Grouped pages, project pages, price-from pages, and mixed unit pages stay source-publication-only. They can be analyzed, but they are not promoted or matched as one exact property unless unit-level URL, price/status, area, floor/rooms, and media evidence are present.

## Comparable Search Mechanism

Implemented entrypoint:

```bash
python scripts/property_link_comparable_search.py --url '<detail-url>' --fetch-live
```

Offline/fixture mode:

```bash
python scripts/property_link_comparable_search.py --url '<detail-url>' --source 'Address.bg' --html-file tests/fixtures/.../raw.html
```

Defaults:

- searched tiers: `1,2,3`;
- source corpus: saved `data/scraped/**/listings/*.json`;
- candidate filter: accepted single-unit source-publications only;
- same source excluded by default because the operator asked for all other sources;
- live intake allowed only for `public_crawl_with_review` or `official_api_allowed` sources.
- `--max-corpus-files N` exists for smoke tests; production/operator investigations should leave it unset so all saved tier 1/2/3 rows are considered.

Scoring evidence:

- intent compatibility;
- category compatibility;
- same city/district;
- normalized address/token similarity;
- coordinate distance;
- price closeness;
- area closeness;
- rooms/floor match;
- title/description token overlap;
- image URL overlap;
- weak contact overlap;
- candidate QA acceptability.

Classification:

- `same_property_candidate`: high score plus identity evidence, no major city/category/intent conflict;
- `comparable_property`: compatible property with similar commercial/location fields;
- `weak_candidate`: retained only when above the minimum score but not reliable enough for action.

## Reliability Rules

- Never treat raw scrape volume as comparable-search proof.
- Default to accepted-only single-unit candidates.
- Keep query page blockers visible in output.
- Preserve score components and conflicts for operator review.
- Do not merge property entities automatically from this workflow.
- Tier 3 partner/vendor/official sources are searched from saved/imported evidence; live partner routes remain contract/manual-gated.

## Next Implementation Steps

1. `scraper_1`: add/repair source-specific detail parsers and fixtures for the highest-value tier 1/2 sources that still cannot produce reliable one-page fingerprints.
2. `scraper_sm`: map tier 3 official/vendor/partner evidence that can safely participate in comparable search without unauthorized scraping.
3. `data_analyst`: build an evaluation set of known same-property and known-not-same pairs from accepted rows.
4. `entity_resolution_agent`: persist reviewed comparable candidates into `entity_resolution_candidate`, separate exact duplicates from market comparables.
5. `backend_developer`: add a DB/API endpoint after accepted-only import and read-model proof.
6. `ux_ui_designer`: expose an operator review view that shows the query page, candidates, score components, conflicts, and source links.
7. `debugger`: verify no live-network tests, no grouped promotion, no stale public claims, and no unsafe tier 3 access.
