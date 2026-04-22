---
name: browser-scrape-ops
description: Use when a source needs browser tracing, pagination/XHR mapping, or JS-aware scraping strategy before connector implementation.
---

# browser-scrape-ops

Use this skill when a tier-1 or tier-2 source is not fully recoverable with plain `httpx` + HTML parsing.

## Read First
- `AGENTS.md`
- `data/source_registry.json`
- `scripts/live_scraper.py`
- `docs/exports/tier12-source-analysis.md`

## Workflow
1. Confirm the source is allowed by `legal_mode`, `risk_mode`, and `access_mode`.
2. Start with plain HTTP discovery first. Escalate to browser tooling only when one of these is true:
   - listing grids are JS-rendered
   - pagination is driven by XHR or GraphQL
   - detail URLs are hidden behind client-side state
   - anti-bot behavior blocks stable HTML capture
3. Map the browse flow explicitly:
   - entry category page
   - filter state or API/XHR endpoint
   - pagination pattern
   - detail URL pattern
   - media/gallery loading path
4. Capture the smallest reproducible live trace:
   - one listing grid page
   - one detail page
   - relevant XHR payloads if present
5. Convert the browser findings into a fixture-first parser plan before adding more live code.
6. Prefer Playwright for modern browser automation and keep tests fixture-only.

## Output Format

```text
Source:
Access gate:
Observed browse flow:
Best extraction path:
Pagination rule:
Detail-page requirement:
Media path:
Known blockers:
Next parser task:
```

## Acceptance
- Browser use is justified by evidence, not habit.
- Entry pages, pagination, and detail URLs are documented.
- The final recommendation can be implemented as a reproducible connector plan.
