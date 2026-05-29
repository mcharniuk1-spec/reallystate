---
project: real-estate-bulgaria
type: strategy
status: active
date: 2026-05-29
owner: lead_agent
---

# Property Link Comparable Search Strategy

## Purpose

Create the operator workflow: given one property URL, parse that page into a conservative source-publication fingerprint, then search comparable and same-property candidates across saved tier 1, tier 2, and tier 3 evidence without broad live crawling or automatic canonical merges.

## Current State

FACT:
- The repo now contains `src/bgrealestate/matching/comparable.py` for property fingerprints, publication classification, pair scoring, and ranked comparable output.
- The repo now contains `scripts/property_link_comparable_search.py` for one-link intake from a fixture file or one explicitly approved live fetch.
- The CLI defaults to tiers `1,2,3`, accepted-only saved evidence, single-unit candidates, active rows, and cross-source matches only.
- Source registry legal gates still control live fetches. Partner, vendor, licensing, legal-review-only, and consent/manual sources are not live-fetched by this workflow.
- The first output is a JSON report under `docs/exports/`, not a canonical merge.

INTERPRETATION:
- This is the correct bridge between scraping and entity resolution. It gives the operator an explicit investigation artifact before DB/API/UI automation.
- The first reliable unit of truth remains the source publication. A page becomes a property candidate only after classification shows stable URL, property attributes, location evidence, and price or explicit price-status provenance.

GAP:
- The saved corpus is large and still needs an indexed search/read model for production speed.
- DB/API persistence, operator review UI, and debugger evaluation sets remain follow-up work.
- Live source truth for the full saved corpus still depends on the planned active-link audit and accepted-only DB proof.

## Pattern

1. Identify source from `data/source_registry.json` or explicit operator source.
2. Parse the one page using a source-specific parser when present, otherwise the generic detail parser.
3. Convert parsed fields into a `PropertyFingerprint`.
4. Classify the publication:
   - `single_unit_candidate`: stable detail URL, not grouped/development, not inactive/lost, price or explicit price status, and enough area/location evidence.
   - `grouped_or_development`: building/development/multi-unit signals, price-from signals, or missing unit-level evidence.
   - `insufficient_property_evidence`: page does not carry enough property fields to compare reliably.
5. Search saved source-publication rows from allowed tiers.
6. Score evidence without merging:
   - strong: same intent/category, city/district/address or close geospatial evidence, close area and price/status, image overlap, and strong textual overlap.
   - comparable: same market segment with plausible area/price/location similarity.
   - weak: missing or conflicting evidence.
7. Emit blockers, score components, evidence, conflicts, and source URLs for operator review.

## Agent Route

Use [[Strategic Planning Knowledge Entity]] for planning sequence and use the repo skill `agent-skills/property-link-comparable-search/SKILL.md` for execution.

Immediate sequence:
- `S1-28`: scraper_1 proves one-link fingerprints for each tier-1/tier-2 parser family using fixtures.
- `DA-09`: data_analyst builds an evaluation set and threshold report.
- `ER-09`: entity_resolution_agent defines persistence and manual-review policy, no auto-merge.
- `BD-24`: backend_developer adds API/read-model contracts after DB proof.
- `SM-17`: scraper_sm maps only public/consent-gated tier-3 comparable evidence.
- `UX-26`: ux_ui_designer designs the operator review surface.
- `DBG-33`: debugger verifies the CLI, fixtures, gates, and dashboard artifacts.
