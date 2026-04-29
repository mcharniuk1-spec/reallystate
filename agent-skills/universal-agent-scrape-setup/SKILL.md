---
name: universal-agent-scrape-setup
description: Use when preparing a shared scraping runtime for Codex, Claude, and the project’s specialist agents with one reproducible stack.
---

# universal-agent-scrape-setup

Use this skill when the repo needs a shared scraping environment, tool policy, and agent-role mapping.

## Read First
- `AGENTS.md`
- `docs/agents/TASKS.md`
- `docs/exports/detective-product-orchestration-2026-04-30.md` (per-source approach + gates)
- `pyproject.toml`
- `.env.example`
- `docs/exports/universal-agent-scrape-setup-2026-04-20.md`

## Core setup
1. Install the base project stack:
   - `make install`
2. Install shared scrape-agent extras when browser-grade work is expected:
   - `make install-scrape-agents`
3. Install Playwright browsers only on machines that will do live browser work:
   - `python -m playwright install chromium`
4. Keep managed-platform secrets optional and out of git:
   - `BROWSERBASE_API_KEY`
   - `BROWSERBASE_PROJECT_ID`
   - `FIRECRAWL_API_KEY`
   - `ZYTE_API_KEY`

## Shared libraries
- Local default:
  - `httpx`
  - `curl_cffi`
  - `selectolax`
  - `lxml`
  - `beautifulsoup4`
  - `pydantic`
- Browser and queue:
  - `playwright`
  - Crawlee when orchestration exceeds simple local scripts
- Media:
  - `Pillow`
  - `imagehash`
  - optional native acceleration such as `pyvips` only where the host is prepared for it

## Agent mapping
- `scraper_1`:
  - HTTP-first tier-1 and tier-2 harvesting
  - Playwright only to discover replayable calls or recover JS-heavy routes
- `scraper_t3`:
  - official, licensed, partner, or registry routes only
  - managed platforms only if contracts and legal gates permit them
- `scraper_sm`:
  - no broad scraping of private or unsafe channels
  - use consented or official overlays only
- `backend_developer`:
  - owns storage schema, import path, object-storage strategy, and DB verification
- `debugger`:
  - owns trace capture, replay validation, evidence packs, and regression proof
- `ux_ui_designer`:
  - consumes exported data and screenshots, not raw scraping experiments

## Operational rules
1. Start every source from category pages that list many properties.
2. Always identify the stable detail URL and the media path.
3. Persist enough evidence for replay:
   - raw HTML or JSON
   - normalized listing JSON
   - media metadata
   - command and date used
4. Keep tests offline and fixture-backed.
5. Promote new patterns into repo-local skills before relying on them repeatedly.

## Acceptance
- Codex and Claude agents can follow the same environment and decision tree.
- Agent roles stay aligned with project guardrails.
- The setup supports both low-cost bulk scraping and higher-complexity recovery paths.
