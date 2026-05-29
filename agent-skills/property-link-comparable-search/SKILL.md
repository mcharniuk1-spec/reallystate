---
name: property-link-comparable-search
description: Use when an agent must intake one Bulgarian real-estate property URL, classify whether it is one unit, and search comparable or same-property candidates across tier 1/2/3 sources.
---

# Property Link Comparable Search Skill

## Purpose

Use this skill for the bounded workflow: one operator-provided property detail URL -> source/legal gate -> one-page scrape or fixture parse -> property fingerprint -> comparable search across saved tier 1/2/3 evidence.

Do not use it for broad crawling, Action1/Action2 expansion, private social/messenger scraping, partner-feed access, or public property promotion.

## Required Inputs

- Property detail URL.
- Optional source hint when host/source inference is ambiguous.
- Operator approval if `--fetch-live` is used.
- Saved HTML fixture if running offline or testing.

## Workflow

1. Read `data/source_registry.json` and identify the source and tier.
2. Check `legal_mode`, `risk_mode`, and `access_mode`.
3. For live intake, fetch only the provided detail URL and only when legal mode allows public review or official API access.
4. Parse with source-specific detail parser where available; otherwise stop with a parser gap rather than inventing fields.
5. Build a property fingerprint: URL, source, external/reference ID, intent, category, city/district/address, coordinates, price/status, area, rooms/floor, description, images, contacts, QA fields.
6. Classify the page:
   - single-unit candidate;
   - source-publication-only grouped/development;
   - blocked/incomplete with explicit blockers.
7. Search saved tier 1/2/3 source-publications from all other sources. Default to accepted-only single-unit candidates.
8. Return ranked results with score components, evidence, and conflicts.

## Command

Offline:

```bash
python scripts/property_link_comparable_search.py --url '<detail-url>' --source '<source name>' --html-file '<saved-detail.html>'
```

Single approved live URL:

```bash
python scripts/property_link_comparable_search.py --url '<detail-url>' --fetch-live
```

Useful flags:

- `--tiers 1,2,3`
- `--include-same-source`
- `--include-unreviewed`
- `--min-score 0.25`
- `--limit 50`
- `--max-corpus-files N` for smoke tests only; leave unset for operator investigations

## Acceptance Gate

- Query page blockers are visible.
- Grouped/development pages are never promoted as exact properties.
- Same-source candidates are excluded unless explicitly requested.
- Score components and conflicts are included.
- Tests use fixtures or pure functions only; no live network in tests.

## Files

- `src/bgrealestate/matching/comparable.py`
- `scripts/property_link_comparable_search.py`
- `docs/architecture/property-link-comparable-search.md`
- `tests/test_property_comparable_search.py`
