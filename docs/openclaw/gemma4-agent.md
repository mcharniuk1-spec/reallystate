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
- **Four-bucket tier-1/2 source reporting** for `Address.bg`, `BulgarianProperties`, `Homes.bg`, `imot.bg`, `LUXIMMO`, `property.bg`, and `SUPRIMMO` across buy residential, buy commercial, rent residential, and rent commercial.
- **Reporting pack review** using `docs/exports/reporting-and-instruction-index.md` and the generated DOCX files before operator handoff.

### 2) Hard guardrails (must follow)

These mirror `AGENTS.md` and project safety gates:

- Treat `data/source_registry.json` as the authoritative source/legal matrix.
- Do not propose or automate scraping of private messaging/social sources without explicit consent and a consent-gated design.
- Do not add live-network dependencies to tests.
- Do not attempt account creation, CAPTCHA bypass, or KYC bypass.
- Do not run or widen tier-1/2 scraping unless the operator explicitly sends **`Action1 ACCEPT`** (or legacy `Action1 now`) and the task is scoped to `S1-22B`. For offline passes, consume Codex-prepared eligible listing sets and generate image reports plus per-property QA only.
- For every apartment report, check photo coverage, ordered image descriptions, scraped description match, price/size plausibility, source links, and building-match status. Use `GET /api/property-quality/<encoded reference_id>` when the local website is running, or replicate that contract offline.
- Before accepting any row as a single property item, check whether the source page is a single-unit publication or a mixed/development publication. Terms such as `1-2 bedroom`, `apartments (various types)`, `selection of`, `prices from`, whole residential building/development pages, and multiple unit tables mean `suspected_multi_unit_publication` unless unit-level URL, price, area, and media evidence exists.
- Do not treat numeric `0` as a real price. Preserve `on request` or `undefined` as a price status in the report/provenance and mark the listing for parser repair if the source showed that state but the saved data lost it.
- Do not claim building-level geospatial precision until an OSM/PostGIS building footprint match exists.
- Do not invent missing rooms, furniture, colors, damage, floorplans, or tools. If a visual element is uncertain, write `unclear` and include a confidence value.
- If a task involves “is this legally OK?”, answer: **“Check `legal_mode` and `risk_mode` in `data/source_registry.json` and follow `AGENTS.md`.”**

### 3) Required context inputs

When you hand a task to this agent, include:

- **Exactly what artifact(s)** to read and output format desired.
- The **source key** (if source-specific), e.g. `olx_bg`, `imot_bg`.
- Whether the output is **operator-only** or **committable**.
- For image-report work: the exact eligible listing JSON files, local image file list, property-quality check output, and output directory under `docs/exports/apartment-image-reports/`.

### 3.1) Current Action0 / Action1 / Action2 sequence (**operator gate 2026-04-30**)

This is the active OpenClaw/Gemma4 execution contract.

1. **Always** load Action0 + Action1 + Action2 text from `docs/exports/taskforgema.md` in the operator prompt so the model never claims it is waiting for new URLs/patterns.
2. **Do not execute** Action0 or Action2 (no report writes / no extra-source scrapes) until the operator sends **`Action1 ACCEPT`**.
3. **After `Action1 ACCEPT`**: run **Action1 (`S1-22B`)** first — seven sources × four buckets, legal gates on, detached runner when needed.
4. **Telegram cadence**: after every **+100 net new** saved listing JSON rows across the seven Action1 sources, send a **7×4** matrix (counts + full-gallery % + avg description chars) plus top errors — use `make action1-matrix-snapshot` on the host for an honest table.
5. **Action0 (`S1-22A`)**: only after **`Action0 now`** following Action1 completion (unless a parallel waiver is logged in `docs/agents/scraper_1/JOURNEY.md`).
6. **Action2 (`S1-22C`)**: only after **`Action2 now`** + Action1 QA.

#### Action0 — local-gallery image reports

- **Task ID**: `S1-22A`
- **Input**: `docs/exports/s1-21-gemma-action0-eligible.json`
- **Supporting files**: `docs/exports/taskforgema.md`, `docs/exports/s1-21-tier12-quality-audit-2026-04-29.json`, `docs/exports/property-quality-and-building-contract.md`, `data/scraped/*/listings/*.json`, `data/media/`
- **Do**: generate one Markdown and one JSON property image report per eligible row, using already-downloaded local images only.
- **Also required**: for each property item, include a **single-property validity** decision with:
  - `single_property_ok` (boolean)
  - `single_property_comment` (why)
  - `mismatch_notes` (photo/description/category/price mismatches)
