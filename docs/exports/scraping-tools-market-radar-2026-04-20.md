# Scraping Tools Market Radar

Date: 2026-04-20  
Scope: tier-1 and tier-2 real-estate scraping for Bulgaria Real Estate MVP

## Executive Summary

FACT:
- The 2025-2026 scraping market has converged around a hybrid model, not a single winner.
- Playwright remains the core browser-control layer for tracing and deterministic interaction.
- Crawlee keeps improving as an orchestration layer and added `@crawlee/stagehand` in `3.16.0` on `2026-02-06`.
- Browserbase is pushing Stagehand toward faster, cached, multi-language agentic browser workflows.
- Firecrawl is increasingly agent-native, with a browser sandbox announced on `2026-02-17` and a CLI plus skill announced on `2026-01-27`.
- Zyte continues to matter as a managed extraction and anti-bot fallback, especially for structured extraction.
- `curl_cffi` remains one of the most useful low-cost upgrades when a site blocks plain `httpx` but does not truly require full browser automation.

INTERPRETATION:
- For this project, the winning setup is a layered stack:
  1. `httpx` or `curl_cffi`
  2. parser stack
  3. Playwright trace and replay
  4. Crawlee for orchestration
  5. Browserbase, Firecrawl, or Zyte only as escalation layers

HYPOTHESIS:
- If we keep most tier-1 and tier-2 sources on HTTP or replayed XHR flows, managed browser spend stays low while coverage remains high.

GAP:
- We still need live per-source trials before standardizing any one managed platform as the default fallback for this repo.

## Market View

| Tool or layer | Current signal | Why it matters here | Recommended role |
| --- | --- | --- | --- |
| Playwright | Strong and current | Best direct network inspection, tracing, codegen, and deterministic browser control | Primary browser debugger and recovery layer |
| Crawlee | Strong and current | Adds queues, retries, storage, and browser orchestration; recent Stagehand integration is notable | Use when local live scraping grows beyond simple scripts |
| `curl_cffi` | Strong niche tool | Cheap way to gain browser-like TLS and HTTP/2 fingerprints | First anti-bot escalation before full browser |
| Browserbase + Stagehand | Rapidly improving | Best fit for agentic browser work, observability, caching, and remote sessions | Escalation for hard interactive flows |
| Firecrawl | Rapidly improving | Strong agent-facing scrape, crawl, map, search, and sandbox toolkit | Escalation for discovery-heavy or agent-driven work |
| Zyte API | Stable managed fallback | Good structured extraction and anti-bot outsourcing | Use for hard targets where engineering cost is too high |

## What Changed Recently

### Playwright

FACT:
- Playwright release notes currently show `1.59` with new `page.screencast` APIs and improved trace-viewer style debugging.
- Official docs still emphasize network interception, request routing, and code generation as first-class features.

INTERPRETATION:
- Playwright is still the right browser baseline for this repo because it excels at turning "unknown dynamic website" into "known reproducible network path".

