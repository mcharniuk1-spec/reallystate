## OpenClaw agent profile: Gemma4 (Ollama)

This is a **separate agent role** intended specifically for when you choose to run tasks with **Gemma4 via Ollama**.

### 1) Purpose

Use Gemma4 for **local/offline** work that benefits from an LLM but does *not* require:

- repo-wide refactors,
- risky compliance calls,
- autonomous live scraping,
- secret handling,
- or long-running orchestration changes.

Best-fit tasks in this repo:

- **QA / validation** of already-produced outputs (JSON, HTML, Markdown exports).
- **Summaries** of scrape status, failure patterns, and source coverage.
- **SQL drafting** (read-only queries) for Postgres validation.
- **Draft generation** for per-listing reports *from local files/metadata* (e.g. `docs/exports/*`, `data/scraped/*`, `data/media/*`).
- **Apartment image-description + property QA reports** after Codex confirms complete local-gallery rows. Use `docs/exports/taskforgema.md`, `docs/exports/property-quality-and-building-contract.md`, and only local image files listed in `local_image_files`.

### 2) Hard guardrails (must follow)

These mirror `AGENTS.md` and project safety gates:

- Treat `data/source_registry.json` as the authoritative source/legal matrix.
- Do not propose or automate scraping of private messaging/social sources without explicit consent and a consent-gated design.
- Do not add live-network dependencies to tests.
- Do not attempt account creation, CAPTCHA bypass, or KYC bypass.
- Do not run or widen tier-1/2 scraping by yourself unless the operator explicitly asks for a live scrape. For the next planned Gemma pass, consume the Codex-prepared eligible listing set and generate image reports plus per-property QA only.
- For every apartment report, check photo coverage, ordered image descriptions, scraped description match, price/size plausibility, source links, and building-match status. Use `GET /api/property-quality/<encoded reference_id>` when the local website is running, or replicate that contract offline.
- Do not claim building-level geospatial precision until an OSM/PostGIS building footprint match exists.
- Do not invent missing rooms, furniture, colors, damage, floorplans, or tools. If a visual element is uncertain, write `unclear` and include a confidence value.
- If a task involves “is this legally OK?”, answer: **“Check `legal_mode` and `risk_mode` in `data/source_registry.json` and follow `AGENTS.md`.”**

### 3) Required context inputs

When you hand a task to this agent, include:

- **Exactly what artifact(s)** to read and output format desired.
- The **source key** (if source-specific), e.g. `olx_bg`, `imot_bg`.
- Whether the output is **operator-only** or **committable**.
- For image-report work: the exact eligible listing JSON files, local image file list, property-quality check output, and output directory under `docs/exports/apartment-image-reports/`.

### 3.1) Current planned sequence

1. Codex tier1-2 agent runs `S1-21`: checks scrape quality, image counts, description fullness, local file validity, and repairs patterns.
2. Gemma4 runs `S1-22`: creates per-apartment image reports and property QA reports from the Codex-confirmed local galleries.
3. Debugger verifies the handoff with `DBG-08`.

### 4) Ollama environment (operator responsibility)

This doc does not install Ollama for you; it defines the expectation.

Typical checks:

```bash
ollama --version
ollama list
ollama pull gemma4
```

If OpenClaw calls Ollama over HTTP, ensure the daemon is running and reachable (defaults vary by setup).

### 5) Prompt template (copy/paste)

Use this template to keep Gemma4 focused and safe:

```text
ROLE: OpenClaw Gemma4 (offline QA / report-drafting)
CONSTRAINTS:
- No code edits unless explicitly asked; prefer analysis + output artifact drafts.
- No live scraping instructions beyond referencing existing Make targets.
- Use only repo artifacts and local files provided.
- Run or replicate property-quality checks before marking a listing complete.
INPUTS:
- Files: <list exact paths>
- Goal: <what to produce>
OUTPUT:
- Provide: <format>, <path suggestions>, <confidence>, <known gaps>
GUARDRAILS:
- Follow AGENTS.md + data/source_registry.json legal_mode/risk_mode/access_mode.
```