- **Output**: `docs/exports/property-image-reports/<source_key>/<safe_reference_id>.md` and `.json`, plus `docs/exports/property-image-reports/index.md` and `index.json`.
- **Forbidden in Action0**: no live scraping, no remote image analysis except as a documented gap, no widening source scope.

#### Action1 — seven-source all-Bulgaria scrape/backfill

- **Task ID**: `S1-22B`
- **Scope**: `Address.bg`, `BulgarianProperties`, `Homes.bg`, `imot.bg`, `LUXIMMO`, `property.bg`, `SUPRIMMO`
- **Buckets**: `buy_personal`, `buy_commercial`, `rent_personal`, `rent_commercial`
- **Do**: run/backfill **all Bulgaria** for the seven scoped sources and **do not stop early** until the run reaches its configured stop condition (target counts or wave budgets). Save all accepted source publications with full text, structured fields, bucket evidence (`bucket_key` / `segment_key`), price status, source links, remote image URLs, downloaded local image files, parse warnings, and media validity.
- **Output**: refreshed `data/scraped/`, `data/media/`, source/bucket logs, dashboards, and coverage exports.
- **Forbidden in Action1**: do not include remaining tier-1/2 sources; do not scrape legal-review/licensing/private sources.

#### Action2 — remaining legal tier-1/2 expansion

- **Task ID**: `S1-22C`
- **Scope**: only remaining tier-1/2 sources allowed by `data/source_registry.json`.
- **Do**: after Action1 QA, repeat the scrape/backfill and image-report process for additional legal tier-1/2 sources.
- **Forbidden in Action2**: no `legal_review_required`, `licensing_required`, private/social/messenger-only, or blocked `access_mode` sources without separate operator/legal approval.

Debugger verifies the handoff with `DBG-08` after each action that changes outputs.

### 3.2) Required report fields per property

Each property report must include:

- listing identity: `reference_id`, source name, source links, local listing JSON path, and local image files used
- structured facts: price, currency, size, rooms/floor when present, category, service type, city/district/address
- source-text summary: page title, scraped description, structured attributes, and combined text
- image report: one ordered description per image, plus a grouped visual summary
- visual content: style, colors, apparent condition, layout/planning clues, visible tools/equipment/appliances/furniture, and exterior/building context when visible
- QA checks: photo-count match, description-image consistency, price/size plausibility, category consistency, source-link availability, and uncertainty/confidence
- gaps: anything missing or unclear; do not invent missing attributes

### 4) Ollama environment (operator responsibility)

This doc does not install Ollama for you; it defines the expectation.

Typical checks:

```bash
ollama --version
ollama list
ollama pull gemma4
```

If OpenClaw calls Ollama over HTTP, ensure the daemon is running and reachable (defaults vary by setup).

### 4.1) OpenClaw timeout requirement (important for long runs)

If the agent returns “couldn’t generate a response” or appears to hang, the most common cause is an Ollama/provider timeout. Set a long timeout and restart the gateway:

```bash
openclaw --profile codex config set models.providers.ollama.timeoutSeconds 3600
openclaw --profile codex gateway restart
openclaw --profile codex gateway probe
```

### 4.2) Telegram progress reporting

For this project, the operator chat id used for progress updates is `181488201`.

Send a manual ping:

```bash
openclaw --profile codex message send --channel telegram --target 181488201 --message "ping" --json
```

When you instruct Gemma4 to run Action0/1/2, require periodic updates to that chat id with counts and blockers.

### 5) Prompt template (copy/paste)

Use this template to keep Gemma4 focused and safe:

```text
ROLE: OpenClaw Gemma4 (scrape QA / report generation)
ACTION:
- Run exactly one named action: Action0, Action1, or Action2.
CONSTRAINTS:
- Follow AGENTS.md, docs/agents/TASKS.md, docs/exports/taskforgema.md, and data/source_registry.json.
- Do not reorder Action0, Action1, and Action2 unless the operator explicitly says so.
- Action0 uses only already-downloaded local images from docs/exports/s1-21-gemma-action0-eligible.json.
- Action1 is only the seven-source all-Bulgaria scrape/backfill across four buckets.
- Action2 is only remaining legal tier-1/2 expansion after Action1 QA.
- Run or replicate property-quality checks before marking a listing/report complete.
INPUTS:
- Files: <list exact paths>
- Goal: <what to produce>
OUTPUT:
- Provide: <files written>, <counts>, <skip reasons>, <QA warnings>, <confidence>, <known gaps>
GUARDRAILS:
- Follow AGENTS.md + data/source_registry.json legal_mode/risk_mode/access_mode.
```
