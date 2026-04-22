---
name: managed-scrape-platforms
description: Use when evaluating Browserbase, Firecrawl, or Zyte as escalation layers for difficult sources, agent workflows, or structured extraction.
---

# managed-scrape-platforms

Use this skill when local `httpx` or Playwright workflows stop being the best operational choice.

## Read First
- `AGENTS.md`
- `agent-skills/hybrid-scrape-stack/SKILL.md`
- `agent-skills/browser-scrape-ops/SKILL.md`
- `.env.example`

## Platform roles
- Browserbase and Stagehand:
  - best for agentic browsing, interactive flows, session replay, and tool-calling automation
  - use when actions must be interpreted, cached, observed, or replayed across dynamic UI
- Firecrawl:
  - best for agent-friendly search, crawl, map, scrape, and browser sandbox workflows
  - use when the team needs broad coverage fast, especially for research or large URL discovery
- Zyte API:
  - best for managed extraction and anti-bot recovery, especially when structured extraction is more important than raw browser control
  - use when local maintenance cost is higher than per-request platform cost

## Decision rules
1. Default to local extraction for high-volume, repetitive real-estate pages.
2. Prefer Browserbase or Firecrawl when the value is in remote browser execution, observability, or agent ergonomics.
3. Prefer Zyte when the value is in structured extraction or recovery from blocking, not in running a custom browser flow.
4. Do not move a whole source to a managed platform just because one category page is annoying.
5. Keep a per-source note on why the escalation exists, what it costs, and what would let us de-escalate later.

## Cost and reliability lens
- Lowest marginal cost:
  - `httpx` or `curl_cffi`
- Best deterministic control:
  - Playwright or Crawlee
- Best agent ergonomics:
  - Browserbase and Firecrawl
- Best extraction outsourcing:
  - Zyte API

## Output Format

```text
Source:
Failure in local stack:
Managed platform candidate:
Why this platform fits:
Expected gain:
Lock-in risk:
Cost discipline:
Exit plan:
```

## Acceptance
- Managed platforms are treated as escalation layers, not default dependencies.
- The choice is tied to a specific failure mode.
- The plan includes a cost and exit story.