Sources:
- [Release notes](https://playwright.dev/docs/release-notes)
- [Network docs](https://playwright.dev/docs/network)
- [Codegen docs](https://playwright.dev/docs/codegen)
- [Tracing API](https://playwright.dev/docs/api/class-tracing)

### Crawlee

FACT:
- Crawlee `3.16.0` was published on `2026-02-06`.
- Its changelog notes async-iterator improvements and a new `@crawlee/stagehand` package.

INTERPRETATION:
- Crawlee is no longer just "nice queueing around Puppeteer." It is increasingly a browser-orchestration layer that can bridge deterministic crawling and newer agentic flows.

Sources:
- [Crawlee changelog](https://crawlee.dev/js/api/core/changelog)
- [Browser pool changelog](https://crawlee.dev/js/api/3.15/browser-pool/changelog)
- [Playwright crawler guide](https://crawlee.dev/python/docs/guides/playwright-crawler)

### Browserbase and Stagehand

FACT:
- Browserbase announced Stagehand caching on `2026-02-17`, with reported speedups up to roughly `80%` on repeat actions.
- Browserbase announced that Stagehand works with every language on `2026-01-13`.
- Stagehand v3 launched on `2025-10-29` with a large performance push and broader browser compatibility.

INTERPRETATION:
- Stagehand is valuable when the problem is not raw HTML extraction but agent reliability across messy UI, iframes, and shadow DOM.
- It should not replace deterministic scrapers for repetitive real-estate pages, but it is a strong fallback for hostile or highly interactive flows.

Sources:
- [Stagehand v3 changelog](https://www.browserbase.com/changelog/stagehand-v3)
- [Stagehand caching blog](https://www.browserbase.com/blog/stagehand-caching)
- [Browserbase MCP changelog](https://www.browserbase.com/changelog/browserbase-mcp)
- [Stagehand announcement](https://www.browserbase.com/changelog/announcing-stagehand)

### Firecrawl

FACT:
- Firecrawl announced its CLI and skill on `2026-01-27`.
- Firecrawl announced Browser Sandbox on `2026-02-17`.
- Firecrawl changelog emphasizes parallel agent workflows, change tracking, browser-based extraction, and broad engine benchmarks in late 2025 and early 2026.

INTERPRETATION:
- Firecrawl is strongest when the team wants a fast agent-facing extraction surface across many URLs, especially for discovery or large-scale research tasks.
- For this project, it is best treated as an escalation platform for complex categories, sitemap discovery, or benchmark comparison, not as the default ingestion engine.

Sources:
- [Firecrawl changelog](https://www.firecrawl.dev/changelog)
- [Skill and CLI announcement](https://www.firecrawl.dev/blog/introducing-firecrawl-skill-and-cli)
- [Advanced scraping guide](https://docs.firecrawl.dev/advanced-scraping-guide)
- [Change tracking docs](https://docs.firecrawl.dev/features/change-tracking)

### Zyte

FACT:
- Zyte API automatic extraction supports AI-powered extraction for `product`, `productList`, `article`, `articleList`, `jobPosting`, and custom attributes.
- Zyte docs explicitly note `extractFrom=httpResponseBody` as usually faster and cheaper than browser-based sources.

INTERPRETATION:
- Zyte fits this repo as a targeted extraction fallback when structured outputs or anti-bot recovery matter more than owning the whole browser path.
- It is especially relevant if we later want product-style normalized outputs from difficult partner/vendor sources.

Sources:
- [Automatic extraction](https://docs.zyte.com/zyte-api/usage/extract/index.html)
- [Custom attributes extraction](https://docs.zyte.com/zyte-api/usage/extract/custom-attributes.html)

### curl_cffi

FACT:
- Current docs show broad impersonation support including newer Chrome, Safari, Firefox, and Tor targets.
- The project highlights browser-signature impersonation, HTTP/2 support, async support, and performance competitive with lower-level clients.

INTERPRETATION:
- `curl_cffi` is the best low-cost "middle rung" for this repo.
- It should be tried before shipping a full-time browser bot whenever the page content is still server-delivered but anti-bot behavior blocks ordinary clients.

Sources:
- [curl_cffi overview](https://curl-cffi.readthedocs.io/en/v0.7.0/index.html)
- [Supported impersonation targets](https://curl-cffi.readthedocs.io/en/latest/impersonate/targets.html)

## Best Methods For This Project

1. Start from category pages, not homepages.
2. Use HTTP-first extraction on listing grids and detail pages.
3. When grids are dynamic, trace them once in Playwright and replay the actual API or XHR path.
4. Use `curl_cffi` before a full browser when the issue is fingerprinting, TLS, or HTTP/2 behavior.
5. Keep browser automation as a recovery or discovery tool, not the default pipeline.
6. Use managed platforms only where they clearly beat local maintenance cost.
7. Store raw evidence, normalized JSON, and media metadata so debugging stays reproducible.

## Recommendation For Bulgaria Real Estate MVP

### Default local stack
- `httpx`
- `curl_cffi`
- `selectolax`
- `lxml`
- `beautifulsoup4`
- `pydantic`
- `playwright`

### Add when complexity rises
- Crawlee for browser queueing and retry orchestration
- Browserbase or Firecrawl for agentic or remote browser fallback
- Zyte for structured managed extraction

### What not to do
- Do not default every difficult source to Playwright.
- Do not default every source to a paid managed browser.
- Do not rely on homepage scraping when category and detail routes are available.
- Do not put binary images directly into hot relational tables unless there is an explicit archival reason.

## Repo Outputs Added From This Research

- `agent-skills/hybrid-scrape-stack/SKILL.md`
- `agent-skills/managed-scrape-platforms/SKILL.md`
- `agent-skills/universal-agent-scrape-setup/SKILL.md`
- `docs/exports/universal-agent-scrape-setup-2026-04-20.md`

