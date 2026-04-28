# Skill: OpenClaw Ollama Gemma4 (offline QA + report drafting)

## When to use

Use this skill when the operator explicitly wants **Gemma4 via Ollama** to handle tasks that are:

- **offline/local** (no live crawling, no private data access),
- primarily **analysis, QA, summarization, or report drafting**, and
- based on existing repo artifacts such as:
  - `docs/exports/*`
  - `docs/dashboard/*`
  - `data/scraped/*`
  - `data/media/*`
  - `sql/helpers/*`

Examples:

- Summarize scrape-status dashboards into a short operator report.
- Draft SQL queries to validate per-source counts in `canonical_listing`.
- Produce a Markdown “image report” draft for a listing given a set of local image paths + listing metadata JSON.

## Hard constraints (non-negotiable)

- Follow `AGENTS.md` guardrails.
- Treat `data/source_registry.json` as authoritative for `legal_mode`, `risk_mode`, and `access_mode`.
- Do **not** add live-network dependencies to tests.
- Do **not** propose or automate private social/messenger scraping.
- Do **not** handle secrets (API keys) beyond saying “set env var locally”.

If asked about legality/compliance: point to `data/source_registry.json` + `AGENTS.md` and stop.

## Required inputs from the operator

To run a Gemma4 task safely, require:

- **Exact file paths** to read (or the precise directory scope).
- The **desired output format** (Markdown / JSON / SQL).
- The **intended destination path** in-repo if writing an artifact.

## Standard workflow

1. Confirm the task is offline/local and within guardrails.
2. Read only the provided inputs; do not crawl the web.
3. Produce an output that is:
   - structured,
   - reproducible,
   - includes known gaps, and
   - includes confidence where interpretation is involved.

## Output contracts

### A) Scrape-status summary (Markdown)

Must include:

- time window (from artifact timestamp)
- top 3 sources by saved count
- sources with **low full-gallery** vs saved count (e.g. remote > local photo count)
- recommended next operator command (only from existing `make` targets)

### B) SQL validation bundle

Must include read-only queries to compute:

- `canonical_listing` rows by `source_name`
- `listing_media` completion ratios (where present)

### C) Image report draft

Only allowed when all image inputs are local files.

- Per-listing summary (style, condition, layout cues, colors, equipment/tools)
- Per-image entries in order with `scene_type`, observations, risks, confidence

Never invent unseen features; mark unclear items explicitly.

