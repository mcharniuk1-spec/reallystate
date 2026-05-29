# Property-Link Comparable Search Agent Plan

Date: 2026-05-29

## FACT

- The current branch is `reallystate1`.
- Local `reallystate` and `reallystate1` point to the same commit.
- `origin/main` is eleven commits behind the current branch; `origin/reallystate` is two commits behind.
- The project already has source registry gating, one-page parsers for many tier 1/2 sources, source-publication QA states, accepted-only import defaults, canonical listing models, property entity/offer models, and conservative unification.
- The new implementation adds file-backed property-link comparable search through `scripts/property_link_comparable_search.py` and pure scoring through `src/bgrealestate/matching/comparable.py`.

## INTERPRETATION

The best next architecture is not to start another broad scraping wave. The correct operator loop is:

1. scrape or fixture-parse one provided property URL;
2. classify the page as a single-unit candidate or source-publication-only page;
3. search accepted saved evidence from all other tier 1/2/3 sources;
4. expose score components and conflicts;
5. keep review and promotion separate.

## HYPOTHESIS

Once DA builds a labeled evaluation set and ER turns the scoring result into reviewed candidate policy, the backend can safely expose a DB-backed endpoint and UX can ship an operator review screen without making unsupported public claims.

## GAP

- Active-link truth for the full corpus remains blocked by low disk and `S1-27`.
- DB-backed accepted-only proof still depends on `BD-18`/`BD-19` and runtime credentials.
- Tier 3 partner/vendor/official comparable evidence needs `SM-17` before it can be trusted beyond saved/imported fixtures.

## Agent Execution Plan

| Order | Agent | Slice | Mode | Rationale |
|---|---|---|---|---|
| 1 | `debugger` | `DBG-33` | immediate verify | Verify the pure scoring layer and CLI safety gates before others build on it. |
| 2A | `scraper_1` | `S1-28` | parallel after debugger starts | Source-specific one-page parser proof can proceed independently from DB work. |
| 2B | `data_analyst` | `DA-09` | parallel after debugger starts | Threshold evaluation needs accepted rows and pure scorer, not live DB. |
| 2C | `scraper_sm` | `SM-17` | parallel after debugger starts | Tier 3 mapping is planning/fixture work and must stay legal-gated. |
| 3A | `entity_resolution_agent` | `ER-09` | after DA-09 draft | ER policy needs threshold evidence and conflict classes. |
| 3B | `backend_developer` | `BD-24` | after BD-18/BD-19 proof | API/read-model work should wait for accepted-only DB proof. |
| 4 | `ux_ui_designer` | `UX-26` | after BD-24 contract | Operator UI should consume stable API/result semantics. |
| recurring | `planner` | `PLAN-13` | monitor | Keep this workflow separated from Action1/Action2 broad crawl gates. |

## Safety Gates

- No live-network dependency in tests.
- No automatic merge into `property_entity`.
- No grouped/development promotion.
- No same-source candidate unless operator requests it.
- No tier 3 live access unless official, contract, licensed, or manual route is present.
- No public comparable-search claims until debugger verifies accepted-only DB/read-model proof.
