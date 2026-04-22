# Universal Agent Scrape Setup

Date: 2026-04-20

This document standardizes the scraping runtime for Codex, Claude, and the repo's specialist agents.

## Goal

One shared operating model:
- cheap HTTP by default
- browser tracing when evidence requires it
- managed platforms only as escalation layers
- fixture-first tests
- media kept traceable and auditable

## Baseline Install

1. Base project setup

```bash
make install
```

2. Shared scrape-agent extras

```bash
make install-scrape-agents
```

3. Browser install for live browser operators only

```bash
python -m playwright install chromium
```

## Core Libraries

| Layer | Primary tools | Why |
| --- | --- | --- |
| Standard HTTP | `httpx` | fast, clean, already core to repo |
| Browser-grade HTTP | `curl_cffi` | impersonation, HTTP/2, anti-bot middle layer |
| Parsing | `selectolax`, `lxml`, `beautifulsoup4` | resilient HTML extraction |
| Validation | `pydantic` | normalized listing schemas |
| Browser control | `playwright` | network tracing, screenshots, replay discovery |
| Orchestration | Crawlee | retries, queues, browser pools when local scripts are no longer enough |
| Managed escalation | Browserbase, Firecrawl, Zyte | difficult flows, remote browsers, structured extraction |
| Media QA | `Pillow`, `imagehash` | readable-image checks, dedupe hints |

## Environment Variables

Add these only when needed.

```dotenv
HTTP_PROXY=
HTTPS_PROXY=
PLAYWRIGHT_BROWSERS_PATH=
BROWSERBASE_API_KEY=
BROWSERBASE_PROJECT_ID=
FIRECRAWL_API_KEY=
ZYTE_API_KEY=
ZYTE_API_URL=https://api.zyte.com/v1/extract
```

## Shared Decision Tree

1. Can `httpx` fetch the category page and detail page cleanly?
   - If yes, stay local and deterministic.
2. Is the page incomplete but the browser reveals XHR or GraphQL calls?
   - Use Playwright once, then replay the network path.
3. Is the failure mostly fingerprinting or transport-level blocking?
   - Try `curl_cffi`.
4. Is the source interactive, agentic, or operationally too costly to host locally?
   - Evaluate Browserbase or Firecrawl.
5. Is the value primarily in outsourced structured extraction or anti-bot resilience?
   - Evaluate Zyte.

## Agent Policy

### scraper_1
- Owns tier-1 and tier-2 sites.
- Uses HTTP-first plus replay-first methods.
- Uses Playwright for evidence capture, not as the default end-state.

### scraper_t3
- Owns official, partner, licensed, and registry routes only.
- May use managed platforms only if legal and contract posture permit.

### scraper_sm
- No broad scraping of private or unsafe channels.
- Only consented, official, or manually assisted routes.

### backend_developer
- Owns import path, DB verification, object storage, and media metadata persistence.

### debugger
- Owns trace proof, replay proof, and acceptance evidence after each agent run.

### ux_ui_designer
- Consumes normalized outputs, screenshots, and dashboard exports.
- Does not become a primary scraper lane.

## Media Guidance

- Keep the original URL and local storage key.
- Store large binaries in filesystem or object storage, not hot relational rows.
- Persist:
  - MIME type
  - file size
  - dimensions
  - content hash
  - readability or decode status
  - source ordering
- Generate derivatives for UI use; preserve the original when practical.

## Recommended Defaults For This Repo

- Bulk tier-1 and tier-2 collection: `httpx` plus parser stack
- Anti-bot recovery before browsers: `curl_cffi`
- Dynamic-page diagnosis: Playwright
- Bigger browser fleets or queue-heavy recovery: Crawlee
- Hard fallback for agentic workflows: Browserbase or Firecrawl
- Managed structured extraction: Zyte

## Required Repo Skills

- `agent-skills/hybrid-scrape-stack/SKILL.md`
- `agent-skills/managed-scrape-platforms/SKILL.md`
- `agent-skills/universal-agent-scrape-setup/SKILL.md`
- `agent-skills/browser-scrape-ops/SKILL.md`
- `agent-skills/image-media-pipeline/SKILL.md`
- `agent-skills/postgres-ops-psql/SKILL.md`

