---
name: hybrid-scrape-stack
description: Use when designing or repairing a scraper that must move deliberately from cheap HTTP extraction to browser tracing and only then to managed platforms.
---

# hybrid-scrape-stack

Use this skill when a source is complex enough that "just use Playwright" would be too expensive, too brittle, or too slow.

## Read First
- `AGENTS.md`
- `data/source_registry.json`
- `agent-skills/browser-scrape-ops/SKILL.md`
- `agent-skills/runtime-compliance-evaluator/SKILL.md`
- `scripts/live_scraper.py`

## Principle
Treat scraping as a ladder:

1. Plain HTTP and HTML or JSON parsing
2. Browser-assisted network tracing
3. Replayed XHR, GraphQL, or JSON API requests
4. Managed browser or extraction platforms only when the lower tiers fail or cost more to maintain

The browser is a diagnostic tool first and a permanent dependency second.

## Recommended stack
- HTTP-first:
  - `httpx` for normal requests
  - `curl_cffi` when browser-grade TLS or HTTP/2 fingerprints matter
  - `selectolax`, `lxml`, or `BeautifulSoup` for parsing
- Trace and replay:
  - Playwright network inspection
  - Playwright tracing or screencasts for hard-to-reproduce flows
  - Crawlee when queueing, retries, and browser orchestration become the bottleneck
- Managed escalation:
  - Browserbase and Stagehand for agentic browser workflows
  - Firecrawl for agent-friendly browsing, mapping, and difficult JS extraction
  - Zyte API for structured extraction or hard anti-bot recovery

## Workflow
1. Confirm the source is legal to touch under `legal_mode`, `risk_mode`, and `access_mode`.
2. Start from a real listing category page, not the homepage.
3. Attempt `httpx` extraction first and record:
   - listing links
   - pagination pattern
   - canonical detail URL pattern
   - media endpoint pattern
4. If HTML is incomplete, open the same path in Playwright and inspect:
   - XHR or GraphQL calls
   - request headers and cookies that matter
   - hidden detail endpoints
   - whether pagination is cursor, page-number, or infinite scroll
5. Prefer replaying the discovered network calls over keeping a long-term DOM-click bot.
6. Escalate to `curl_cffi` before full browser automation when the site appears to be blocking on TLS or fingerprint signals.
7. Escalate to a managed platform only if one of these is true:
   - browser sessions are too flaky or expensive to host locally
   - the site has repeated anti-bot behavior that local replay cannot stabilize
   - an agentic browse flow is materially faster than engineering a deterministic path
8. Save the final extractor plan as fixtures, rules, and source notes.

## Output Format

```text
Source:
Allowed access mode:
HTTP-first result:
Replayable network path:
When browser is still required:
Managed fallback:
Media strategy:
Known risks:
Next implementation step:
```

## Acceptance
- Browser usage is justified with evidence.
- The chosen path is the cheapest reliable option, not the fanciest one.
- The plan preserves fixture-first tests and project compliance gates.
