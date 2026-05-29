# Agent Task Queue

Single source of truth for **what to do next** per specialist agent.

**Rules** (see `docs/agents/README.md` for the full protocol):

- One active slice per agent at a time.
- When done, set status to `DONE_AWAITING_VERIFY` and wait for the verifier.
- When verified, verifier sets status to `VERIFIED`.
- If blocked, record the blocker (points to another slice ID) and propose an alternative.
- Append a journal entry to `docs/agents/<agent>/JOURNEY.md` after every slice (done or blocked).

**Statuses**: `TODO` → `IN_PROGRESS` → `DONE_AWAITING_VERIFY` → `VERIFIED` / `BLOCKED`

**Goal**: Working website at `https://bgrealestate.vercel.app` (frontend) + `https://bgrealestate-api.up.railway.app` (backend) with live scrapers, unified database, map, shop view, user profiles, and admin dashboard.

**Hosting stack**: Railway (PostgreSQL+PostGIS, Python backend, scraper workers) + Vercel (Next.js frontend) + GitLab CI/CD.

## Session backlog context digest (2026-04-08)

This digest captures the full operator intent and execution context from the latest orchestration chat so no agent loses strategic direction between activations.

### A) Locked scope and product intent

- Build a LUN-style, buyer-oriented marketplace with map + feed + AI chat.
- Owners are the primary posters; agency participants are represented as owner representatives.
- MVP **3D / building-data** focus may remain Varna-first (BD-08 / UX-07); **map + listings browse UX (`UX-04`)** is **nationwide Bulgaria** (all regions/cities), not Varna-only.
- Scraping/output must feed a continuously updated database with canonical unification and exports.

### B) Agent governance and runtime behavior

- Parallel lanes are required; dependencies are enforced at slice level.
- Tier ownership is strict after the 2026-05-05 reset:
  - `planner`: cross-agent task sequencing, dependency control, OpenClaw handoff clarity
  - `backend_developer`: database, API, persistence, orchestration/runtime
  - `data_analyst`: scraped-corpus QA, inconsistency detection, source/bucket metrics, dashboard truth
  - `scraper_1`: tier-1/2 marketplace website connectors and patterns
  - `scraper_sm` (**S&M**): tier-3 vendor/partner/official intelligence routes plus tier-4 social/messenger overlays
  - `ux_ui_designer`: frontend/operator UI only
  - `debugger`: acceptance gates, safety, regression verification
- `scraper_t3` is now a historical log lane. Do not assign new work there; migrate any unverified tier-3 follow-up into `scraper_sm` / S&M.
- No slice is complete before verifier promotion to `VERIFIED`.
- Non-stop continuation is mandatory for every agent:
  - continue to next unblocked slice after each completion
  - stop only on `END`, no unblocked slices, or real blocker
  - when idle, ask: `Which <agent_name> task should I execute next?`

### C) Session deliverables already completed

- Business/model outputs completed:
  - `docs/business/unit-economics-market-analysis.md`
  - `docs/business/product-ux-structure.md`
  - `docs/business/varna-3d-osm-integration.md`
  - `output/pdf/investor-presentation-2026-04-08.pdf`
- Backlog enriched with new backend/frontend/scraper/debugger/lead slices for deployment-ready execution.
- Dashboard reliability issue fixed (embedded payload support for local `file://` opens) and dashboard regenerated.

### D) Immediate execution priorities (2026-04-09 — operator lock-in)

**Single focus lane until the volume gate is met:** `scraper_1` tier-1/2 live harvesting. Other specialists **do not start new non-blocking slices** except the narrow backend prerequisite below and recurring `CONST-*` hygiene.

1. **`scraper_1` — non-stop until volume gate (see `S1-18`)**
   Implement/complete live HTTP + discovery + detail ingest (`S1-15`), then **continue running harvests without pausing for “slice done”** until **at least 5 distinct tier-1 or tier-2 sources** each have **≥100** persisted listing rows (see `S1-18` for counting rules).

2. **`backend_developer` — prerequisite only until `S1-18` is met**
   **`BD-11` is the mandatory prerequisite** so live scrapes can land in `canonical_listing` (and related tables) for auditable counts. **Do not** treat `BD-12`–`BD-16` as in-scope for the same sprint wave as `S1-18` unless they unblock ingest. After `S1-18` is `VERIFIED`, resume the backend chain: `BD-12` → `BD-13` → `BD-14` → `BD-15` → …

3. **`debugger` — planned after backend chain catches up**
   - **`DBG-06`**: batch-verify all `DONE_AWAITING_VERIFY` slices **after** `S1-18` is `VERIFIED` and **`BD-11` ingest is proven** on live rows (or operator explicitly waives DB counts — document in JOURNEY).
   - **`DBG-05`**: stage-1 quality gate (fixtures + product types per `docs/exports/stage1-product-type-coverage.md`) **after** live volume evidence exists or is explicitly deferred.

4. **Parked (do not expand until `S1-18` VERIFIED):** new S&M live tier-3/tier-4 work, LUN-style UX expansion (`UX-04`–`UX-12`), and deployment slices — unless they fix a blocker for tier-1/2 ingest.

5. **Recurring:** `CONST-01` / `CONST-02`, `LEAD-05` dashboard refresh after any TASKS/JOURNEY change.

**Fixture / stage-1 analysis (no live DB):** `docs/exports/stage1-product-type-coverage.md` — all required product types (`sale`, `long_term_rent`, `short_term_rent`, `land`, `new_build`) are covered by tier-1/2 fixtures; this is **parser readiness**, not production volume.

### E) Current Gemma/OpenClaw execution order (2026-04-29, **operator gate 2026-04-30**)

The next OpenClaw/Gemma4 run must use the action split below. **Load Action0 + Action1 + Action2 context in every prompt**, but **do not execute** Action0 or Action2 until the operator sends **`Action1 ACCEPT`** (then run Action1 live scrape first). See `docs/exports/taskforgema.md` § *Operator acceptance gate* for Telegram cadence (**+100 net new saves → 7×4 matrix**; host shortcut `make action1-matrix-snapshot`).

1. **Action1 / `S1-22B`**: scrape/backfill the seven priority all-Bulgaria tier-1/2 sources across the four buckets `buy_personal`, `buy_commercial`, `rent_personal`, and `rent_commercial` — **first executable action after `Action1 ACCEPT`**.
2. **Action0 / `S1-22A`**: generate property image reports from already-downloaded local galleries using `docs/exports/s1-21-gemma-action0-eligible.json`. No live scraping — run only after operator **`Action0 now`** following Action1 completion (unless a parallel waiver is logged in `docs/agents/scraper_1/JOURNEY.md`).
3. **Action2 / `S1-22C`**: after Action1 QA, expand the same process to remaining legal tier-1/2 sources from `data/source_registry.json` — run only after operator **`Action2 now`**.

Gemma/OpenClaw must not reorder these actions unless the operator explicitly says to skip or start a specific action.

## Agent reset and active operating model (2026-05-05)

**FACT — current OpenClaw/A1 state:** Action1/A1 is the seven-source marketplace scrape group: `Address.bg`, `BulgarianProperties`, `Homes.bg`, `imot.bg`, `LUXIMMO`, `property.bg`, `SUPRIMMO`. OpenClaw is not the scraper implementation; it is the scraper **operator/monitor** that reads repo instructions, starts approved Make targets, watches logs, reports Telegram status, and asks Qwen/DeepSeek for bounded fixes.

**INTERPRETATION — efficiency issue:** prior coordination split tier-3 and social into separate live lanes while Action1 still had QA/media/inconsistency debt. New work must reduce context drift: one planner, one data analyst, one backend owner, one front-end owner, one tier-1/2 scraper owner, one S&M intelligence owner, and one debugger.

**Required active agents:**

| Agent | Active responsibility | Stop condition |
|-------|------------------------|----------------|
| `planner` | Keep this task queue, dependencies, OpenClaw order, and handoffs consistent. | All active slices have one clear owner and verifier. |
| `backend_developer` | DB/API/import/runtime support for scraped source publications and canonical listings. | DB/import path and APIs match scraper QA contracts. |
| `data_analyst` | File-backed and DB-backed corpus QA: good/bad/grouped/LOST, image/description/price/location consistency, source/bucket metrics. | A1 quality report and dashboard counts are reproducible from artifacts. |
| `scraper_1` | Tier-1/2 code patterns and live scraping routes. Finish Action1 before Action0/Action2 unless operator overrides. | A1 source/bucket scraper gaps are fixed or explicitly blocked. |
| `scraper_sm` / **S&M** | Tier-3 official/vendor/partner routes and tier-4 social/messenger overlays; monitor-only unless legal/consent gates pass. | S&M outputs are fixture-first, consent-safe, and never mixed into A1 marketplace completeness. |
| `ux_ui_designer` | Frontend/dashboard truth surfaces only; no data claims not backed by analyst/debugger artifacts. | UI shows accepted/LOST/grouped/media states correctly. |
| `debugger` | Verify every agent output; run parser/QA/import smoke gates; block unsafe imports/exports. | Slice is `VERIFIED` or has a concrete blocker. |

**Action1 continuation rule:** OpenClaw/S&M/scraper runs must resume from persisted files and logs, not chat memory. For A1 full backfill use `SCRAPER_PAGE_ORDER=oldest_first` and the uncapped Action1 target so the runner scans the older pages in the currently visible window before newer pages, then repeats wider waves. The runner must record `before_count`, `after_count`, `added_count`, `max_pages`, and parser/media warnings per wave. Do not claim "finished Action1" until debugger verifies all seven A1 sources across all four buckets with accepted/good, grouped, LOST, inactive, media, and description counts.

**Sequence lock:** Finish Action1/A1 QA first. Then run Action0 local image-description reporting only after `Action0 now`. Then run Action2 remaining legal tier-1/2 sources only after `Action2 now` and Action1 QA.

---

## 2026-05-13 architecture rebuild and server-migration preparation

**FACT**: `plan 13.05.md` requires safe git hygiene, stronger agent architecture, role-specific MDs, skills/MCP setup guidance, and preparation for the next server/DB migration step.

**INTERPRETATION**: The existing agent system should be extended, not replaced. Existing lanes remain active; new support lanes cover release, infrastructure, market intelligence, user analytics, media vision, entity resolution, and knowledge capture.

**GAP**: Remote server/SSH credentials and live DB counts are not available yet, so migration is prepared as a runbook and Make targets, not executed.

## 2026-05-13 planner handoff while `data_analyst` is active

**FACT**: `data_analyst` is the active evidence owner for Action1/A1 corpus truth, dashboard denominators, and accepted/LOST/grouped/media counts. `DA-01` is verified as file-backed only; DB-backed counts remain blocked by missing `DATABASE_URL` and `BD-18`.

**INTERPRETATION**: backend, scraper, UX, infra, and knowledge work may prepare contracts and fixes, but must not promote claims from chat or raw corpus volume. Use `DA-02` / `DA-03` outputs as the next dashboard-count evidence before UI or release claims.

**GAP**: the current scraped corpus is dirty and moving; do not touch scraped DB/corpus directly in planner/debugger/UX/infra runs.

**Active dependency map**:

- `BD-18` depends on `DA-01` plus unresolved `BD-11` verification/live-DB proof; it must preserve analyst QA states before any canonical import.
- `BD-19` depends on `BD-18` + `DA-02` and must expose DB-backed QA/read-model counts only after import proof.
- `ER-01` is a planning-only entity-resolution contract; `ER-02`/`ER-03`/`ER-04` and `BD-21` must wait for accepted source-publication import/read-model proof before generating candidates.
- `S1-23` / `S1-24` depend on analyst queues and must not widen Action2 before Action1 QA repair.
- `UX-15` captures expected DA-driven UX requirements now; implementation slices `UX-16`/`UX-17`/`UX-18` depend on `DA-02`, `BD-18`, and `BD-19` so UI does not invent counts.
- `INFRA-02` depends on `INFRA-01`, `BD-18`, and analyst count artifacts; it verifies DB counts, not scrape quality.
- `KCA-01` captures durable run/memory/insight only after analyst/verifier outputs exist.
- `DBG-15` verifies this handoff and `DBG-16` verifies downstream DA-dependent implementation slices.

**Handoff list**:

- `backend_developer`: start with `BD-18` prep, but do not claim canonical DB import until `BD-11`/DB fixture proof is verified; prepare `BD-19` only after analyst dashboard semantics are final; `BD-21` waits for ER accepted-only candidate contracts.
- `entity_resolution_agent`: ER planning may define accepted-only matching contracts now; candidate generation waits for `BD-18`, `BD-19`, `DA-02`, and `BD-21`.
- `scraper_1`: start with `S1-23`; execute `S1-24` only from analyst queues.
- `ux_ui_designer`: prepare `UX-15` requirements now, then wait for `DA-02`/`BD-18`/`BD-19` before implementing data-quality surfaces.
- `infra_db_operator`: wait for credentials plus `BD-18`, then execute `INFRA-02` DB count verification.
- `knowledge_context_agent`: run `KCA-01` after analyst/verifier outputs are stable; update wiki under strict filters.
- `debugger`: run `DBG-15` now; run `DBG-16` when producing agents hand off DA-dependent slices.

## 2026-05-13 whole-project plan and four-dashboard operating model

**FACT**: Multiple agents concluded planning/evidence slices on 2026-05-13. Current durable outputs include DA-01, DBG-15, BD-18 prep notes, MI-01, UX-15, OPS-02, INFRA-02 readiness notes, ER-01, VM-01, UA-01, SM-10/13, and KCA-01. Several are `DONE_AWAITING_VERIFY`, not complete.

**INTERPRETATION**: The project should run as four explicit operator dashboards plus one task queue: (1) Project Progress with all agent subsections, (2) Properties Database with scraping/description/media/accepted evidence, (3) Website with public/admin UI gates, and (4) Support with release/infra/analytics/media/entity-resolution/knowledge/debugger assistance. The dashboards summarize reproducible artifacts; they must not become new sources of truth.

**HYPOTHESIS**: Once DA-02 reconciles denominators and BD-18 proves accepted-only import, UX/admin queues can move faster because all labels and counts will have stable semantics.

**GAP**: DB-backed count proof, dashboard coverage generator performance (`DA-03`), and operator-gated Action0 media processing remain unresolved.

**Four-dashboard contract**:

- Project Progress dashboard: all agents, slice status, verifier queue, critical path, latest agent insights, and handoff details.
- Properties Database dashboard: saved rows, accepted/good rows, `LOST`, grouped/development, descriptions, local/readable media, Action1 scope, denominator warnings, and source-level details.
- Website dashboard: Next.js route readiness, admin/public UX gates, backend read-model dependencies, public accepted-only rule, and product-surface blockers.
- Support dashboard: release, infrastructure, market intelligence, analytics, vision media, entity resolution, S&M, knowledge capture, and debugger operational queues.

**Updated critical path**:

1. `debugger`: verify concluded docs/contracts in batches (`DBG-16`, `DBG-21`, `DBG-22`, new dashboard verifier) while keeping runtime/DB gates separate.
2. `data_analyst`: execute `DA-02` denominator contract and `DA-03` dashboard performance repair; no UI/public count claim advances without these.
3. `backend_developer`: finish `BD-18` accepted-only import/schema proof, then `BD-19` QA read model; keep file-backed artifacts authoritative until DB proof passes.
4. `infra_db_operator`: keep `INFRA-02` blocked until real DB URLs/credentials and `BD-18` proof exist; then verify count parity only.
5. `scraper_1`: execute `S1-23` and `S1-24` only from analyst queues; do not widen to Action2 or touch social/private routes.
6. `ux_ui_designer`: implement `UX-16`/`UX-18` only after DA/BD count semantics exist; until then, keep dashboard/admin labels contract-only.
7. `entity_resolution_agent`: advance `ER-02`/`ER-03` contracts only after accepted-only import/read-model proof; no auto-merge or public promotion.
8. `vision_media_agent`: keep `VM-02` blocked until operator `Action0 now`; define promotion/readiness fields through `VM-03` after DA/BD gates.
9. `market_intelligence_analyst`: run `MI-02` only from accepted-only evidence; no market coverage claims from raw scrape volume.
10. `user_analytics_agent`: run `UA-02` after `BD-13`/`BD-17`/`BD-19`/`UX-15` contracts stabilize; keep payloads PII-free.
11. `scraper_sm`: keep S&M route work consent-safe and separated from Action1 marketplace completeness; do not mix social/vendor observations into accepted property counts.
12. `ops_release_manager`: use `OPS-02` checklist; block release notes until DA/BD/INFRA/debugger evidence is cited by artifact path.
13. `knowledge_context_agent`: record run/log/insight closeouts after each verified planning or dashboard change; do not write raw scrape facts into memory.
14. `planner`: maintain this dependency chain, dashboard contract, and verifier queues; do not touch scraped DB/corpus directly.

## 2026-05-14 planner reconciliation after product prompt pack section 1

**FACT**: `PLAN-08` and the full product/website prompt pack are verified for planning safety only. `DBG-25` still blocks public website readiness on claim-neutral copy, Codex hook/export predicate drift, frontend typecheck completion, and missing DB-backed proof. `DA-07` produced a bad-scrape review pack and tightened the public export to 1,606 accepted single-unit rows, but `S1-23` / `S1-24` remain the next unexecuted repair work.

**INTERPRETATION**: The next productive task is a working `scraper_1` repair wave over the existing Action1/A1 sources, not more product expansion. Entity-resolution and DB/operator work should consume the repaired accepted-only evidence after scraper fixes reduce bad, grouped, pending, media-gap, and parser-error states.

**HYPOTHESIS**: Once `S1-23` produces fixture-backed parser/media/contact fixes and a bounded `S1-24` repair wave, `ER-03` / `ER-04` and `BD-18` / `INFRA-02` can advance with fewer false-merge and import-blocker cases.

**GAP**: PostgreSQL count proof remains blocked by missing `DATABASE_URL`; public website readiness remains blocked by `UX-24`, `DBG-27`, `DBG-28`, and DB-backed accepted-only read-model verification.

**Immediate next sequence**:

1. `scraper_1`: execute `S1-23`, then `S1-24` if unblocked. Scope is Action1/A1 only: `Address.bg`, `BulgarianProperties`, `Homes.bg`, `imot.bg`, `LUXIMMO`, `property.bg`, `SUPRIMMO`. Fix badly scraped rows before any Action2 widening.
2. `entity_resolution_agent`: after scraper repair evidence is refreshed, run `ER-03` scoring matrix and then `ER-04` review policy. Do not generate candidates or promote canonical property entities until accepted-only DB/read-model proof exists.
3. `infra_db_operator` + `backend_developer`: resume `BD-18` / `INFRA-02` DB proof only when a libpq-compatible `DATABASE_URL` is available; keep import source-publication-first and accepted-only.
4. `debugger`: batch-verify `S1-23`/`S1-24`, `DA-07`/`DBG-27`, `BD-22`/`DBG-28`, and any DB proof. Do not mark public readiness or Action1 completion before these gates pass.

**Dashboard rule**: planner/doc-only closeouts use `make operational-dashboard-doc`. Full `make dashboard-doc` remains DA-03/full-corpus work unless the run explicitly targets source/photo coverage repair.

## 2026-05-15 operator correction wave

**FACT**: The operator reported broken/weak website operability, including profile/chat/settings interactions, property detail opening, unclear scraped names, area/square-meter fields not prominent enough, weak filters under the map, unsupported 3D-map expectations, bad map placement such as Burgas points in the sea, and confusing aggregation over non-identical properties.

**FACT**: Current safe public website data remains the DA-07 accepted-only file-backed export with 1,606 rows. The broader scraped corpus is dirty and cannot be treated as public inventory or canonical property truth without DA/BD/debugger gates.

**INTERPRETATION**: Run two agents at a time. Wave 1 handles visible UI operability and operator-facing XLS evidence. Wave 2 repairs scraper/parser/entity-resolution contracts from that evidence. Wave 3 wires backend/read-model/profile publishing surfaces after evidence contracts are stable. Debugger verifies each wave before promotion.

**GAP**: True satellite/relief/3D map provider, exact building footprints, semantic image descriptions, DB-backed counts, and geocode correction at national scale are not yet proven.

**Communication board**: `docs/agents/COMMUNICATION.md` and `docs/agents/communication/2026-05-15-wave1.md`.

**Execution waves**:

1. Wave 1A/B in parallel:
   - `UX-25`: website operability and area/filter/detail cleanup.
   - `DA-08`: operator XLS dataset review with transformation, geocode, aggregation, image/source evidence.
2. Wave 2A/B after Wave 1 handoff:
   - `S1-25`: scraper parser repair for clean title, area, source-derived categories, and location evidence on Action1 sources.
   - `ER-06`: accepted-only aggregation rule matrix: same street/city, same or close price, comparable area, similar description, source diversity, and no grouped/development rows.
3. Wave 3A/B after Wave 2 handoff:
   - `BD-23`: profile/publishing/read-model contract for owner/customer profiles and all incoming listing variables.
   - `VM-07`: media-description-to-property-metric contract, still blocked from semantic generation until `Action0 now`.
4. Verification:
   - `DBG-29`: browser/typecheck/XLS/safety verification for Wave 1.
   - Later debugger follow-ups verify Wave 2 and Wave 3.

## 2026-05-15 full-dataset active-audit correction

**FACT**: The operator rejected the prior audit/scraper/entity-resolution result as incomplete. Local artifacts confirm the concern: `S1-26` only generated a queue and stopped on low disk; `ER-07` used only `1,606` public-safe rows and had no completed active-link truth.

**INTERPRETATION**: The next run must audit the whole saved corpus first, property by property and URL by URL, before cleanup, broad patterned rescrape, or final entity resolution.

**GAP**: The system does not yet know which of the roughly 30k saved source publications are still active on source websites. The 1.6k public export is not a full-corpus answer.

**Active correction prompt pack**: `docs/exports/triagent-full-dataset-active-audit-clean-rescrape-prompts-2026-05-15.md`.

**Execution**:

1. `S1-27`: full saved-corpus active-link audit, reversible cleanup manifest, then patterned background rescrape after debugger PASS.
2. `ER-08`: entity resolution waits for active-link truth; ER-07 is preliminary/superseded for merge use.
3. `DBG-32`: concurrent guard/verifier with `gpt-5.5`, `xhigh`.

## 2026-05-29 property-link comparable search layer

**FACT**: The repo now has a bounded one-link intake and comparable-search path: `scripts/property_link_comparable_search.py`, pure scoring in `src/bgrealestate/matching/comparable.py`, docs in `docs/architecture/property-link-comparable-search.md`, and a project skill at `agent-skills/property-link-comparable-search/SKILL.md`.

**INTERPRETATION**: This is the operator workflow for “I give you one property URL; scrape/analyze that page; search all other tier 1/2/3 evidence for the same or comparable property.” It must remain separate from broad crawl activation and from automatic property-entity promotion.

**GAP**: The current implementation is file-backed by saved `data/scraped/**/listings/*.json` evidence. DB-backed endpoint, reviewed candidate persistence, and frontend operator review still need agent work after accepted-only DB proof.

**Immediate next sequence**:

1. `S1-28`: expand source-specific one-page parser proof for tier 1/2 sources that are missing reliable property fingerprints.
2. `DA-09`: build a known-good/known-bad evaluation set and threshold report for same-property and comparable-property matches.
3. `ER-09`: turn score output into reviewable `entity_resolution_candidate` rows after DB proof; do not auto-merge.
4. `BD-24`: add a DB/API contract for link-intake comparable search after `BD-18`/`BD-19` are verified.
5. `SM-17`: map tier 3 official/vendor/partner comparable evidence under contract/manual gates.
6. `UX-26`: design the operator candidate-review surface with score components and conflicts.
7. `DBG-33`: verify fixture-only tests, no live-network tests, no grouped promotion, no tier 3 legal bypass, and no stale public claims.

### PLAN-13: Property-link comparable search orchestration
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-29; file-backed implementation and cross-agent task pack added)
- **Priority**: **CRITICAL**
- **Read first**: `docs/architecture/property-link-comparable-search.md`, `agent-skills/property-link-comparable-search/SKILL.md`, `docs/agents/TASKS.md`
- **Do**: keep the one-link intake workflow separate from broad crawling and property promotion; route follow-up work to scraper, analyst, entity-resolution, backend, S&M, UX, and debugger lanes.
- **Acceptance gate**: `pytest tests/test_property_comparable_search.py` passes and follow-up slices exist for all impacted agents.
- **Output**: comparable-search script/module/docs/skill, task updates, planner journey entry.
- **Verifier**: debugger
- **Depends on**: PLAN-12

### S1-28: One-link parser fingerprint proof for comparable search
- **Status**: `TODO`
- **Priority**: **CRITICAL**
- **Read first**: `agent-skills/property-link-comparable-search/SKILL.md`, `scripts/property_link_comparable_search.py`, `scripts/live_scraper.py`, `data/source_registry.json`
- **Do**: add fixture-backed one-page parser proof for priority tier 1/2 sources; keep grouped/development pages source-publication-only; ensure fingerprints contain URL, ID, intent, category, location, price/status, area, description, and media evidence where available.
- **Acceptance gate**: parser fixtures pass without live network and comparable-search CLI parses each fixture.
- **Output**: fixtures, parser repairs, and source-specific blocker notes.
- **Verifier**: debugger
- **Depends on**: PLAN-13

### DA-09: Comparable-search evaluation set and threshold report
- **Status**: `TODO`
- **Priority**: **CRITICAL**
- **Read first**: `docs/architecture/property-link-comparable-search.md`, `docs/exports/data-quality-deep-review-2026-05-13.md`, `src/bgrealestate/matching/comparable.py`
- **Do**: build known same-property, comparable-not-same, and bad-pair fixtures from accepted rows; report false-positive risk by source family, city, category, media, and location gaps.
- **Acceptance gate**: reproducible JSON/MD report with no live network and no raw private contact values.
- **Output**: `docs/exports/comparable-search-evaluation-*.json` and `.md`.
- **Verifier**: debugger
- **Depends on**: PLAN-13

### ER-09: Comparable-search candidate persistence policy
- **Status**: `TODO`
- **Priority**: **CRITICAL**
- **Read first**: `docs/architecture/property-link-comparable-search.md`, `src/bgrealestate/matching/comparable.py`, `docs/exports/entity-resolution-accepted-only-candidate-layer-2026-05-13.md`
- **Do**: map `same_property_candidate`, `comparable_property`, and `weak_candidate` into reviewable candidate types; define what can become `entity_resolution_candidate` and what remains non-merge market comparable.
- **Acceptance gate**: policy distinguishes exact-identity evidence from market-comparable evidence and lists conflict blockers.
- **Output**: ER policy doc and follow-up implementation tasks.
- **Verifier**: debugger
- **Depends on**: PLAN-13, DA-09, BD-18

### BD-24: Link-intake comparable search API/read-model contract
- **Status**: `TODO`
- **Priority**: **HIGH**
- **Read first**: `docs/architecture/property-link-comparable-search.md`, `src/bgrealestate/matching/comparable.py`, `scripts/property_link_comparable_search.py`, `BD-18`, `BD-19`
- **Do**: define DB-backed endpoint contract after accepted-only import/read-model proof; preserve source-publication-first semantics; persist candidates only as reviewable evidence with score components and conflicts.
- **Acceptance gate**: API tests cover unavailable DB, grouped query page, accepted-only filtering, same-source exclusion, and no live-network test behavior.
- **Output**: endpoint/schema contract or implementation patch depending on `BD-18`/`BD-19` status.
- **Verifier**: debugger
- **Depends on**: BD-18, BD-19, DA-09, ER-09

### SM-17: Tier-3 comparable evidence mapping
- **Status**: `TODO`
- **Priority**: HIGH
- **Read first**: `docs/architecture/property-link-comparable-search.md`, `data/source_registry.json`, `docs/agents/scraper_sm/tier3-tier4-intelligence-paths-2026-05-13.md`
- **Do**: identify tier 3 official/vendor/partner sources that can contribute saved comparable evidence through public, official, contract, licensed, or manual routes; keep blocked routes explicit.
- **Acceptance gate**: tier 3 matrix separates searchable saved evidence from blocked live intake and includes legal reasons.
- **Output**: tier 3 comparable-evidence matrix and fixture follow-ups.
- **Verifier**: debugger
- **Depends on**: PLAN-13

### UX-26: Operator comparable-search review surface
- **Status**: `TODO`
- **Priority**: HIGH
- **Read first**: `docs/architecture/property-link-comparable-search.md`, `scripts/property_link_comparable_search.py`, `UX-25`, `BD-24`
- **Do**: design an operator view for one input URL, parsed facts, page blockers, same-property candidates, comparable properties, score components, conflicts, and source links.
- **Acceptance gate**: UI contract uses explicit evidence labels and does not create public search claims or grouped-property promotion.
- **Output**: UX spec or implementation after `BD-24`.
- **Verifier**: debugger
- **Depends on**: PLAN-13, BD-24

### DBG-33: Verify property-link comparable search layer
- **Status**: `TODO`
- **Priority**: **CRITICAL**
- **Read first**: `docs/architecture/property-link-comparable-search.md`, `agent-skills/property-link-comparable-search/SKILL.md`, `tests/test_property_comparable_search.py`, `scripts/property_link_comparable_search.py`
- **Do**: run fixture-only tests; verify CLI requires fixture or explicit live fetch; verify grouped pages are source-publication-only; verify tier 3 legal gates, same-source exclusion, and accepted-only default behavior.
- **Acceptance gate**: no live network in tests, no public promotion, no auto-merge, no source registry bypass.
- **Output**: debugger report and TASKS status update.
- **Verifier**: debugger
- **Depends on**: PLAN-13

### PLAN-03: Self-development architecture rebuild
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-13)
- **Priority**: **CRITICAL**
- **Read first**: `plan 13.05.md`, `docs/agents/SELF_DEVELOPMENT_ARCHITECTURE.md`, `docs/agents/AGENT_LOOP_AND_CADENCE.md`, `docs/agents/roles/*.md`
- **Do**:
  1. Keep existing core lanes: `planner`, `backend_developer`, `data_analyst`, `scraper_1`, `scraper_sm`, `ux_ui_designer`, `debugger`.
  2. Add support lanes: `ops_release_manager`, `infra_db_operator`, `market_intelligence_analyst`, `user_analytics_agent`, `vision_media_agent`, `entity_resolution_agent`, `knowledge_context_agent`.
  3. Define constant vs triggered cadence and review loop.
  4. Keep Action1 -> Action0 -> Action2 gate unchanged.
- **Acceptance gate**: docs define owner, verifier, cadence, skills, and next responsibilities without widening unsafe scraping or touching live DB data.
- **Output**: architecture docs, role docs, skill files, planner journey entry.
- **Verifier**: debugger
- **Depends on**: PLAN-01

### OPS-01: Safe git push gate for Plan 13.05
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-13; pushed to `origin reallystate`)
- **Priority**: **CRITICAL**
- **Read first**: `.gitignore`, `plan 13.05.md`, `agent-skills/ops-release-management/SKILL.md`
- **Do**:
  1. Unstage unsafe existing index entries without modifying working files.
  2. Stage only safe code/docs/config/skills/runbooks.
  3. Exclude secrets, raw capture dirs, DB dumps, runtime logs, OpenClaw state, and unreviewed large scraped corpus.
  4. Run staged secret scan.
  5. Commit and push `reallystate` if checks pass and remote accepts.
- **Acceptance gate**: no unsafe paths or secrets in staged diff; push succeeds or blocker is recorded.
- **Output**: release report in `docs/agents/ops_release_manager/JOURNEY.md`.
- **Verifier**: debugger
- **Depends on**: PLAN-03

### OPS-02: Data-analysis-driven release gate checklist
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-13; checklist only, no staging or push)
- **Priority**: **CRITICAL**
- **Read first**: `docs/agents/TASKS.md`, `docs/agents/roles/ops_release_manager.md`, `docs/integrations/mcp-and-skills-setup.md`, `.gitignore`, latest `data_analyst` outputs when ready
- **Do**:
  1. Treat `data_analyst` as the evidence owner for accepted/LOST/grouped/media/dashboard counts; release notes must cite reproducible artifact paths, not chat summaries.
  2. Require DA-02 dashboard denominator semantics before any public count claim, and DA-03 or an explicit dashboard-refresh blocker note before broad validation claims.
  3. Block DB-backed release claims until `BD-18` import/schema alignment and `INFRA-02` DB count verification succeed with a real `DATABASE_URL` / `REMOTE_DATABASE_URL`.
  4. Confirm git exclusions before staging, including unsafe files that may already be tracked: `.env`, `.env.*` except `.env.example`, `.openclaw/`, `.cursor/*.log`, raw scrape dumps `data/scraped/**/raw/`, runtime logs/pids/locks, `data/scraper.log` changes unless intentional, DB dumps/backups/SQLite files, archives, build outputs, caches, virtualenvs, and unreviewed large scraped corpus batches.
  5. Before any future commit, run staged unsafe-path scan, staged secret scan, `git diff --check`, and focused tests for changed code; record any skipped full validation with cause.
- **Acceptance gate**: release checklist exists in ops journey and this task board; unsafe data/runtime/secrets exclusions are explicit; debugger release-hygiene verification is queued; no files are staged or pushed by this slice.
- **Output**: `docs/agents/ops_release_manager/JOURNEY.md`, TASKS release gate notes.
- **Verifier**: debugger
- **Depends on**: DA-02 or current data_analyst handoff; DBG-21 verifies this checklist before release use.

### INFRA-01: Server and DB migration readiness
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-13)
- **Priority**: **CRITICAL**
- **Read first**: `docs/runbooks/server-db-migration.md`, `agent-skills/infra-db-migration/SKILL.md`, `Makefile`, `docs/docker-and-database.md`
- **Do**:
  1. Prepare backup/restore/count verification commands.
  2. Document server prerequisites and provider recommendation.
  3. Define transfer/restore/rollback steps.
  4. Block live scraping resume until count verification passes.
- **Acceptance gate**: migration can be executed next once server SSH and DB URLs exist; no DB dump is committed.
- **Output**: migration runbook, Make targets `backup-db`, `restore-db`, `verify-db-counts`, infra journey entry.
- **Verifier**: debugger + backend_developer
- **Depends on**: PLAN-03

### INFRA-02: DB count verification execution gate
- **Status**: `BLOCKED` (2026-05-13; `DATABASE_URL` missing, readiness inputs prepared, waiting on credentials/URLs and BD-18 DB smoke execution)
- **Priority**: **CRITICAL**
- **Read first**: `docs/runbooks/server-db-migration.md`, `docs/exports/scrape-database-quality-audit-2026-05-13.md`, `docs/exports/action1-dataset-quality-gate.json`, `scripts/import_scraped_listings.py`, `Makefile`
- **Do**:
  1. Once `DATABASE_URL` / `REMOTE_DATABASE_URL` exist, run backup/restore/count verification without committing dumps or runtime logs.
  2. Compare DB counts with the latest data_analyst accepted/LOST/grouped/media artifacts.
  3. Record mismatches as blockers for `BD-18` or `DA-02`; do not reinterpret scrape quality.
- **Migration readiness notes (2026-05-13, infra_db_operator)**:
  - Missing operator inputs: server provider/OS confirmation, SSH host/user/key, remote deploy user/sudo policy, remote app directory, Git clone/deploy-key access, local libpq `DATABASE_URL`, remote libpq `REMOTE_DATABASE_URL`, fixed `DB_DUMP` path/name, media transfer path or object-storage bucket, remote `REDIS_URL`/S3/MinIO/env values, firewall/Tailscale/TLS hostnames, and confirmation that live scraping/workers are paused.
  - Command sequence confirmed from docs/Makefile: export local `DATABASE_URL` -> `make backup-db` -> transfer dump/checksum/media -> remote `docker compose up -d postgres redis minio temporal temporal-ui` -> export `REMOTE_DATABASE_URL` + `DB_DUMP` -> `make restore-db` -> local/remote `make verify-db-counts` using `DATABASE_URL` -> `diff -u` count files.
  - URL constraint: backup/count commands call `pg_dump`/`psql`, so use `postgresql://...` libpq URLs, not SQLAlchemy-only `postgresql+psycopg://...` URLs.
  - Planner blocker: keep this slice blocked until `INFRA-01` is verified and `BD-18` proves DB-backed import/schema alignment.
  - Debugger blocker: later verify dry-run-to-live transition, no committed dumps/secrets/logs, checksum match, PostGIS availability, and count parity before any live scraping resumes.
  - 2026-05-13 sequential run: `make verify-db-counts` and `make bd18-db-smoke-import` both block immediately because `DATABASE_URL` is not set. When provided, run `make migrate` first, then the BD-18 smoke import, then count verification.
- **Acceptance gate**: `make verify-db-counts` succeeds against the target DB and the report names accepted, skipped, grouped/development, LOST, inactive, and media-count gaps with source/bucket scope.
- **Output**: infra journey entry plus `docs/exports/db-count-verification-YYYY-MM-DD.md` if counts run.
- **Verifier**: debugger + backend_developer + data_analyst
- **Depends on**: INFRA-01, BD-18

### INFRA-03: Product website environment readiness matrix
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-14; matrix prepared, DB/runtime proof still blocked by missing credentials)
- **Priority**: **CRITICAL**
- **Read first**: `docs/exports/product-website-agent-prompts-2026-05-14.md` section 9, `docs/exports/product-website-ux-rebuild-plan-2026-05-14.md`, `docs/runbooks/server-db-migration.md`, `.env.example`, `Makefile`, `docs/docker-and-database.md`
- **Do**:
  1. List required env vars for auth/JWT, DB, chat provider, CORS, frontend backend proxy, and map provider across local/staging/production.
  2. Keep all API keys, DB URLs, JWT secrets, and provider keys out of committed docs/code.
  3. Define smoke command order once `DATABASE_URL` is available.
  4. Do not execute migrations without credentials and operator approval.
- **Acceptance gate**: readiness runbook exists, `.env.example` names current code-read variables without real secrets, DB proof remains explicitly blocked when credentials are missing, and verifier can rerun smoke commands after credentials are supplied.
- **Output**: `docs/runbooks/product-website-env-readiness-2026-05-14.md`, `.env.example`, infra JOURNEY entry, wiki run/log closeout.
- **Verifier**: debugger + backend_developer
- **Depends on**: PLAN-08, UX-23, DA-06, ER-05, UA-04

### MI-01: Weekly market and rival intelligence baseline
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-13; file-backed only, no browsing/scraping)
- **Priority**: HIGH
- **Read first**: `docs/agents/roles/market_intelligence_analyst.md`, `deep-research-report.md`, `data/source_registry.json`, latest data analyst reports
- **Do**: produce market/rival intelligence for portals, agencies, STR vendors, price/supply signals, and source-priority implications.
- **Acceptance gate**: report separates FACT / INTERPRETATION / HYPOTHESIS / GAP and maps recommendations to planner tasks.
- **Output**: `docs/exports/market-intelligence-2026-05-13.md`, market intelligence journey entry.
- **Verifier**: debugger + planner
- **Depends on**: PLAN-03

### MI-02: Next weekly market review scorecard
- **Status**: `TODO`
- **Priority**: HIGH
- **Read first**: `docs/exports/market-intelligence-2026-05-13.md`, `docs/exports/data-quality-deep-review-2026-05-13.md`, `docs/exports/properties-deep-analytics-agent-handoff-2026-05-13.md`, `DA-02`, `DA-05`, `BD-19` output, `docs/exports/website-inventory-analysis.md`, `data/source_registry.json`
- **Do**:
  1. Build a weekly source scorecard from accepted-only evidence: source family, legal/access mode, website-total basis, landed rows, accepted rows, grouped rows, LOST rows, media/description coverage, city/district coverage, price-status coverage, and product role.
  2. Identify strategic supply gaps by geography, intent, property type, source family, price band, price-per-sqm band, media strength, and textual tendencies without using raw scraped volume as a market fact.
  3. Separate sale and rent medians; never mix them into one public price claim.
  4. Separate marketable claims from internal hypotheses and blocked data needs.
- **Acceptance gate**: every source-strength or supply-gap claim cites a reproducible artifact; no private/unauthorized source route is proposed; public positioning language is blocked unless accepted-only DB counts support it.
- **Output**: `docs/exports/market-review-scorecard-YYYY-MM-DD.md`, market intelligence journey entry, planner-ready source priority list.
- **Verifier**: debugger + planner + data_analyst
- **Depends on**: MI-01, DA-02, BD-19

### UA-01: Website analytics event taxonomy
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-13: privacy-safe taxonomy written; implementation deferred until UI/backend contracts stabilize)
- **Priority**: HIGH
- **Read first**: `docs/agents/roles/user_analytics_agent.md`, `agent-skills/user-analytics-instrumentation/SKILL.md`, `app/`, `components/`, `docs/business/product-ux-structure.md`
- **Do**: define privacy-safe events and funnels for browse, search, map, detail, saved properties, chat, source clicks, account mode, and admin review.
- **Acceptance gate**: no PII-bearing payloads; frontend/backend tasks are explicit.
- **Output**: `docs/analytics/user-event-taxonomy.md`, user analytics journey entry.
- **Verifier**: debugger + ux_ui_designer
- **Depends on**: PLAN-03

### UA-02: Privacy-safe instrumentation implementation plan
- **Status**: `TODO`
- **Priority**: HIGH
- **Read first**: `docs/analytics/user-event-taxonomy.md`, `docs/exports/data-quality-deep-review-2026-05-13.md`, `BD-20`, `UX-20`, `BD-13`, `BD-17`, `BD-19`, `UX-15`
- **Do**:
  1. After account/chat/admin/read-model contracts stabilize, freeze the event dictionary, payload allowlists, sampling/debounce rules, retention windows, and dashboard metrics.
  2. Confirm UX events use derived fields only: no raw search text, raw chat text, emails, phones, names, source URLs, IPs, user agents, tokens, or admin private notes.
  3. Map each event to an owner component/API and a debugger verification fixture.
- **Acceptance gate**: implementation plan maps every event to frontend/backend owner, payload schema, privacy rule, and verification case; no external analytics dependency.
- **Output**: `docs/analytics/instrumentation-implementation-plan.md`, user analytics journey entry.
- **Verifier**: debugger + ux_ui_designer + backend_developer
- **Depends on**: UA-01, BD-13, BD-17, BD-19, UX-15

### UA-03: Product analytics dashboard contract
- **Status**: `TODO`
- **Priority**: MEDIUM
- **Read first**: `docs/analytics/user-event-taxonomy.md`, `UA-02`, `BD-20`, `UX-20`, latest data analyst dashboard contracts
- **Do**: define first-party dashboard views for browse-to-detail, search-to-result, map-to-detail, detail-to-save/contact/chat, profile retention, admin throughput, and media-confidence funnels.
- **Acceptance gate**: dashboard spec includes metric definitions, required events, denominator rules, privacy constraints, and example SQL/API query shapes using only first-party event data.
- **Output**: `docs/analytics/product-dashboard-spec.md`, user analytics journey entry.
- **Verifier**: debugger + ux_ui_designer + data_analyst
- **Depends on**: UA-02, BD-20, UX-20

### VM-01: Vision media agent readiness
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-13; planning only, no image processing)
- **Priority**: HIGH
- **Read first**: `docs/agents/roles/vision_media_agent.md`, `docs/agents/roles/data_analyst.md`, `agent-skills/image-media-pipeline/SKILL.md`, `docs/exports/source-item-photo-coverage.json`, `docs/exports/s1-21-gemma-action0-eligible.json`, `docs/exports/scrape-database-quality-audit-2026-05-13.md`, `docs/exports/action1-dataset-quality-gate.json`
- **Do**:
  1. Convert data analyst media gaps into semantic media QA tasks: gallery completeness, scene/room coverage, condition, equipment, style, photo-text consistency, and uncertainty.
  2. Define the visual evidence threshold for buyer-facing display and stronger property promotion.
  3. Define Action0 queue rules without running image processing; use only local files after operator `Action0 now`.
  4. Hand debugger explicit verification needs for report schema, uncertainty, gate enforcement, and no-fact-overwrite behavior.
- **Acceptance gate**: readiness report separates FACT / INTERPRETATION / HYPOTHESIS / GAP; reports remain evidence, not final property facts; execution waits for operator `Action0 now`; buyer-facing promotion requires accepted single-unit status plus visual evidence gates.
- **Output**: `docs/exports/vision-media-action0-readiness-2026-05-13.md`, vision journey entry, media QA follow-up slices.
- **Verifier**: debugger + data_analyst
- **Depends on**: DA-01 file-backed audit; Action0 execution remains blocked until operator `Action0 now`

### VM-02: Action0 semantic media QA execution queue
- **Status**: `BLOCKED` (operator `Action0 now` required; do not run during planning)
- **Priority**: HIGH
- **Read first**: `VM-01`, `docs/exports/vision-media-action0-readiness-2026-05-13.md`, `docs/exports/taskforgema.md`, `docs/exports/s1-21-gemma-action0-eligible.json`, `docs/exports/property-quality-and-building-contract.md`
- **Do**:
  1. After operator `Action0 now`, process only rows from `s1-21-gemma-action0-eligible.json` or a debugger/data_analyst-approved successor queue.
  2. Use only `local_image_files`; no remote fetch or gallery backfill inside semantic reporting.
  3. Write one JSON and one Markdown report per property under `docs/exports/property-image-reports/<source_key>/`.
  4. Include per-image scene type, style, layout clues, visible equipment/tools, colors/materials, condition, defects/risks, usefulness, confidence, and uncertainty.
  5. Include whole-property report with photo-text consistency, single-property validity, missing-scene warnings, buyer/renter usability evidence, and human-review gaps.
  6. Write index files with source totals, reports, images, skips, skip reasons, warnings, and human-review fields.
- **Acceptance gate**: every eligible row has a report or precise skip reason; every report references existing local files only; no rooms/equipment/condition/floorplans are invented; uncertainty is present for every non-obvious conclusion.
- **Output**: `docs/exports/property-image-reports/`, optional compatibility mirror to `docs/exports/apartment-image-reports/`, vision journey entry.
- **Verifier**: debugger + data_analyst
- **Depends on**: VM-01 verification, operator `Action0 now`, Action1 QA state accepted by debugger/data_analyst

### VM-03: Visual evidence promotion gate
- **Status**: `TODO`
- **Priority**: HIGH
- **Read first**: `docs/exports/vision-media-action0-readiness-2026-05-13.md`, `DA-02`, `BD-18`, `BD-19`, `UX-16`, `UX-18`
- **Do**:
  1. Turn the readiness report thresholds into product/DB/API fields: `visual_evidence_status`, `semantic_report_status`, `missing_scene_warnings`, `human_review_required`, and `visual_promotion_blockers`.
  2. Separate buyer-facing display from promoted/enriched property use; promoted use needs a complete semantic report, not only local photos.
  3. Keep grouped/development, `LOST`, inactive, pending-QA, partial-gallery, and no-report rows out of promoted property sets.
  4. Define property-type-specific evidence expectations for apartment/house, commercial, land, and development/source-publication pages.
- **Acceptance gate**: backend/API/UI consumers can tell `display_allowed_with_limited_media` from `promotion_allowed`; no semantic image statement overwrites source facts; all blockers are auditable.
- **Output**: field contract or task handoff for backend/UX/dashboard implementation, vision journey entry.
- **Verifier**: debugger + data_analyst + backend_developer + ux_ui_designer
- **Depends on**: DA-02, BD-18, BD-19

### VM-04: Media QA dashboard handoff
- **Status**: `TODO`
- **Priority**: MEDIUM
- **Read first**: `VM-01`, `VM-02`, `DA-02`, `DA-03`, `docs/exports/data-quality-deep-review-2026-05-13.md`, `scripts/generate_source_item_photo_coverage.py`, `docs/exports/property-image-reports/index.json`
- **Do**:
  1. Define dashboard metrics for media capture completeness and semantic report completeness separately.
  2. Track per-source/per-bucket counts for accepted rows with full local gallery, partial gallery, unreadable/duplicate images, semantic report complete, semantic report skipped, and human-review required.
  3. Ensure `source-item-photo-coverage.json` is not used as the accepted-row denominator until DA-02 reconciles stored status vs quality-gate status.
- **Acceptance gate**: dashboard terms distinguish raw media capture, gallery completeness, semantic image-report coverage, and buyer-facing promotion readiness.
- **Output**: dashboard contract update or implementation handoff, vision journey entry.
- **Verifier**: debugger + data_analyst + ux_ui_designer
- **Depends on**: VM-01, DA-02, DA-03

### VM-05: Local-gallery verification before image descriptions
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-13; file-backed verification contract prepared, no image descriptions generated)
- **Priority**: HIGH
- **Read first**: `docs/exports/vision-media-local-gallery-verification-2026-05-13.md`, `docs/exports/source-item-photo-coverage.json`, `docs/exports/data-quality-deep-review-2026-05-13.md`, `DA-02`
- **Do**:
  1. Verify local-gallery evidence separately from semantic image-description coverage.
  2. Keep Action0 image-description execution blocked until operator `Action0 now`.
  3. Require accepted single-unit state, local file existence/readability, explicit full/partial gallery status, and uncertainty before any semantic report can be promoted.
- **Acceptance gate**: report states current local media totals, identifies that image descriptions are not generated, and keeps remote fetch/semantic generation out of this run.
- **Output**: `docs/exports/vision-media-local-gallery-verification-2026-05-13.md`, vision journey entry.
- **Verifier**: debugger + data_analyst + ux_ui_designer
- **Depends on**: DA-02, VM-01

### ER-01: Conservative entity-resolution queue plan
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-13: planning only; no candidate generation, import, or property-entity promotion)
- **Priority**: MEDIUM
- **Read first**: `docs/agents/roles/entity_resolution_agent.md`, `docs/agents/roles/data_analyst.md`, `src/bgrealestate/services/unification.py`, `src/bgrealestate/pipeline.py`, `tests/test_unification.py`, `sql/schema.sql`, `scripts/import_scraped_listings.py`, `docs/exports/property-identity-anomaly-audit-2026-04-29.md`, `docs/exports/action1-multi-unit-publications.json`, `docs/exports/scrape-database-quality-audit-2026-05-13.md`
- **Do**: define duplicate candidate queue inputs, accepted-only source-publication filters, single-unit/grouped/unknown/duplicate/conflict taxonomy, evidence fields, confidence thresholds, backend schema/API handoff, and no-auto-merge review policy.
- **Acceptance gate**: grouped/development publications cannot be auto-merged as single units; plan states no `property_entity` / `property_offer` promotion in ER planning; follow-up slices depend on `BD-18`/`BD-19` accepted source-publication evidence.
- **Output**: `docs/exports/entity-resolution-queue-plan-2026-05-13.md`, entity resolution journey entry.
- **Verifier**: debugger + data_analyst
- **Depends on**: DA-01 file-backed audit; execution candidates depend on BD-18, BD-19, DA-02, and accepted source-publication import evidence

### ER-02: Accepted-only duplicate candidate extraction contract
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-13; accepted-only candidate layer designed, no candidate generation)
- **Priority**: HIGH
- **Read first**: ER-01 output, `BD-18`, `BD-19`, `DA-02`, `src/bgrealestate/services/unification.py`, `sql/schema.sql`, `scripts/import_scraped_listings.py`
- **Do**:
  1. Define the exact accepted-only input query for source publications: `SCRAPED_OK`, accepted/single-entity state, not grouped/development, not `LOST`, not inactive/removed/expired, not pending/missing QA, and registry-backed source provenance.
  2. Define candidate blocking keys and pair generation for exact source duplicates, strong cross-source same-unit candidates, weak same-building/project candidates, and conflict candidates.
  3. Keep output as candidate rows/evidence only; do not create or update `property_entity`, `property_offer`, public `/properties` results, or buyer-facing labels.
  4. Hand backend_developer the SQL/API contract needed by `BD-21`.
- **Acceptance gate**: contract includes deterministic input filters, source/bucket scope, idempotency key, and negative filters for grouped/development/unknown/LOST/inactive rows.
- **Output**: `docs/exports/entity-resolution-accepted-only-candidate-layer-2026-05-13.md`, entity resolution journey entry.
- **Verifier**: debugger + data_analyst + backend_developer
- **Depends on**: ER-01, BD-18, BD-19, DA-02

### ER-03: Evidence scoring and case-classification matrix
- **Status**: `TODO`
- **Priority**: HIGH
- **Read first**: ER-01 output, ER-02 output, `docs/exports/action1-multi-unit-publications.json`, `docs/exports/scrape-database-quality-audit-2026-05-13.md`, `tests/test_unification.py`
- **Do**:
  1. Define score components for source URL/id, city/district/address/building/project, area, price/price-status, rooms/floor/unit clues, contacts, photo overlap, media counts, and lifecycle dates.
  2. Define hard blockers that override any score: grouped/development, unknown QA state, inactive, `LOST`, same-source non-exact records, zero-price-as-real-price, contradictory area/price/media/unit evidence.
  3. Separate review labels: `single_unit`, `grouped_or_development`, `unknown`, `source_duplicate`, `same_unit_candidate`, `same_complex_only`, and `conflicting_evidence`.
  4. Require operator review for every cross-source link until a labeled Bulgarian sample validates thresholds.
- **Acceptance gate**: matrix prevents confidence scores from overriding exclusion states and documents review actions for each case.
- **Output**: `docs/exports/entity-resolution-scoring-matrix-YYYY-MM-DD.md`, entity resolution journey entry.
- **Verifier**: debugger + data_analyst
- **Depends on**: ER-02

### ER-04: Source-publication relationship and conflict review policy
- **Status**: `TODO`
- **Priority**: MEDIUM
- **Read first**: ER-01 output, ER-02 output, ER-03 output, `docs/agents/ux_ui_designer/data-quality-ui-decision-notes-2026-05-13.md`, UX-15
- **Do**:
  1. Define lifecycle for candidate review actions: `link`, `dismiss`, `defer`, `mark_conflict`, `needs_unit_split`, and `needs_parser_repair`.
  2. Define audit fields for who/when/why plus immutable evidence snapshot.
  3. Hand UX the operator-side wording for duplicate/confidence/provenance review without buyer-facing claims.
  4. Hand debugger fixture scenarios for grouped/development negatives, same-complex false positives, conflicting price/area/media, and exact source duplicate cases.
- **Acceptance gate**: policy keeps source-publication evidence separate from canonical property promotion and names verifier fixtures for all five required case classes.
- **Output**: `docs/exports/entity-resolution-review-policy-YYYY-MM-DD.md`, entity resolution journey entry.
- **Verifier**: debugger + ux_ui_designer + data_analyst
- **Depends on**: ER-03, UX-15

### KCA-01: Data-analyst evidence capture and wiki closeout
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-13: wiki run/log recorded; memory/insights unchanged under strict filters; `DBG-15` dependency met)
- **Priority**: HIGH
- **Read first**: `docs/agents/roles/knowledge_context_agent.md`, `/Users/getapple/core/wiki/projects/real-estate-bulgaria/{index.md,memory.md,insights.md}`, `docs/exports/scrape-database-quality-audit-2026-05-13.md`, latest `data_analyst` and `debugger` JOURNEY entries
- **Do**:
  1. Create a wiki run record for the data-analyst-centered loop after the current analyst/debugger outputs are stable.
  2. Update project log, memory, and insights under the strict filters only.
  3. Update docs/reporting index if a new durable artifact becomes source-of-truth.
- **Acceptance gate**: no meaningful conclusion exists only in chat; memory is updated only for future-affecting patterns; insights separate FACT / INTERPRETATION / HYPOTHESIS / GAP.
- **Output**: wiki run/log/memory/insight updates and knowledge_context_agent JOURNEY entry.
- **Verifier**: debugger + planner
- **Depends on**: DA-02 or DBG-15

### KCA-02: Four-dashboard knowledge capture
- **Status**: `TODO`
- **Priority**: HIGH
- **Read first**: `PLAN-06`, `docs/exports/operational-dashboards.json`, `docs/exports/all-agent-execution-plan-2026-05-13.md`, latest planner/debugger/data_analyst JOURNEY entries, `/Users/getapple/core/wiki/projects/real-estate-bulgaria/{index.md,memory.md,insights.md}`
- **Do**:
  1. Record the four-dashboard operating model as a wiki run after debugger verifies `PLAN-06`.
  2. Update project log and insights only for reusable conclusions: dashboard role split, accepted-only evidence chain, and verifier queue hygiene.
  3. Update memory only if the dashboard/denominator blocker is a repeating future-run constraint.
  4. Keep scraped corpus details out of memory; cite artifact paths instead.
- **Acceptance gate**: no dashboard/planning conclusion exists only in chat; wiki entries separate FACT / INTERPRETATION / HYPOTHESIS / GAP and preserve strict memory filters.
- **Output**: wiki run/log/insight/memory updates as applicable, knowledge_context_agent JOURNEY.
- **Verifier**: debugger + planner
- **Depends on**: PLAN-06, DBG dashboard verification

### DA-03: Dashboard source/photo coverage generator performance repair
- **Status**: `TODO`
- **Priority**: HIGH
- **Read first**: `scripts/generate_source_item_photo_coverage.py`, `scripts/generate_progress_dashboard.py`, `docs/exports/source-item-photo-coverage.json`, latest `data/scraped/**/listings/*.json` corpus size
- **Do**: make `make dashboard-doc` reliable on the current large workspace by adding bounded/changed-file mode, progress output, or cached corpus scan behavior. `make operational-dashboard-doc` now exists as a fast task/JOURNEY/dashboard refresh fallback, but it does not replace full source/photo coverage regeneration.
- **Acceptance gate**: `make dashboard-doc` completes without manual kill, or a documented fast dashboard target exists for task/JOURNEY-only changes.
- **Output**: script update or documented fallback, data analyst journey entry, and clear instructions for when to use the fast fallback versus full corpus dashboards.
- **Verifier**: debugger
- **Depends on**: PLAN-03

### DBG-13: Verify Plan 13.05 architecture reset and release gate
- **Status**: `TODO`
- **Priority**: HIGH
- **Read first**: `docs/agents/SELF_DEVELOPMENT_ARCHITECTURE.md`, `docs/agents/roles/*.md`, `.gitignore`, `docs/runbooks/server-db-migration.md`, staged diff once OPS-01 reaches handoff
- **Do**: verify architecture docs, role boundaries, Action1 gate consistency, migration readiness, and staged release hygiene.
- **Acceptance gate**: unsafe files are absent from staged diff; role docs and task board have clear owners/verifiers; dashboard refresh blocker is recorded as DA-03 if unresolved.
- **Output**: debugger journey entry and task status updates.
- **Verifier**: debugger
- **Depends on**: OPS-01

---

## Constant recurring slices (all agents)

### CONST-01: Activation sync + dashboard refresh
- **Status**: `TODO` (recurring)
- **Read first**: `docs/agents/TASKS.md`, all `docs/agents/*/JOURNEY.md`, `docs/dashboard/index.html`, `docs/dashboard/project-progress.html`, `docs/dashboard/properties-database.html`, `docs/dashboard/website.html`, `docs/dashboard/support.html`
- **Do**: on each activation, review progress deltas, update task dependencies/notes, and regenerate the four dashboard surfaces plus legacy exports after doc/task changes.
- **Acceptance gate**: latest run updates `TASKS.md`, `docs/exports/operational-dashboards.json`, and dashboard HTML timestamps; if full `make dashboard-doc` is blocked by corpus scan performance, run the operational dashboard generator and keep `DA-03` blocker visible.
- **Output**: refreshed `docs/exports/progress-dashboard.json`, `docs/exports/operational-dashboards.json`, `docs/dashboard/index.html`, `docs/dashboard/project-progress.html`, `docs/dashboard/properties-database.html`, `docs/dashboard/website.html`, `docs/dashboard/support.html`, `docs/exports/all-agent-execution-plan-2026-05-13.md`, `docs/exports/parallel-execution-timeline.md`, `docs/exports/scraper-activity-snapshot.md`, and updated task notes.
- **Verifier**: debugger
- **Depends on**: —

### CONST-02: Cross-agent note propagation
- **Status**: `TODO` (recurring)
- **Read first**: latest entries in all `JOURNEY.md` files
- **Do**: convert blockers/findings from one agent into explicit follow-up tasks for impacted agents, and preserve recurring scraper evidence rules in the affected task notes
- **Standing scraper memory**:
  - for each property item, try to identify the full gallery on the detail page
  - download all reachable item photos, not only the lead thumbnail or first image
  - check whether the downloaded photos are readable or decodable, and record partial-gallery failures
  - treat full item capture as the default target: description, attributes, contacts, and the full reachable media set
  - store image binaries as local files under `data/media/<reference_id>/...`; keep remote image URLs only as traceability metadata, not as the primary image storage
  - only call a source `Patterned` when one saved sample item proves local image-file capture for the full reachable gallery and also lands the core item fields (`price` plus `city` or `address`) and at least two structured fields such as `area`, `rooms`, `floor`, or `phones`
  - treat every scraped row as a source publication first; promote it to one property item only when the page advertises one unit with its own URL plus one price or an explicit `on_request` / `undefined` price state
  - flag mixed inventory pages (`1-2 bedroom`, `apartments (various types)`, whole residential-building/development pages, price-from pages) as `suspected_multi_unit_publication`; split only when unit-level price/area/URL/media evidence exists
  - never store numeric `0` as a real price; keep `price = null` and provenance `price_status = on_request` or `price_status = undefined` until the schema gets a first-class field
  - reject or quarantine area parses below 2 sqm for apartments/houses/offices unless the source explicitly proves that unit; this usually means a decimal/locale parse error
  - for each website, find the reusable parsing pattern for every property/service route and save that pattern as code before calling the source `Patterned`
  - keep a website-level status split between item-pattern readiness and count-method readiness; do not mark a source fully ready if live counts are still estimate-only
  - the recurring scraper_1 operating loop is incremental: every 15 minutes append new listings, refresh changed listings, and mark disappeared listings inactive instead of silently dropping them
  - after every scrape run, refresh source metrics with explicit counts for:
    - saved items started out of latest saved website-total count
    - fully parsed/full-gallery items out of saved items
    - description coverage out of saved items
    - local/remote image capture totals plus average images per item
    - image-description coverage out of saved local images
  - dashboard metrics must use source-total counts for operator views; threshold-only counters such as `100` belong only in dedicated control-plane views
- **Acceptance gate**: each blocker has at least one mapped follow-up slice with dependency, and scraper-facing follow-ups keep the full-item/full-gallery requirement visible
- **Output**: updated `TASKS.md` dependencies and notes
- **Verifier**: lead agent + debugger
- **Depends on**: —

---

## ═══════════════════════════════════════════════════════
## PLANNER (coordination + OpenClaw control-plane)
## ═══════════════════════════════════════════════════════

**Mission**: Keep the multi-agent system coherent. Maintain task order, dependencies, OpenClaw bootstrap consistency, and handoffs. Planner does not scrape, import, or change production data directly.

### PLAN-01: Agent reset and OpenClaw Action1 control reset
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-05)
- **Priority**: **CRITICAL**
- **Read first**: `docs/agents/TASKS.md`, `docs/agents/README.md`, `docs/openclaw/ACTION1_AGENT_BOOTSTRAP.md`, `docs/openclaw/scrape-taxonomy-a1-a12.md`, `agent-skills/openclaw-ollama-gemma4/SKILL.md`, `agent-skills/reporter/SKILL.md`
- **Do**:
  1. Keep exactly these active lanes: planner, backend_developer, data_analyst, scraper_1, scraper_sm/S&M, ux_ui_designer, debugger.
  2. Keep `scraper_t3` historical only; move new tier-3 work into S&M.
  3. Ensure OpenClaw reads Action0 + Action1 + Action2 but executes only the operator-approved next action.
  4. Ensure Action1/A1 remains exactly seven sources until Action1 QA is complete or operator changes scope.
  5. Preserve the oldest-first backfill instruction and +100/5-minute reporting instructions in OpenClaw files.
- **Acceptance gate**: task queue and OpenClaw docs agree on agents, source scope, model roles, reporting, Action1 -> Action0 -> Action2 sequence, and debugger handoff.
- **Output**: updated task queue, OpenClaw docs/skills, planner JOURNEY.
- **Verifier**: debugger
- **Depends on**: —

### PLAN-02: Weekly dependency and blocker pruning
- **Status**: `TODO`
- **Priority**: MEDIUM
- **Read first**: all `docs/agents/*/JOURNEY.md`, `docs/exports/*quality*`, `docs/exports/*dashboard*`
- **Do**: collapse stale blockers, map every `DONE_AWAITING_VERIFY` item to a debugger gate, and prevent old Varna-only/T3/T4 notes from hijacking Action1 priority.
- **Acceptance gate**: no active slice has unclear owner, unclear verifier, or outdated source scope.
- **Output**: updated `TASKS.md`, planner JOURNEY, optional decision doc.
- **Verifier**: debugger
- **Depends on**: PLAN-01

### PLAN-04: Data-analyst-centered loop handoff
- **Status**: `VERIFIED` (2026-05-13 by DBG-15; handoff protocol passed, DB/dashboard blockers retained)
- **Priority**: **CRITICAL**
- **Read first**: `docs/agents/TASKS.md`, `docs/agents/README.md`, `docs/agents/AGENT_LOOP_AND_CADENCE.md`, `docs/agents/roles/planner.md`, latest `data_analyst` / `debugger` JOURNEY entries
- **Do**:
  1. Treat `data_analyst` as the active evidence owner.
  2. Identify slices depending on data_analyst outputs.
  3. Add/refine next execution slices for backend, debugger, scraper_1, UX, infra, and knowledge lanes.
  4. Do not touch scraped DB/corpus directly.
- **Acceptance gate**: TASKS has an active dependency map, each dependent lane has a next slice and verifier, and debugger verification is queued.
- **Output**: TASKS updates, planner JOURNEY entry, handoff list.
- **Verifier**: debugger
- **Depends on**: DA-01

### PLAN-05: Market intelligence source-priority conversion
- **Status**: `TODO`
- **Priority**: HIGH
- **Read first**: `docs/exports/market-intelligence-2026-05-13.md`, `DA-02`, `BD-18`, `BD-19`, `S1-23`, `UX-15`
- **Do**:
  1. Convert MI-01 recommendations into the next cross-agent priority order after dashboard/import semantics are verified.
  2. Keep source priorities split between current trusted browse base, high-gap next review group, partner/licensed STR routes, official verification routes, and consent-gated social overlays.
  3. Block public "complete market" or "95% coverage" language until accepted-only DB-backed counts exist.
- **Acceptance gate**: planner task order cites analyst/debugger artifacts, preserves Action1 -> Action0 -> Action2 gates, and feeds UX with positioning limits.
- **Output**: updated `TASKS.md`, planner journey entry, optional source-priority decision doc.
- **Verifier**: debugger + market_intelligence_analyst + ux_ui_designer
- **Depends on**: MI-01, DA-02, BD-18, BD-19

### PLAN-06: Whole-project plan and four-dashboard operating model
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-13; file-backed dashboard generator and all-agent handoff plan added)
- **Priority**: **CRITICAL**
- **Read first**: `docs/agents/TASKS.md`, all `docs/agents/*/JOURNEY.md`, `docs/exports/scrape-database-quality-audit-2026-05-13.json`, `docs/exports/action1-dataset-quality-gate.json`, `docs/exports/scrape-status-dashboard.json`, `scripts/generate_operational_dashboards.py`
- **Do**:
  1. Review concluded execution across all agent journey logs and distinguish verified work from `DONE_AWAITING_VERIFY` handoffs.
  2. Publish four explicit dashboards: Project Progress, Properties Database, Website, and Support.
  3. Ensure every dashboard stat opens with insight, details, and next action; do not claim DB-backed truth from file-backed exports.
  4. Export the all-agent next-action plan for planner/debugger handoff.
  5. Keep scraped DB/corpus untouched; use current analyst/debugger artifacts only.
- **Acceptance gate**: dashboard pages exist under `docs/dashboard/`, `docs/exports/operational-dashboards.json` and `docs/exports/all-agent-execution-plan-2026-05-13.md` are refreshed, all current agents have visible open-slice summaries, and debugger has a queued verification task.
- **Output**: four dashboard HTML pages, operational dashboard JSON, all-agent execution plan export, planner JOURNEY entry.
- **Verifier**: debugger + data_analyst + ux_ui_designer
- **Depends on**: PLAN-04, DA-01, DBG-15

### PLAN-07: DA-02/BD-18 next-owner prompt execution
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-13; sequential owner prompts and role outputs recorded)
- **Priority**: **CRITICAL**
- **Read first**: `docs/exports/data-quality-deep-review-2026-05-13.md`, `docs/exports/bd18-database-review-and-correction-spec-2026-05-13.md`, `docs/exports/next-owner-prompts-2026-05-13.md`
- **Do**:
  1. Start as planner and publish precise prompts for debugger, backend, infra, entity resolution, vision media, and UX.
  2. Run each owner lane sequentially with file-backed evidence and explicit DB/operator blockers.
  3. Keep `data_analyst` as evidence owner; do not touch scraped DB/corpus directly.
  4. Refresh operational dashboards and hand debugger the remaining runtime gates.
- **Acceptance gate**: every named next owner has a prompt, output artifact or JOURNEY entry, and a clear next blocker/action; dashboards link to updated artifacts.
- **Output**: `docs/exports/next-owner-prompts-2026-05-13.md`, owner JOURNEY entries, updated dashboards.
- **Verifier**: debugger + planner
- **Depends on**: DA-02, BD-18, PLAN-06

### PLAN-08: Product website UX/backend rebuild prompt pack
- **Status**: `VERIFIED` (2026-05-14 by DBG-25 for planning/prompt-pack safety; public-readiness and implementation gates remain blocked)
- **Priority**: **CRITICAL**
- **Read first**: `docs/exports/product-website-ux-rebuild-plan-2026-05-14.md`, `docs/exports/product-website-agent-prompts-2026-05-14.md`, `docs/business/product-ux-structure.md`, `docs/agents/ux_ui_designer/product-ux-structure-refined.md`, `docs/analytics/user-event-taxonomy.md`
- **Do**:
  1. Re-analyze the product/website structure around map-first search, listing feed, filters, AI chat, customer accounts, owner accounts, owner property editing, and reliable login.
  2. Keep the plan as planning-only; do not implement UI/backend code in this slice.
  3. Use current public rival evidence for UX implications without unauthorized scraping or private account access.
  4. Save copy/paste prompts for every relevant product/website agent.
  5. Preserve accepted-only DB/read-model, source-publication-first, privacy, and owner-permission gates.
- **Acceptance gate**: plan and prompt files exist; every proposed agent has inputs, actions, outputs, acceptance gates, and blockers; no buyer-facing raw-scrape or 3D-building precision claim is introduced.
- **Output**: product website plan, product website agent prompt pack, planner JOURNEY entry, wiki run/log/insight closeout.
- **Verifier**: debugger + ux_ui_designer + backend_developer
- **Depends on**: PLAN-07, UX-15, UX-22, MI-01, UA-01, ER-01, BD-18 prep

### PLAN-09: Prompt-pack section 1 reconciliation and next-task lock
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-14; planner-only reconciliation, no live scrape/import)
- **Priority**: **CRITICAL**
- **Read first**: `docs/exports/product-website-agent-prompts-2026-05-14.md` section 1, `docs/exports/product-website-plan-verification-2026-05-14.md`, `docs/exports/badly-scraped-review-2026-05-14.json`, `docs/agents/TASKS.md`, all `docs/agents/*/JOURNEY.md`, project wiki memory/insights.
- **Do**:
  1. Reconcile product-plan outputs, DA-07 bad-scrape outputs, dashboards, TASKS/JOURNEY, and wiki state.
  2. Lock the next execution to `scraper_1` repair first: `S1-23` then `S1-24`, Action1/A1 only.
  3. Keep entity-resolution next as contract/review work only; no candidate generation or property promotion before accepted-only DB/read-model proof.
  4. Keep DB/operator proof blocked on credentials and `BD-18` smoke/count verification.
  5. Queue debugger verification after the scraper/ER/DB outputs rather than claiming readiness from planner chat.
- **Acceptance gate**: TASKS names the scraper-first sequence, every next lane has owner/verifier/dependency, dashboards are refreshed through the fast target, and wiki run/log/decision/memory/insight closeout is recorded under strict filters.
- **Output**: `docs/exports/planner-reconciliation-2026-05-14.md`, TASKS/JOURNEY updates, refreshed operational dashboards, wiki run/log/decision/memory/insight updates.
- **Verifier**: debugger + data_analyst + scraper_1
- **Depends on**: PLAN-08, DA-07, DBG-25

### PLAN-10: Operator correction wave orchestration
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-15; Wave 1 dispatched, outputs integrated, debugger verification queued)
- **Priority**: **CRITICAL**
- **Read first**: project wiki `index.md`/`memory.md`/`insights.md`, `docs/agents/TASKS.md`, all `docs/agents/*/JOURNEY.md`, `docs/agents/README.md`, latest operator prompt.
- **Do**:
  1. Translate the operator's UI, scraping, dataset, map, profile, and aggregation concerns into executable agent slices.
  2. Create a shared MD communication board for parallel work.
  3. Dispatch two non-overlapping Wave 1 agents: UX frontend operability and data/XLS evidence.
  4. Queue Wave 2 parser/entity-resolution repair and Wave 3 backend/media contracts.
  5. Preserve accepted-only, source-publication-first, no-unsafe-scraping, DB-blocked, and semantic-image-blocked gates.
- **Acceptance gate**: TASKS has owners/verifiers/dependencies for all wave slices; communication board exists; Wave 1 outputs are either produced or have exact blockers; operational dashboards are refreshed; wiki run/log/insight closeout is recorded under strict filters.
- **Output**: `docs/exports/operator-correction-execution-plan-2026-05-15.md`, communication board files, TASKS/JOURNEY updates, Wave 1 handoff.
- **Verifier**: debugger + data_analyst + ux_ui_designer
- **Depends on**: PLAN-09, DA-07, UX-23, BD-22

### PLAN-11: Final all-agent two-branch execution prompt pack
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-15; prompt pack and branch communication contract created)
- **Priority**: **CRITICAL**
- **Read first**: project wiki `index.md`/`memory.md`/`insights.md`, `docs/agents/TASKS.md`, all `docs/agents/*/JOURNEY.md`, `docs/exports/operator-correction-execution-plan-2026-05-15.md`, `docs/exports/competitor-account-ux-audit-2026-05-14.md`, latest public market sources.
- **Do**:
  1. Review the last project steps, current strategic direction, market/rival evidence, and active blockers.
  2. Convert the result into an all-agent execution sequence with strategic agents first, two parallel implementation branches, and a final merge prompt.
  3. Assign `reallystate` to data/backend/evidence cleanup and `reallystate1` to product/frontend/UX polish.
  4. Preserve accepted-only, source-publication-first, no-unsafe-scraping, DB-blocked, Action0-blocked, Action2-blocked, and claim-neutral gates.
  5. Write copy/paste prompts for strategic kickoff, branch A, branch B, and final merge.
- **Acceptance gate**: prompt pack separates FACT / INTERPRETATION / HYPOTHESIS / GAP, cites current market sources, names all active agents, defines branch ownership and merge gates, and does not instruct agents to promote dirty corpus rows or unsupported public claims.
- **Output**: `docs/exports/final-all-agent-branch-execution-plan-2026-05-15.md`, `docs/agents/communication/2026-05-15-final-branch-sync.md`, planner JOURNEY entry, wiki run/log/decision/memory/insight closeout.
- **Verifier**: debugger + ops_release_manager + knowledge_context_agent
- **Depends on**: PLAN-10, DA-08, UX-25, MI-03, BD-22

### PLAN-12: Strategic kickoff handoff confirmation
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-15; handoff written, no scraped corpus or DB mutation)
- **Priority**: **CRITICAL**
- **Read first**: `AGENTS.md`, project wiki `index.md`/`memory.md`/`insights.md`, `docs/agents/TASKS.md`, all `docs/agents/*/JOURNEY.md` tails, `docs/exports/final-all-agent-branch-execution-plan-2026-05-15.md`, `docs/exports/competitor-account-ux-audit-2026-05-14.md`, `docs/exports/product-website-ux-rebuild-plan-2026-05-14.md`, `docs/exports/operator-dataset-review-2026-05-15.md`.
- **Do**:
  1. Confirm `reallystate` owns data/backend/evidence and `reallystate1` owns frontend/product/UX.
  2. Confirm map/list cockpit, saved searches, favorites, alerts, owner workspace, property chat, and provenance/trust labels as current product implications.
  3. Confirm blocked public claims: complete market, `95% coverage`, verified owner inventory, exact 3D/building precision, valuation/yield/below-market labels, and semantic image facts.
  4. Confirm success metrics: active accepted properties, detail opens, saved searches/alerts, favorites, property chats/viewing requests, owner drafts, QA throughput, parser repair reduction, and unsafe public rows = 0.
  5. Write a short communication artifact before implementation starts.
  6. Queue debugger verification.
- **Acceptance gate**: handoff separates FACT / INTERPRETATION / HYPOTHESIS / GAP; names branch ownership, blocked claims, metrics, and verifier queue; does not instruct corpus or DB mutation.
- **Output**: `docs/exports/strategic-handoff-2026-05-15.md`, `docs/agents/communication/2026-05-15-strategic-handoff.md`, TASKS/JOURNEY/wiki closeout.
- **Verifier**: debugger + ops_release_manager + knowledge_context_agent
- **Depends on**: PLAN-11, MI-03, DA-08, UX-25

### MI-03: Current competitor account and UX audit
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-14; public-source UX/account audit, no private account access)
- **Priority**: HIGH
- **Read first**: `docs/exports/product-website-ux-rebuild-plan-2026-05-14.md`, `docs/exports/market-intelligence-2026-05-13.md`, `data/source_registry.json`
- **Do**: Audit public UX/account patterns for Bulgarian and global real-estate rivals: search/map filters, saved searches, owner posting, direct-owner positioning, account dashboards, alerts, chat/contact, trust labels, and new-build/project surfaces. Use only public/legal browsing and cite URLs.
- **Acceptance gate**: report separates FACT / INTERPRETATION / HYPOTHESIS / GAP, cites public sources, and recommends product implications without unsafe scraping or unsupported market claims.
- **Output**: `docs/exports/competitor-account-ux-audit-YYYY-MM-DD.md`, market intelligence JOURNEY entry.
- **Verifier**: debugger + planner
- **Depends on**: PLAN-08
- **2026-05-14 handoff**: Output saved as `docs/exports/competitor-account-ux-audit-2026-05-14.md`. Feed findings into `UX-23` and `BD-22`: account-gated saved searches/favorites/alerts, owner workspace lifecycle states, property-specific chat/viewing requests, evidence-backed trust labels, and grouped/development project surfaces. Keep public coverage, valuation, owner-verified, and exact-building claims blocked until accepted-only DB/read-model proof.

### UX-23: Product website IA and first-page redesign spec
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-14; spec created, no UI/backend implementation)
- **Priority**: **CRITICAL**
- **Read first**: `docs/exports/product-website-ux-rebuild-plan-2026-05-14.md`, `docs/exports/product-website-agent-prompts-2026-05-14.md`, `docs/exports/competitor-account-ux-audit-2026-05-14.md`, `components/listings/MainExplorer.tsx`, `components/map/MapCanvas.tsx`, `components/chat/ChatWorkspace.tsx`, `components/account/AccountCabinet.tsx`, `app/globals.css`
- **Do**: Produce a high-minimal, map-first UX/UI spec for homepage filters, map/list split, property cards, customer vs owner account flows, owner workspace, property detail, chat UI actions, visual tokens, motion, and logo direction.
- **Acceptance gate**: spec covers desktop/mobile, loading/empty/error/permission states, accessibility, reduced motion, and blocks all public claims requiring accepted-only DB proof.
- **Output**: `docs/agents/ux_ui_designer/product-website-rebuild-spec-YYYY-MM-DD.md`, ux_ui_designer JOURNEY entry.
- **Verifier**: debugger + planner + backend_developer
- **Depends on**: PLAN-08; implementation remains blocked by DA-02, BD-18, BD-19 for public data surfaces.
- **2026-05-14 handoff**: Output saved as `docs/agents/ux_ui_designer/product-website-rebuild-spec-2026-05-14.md`. Feed into `BD-22`, `DA-06`, `ER-05`, `UA-04`, `VM-06`, and `DBG-25`. Public inventory/trust labels, exact 3D building precision, owner-verified claims, valuations, and market coverage copy remain blocked until accepted-only DB/read-model proof and debugger verification.

### UX-24: Public website claim-neutral copy scrub
- **Status**: `TODO` (2026-05-14; queued by DBG-25)
- **Priority**: **CRITICAL**
- **Read first**: `docs/exports/product-website-plan-verification-2026-05-14.md`, `docs/agents/ux_ui_designer/product-website-rebuild-spec-2026-05-14.md`, `docs/exports/public-search-facet-dictionary-2026-05-14.md`, `app/layout.tsx`, `app/(main)/page.tsx`, `components/shell/AppShell.tsx`
- **Do**:
  1. Replace public runtime copy that implies complete inventory, market coverage, or exact 3D/building proof.
  2. Keep brand/product copy claim-neutral until accepted-only DB/read-model, facet, geometry, and debugger gates pass.
  3. Preserve internal/operator labels where they are explicitly labeled as demo, file-backed, or blocked.
- **Acceptance gate**: public app metadata/footer/homepage copy no longer contains unsupported `Every property`, complete-market, 95% coverage, owner-verified, valuation/yield, or exact-building/3D precision claims; `npm run typecheck` passes or a frontend-typecheck blocker is recorded with process/output details.
- **Output**: UX JOURNEY entry and scoped frontend copy patch.
- **Verifier**: debugger
- **Depends on**: UX-23, DA-06, DBG-25

### UX-25: Wave 1 website operability and area-first property UX
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-15; frontend patch integrated, typecheck passed)
- **Priority**: **CRITICAL**
- **Read first**: `docs/agents/communication/2026-05-15-wave1.md`, `docs/agents/ux_ui_designer/product-website-rebuild-spec-2026-05-14.md`, `docs/exports/public-search-facet-dictionary-2026-05-14.md`, `public/data/scraped-listings.json`, `components/listings/MainExplorer.tsx`, `components/map/MapCanvas.tsx`, `components/chat/ChatWorkspace.tsx`, `components/account/AccountCabinet.tsx`, `app/(main)/properties/[id]/detail-client.tsx`, `app/(main)/settings/page.tsx`
- **Do**:
  1. Make property cards, map/list selections, and chat actions open or highlight the property detail route reliably.
  2. Make profile/settings/chat buttons either perform visible state changes or navigate to existing routes; remove dead clickable affordances.
  3. Use clean buyer-facing property titles and move source IDs/numbering such as `objava`/listing numbers into provenance/comment/detail metadata.
  4. Make `area_sqm` prominent on cards, detail insights, and filter controls; add area bands under or near the map.
  5. Increase readable text/button sizing and deepen the background without adding unsupported market/3D claims.
  6. Keep true satellite/relief/building-level 3D labeled as blocked/planned unless an implemented provider and geometry proof exists.
- **Acceptance gate**: property detail navigation works from list/map/chat; area filters apply to the shared result set; profile/chat/settings visible controls are operable; `npm run typecheck` passes or a concrete typecheck blocker is recorded; no public copy claims complete inventory, exact building precision, semantic image facts, or DB-backed truth.
- **Output**: scoped frontend patch, UX JOURNEY entry, `docs/agents/communication/2026-05-15-wave1-ux.md`.
- **Verifier**: debugger + data_analyst
- **Depends on**: UX-23, UX-24, DA-06, DA-07
- **2026-05-15 Branch B closeout**: `reallystate1` final product/frontend pass completed. `/listings` now renders the cockpit; detail/settings/chat/admin/map controls are operable with accepted file-backed data or explicit blocked states. Typecheck, browser route/click checks, accepted-only export predicate, public-claim scan, analytics/no-raw-field scan, and diff check passed. Full frontend export regeneration script hung in this environment; generator is patched and current public/mock exports were normalized deterministically for `price_status`.

### BD-22: Customer/owner account, chat-search, and owner-edit API contract
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-14; fixture-safe schema/API/contracts/tests implemented, DB runtime proof still blocked by missing `DATABASE_URL`)
- **Priority**: **CRITICAL**
- **Read first**: `docs/exports/product-website-ux-rebuild-plan-2026-05-14.md`, `docs/exports/competitor-account-ux-audit-2026-05-14.md`, `src/bgrealestate/api/routers/user_auth.py`, `src/bgrealestate/api/routers/users.py`, `src/bgrealestate/api/routers/chat.py`, `src/bgrealestate/api/routers/properties.py`, `sql/schema.sql`, `BD-18` output
- **Do**: Define and then implement only dependency-safe API/schema pieces for branch-aware accounts, owner property claims/edits, accepted-only map/list search, chat UI actions, saved searches/areas, owner/customer chat permissions, alert cadence, viewing requests, and owner listing lifecycle states.
- **Acceptance gate**: fixture-safe tests cover auth/RBAC, owner edit permissions, structured chat action schema, accepted-only search labels, and no invented property facts. DB runtime proof remains blocked when `DATABASE_URL` is absent.
- **Output**: backend contract doc or code/tests depending on DB blocker state, backend JOURNEY entry.
- **Verifier**: debugger + ux_ui_designer
- **Depends on**: PLAN-08, BD-18, BD-19 for DB-backed public read models
- **2026-05-14 handoff**: Output saved as `docs/exports/bd22-backend-contract-2026-05-14.md`. Implemented branch/capability auth response fields, customer saved search/area/viewing-request APIs, owner claim/permission/revision/audit APIs, accepted-only `/properties/search` + `/properties/facets`, accepted-only `/map/viewport` + `/map/clusters`, and structured chat UI actions. Tests pass under Python 3.12.9. Do not promote DB-backed public readiness until `DATABASE_URL`, migrations, accepted-only counts, and debugger verification are complete.

### BD-23: Profile publishing and source-variable read-model contract
- **Status**: `TODO` (Wave 3; wait for Wave 1/2 evidence)
- **Priority**: **HIGH**
- **Read first**: `BD-22`, `DA-08` output, `S1-25` output, `ER-06` output, `docs/exports/public-search-facet-dictionary-2026-05-14.md`, `src/bgrealestate/api/routers/owner.py`, `src/bgrealestate/api/routers/properties.py`, `sql/schema.sql`
- **Do**:
  1. Define profile/account types for customer, owner, representative/agency participant, and operator.
  2. Define owner publishing/edit draft inputs for source-derived variables, area, media evidence, location evidence, price status, availability, and provenance.
  3. Preserve source-publication facts separately from owner assertions and operator-reviewed revisions.
  4. Expose read-model fields needed by public cards/detail/profile without promoting unreviewed or grouped/development rows.
- **Acceptance gate**: no owner/profile action can bypass accepted-only, grouped/development, price-status, media, location-confidence, and review gates; API/schema docs or tests identify DB-backed blockers explicitly.
- **Output**: backend contract doc or code/test patch, backend JOURNEY entry.
- **Verifier**: debugger + ux_ui_designer + data_analyst
- **Depends on**: BD-22, DA-08, S1-25, ER-06, BD-18/BD-19 for DB-backed proof

### DA-06: Public search facet dictionary
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-14; public contract only, runtime public use still blocked until DB/read-model proof)
- **Priority**: HIGH
- **Read first**: `docs/exports/product-website-ux-rebuild-plan-2026-05-14.md`, `docs/exports/data-quality-deep-review-2026-05-13.md`, `docs/exports/properties-deep-analytics-agent-handoff-2026-05-13.md`, `docs/agents/ux_ui_designer/verified-field-consumption-2026-05-13.md`
- **Do**: Define public-safe filter facets, values, labels, blockers, and evidence sources for homepage/listing/map search. Separate public accepted-only fields from operator-only file-backed fields.
- **Acceptance gate**: every facet names DB/file-backed status, accepted-only requirement, denominator, and whether it is public, owner-only, or operator-only.
- **Output**: `docs/exports/public-search-facet-dictionary-YYYY-MM-DD.md`, data_analyst JOURNEY entry.
- **Verifier**: debugger + ux_ui_designer + backend_developer
- **Depends on**: PLAN-08, DA-02, BD-18
- **2026-05-14 handoff**: Output saved as `docs/exports/public-search-facet-dictionary-2026-05-14.md`. It uses only the 1,606 persisted importer-safe source-publication candidates for current baseline evidence, separates sale/rent price semantics, blocks raw/unreviewed/grouped/LOST rows from public facets, and keeps actual public search counts blocked until accepted-only DB/read-model verification.

### DA-07: Badly scraped review pack and website exclusion gate
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-14; file-backed review artifacts created, website export tightened to 1,606 safe rows)
- **Priority**: **HIGH**
- **Read first**: `docs/exports/action1-dataset-quality-gate.json`, `docs/exports/scrape-database-quality-audit-2026-05-13.json`, `scripts/generate_frontend_scraped_listings.py`, `scripts/generate_operational_dashboards.py`
- **Do**:
  1. Create XLSX/PDF review artifacts for the whole saved listing corpus grouped by issue pattern, with photo paths/samples, source URLs, reasons, actions, and expected rescrape changes.
  2. Ensure wrongly/badly scraped, grouped/development, pending/missing QA, inactive, suspected multi-unit, and zero-price rows are excluded from website property exports.
  3. Surface the bad-scrape review totals and artifact links in the Properties Database dashboard.
- **Acceptance gate**: `public/data/scraped-listings.json` contains only `SCRAPED_OK` + `accepted_single_entity_candidate` + `single_unit_candidate` rows with no suspected multi-unit flags and no numeric zero price; XLSX opens with whole-corpus and issue sheets; PDF renders with issue and photo sample pages; operational dashboards link the artifacts.
- **Output**: `docs/exports/badly-scraped-review-2026-05-14.xlsx`, `output/pdf/badly-scraped-review-2026-05-14.pdf`, `docs/exports/badly-scraped-review-2026-05-14.json`, refreshed website export and dashboards, data_analyst JOURNEY entry.
- **Verifier**: debugger + ux_ui_designer + backend_developer
- **Depends on**: DA-02, DA-06

### DA-08: Wave 1 operator dataset XLS and transformation audit
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-15; XLS/JSON/MD generated and structurally validated)
- **Priority**: **CRITICAL**
- **Read first**: `docs/agents/communication/2026-05-15-wave1.md`, `docs/exports/badly-scraped-review-2026-05-14.json`, `docs/exports/data-quality-deep-review-2026-05-13.json`, `docs/exports/action1-dataset-quality-gate.json`, `docs/exports/scrape-database-quality-audit-2026-05-13.json`, `public/data/scraped-listings.json`, `scripts/generate_bad_scrape_review_artifacts.py`, `scripts/generate_frontend_scraped_listings.py`
- **Do**:
  1. Produce an operator-facing XLSX that explains the transformation from raw scraped rows to website-eligible rows.
  2. Include issue buckets, source counts, field coverage, geocode/location risks, sea/wrong-coordinate detection where possible, aggregation limitations, and duplicate/merge rules.
  3. Include row-level review tabs with source URLs, image links/local paths when available, source title, clean title, area sqm, price/status, city/district, coordinates, QA state, grouped/LOST/pending reason, and reviewer comments.
  4. Use Excel hyperlinks, filters, formulas, frozen panes, and check columns instead of unsafe macros/buttons.
  5. Export companion JSON/MD summary with FACT / INTERPRETATION / HYPOTHESIS / GAP.
- **Acceptance gate**: XLSX opens and validates structurally; formulas/check cells have no obvious errors; summary counts reconcile the 30k-ish corpus, DA-07 website-eligible count, grouped/development, bad/lost, and pending/missing QA denominators; no raw private/contact data or unsupported DB-backed claims are introduced.
- **Output**: `docs/exports/operator-dataset-review-2026-05-15.xlsx`, companion JSON/MD, data_analyst JOURNEY entry, `docs/agents/communication/2026-05-15-wave1-data.md`.
- **Verifier**: debugger + ux_ui_designer
- **Depends on**: DA-07, DA-06

### ER-05: Owner claim and edit safety contract
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-14; safety contract only, no schema/API/code implementation)
- **Priority**: HIGH
- **Read first**: `docs/exports/product-website-ux-rebuild-plan-2026-05-14.md`, `docs/exports/entity-resolution-queue-plan-2026-05-13.md`, `docs/exports/entity-resolution-accepted-only-candidate-layer-2026-05-13.md`, `sql/schema.sql`, `src/bgrealestate/services/unification.py`
- **Do**: Define how owner claims, owner edits, source-publication provenance, duplicate candidates, grouped/development pages, and canonical property entities interact without unsafe auto-promotion.
- **Acceptance gate**: no owner claim or edit can auto-promote unaccepted, grouped/development, LOST, inactive, unknown, or conflicting source rows; all edits have draft/review/audit semantics.
- **Output**: `docs/exports/owner-claim-entity-resolution-contract-YYYY-MM-DD.md`, entity_resolution_agent JOURNEY entry.
- **Verifier**: debugger + backend_developer + data_analyst
- **Depends on**: PLAN-08, ER-02, BD-18, BD-19
- **2026-05-14 handoff**: Output saved as `docs/exports/owner-claim-entity-resolution-contract-2026-05-14.md`. Feed into `BD-22` and `DBG-25`; implementation remains blocked until DB/read-model proof or fixture-safe migration prep. Owner claim/edit flows must preserve source facts, use draft/review/audit revisions, and route grouped/development pages to project/unit-split review instead of single-unit promotion.

### ER-06: Wave 2 accepted-only aggregation rule matrix
- **Status**: `TODO` (Wave 2; wait for Wave 1 evidence)
- **Priority**: **CRITICAL**
- **Read first**: `DA-08` output, `S1-25` output if available, `ER-02`, `ER-03`, `docs/exports/action1-multi-unit-publications.json`, `docs/exports/scrape-database-quality-audit-2026-05-13.md`, `src/bgrealestate/services/unification.py`
- **Do**:
  1. Define aggregation only for candidate same-property source publications, not for nearby different properties.
  2. Require accepted single-unit state, compatible city/district/street/address evidence, same or close price with price-status awareness, comparable area, similar normalized description/title tokens, and no grouped/development flags.
  3. Treat same city/street alone as insufficient; same complex/development pages route to project/unit-split review.
  4. Produce negative examples: same building different floor/area/price, same street different unit, same agency template text, same development multiple units, Burgas sea/wrong-coordinate cases.
- **Acceptance gate**: rule matrix blocks false merges and names review actions for duplicate, possible duplicate, same development/project, location-conflict, and distinct-property cases; no canonical merge or DB mutation is performed.
- **Output**: `docs/exports/entity-resolution-aggregation-rule-matrix-2026-05-15.md`, entity_resolution_agent JOURNEY entry.
- **Verifier**: debugger + data_analyst + scraper_1
- **Depends on**: ER-02, DA-08, S1-25 where parser evidence is needed

### ER-07: Parallel cross-source entity candidates from active-link audit
- **Status**: `DONE_AWAITING_VERIFY` but **SUPERSEDED FOR MERGE DECISIONS** (2026-05-15; used only `1,606` website-eligible rows and lacked completed active-link truth; see `ER-08`)
- **Priority**: **CRITICAL**
- **Model**: `5.3-codex-spark`
- **Read first**: `docs/exports/scraper-active-link-review-codex-spark-prompt-2026-05-15.md`, `docs/agents/communication/2026-05-15-triagent-active-link-er-debugger.md`, `ER-02`, `ER-03`, `ER-06`, `DA-08` output, `public/data/scraped-listings.json`, `docs/exports/action1-multi-unit-publications.json`, `src/bgrealestate/services/unification.py`, `tests/test_unification.py`.
- **Do**:
  1. Build reviewable same-property candidate clusters from accepted/single-unit Action1 source publications while `scraper_1` audits active links.
  2. Require at least two different sources for cross-source same-property candidates; same-source exact URL/source-ID duplicates are `source_duplicate` cleanup candidates only.
  3. Score compatible address/city/district, price/price-status, area, rooms, floor, title/description tokens, contact markers, and existing media evidence such as image URL/hash overlap or existing semantic reports.
  4. Block grouped/development, inactive, `LOST`, pending/missing QA, unknown, and conflicting rows from merge-ready status.
  5. Describe image/media evidence as metadata only unless operator sends `Action0 now`; do not generate semantic image reports.
  6. Do not merge, delete, mutate DB/corpus state, or promote canonical entities.
- **Acceptance gate**: candidate matrix includes `definite_same_property_candidate`, `probable_same_property_candidate`, `possible_duplicate`, `same_development_or_project`, `source_duplicate`, `distinct_property`, and `conflicting_evidence`; every candidate cites evidence and blockers; no automatic merge or DB/corpus mutation occurs; `tests.test_unification` passes if code changes; `git diff --check` passes for changed docs/scripts.
- **Output**: `docs/exports/er-07-cross-source-entity-candidates-2026-05-15.md`, `.json`, rules CSV, entity_resolution_agent JOURNEY entry, communication-board update.
- **Verifier**: debugger + data_analyst + scraper_1
- **Depends on**: DA-08, ER-02, ER-03

### ER-08: Full-dataset entity resolution after active-link truth
- **Status**: `BLOCKED_ACTIVE_LINK_TRUTH` (2026-05-15; blocked/preliminary rules artifacts written; final candidates wait for `S1-27` active-link audit and `DBG-32` PASS)
- **Priority**: **CRITICAL**
- **Model**: `5.3-codex-spark`
- **Read first**: `docs/exports/triagent-full-dataset-active-audit-clean-rescrape-prompts-2026-05-15.md`, `docs/agents/communication/2026-05-15-full-dataset-audit-clean-rescrape.md`, `ER-07` outputs, `ER-02`, `ER-03`, `ER-06`, `DA-08` output, `docs/exports/operator-dataset-review-2026-05-15.json`, `docs/exports/action1-multi-unit-publications.json`, `src/bgrealestate/services/unification.py`, `tests/test_unification.py`.
- **Do**:
  1. Mark `ER-07` as preliminary/superseded for merge decisions because it only used website-eligible rows and active-link truth was incomplete.
  2. Prepare normalization/scoring rules while `scraper_1` audits the whole saved corpus.
  3. Produce final same-property/source-duplicate candidates only after `S1-27` active-link status exists for the full saved corpus.
  4. Use only active, accepted, single-unit source publications for same-property candidates; keep inactive, wrong-property, grouped/development, unknown, `LOST`, pending/missing QA, and conflicting rows as negative/cleanup evidence.
  5. Require at least two different active sources for cross-source same-property candidates; same-source exact URL/source-ID duplicates route to cleanup only.
  6. Score compatible offer kind, price/price-status, area, rooms, floor, address/project/unit evidence, title/description tokens, contact/agency markers, and existing media URL/hash/description evidence.
  7. Do not merge, delete, mutate DB/corpus state, or generate Action0 image descriptions.
- **Acceptance gate**: ER-07 is explicitly superseded for merge use; no final ER candidate depends on stale/inactive/unknown/grouped/pending rows; every cross-source candidate cites active-link evidence and blocker state; same-development/different-unit and sale/rent mismatch examples are rejected or review-only; `tests.test_unification` passes if code changes; `git diff --check` passes for changed docs/scripts.
- **Output**: `docs/exports/er-08-full-dataset-entity-resolution-2026-05-15.md`, `.json`, rules CSV, ER-07 supersession note, entity_resolution_agent JOURNEY entry, communication-board update.
- **Verifier**: debugger + data_analyst + scraper_1
- **Depends on**: DA-08, ER-02, ER-03, `S1-27` full active-link audit for final candidates.

### UA-04: Customer/owner website event taxonomy addendum
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-14; taxonomy addendum only, no instrumentation implementation)
- **Priority**: MEDIUM
- **Read first**: `docs/analytics/user-event-taxonomy.md`, `docs/exports/product-website-ux-rebuild-plan-2026-05-14.md`
- **Do**: Add privacy-safe events for customer/owner branch selection, saved areas, saved searches, owner property claim/edit, chat UI action applied, map/list synchronization, and owner inbox actions.
- **Acceptance gate**: payloads remain allowlisted and exclude raw chat/search text, contacts, URLs, IPs, user agents, private notes, and secrets.
- **Output**: analytics taxonomy update/addendum, user_analytics_agent JOURNEY entry.
- **Verifier**: debugger
- **Depends on**: PLAN-08, UA-01
- **2026-05-14 handoff**: Added `Customer/Owner Branch Addendum` to `docs/analytics/user-event-taxonomy.md` with branch/capability, saved search/area, chat UI action, map/list sync, owner claim/edit, and owner inbox events. Debugger should verify rejection cases for raw text/contact/URL/IP/user-agent/private-note/secret fields and keep implementation blocked until `BD-20`/`BD-22`/`UX-20` intake hooks exist.

### VM-06: Premium logo and visual identity directions
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-14; visual direction and local SVG concepts created)
- **Priority**: MEDIUM
- **Read first**: `docs/exports/product-website-ux-rebuild-plan-2026-05-14.md`, UX-23 output when available, `app/globals.css`
- **Do**: Produce premium minimalist logo directions for BGEstate / Real Estate BG with SVG concepts, dark/light variants, favicon/app-icon crop, and usage rules.
- **Acceptance gate**: logo works at 32px, header size, monochrome, dark/light backgrounds; no cartoon house, skyline cliche, or decorative gradient blob.
- **Output**: `docs/agents/vision_media_agent/logo-visual-direction-YYYY-MM-DD.md`, optional `public/brand/*` assets, vision_media_agent JOURNEY entry.
- **Verifier**: ux_ui_designer + debugger
- **Depends on**: PLAN-08, UX-23
- **2026-05-14 handoff**: Output saved as `docs/agents/vision_media_agent/logo-visual-direction-2026-05-14.md` with six local SVG assets under `public/brand/`. Recommended direction is the cadastral `BG` monogram. Verifiers should check 32 px readability, header use, monochrome rendering, dark/light backgrounds, and that no public data-readiness claim is implied.

### VM-07: Wave 3 media-description-to-property-metric contract
- **Status**: `TODO` (Wave 3; semantic generation still blocked until operator `Action0 now`)
- **Priority**: HIGH
- **Read first**: `VM-01`, `VM-05`, `DA-08` output, `S1-25` output, `docs/exports/s1-21-gemma-action0-eligible.json`, `docs/exports/public-search-facet-dictionary-2026-05-14.md`, `agent-skills/image-media-pipeline/SKILL.md`
- **Do**:
  1. Define how semantic image descriptions can add auditable metrics such as room type, visible condition, equipment, style, uncertainty, and media confidence.
  2. Keep area/square meters, price, location, rooms, and source category as scraper/source-text facts first; image descriptions may corroborate or flag uncertainty but must not overwrite source facts.
  3. Define which image-derived fields can later feed detail-page insight buttons and which stay operator-only.
  4. Keep execution blocked until `Action0 now`; no remote image fetch or model analysis in this slice.
- **Acceptance gate**: contract distinguishes source facts from image observations, includes uncertainty and contradiction handling, and blocks buyer-facing semantic claims until VM/debugger/data_analyst verification.
- **Output**: media metric contract doc, vision_media_agent JOURNEY entry.
- **Verifier**: debugger + data_analyst + ux_ui_designer
- **Depends on**: VM-01, VM-05, DA-08, S1-25; execution depends on operator `Action0 now`

### DBG-25: Verify product website plan and prompts
- **Status**: `VERIFIED` (2026-05-14; report produced; result `FAIL_WITH_BLOCKERS` for public copy, hook drift, DB proof, and typecheck completion)
- **Priority**: **CRITICAL**
- **Read first**: `docs/exports/product-website-ux-rebuild-plan-2026-05-14.md`, `docs/exports/product-website-agent-prompts-2026-05-14.md`, `docs/agents/ux_ui_designer/product-website-rebuild-spec-2026-05-14.md`, `docs/agents/TASKS.md`, `AGENTS.md`
- **Do**: Verify PLAN-08 and follow-up slices for source-publication-first safety, accepted-only public data gates, auth/RBAC, owner permissions, privacy, no unsafe scraping, map precision honesty, and executable acceptance gates.
- **Acceptance gate**: PASS/FAIL report exists; blockers are routed to specific agent slices; TASKS statuses are updated only for verified work.
- **Output**: `docs/exports/product-website-plan-verification-YYYY-MM-DD.md`, debugger JOURNEY entry.
- **Verifier**: debugger
- **Depends on**: PLAN-08

### DBG-26: Verify DA-06 public search facet dictionary
- **Status**: `TODO`
- **Priority**: **HIGH**
- **Read first**: `docs/exports/public-search-facet-dictionary-2026-05-14.md`, `docs/exports/product-website-agent-prompts-2026-05-14.md` section 5, `docs/agents/ux_ui_designer/product-website-rebuild-spec-2026-05-14.md`, `docs/exports/data-quality-deep-review-2026-05-13.md`, `scripts/import_scraped_listings.py`, `docs/agents/TASKS.md`
- **Do**:
  1. Verify DA-06 uses only properly scraped importer-safe source-publication candidates for current evidence.
  2. Verify no public facet uses raw, unreviewed, `LOST`, grouped/development, inactive, or unknown rows as public truth.
  3. Verify every facet names UI label, scope, DB/file-backed status, field source, allowed values/buckets, accepted-only requirement, denominator, and blocker/rule.
  4. Verify sale/rent metrics are separate and canonical city/region alias needs are explicit.
  5. Verify owner, value/yield, exact building, and semantic image facets remain blocked until their evidence gates pass.
- **Acceptance gate**: verifier report or JOURNEY entry confirms PASS/FAIL and routes any missing facet evidence to `DA-06`, `BD-22`, or `UX-23` follow-up without changing public-readiness claims.
- **Output**: debugger JOURNEY entry, optional `docs/exports/public-search-facet-dictionary-verification-YYYY-MM-DD.md`.
- **Verifier**: debugger + ux_ui_designer + backend_developer
- **Depends on**: DA-06

### DBG-27: Verify DA-07 bad-scrape review and website exclusion gate
- **Status**: `TODO`
- **Priority**: **HIGH**
- **Read first**: `docs/exports/badly-scraped-review-2026-05-14.xlsx`, `output/pdf/badly-scraped-review-2026-05-14.pdf`, `docs/exports/badly-scraped-review-2026-05-14.json`, `scripts/generate_bad_scrape_review_artifacts.py`, `scripts/generate_frontend_scraped_listings.py`, `docs/dashboard/properties-database.html`, `public/data/scraped-listings.json`
- **Do**:
  1. Verify the workbook has whole-corpus, issue-pattern, bad/grouped, website-eligible, and photo-sample review sheets.
  2. Verify the PDF renders readable issue and photo-sample pages.
  3. Verify the public website export contains only accepted single-unit candidates and excludes `LOST`, grouped/development, suspected multi-unit, pending/missing QA, inactive, unknown, and numeric zero-price rows.
  4. Verify the Properties Database dashboard exposes the bad-scrape artifact links and file-backed denominator labels without claiming DB parity.
  5. Reconcile `ux.accepted_only_public_export` in `scripts/codex_project_hooks.py` with the DA-07 export predicate so hook safety and export safety use the same accepted-only terms.
- **Acceptance gate**: verifier records PASS/FAIL and routes any mismatch to `DA-07`, `UX-18`, or `BD-19`; no public-readiness or DB-backed claim is promoted.
- **Output**: debugger JOURNEY entry, optional `docs/exports/bad-scrape-review-verification-YYYY-MM-DD.md`.
- **Verifier**: debugger + data_analyst
- **Depends on**: DA-07

### DBG-28: Verify BD-22 backend account/search/map/chat contracts
- **Status**: `TODO`
- **Priority**: **CRITICAL**
- **Read first**: `docs/exports/bd22-backend-contract-2026-05-14.md`, `docs/exports/product-website-agent-prompts-2026-05-14.md` section 4, `docs/exports/public-search-facet-dictionary-2026-05-14.md`, `docs/exports/owner-claim-entity-resolution-contract-2026-05-14.md`, `src/bgrealestate/services/account_contracts.py`, `src/bgrealestate/api/routers/user_auth.py`, `src/bgrealestate/api/routers/users.py`, `src/bgrealestate/api/routers/owner.py`, `src/bgrealestate/api/routers/properties.py`, `src/bgrealestate/api/routers/map.py`, `src/bgrealestate/api/routers/chat.py`, `src/bgrealestate/db/models.py`, `sql/schema.sql`, `migrations/versions/20260514_0007_bd22_owner_search_contracts.py`, `tests/test_bd22_contracts.py`
- **Do**:
  1. Verify branch-aware auth separates customer, owner, and operator capabilities and blocks public self-registration as operator.
  2. Verify owner claim/edit APIs preserve source facts, require active owner permissions, write revisions/audit/status records, and block customer edits.
  3. Verify accepted-only search/map predicates reject raw/pending/`LOST`/inactive/grouped/development/missing-source/numeric-zero and missing-price-status rows.
  4. Verify chat UI actions are allowlisted and cannot invent property IDs or property facts.
  5. Run focused py_compile and unit/API smoke tests; record DB proof blocked if `DATABASE_URL` remains absent.
- **Acceptance gate**: verifier report or JOURNEY entry confirms PASS/FAIL, lists commands, and keeps DB-backed public readiness blocked until migrations/read-model counts run with `DATABASE_URL`.
- **Output**: debugger JOURNEY entry, optional `docs/exports/bd22-backend-contract-verification-YYYY-MM-DD.md`.
- **Verifier**: debugger + ux_ui_designer + backend_developer
- **Depends on**: BD-22

### DBG-29: Verify Wave 1 website operability and operator XLS
- **Status**: `TODO`
- **Priority**: **CRITICAL**
- **Read first**: `UX-25`, `DA-08`, `docs/agents/communication/2026-05-15-wave1.md`, `docs/agents/communication/2026-05-15-wave1-ux.md`, `docs/agents/communication/2026-05-15-wave1-data.md`, `docs/exports/operator-dataset-review-2026-05-15.xlsx`, `public/data/scraped-listings.json`, frontend changed files.
- **Do**:
  1. Verify property detail route opens from listing cards, map/list actions, and chat actions using file-backed accepted-only data.
  2. Verify profile/chat/settings buttons either navigate or change visible state; no dead primary controls remain.
  3. Verify area filters and prominent area metrics work without exposing unaccepted rows.
  4. Verify workbook sheets, formulas/checks, hyperlinks, row counts, and issue explanations are structurally valid and do not claim DB-backed truth.
  5. Run `npm run typecheck` or record the exact blocker; run workbook validation; run focused export predicate checks.
- **Acceptance gate**: PASS/FAIL report names any UI, typecheck, XLS, data-gate, or public-claim blocker; no task is marked verified without reproducible evidence.
- **Output**: debugger JOURNEY entry, optional `docs/exports/wave1-operator-correction-verification-2026-05-15.md`, TASKS status updates.
- **Verifier**: debugger + planner
- **Depends on**: UX-25, DA-08
- **2026-05-15 Branch B note**: frontend-specific gates were run and logged in debugger JOURNEY. `DBG-29` remains `TODO` because the operator XLS/workbook verification portion was not re-run in this Branch B pass.

### DBG-30: Verify strategic kickoff handoff and branch gates
- **Status**: `TODO`
- **Priority**: **CRITICAL**
- **Read first**: `PLAN-12`, `docs/exports/strategic-handoff-2026-05-15.md`, `docs/agents/communication/2026-05-15-strategic-handoff.md`, `docs/exports/final-all-agent-branch-execution-plan-2026-05-15.md`, `docs/agents/TASKS.md`, project wiki `memory.md`/`insights.md`.
- **Do**:
  1. Verify the two-branch boundary is explicit and does not assign scraped corpus or DB mutation to the strategic kickoff.
  2. Verify market/competitor implications are framed as product priorities, not public coverage proof.
  3. Verify blocked claims remain blocked.
  4. Verify success metrics are measurable without raw text/contact/URL/IP/user-agent/private-note leakage.
  5. Verify communication artifacts exist and point implementation agents to the accepted-only contract.
- **Acceptance gate**: PASS/FAIL verifier note names any branch-boundary, blocked-claim, privacy, release-hygiene, or source-publication-first drift. Implementation branches should not claim readiness before this gate passes unless the operator records a waiver.
- **Output**: debugger JOURNEY entry, optional `docs/exports/debugger-strategic-handoff-verification-2026-05-15.md`, TASKS status update.
- **Verifier**: debugger
- **Depends on**: PLAN-12

### DBG-31: Concurrent verifier for scraper active-link audit and ER candidates
- **Status**: `TODO` but **SUPERSEDED BY `DBG-32`** for the full-dataset cleanup/rescrape goal
- **Priority**: **CRITICAL**
- **Model**: `gpt-5.5`
- **Reasoning**: `xhigh`
- **Read first**: `docs/exports/scraper-active-link-review-codex-spark-prompt-2026-05-15.md`, `docs/agents/communication/2026-05-15-triagent-active-link-er-debugger.md`, `S1-26`, `ER-07`, `docs/agents/roles/debugger.md`, `.cursor/BUGBOT.md`, `data/source_registry.json`, `tests/test_action1_parser_regressions.py`, `tests/test_unification.py`.
- **Do**:
  1. Start immediately as a guard/monitor while scraper and entity-resolution agents run.
  2. Verify disjoint write sets, Action1-only source scope, disk preflight, source legal/access gates, and no deletion/DB mutation/Action2/Action0/media-download/broad-crawl permission.
  3. After producer outputs exist, verify scraper active/inactive/unknown/changed/duplicate evidence and same-detail-URL rescrape staging.
  4. Verify ER candidates require different sources for same-property clusters and block grouped/development, inactive, LOST, pending/missing QA, unknown, and conflicting rows from merge-ready status.
  5. Run focused parser/unification tests if code changes, plus `git diff --check` on changed docs/scripts.
  6. Produce PASS/FAIL with exact blockers and owner follow-ups; update TASKS only if verification is conclusive.
- **Acceptance gate**: no unsafe scrape/delete/import/merge/public-claim drift; FACT / INTERPRETATION / HYPOTHESIS / GAP separated; file-backed, live-link, and DB-backed evidence labels remain distinct.
- **Output**: `docs/exports/dbg-31-triagent-active-link-er-verification-2026-05-15.md`, debugger JOURNEY entry, communication-board update, TASKS verification updates when justified.
- **Verifier**: debugger
- **Depends on**: S1-26, ER-07 for final pass; concurrent guard pass starts immediately.

### DBG-32: Concurrent verifier for full-dataset active audit, cleanup, rescrape, and ER
- **Status**: `VERIFIED` as executed with `BLOCKED_NO_PASS` (2026-05-15; `S1-27` stopped on low disk before live checks and `ER-08` was not produced)
- **Priority**: **CRITICAL**
- **Model**: `gpt-5.5`
- **Reasoning**: `xhigh`
- **Read first**: `docs/exports/triagent-full-dataset-active-audit-clean-rescrape-prompts-2026-05-15.md`, `docs/agents/communication/2026-05-15-full-dataset-audit-clean-rescrape.md`, `S1-27`, `ER-08`, `S1-26` outputs, `ER-07` outputs, `docs/agents/roles/debugger.md`, `.cursor/BUGBOT.md`, `data/source_registry.json`, `tests/test_action1_parser_regressions.py`, `tests/test_unification.py`.
- **Do**:
  1. Start immediately as guard/monitor while scraper and entity-resolution agents run.
  2. Verify `S1-26` is treated as incomplete queue-only evidence and `ER-07` as preliminary/superseded for merge decisions.
  3. Verify `scraper_1` audits every saved row under `data/scraped/*/listings/*.json`, not only `public/data/scraped-listings.json`.
  4. Verify no broad category/search-page patterned rescrape starts before full active-link audit coverage and cleanup manifest PASS.
  5. Verify disk preflight, background PID/log/checkpoint/resume behavior, source-registry legal/access gates, and unsafe-source exclusions.
  6. Verify cleanup is reversible and reason-coded before any row is removed from active/public corpus or archived.
  7. Verify ER final candidates require active verified links and different sources, while grouped/development, inactive, wrong-property, unknown, `LOST`, pending/missing QA, conflicting, and offer-kind-mismatched rows are blocked from merge-ready status.
  8. Run focused parser/unification tests if code changes plus `git diff --check` on changed docs/scripts.
- **Acceptance gate**: PASS only if the whole saved corpus is accounted for, the 30k-vs-1.6k gap is explained by evidence, cleanup is verified before deletion/archive/public-corpus removal, patterned rescrape is post-audit and legal-gated, and ER remains review-only. FAIL with exact owner follow-ups on partial-audit, premature-rescrape, unsafe-delete, or auto-merge drift.
- **Output**: `docs/exports/dbg-32-full-dataset-audit-clean-rescrape-verification-2026-05-15.md`, debugger JOURNEY entry, communication-board update, TASKS verification updates when justified.
- **Verifier**: debugger
- **Depends on**: S1-27, ER-08 for final pass; concurrent guard pass starts immediately.
- **2026-05-15 verifier note**: `docs/exports/dbg-32-full-dataset-audit-clean-rescrape-verification-2026-05-15.md` blocks PASS. Safety gates held, but full active-link truth, cleanup manifest, patterned rescrape, and active-link-based ER remain incomplete.

## ═══════════════════════════════════════════════════════
## DATA_ANALYST (scraped corpus QA + metrics truth)
## ═══════════════════════════════════════════════════════

**Mission**: Be the truth layer for scraped data. Reconcile file-backed and DB-backed counts, detect wrong properties/text/images/coordinates/prices, classify accepted vs `LOST` vs grouped/development, and make dashboards honest.

### DA-01: Action1 A1 corpus consistency audit
- **Status**: `VERIFIED` (2026-05-13 by DBG-14; file-backed audit reproducible, DB counts still blocked by missing `DATABASE_URL`)
- **Priority**: **CRITICAL**
- **Read first**: `docs/exports/a1-pattern-depth-reliability-review-2026-05-04.md`, `docs/exports/action1-dataset-quality-gate-dryrun.json`, `docs/exports/action1-dataset-quality-gate.json`, `docs/exports/source-item-photo-coverage.json`, `docs/exports/scrape-status-dashboard.json`, `data/runs/scrape_metrics.jsonl`, `data/runs/action1_scrape_uncapped_*.log`, A1 `data/scraped/<source>/listings/*.json`
- **Do**:
  1. For each A1 source and each bucket, compute accepted/good, `LOST`, grouped/development, inactive, missing-description, missing-price, suspicious-area, outside-Bulgaria/outside-source-scope, one-photo, remote-vs-local gallery mismatch, and image-readability gaps.
  2. Compare scraper file counts with importer dry-run counts and DB counts when `DATABASE_URL` is available.
  3. Produce source-level issue reasons and exact rescrape queues for scraper_1.
  4. Mark rows as bad only through the existing quality-gate fields; do not silently delete rows.
  5. Refresh dashboard inputs only from reproducible scripts, never from chat summaries.
- **Acceptance gate**: report includes seven A1 sources × four buckets with counts and reasons; every bad class has a clear next action: rescrape, grouped/development review, inactive skip, parser fix, legal/runtime blocker, or human review.
- **Output**: `docs/exports/scrape-database-quality-audit-2026-05-13.md`, `docs/exports/scrape-database-quality-audit-2026-05-13.json`, data_analyst JOURNEY. DB count proof remains blocked until `DATABASE_URL` is available; import dry-run now works offline and skips unreviewed rows by default.
- **Verifier**: debugger
- **Depends on**: S1-22B active corpus evidence

### DA-02: Dashboard metric contract repair
- **Status**: `VERIFIED` (2026-05-13 by DBG-24 for file-backed denominator/readiness handoff; DB counts still blocked)
- **Priority**: HIGH
- **Read first**: `scripts/generate_data_quality_deep_review.py`, `docs/exports/data-quality-deep-review-2026-05-13.md`, `docs/dashboard/data-quality-dashboard.html`, `scripts/generate_scrape_status_dashboard.py`, `scripts/generate_source_item_photo_coverage.py`, `docs/dashboard/scrape-status.html`, DA-01 report
- **Do**: ensure dashboard cells show website/source total, accepted count, fully parsed count, description count, local-gallery count, image-description count, and rescrape/LOST/grouped counts separately. Reconcile grouped/development denominator semantics across `scripts/audit_scrape_database_quality.py`, `scripts/action1_dataset_quality_gate.py`, and dashboard exports so rows that are both bad and multi-unit are not double-counted or mislabeled.
- **Acceptance gate**: dashboard no longer uses threshold denominators such as `100` as source-total denominators; clearly separates accepted properties from grouped source publications; labels stored/importer-state counts separately from DA-01 offline quality estimates; reconciles or explicitly documents `bad_lost`, `grouped_publication`, and `bad_and_grouped` denominator semantics.
- **Output**: `scripts/generate_data_quality_deep_review.py`, `docs/exports/data-quality-deep-review-2026-05-13.md`, `docs/exports/data-quality-deep-review-2026-05-13.json`, `docs/dashboard/data-quality-dashboard.html`, refreshed dashboard exports, data_analyst JOURNEY. Remaining blocker: DB-backed denominator proof still requires `DATABASE_URL` and `INFRA-02`.
- **Verifier**: debugger + ux_ui_designer
- **Depends on**: DA-01

### DA-04: Four-dashboard denominator certification
- **Status**: `TODO`
- **Priority**: HIGH
- **Read first**: `DA-02`, `DA-03`, `docs/exports/operational-dashboards.json`, `docs/dashboard/properties-database.html`, `docs/exports/scrape-database-quality-audit-2026-05-13.json`, `docs/exports/action1-dataset-quality-gate.json`, `docs/exports/scrape-status-dashboard.json`
- **Do**:
  1. Certify which dashboard counts are file-backed audit counts, quality-gate counts, scrape-status operational counts, importer default candidates, or future DB counts.
  2. Add a short denominator note for every Properties Database dashboard metric that can be misread as accepted property count.
  3. Reconcile source-level differences between DA audit, action1 quality gate, and scrape-status export; preserve unresolved overlap as explicit `GAP`, not hidden adjustment.
  4. Hand backend/UX/debugger a stable metric dictionary for `BD-19`, `UX-16`, and dashboard verification.
- **Acceptance gate**: no dashboard cell can be mistaken for public market coverage; accepted single-unit, grouped/development, `LOST`, pending/missing QA, description, and media denominators are named and reproducible.
- **Output**: certified denominator note or JSON overlay, refreshed operational dashboards, data_analyst JOURNEY.
- **Verifier**: debugger + ux_ui_designer + backend_developer
- **Depends on**: DA-02, DA-03, PLAN-06

### DA-05: Deep property analytics dashboard layer
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-13; file-backed source/regional/image/text analytics added, DB proof still blocked)
- **Priority**: **HIGH**
- **Read first**: `scripts/generate_data_quality_deep_review.py`, `scripts/generate_operational_dashboards.py`, `docs/exports/data-quality-deep-review-2026-05-13.md`, `docs/exports/properties-deep-analytics-agent-handoff-2026-05-13.md`, `docs/dashboard/properties-database.html`, `docs/dashboard/data-quality-dashboard.html`
- **Do**:
  1. Add source-level statistical metrics for rows, accepted candidates, blocked rows, median price, median area, median price-per-sqm, description coverage, median description words, full-gallery rate, median remote/local photos, text tendencies, and top bad rules.
  2. Add regional/city property report with candidate rate, sale median, rent median, area, price-per-sqm, source mix, description coverage, gallery completeness, and decision notes.
  3. Add image and description analytics by source, including partial galleries, one-photo suspects, duplicate image URLs, thin/missing/duplicated descriptions, and semantic-description blockers.
  4. Add textual tendency groups for scraper, DB, market, UX, vision, and entity-resolution use, while labeling them as hypotheses, not property facts.
  5. Update Codex hooks so missing deep property analytics is caught before future dashboard/market handoffs.
- **Acceptance gate**: `make operational-dashboard-doc`, JSON validation, `make codex-hooks`, and debugger review pass; every metric is labeled file-backed/un-deduped and no public market coverage claim is made.
- **Output**: refreshed `docs/dashboard/properties-database.html`, `docs/dashboard/data-quality-dashboard.html`, `docs/exports/data-quality-deep-review-2026-05-13.md/json`, `docs/exports/properties-deep-analytics-agent-handoff-2026-05-13.md`, hook updates.
- **Verifier**: debugger + market_intelligence_analyst + scraper_1 + backend_developer + ux_ui_designer
- **Depends on**: DA-02, PLAN-06

## ═══════════════════════════════════════════════════════
## BACKEND_DEVELOPER (data engineer + infrastructure)
## ═══════════════════════════════════════════════════════

**Mission**: Make Postgres + FastAPI the **reliable system of record**: migrations, typed repositories, **BD-11 ingest** so scrapers are auditable in `canonical_listing`, CORS-safe local/LAN hosting, and API contracts that stay aligned with `lib/types/listing.ts` and Next `/api/backend/*` proxies. Data-quality interpretation belongs to `data_analyst`; backend owns persistence and API correctness.

**Detective index (2026-04-30)**: `docs/exports/detective-product-orchestration-2026-04-30.md` (API↔UI alignment, hosting).

**2026-04-09 wave:** Until **`S1-18`** is `VERIFIED`, treat **`BD-11`** (live ingest → `canonical_listing`) as the **only** must-ship backend slice. Defer **`BD-12`–`BD-16`** unless they unblock ingest or the operator reprioritizes.

### BD-01: DB sync + control plane bootstrap
- **Status**: `VERIFIED` — hardened 2026-04-08 session 2 (stats query registry-aware, admin dashboard extended, tests added)
- **Read first**: `docs/development-setup.md`, `src/bgrealestate/db_sync.py`, `src/bgrealestate/connectors/legal.py`, `sql/schema.sql`
- **Do**: run Compose + migrations, sync registry into Postgres (`source_registry`, `source_legal_rule`, `source_endpoint`)
- **Acceptance gate**: `GET /api/v1/ready` returns 200; `GET /admin/source-stats` returns JSON with all registry sources (tier, legal_mode, has_legal_rule, has_endpoint); `make export-source-stats` writes XLSX
- **Output**: `docs/exports/source-stats.xlsx` via `scripts/export_source_stats_xlsx.py`; `tests/test_control_plane.py`
- **Verifier**: debugger
- **Depends on**: —

### BD-02: Listings, CRM, Crawl APIs + DB dependencies
- **Status**: `VERIFIED`
- **Read first**: `src/bgrealestate/api/`, `src/bgrealestate/db/repositories.py`, `PLAN.md` §7
- **Do**: `GET /listings`, `GET /listings/{id}`, `GET /crm/threads`, `GET /crm/threads/{id}/messages`, `POST .../messages` (manual notes only), `GET /crawl-jobs`; shared `get_engine`/`get_db` deps
- **Acceptance gate**: `make test` passes; API returns 503 cleanly when `DATABASE_URL` unset; with DB, returns JSON lists
- **Output**: API routes registered in FastAPI; repository methods for list/get
- **Verifier**: debugger + scraper_1 (API contracts match what connectors write)
- **Depends on**: BD-01

### BD-03: Stats v2 (coverage breakdown)
- **Status**: `VERIFIED` (2026-04-08; debugger acceptance gate pass)
- **Read first**: `src/bgrealestate/api/routers/`, `src/bgrealestate/db/repositories.py`
- **Do**: extend stats to include photo coverage and intent/category breakdown from `canonical_listing`
- **Acceptance gate**: `/admin` dashboard shows coverage bars; XLSX export includes new columns
- **Output**: updated `/admin` dashboard + XLSX export
- **Verifier**: debugger
- **Depends on**: BD-02
- **Resolution**: updated `tests/test_control_plane.py` for expanded `SourceStatRow`; `make validate` passes.

### BD-04: Auth / RBAC on CRM and listings routes
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08)
- **Read first**: `sql/schema.sql` (app_user, api_key, permission_grant), `PLAN.md` §7
- **Do**: API key or session auth middleware; protect CRM write + listings write + admin routes
- **Acceptance gate**: unauthenticated requests return 401/403; `make test` passes with auth fixtures
- **Output**: auth middleware + test fixtures
- **Resolution**: implemented API-key scope checks (`listings:read`, `crm:read`, `crm:write`, `crawl:read`, `admin:read`) with route protection and auth tests.
- **Verifier**: debugger (Bugbot priority: auth/RBAC)
- **Depends on**: BD-02

### BD-05: Temporal workflow wiring
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08: Temporal worker/scheduler runtime scaffold implemented)
- **Read first**: `src/bgrealestate/dev_worker.py`, `src/bgrealestate/dev_scheduler.py`, `agent-skills/workflow-runtime/SKILL.md`
- **Do**: replace dev stubs with real Temporal worker + scheduler; implement `SourceDiscoveryWorkflow` and `ListingDetailWorkflow`
- **Acceptance gate**: jobs survive worker restart; cursors persist; `make test` passes
- **Output**: Temporal workflows, workers, scheduler config
- **Verifier**: debugger (idempotency + restart survival)
- **Depends on**: BD-01, BD-02
- **Verifier note**: run live check with Temporal service (`ENABLE_TEMPORAL_RUNTIME=1`) to confirm restart survival and persistent cursor behavior.

### BD-06: Map/search + chat context APIs (geo scope configurable)
- **Status**: `TODO`
- **Read first**: `PLAN.md` §8, `src/bgrealestate/api/routers/listings.py`, `src/bgrealestate/api/routers/chat.py`, `sql/schema.sql`
- **Do**: expose **configurable** geo scope for `/listings` + map-related contracts: **default = all Bulgaria** (no forced Varna filter). Support optional query params or feature flags for **Varna preset** (city/region bbox) for demos and 3D pilot. Expose chat context payload so AI chat can always view current property + active map filter state.
- **Acceptance gate**: API contract tests prove (a) default/nationwide listing queries return Bulgaria-wide results when data exists, (b) optional Varna scope filter works when requested, (c) chat context returns selected property + active filters
- **Coordination**: **`UX-04`** is **nationwide**; do not ship APIs that hard-lock clients to Varna-only unless behind an explicit opt-in flag.
- **Output**: API contract docs + tests + route updates
- **Verifier**: debugger + ux_ui_designer
- **Depends on**: BD-02, BD-03, DBG-05

### BD-07: AI chat API bridge for property-aware search assistant
- **Status**: `TODO`
- **Read first**: `src/bgrealestate/api/routers/chat.py`, `PLAN.md` §8, UX-05 task
- **Do**: create backend chat bridge endpoint to selected AI chat API with retrieval context from current property item + active listing/map filters
- **Acceptance gate**: chat endpoint returns responses that include referenced property IDs and active filter echo; tests cover fallback/error states
- **Output**: chat bridge contract + tests + provider adapter
- **Verifier**: debugger + ux_ui_designer
- **Depends on**: BD-06

### BD-08: Varna OSM 3D building data pipeline
- **Status**: `TODO`
- **Read first**: `docs/business/varna-3d-osm-integration.md`, `sql/schema.sql` (building_entity)
- **Do**: download GeoFabrik Bulgaria extract, clip to Varna bbox, extract buildings with height/levels, import into PostGIS `building_entity`, generate PMTiles for MapLibre 3D extrusion
- **2026-04-28 product note**: homepage now uses OSM raster base map with at most 20 aggregated city/district points. Do not treat synthetic marker clusters as building-level geospatial objects. This slice must provide real address/coordinate → OSM/PostGIS building footprint matches before the UI can highlight actual buildings.
- **Acceptance gate**: `scripts/import_osm_buildings_varna.py` runs on fixture/sample data; PostGIS query returns building footprints; PMTiles file generated
- **Output**: `scripts/import_osm_buildings_varna.py`, `data/tiles/varna-buildings.pmtiles`, migration for building_entity enrichment, tests
- **Verifier**: debugger + ux_ui_designer
- **Depends on**: BD-01

### BD-09: Property analytics views + duplicate detection
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08: SQL views + API endpoints implemented)
- **Read first**: `sql/schema.sql`, `src/bgrealestate/db/repositories.py`
- **Do**: create SQL views `v_property_analytics` (aggregation by type/district/price/source) and `v_duplicate_candidates` (same address + similar price + similar area); create endpoint `GET /analytics/summary`
- **Acceptance gate**: views return expected shapes on seeded data; API endpoint works; `make test` passes
- **Output**: `sql/views.sql`, `src/bgrealestate/api/routers/analytics.py`, tests in `test_api_fastapi.py` + `test_unification.py`
- **Resolution**: created materialized views in `sql/views.sql`; `GET /analytics/summary` (scope `listings:read`) and `GET /analytics/duplicates` (scope `admin:read`) with inline SQL queries; auth-gated; 503 without DB; tests pass on `make validate`.
- **Verifier**: debugger
- **Depends on**: BD-02

### BD-10: Photo classification pipeline stub
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08: classifier stub + model columns + 14 tests)
- **Read first**: `sql/schema.sql` (media_asset), `src/bgrealestate/models.py`
- **Do**: add columns to `media_asset` (room_type, quality_score, is_exterior, is_floorplan); create stub classifier `src/bgrealestate/analytics/photo_classifier.py` that accepts an image path and returns classification dict; fixture-backed tests
- **Acceptance gate**: migration applies; classifier stub returns expected dict on test image; `make test` passes
- **Output**: `src/bgrealestate/analytics/photo_classifier.py`, updated `sql/schema.sql` + `db/models.py`, `tests/test_photo_classifier.py` (14 tests)
- **Resolution**: Added 4 columns to `media_asset` (room_type, quality_score, is_exterior, is_floorplan). Heuristic classifier detects room types (kitchen, bathroom, bedroom, living_room, balcony, entrance, garage, garden, pool), exterior/facade images, and floorplans from filename/URL + metadata captions. Supports Bulgarian labels. Quality score estimates based on image dimensions. Batch API included. All 14 tests pass.
- **Verifier**: debugger
- **Depends on**: BD-01

### BD-11: Unified listing database — merge scraper outputs into canonical store
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08: unification service + /properties endpoints + pipeline wiring implemented)
- **Priority**: **CRITICAL** — core pipeline for the website; **execution order:** verify/promote **`BD-11` immediately after `S1-15` live path exists** so `S1-18` volume counts use PostgreSQL. Remaining backend slices (`BD-12`+) wait until **`S1-18` VERIFIED** unless they unblock ingest.
- **Read first**: `src/bgrealestate/connectors/ingest.py`, `src/bgrealestate/pipeline.py`, `sql/schema.sql` (source_listing → parsed_listing → canonical_listing → property_entity), `src/bgrealestate/db/models.py`
- **Do**:
  1. Create `src/bgrealestate/services/unification.py` — takes raw scraper output from any tier-1/2/3 connector and writes into `source_listing` → `parsed_listing` → `canonical_listing` pipeline
  2. Implement deduplication: match by address + similar price + similar area within same city/district → link to single `property_entity`
  3. Create `property_entity` records that aggregate all source listings for the same physical property
  4. Merge best data: take highest-quality photos, most complete description, latest price from all sources
  5. Compute `confidence_score` per property based on number of cross-source matches
  6. Create `GET /properties` endpoint (distinct from `/listings`) that returns deduplicated property entities with all source listings attached
  7. Create `GET /properties/{id}` endpoint with full property detail including source breakdown
  8. Wire scraper outputs to unification service via Temporal workflow or cron job
- **Acceptance gate**: given 3 fixture listings for the same apartment from different sources, unification produces 1 `property_entity` with 3 linked `canonical_listing` records; `/properties` endpoint returns deduplicated list; `make test` passes
- **Output**: `src/bgrealestate/services/unification.py`, `src/bgrealestate/api/routers/properties.py`, `PropertyEntityRepository` in `repositories.py`, `tests/test_unification.py`, updated `connectors/ingest.py`
- **Resolution**: Created unification service with dedupe-key matching (city+normalized_address+area_sqm bucket), property_entity creation, property_offer linkage, confidence scoring (0.2/0.5/0.8+ based on distinct source count), best-data merge (longest description, most photos). Wired into `ingest_listing_detail_html` via `unify=True` flag. `GET /properties` and `GET /properties/{id}` endpoints (scope `listings:read`) with full source breakdown. Tests pass on `make validate` (121 tests, 25 skipped for Python 3.9). Full live acceptance gate (3 listings → 1 property_entity) requires DB + Python 3.10+.
- **Verifier**: debugger + scraper_1
- **Depends on**: BD-01, BD-02, S1-13

### BD-12: Shop-style filter API for property feed
- **Status**: `TODO`
- **Priority**: **CRITICAL** — this powers the main listing/shop view (**blocked until `S1-18` VERIFIED** unless operator waives)
- **Read first**: `docs/business/product-ux-structure.md` (§3.1 Homepage), `src/bgrealestate/api/routers/listings.py`, UX-08
- **Do**:
  1. Extend `GET /properties` with full filter parameters: `intent` (buy/rent/str/auction), `category` (apartment/house/villa/studio/land/commercial), `price_min`, `price_max`, `area_min`, `area_max`, `rooms_min`, `rooms_max`, `city`, `district`, `bbox` (map viewport), `sort_by` (price_asc, price_desc, newest, area), `page`, `limit`
  2. Add `GET /properties/facets` — returns available filter options with counts (how many apartments, how many houses, price range, etc.)
  3. Add PostGIS spatial query: filter by map bounding box (`bbox=lat1,lon1,lat2,lon2`) and polygon draw (`polygon=...`)
  4. Add `GET /properties/map-clusters` — return clustered pins for low zoom levels, individual pins for high zoom
  5. Ensure all filters compose correctly (AND logic)
  6. Add sort + pagination with cursor-based pagination for infinite scroll
- **Acceptance gate**: API returns correct filtered results with seeded data; facets reflect filter state; bbox query works; cluster endpoint returns GeoJSON; `make test` passes
- **Output**: updated API routes, PostGIS queries, facet aggregation, tests
- **Verifier**: debugger + ux_ui_designer
- **Depends on**: BD-11, BD-06

### BD-13: User profile + auth system (buyer/renter/seller modes)
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08: registration, login, profile, saved properties, dashboard implemented)
- **Priority**: **HIGH** — users need accounts to save properties, post listings, and switch modes
- **Read first**: `sql/schema.sql` (app_user, organization_account), `docs/business/product-ux-structure.md` (§3.7 Post Listing), `src/bgrealestate/api/auth.py`
- **Do**:
  1. Implement user registration: `POST /auth/register` (email + password + name)
  2. Implement login: `POST /auth/login` → returns JWT token
  3. Implement user profile: `GET /users/me`, `PATCH /users/me`
  4. Add `user_mode` field to `app_user`: enum `buyer` | `renter` | `seller` | `agent` — user can switch freely
  5. Mode-specific features:
     - **Buyer/Renter mode**: saved properties (`POST /users/me/saved`), saved searches, alert preferences, contact history
     - **Seller mode**: my listings (`GET /users/me/listings`), post new listing (`POST /listings`), edit listing, deactivate listing
     - **Agent mode**: managed properties (on behalf of owner), lead inbox from CRM
  6. `GET /users/me/dashboard` — returns mode-appropriate dashboard data (saved count, listing count, leads count)
  7. Photo upload for listings: `POST /media/upload` → S3/MinIO → returns media_asset reference
  8. Listing submission: `POST /listings` with validation (requires photos, price, location, category)
- **Acceptance gate**: registration + login flow works end-to-end; mode switch updates user record; saved properties persist; listing submission creates `canonical_listing` + `property_entity`; `make test` passes
- **Output**: `src/bgrealestate/services/user_auth.py`, `src/bgrealestate/api/routers/user_auth.py`, `src/bgrealestate/api/routers/users.py`, `src/bgrealestate/api/user_deps.py`, `tests/test_user_auth.py`
- **Resolution**: Implemented items 1–6: registration with PBKDF2 password hashing, JWT login, user profile with mode switching, saved properties CRUD, mode-appropriate dashboard. Listing submission (items 7–8) deferred to follow-up slice as it requires media upload pipeline (S3/MinIO). 14 tests pass (pure auth + endpoint registration).
- **Verifier**: debugger + ux_ui_designer
- **Depends on**: BD-04, BD-11

### BD-14: Railway deployment — backend + DB + scraper worker
- **Status**: `TODO`
- **Priority**: **CRITICAL** — nothing works publicly without deployment
- **Read first**: `Dockerfile`, `docker-compose.yml`, `Makefile`, `pyproject.toml`
- **Do**:
  1. Create `railway.toml` configuration for 3 services:
     - **api**: FastAPI backend (`make run-api`), port 8000, `DATABASE_URL` from Railway PostgreSQL plugin
     - **worker**: Temporal/cron scraper worker (`make run-worker`), connects to same DB
     - **scheduler**: Cron scheduler for periodic scrapes (`make run-scheduler`)
  2. Add Railway PostgreSQL plugin with PostGIS extension
  3. Add Railway Redis plugin
  4. Create `scripts/railway_deploy.sh` — automates initial deploy: migrate → sync-registry → seed initial data
  5. Set environment variables: `DATABASE_URL`, `REDIS_URL`, `API_KEYS_JSON`, `OPENAI_API_KEY`, `CORS_ORIGINS`
  6. Configure health check at `GET /api/v1/ready`
  7. Set up auto-deploy from `main` branch via Railway GitHub/GitLab integration
  8. Document deployment in `docs/deployment.md`
- **Acceptance gate**: `https://bgrealestate-api.up.railway.app/api/v1/ready` returns 200; `/admin/source-stats` returns JSON; listings endpoint works from Vercel frontend
- **Output**: `railway.toml`, deploy scripts, deployment docs, environment setup guide
- **Verifier**: debugger
- **Depends on**: BD-01, BD-04

### BD-15: Scraper orchestration — continuous crawl loop
- **Status**: `TODO`
- **Priority**: **CRITICAL** — the database must be populated with real data
- **Read first**: `src/bgrealestate/connectors/factory.py`, `src/bgrealestate/connectors/ingest.py`, `src/bgrealestate/dev_scheduler.py`, BD-05 output
- **Do**:
  1. Implement production scraper loop in `src/bgrealestate/services/scraper_runner.py`:
     - On startup: load all tier-1 sources from `source_registry`
     - For each source: discover listing URLs → fetch detail → parse → unify → store
     - Respect `freshness_target` per source (10min for OLX/Homes, hourly for agencies)
     - Implement crawl cursor persistence (resume from last position)
     - Rate limiting per source (configurable, default 1 req/sec)
     - Error handling: log failures to `crawl_attempt` table, skip and continue
     - Metrics: update `crawl_job` records with success/fail counts
  2. Wire to Temporal workflows OR implement as asyncio cron (simpler for MVP)
  3. Create `make run-scraper` command
  4. Add health endpoint: `GET /api/v1/scraper-status` — returns last crawl time per source, queue depth, error rate
- **Acceptance gate**: scraper runs continuously on Railway; new listings appear in database within freshness_target; `/scraper-status` shows healthy state; no live-network dependency in test suite (tests use fixtures)
- **Output**: `src/bgrealestate/services/scraper_runner.py`, updated Makefile, health endpoint, Railway worker config
- **Verifier**: debugger + scraper_1
- **Depends on**: BD-05, BD-11, BD-14

### BD-16: WebSocket/SSE for real-time listing updates
- **Status**: `TODO`
- **Priority**: MEDIUM — nice-to-have for live feed updates
- **Read first**: `src/bgrealestate/api/main.py`, BD-15 output
- **Do**: add Server-Sent Events endpoint `GET /listings/stream` that pushes new listings as they're ingested; frontend can subscribe for live feed updates
- **Acceptance gate**: SSE endpoint sends events when new listings are inserted; frontend receives and displays them; `make test` passes
- **Output**: SSE endpoint, event publisher in unification service, tests
- **Verifier**: debugger
- **Depends on**: BD-15, BD-12

### BD-17: User-property state ledger + property chat bridge
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-29: liked status ledger, user-property chat join, and Ollama chat adapter implemented)
- **Priority**: HIGH — needed for account UX, liked properties, and property-aware chat
- **Read first**: `sql/schema.sql`, `src/bgrealestate/api/routers/users.py`, `src/bgrealestate/services/chat_service.py`, UX-14
- **Do**:
  1. Persist user-property likes as durable state, not only a row that disappears on unlike.
  2. Record every like/unlike status transition in a separate event table.
  3. Create an explicit `user -> property -> chat -> lead_thread` connection.
  4. Persist property-chat user/assistant messages in `lead_message`.
  5. Route chat replies through a backend provider adapter; default local test provider is Ollama `gemma4:26b`, with API keys kept on the backend process only.
- **Acceptance gate**: focused backend tests pass; `/users/me/liked` and `/users/me/property-chats` require Bearer auth; chat service can call Ollama adapter under mocked HTTP and falls back to stub when local Ollama is unavailable; frontend typecheck passes.
- **Output**: `migrations/versions/20260429_0004_user_property_state_chat.py`, updated schema/models, updated users/chat API, `tests/test_chat_service.py`, expanded auth/API tests.
- **Verifier**: debugger + ux_ui_designer
- **Depends on**: BD-13, BD-11

### BD-18: Canonical import/schema alignment for scraped QA evidence
- **Status**: `IN_PROGRESS` (2026-05-13 backend prep + analyst safety patch + DB table/smoke script implementation; live DB migration/import proof still blocked by missing `DATABASE_URL`)
- **Priority**: **CRITICAL**
- **Read first**: `docs/exports/scrape-database-quality-audit-2026-05-13.md`, `docs/exports/bd18-database-review-and-correction-spec-2026-05-13.md`, `scripts/import_scraped_listings.py`, `src/bgrealestate/models.py`, `src/bgrealestate/db/models.py`, `src/bgrealestate/db/repositories.py`, `sql/schema.sql`
- **Do**:
  1. Align `CanonicalListing` dataclass, `CanonicalListingModel`, SQL migrations/schema, and `CanonicalListingRepository.upsert` so all canonical fields can persist without SQLAlchemy compile/runtime drift.
  2. Add first-class or structured-extra persistence for `price_status`, `source_publication_type`, `scrape_status`, `scrape_acceptance_status`, `single_entity_candidate`, `listing_status`, remote/local photo counts, local image storage keys, and image report status.
  3. Make `scripts/import_scraped_listings.py --dry-run` work without importing DB-only dependencies, then block default import of `PENDING_QA`, missing-status, `LOST`, grouped/development, and inactive rows.
  4. Fix `listing_media` idempotency so repeated imports do not create duplicate media rows for the same listing URL/order.
  5. Resolve the all-Bulgaria bucket/segment conflict with Varna-only `source_section` FKs: either create an all-Bulgaria control-plane model or persist Action1 bucket evidence outside the Varna `source_section_id` FK.
  6. Separate persistence concepts instead of overloading `canonical_listing`: source publications, canonical properties, listing offers, QA reviews, status history, contacts, media assets, media descriptions, dedupe clusters, availability calendars/slots/observations, viewing/inquiry requests, and external chat references only.
  7. Model sale, long-term rent, short-term rent, commercial, and mixed-use offers as compatible but distinct offer flows; do not infer short-term availability from listing existence.
  8. Add import eligibility and blocked import reason fields; preserve price status, contact provenance, local media evidence, and source-publication type through import.
- **Backend prep note (2026-05-13)**:
  - FACT: default import must remain accepted-only: reject missing/`PENDING_QA`/`UNKNOWN`, `LOST`/`needs_rescrape`, grouped/development (`source_publication_type = multi_unit_or_development` or `scrape_acceptance_status = not_single_entity`), and inactive/removed/expired rows unless an explicit operator include flag is passed.
  - FACT: Action1 provenance is all-Bulgaria and bucket-based; it cannot safely populate the current Varna-only `source_section_id` FK. Preserve `geo_scope`, `bucket_key`/`segment_key`, source-section strings, QA state, price status, local media keys, and image-report state in `crawl_provenance`/structured metadata until a scope-neutral control-plane migration exists.
  - FACT: canonical property promotion must require `scrape_acceptance_status = accepted_single_entity_candidate`, `source_publication_type = single_unit_candidate`, not inactive, not rescrape-required, and one unit URL plus one numeric price or explicit `price_status in (on_request, undefined)`.
  - INTERPRETATION: the first implementation wave should make file-backed import compile and persist evidence without using the Varna FK; the second wave should add first-class QA/media columns or a `source_publication_provenance` table and DB smoke tests.
  - GAP: no PostgreSQL-backed fixture import, Alembic upgrade, or `make verify-db-counts` has run because a usable `DATABASE_URL` is not available in this environment.
- **Analyst safety note (2026-05-13)**:
  - FACT: `scripts/import_scraped_listings.py` now coerces numeric price `0` to `None` with `price_status=undefined` provenance unless source evidence already says `on_request`/`undefined`.
  - FACT: scraped-corpus DB import now blocks suspected multi-unit publications, defaults to source-publication-first persistence, and does not run property/entity unification unless `--promote-property-entities` is passed explicitly.
  - FACT: focused backend import contract tests cover zero-price conversion, unsafe QA blocking, provenance preservation, and listing-media deterministic IDs.
  - GAP: first-class DB tables for `qa_reviews`, generic `status_history`, `dedupe_clusters`, `media_descriptions`, `availability_*`, `viewing_or_inquiry_requests`, and `external_chat_refs` still need backend implementation and DB smoke tests.
  - 2026-05-13 sequential backend run: added `source_publication_qa_review`, `status_history`, `entity_resolution_candidate`, `entity_resolution_review_event`, `media_description`, `availability_calendar`, `availability_slot`, `availability_observation`, `viewing_inquiry_request`, and `external_chat_ref` to schema, migration, ORM models, import-evidence repository sync, tests, and `make bd18-db-smoke-import`. Smoke import is implemented but blocked until `DATABASE_URL` is supplied and migrations are applied.
- **Acceptance gate**: import dry-run prints accepted/skipped counts from the current corpus; a DB-backed fixture import persists QA/media/segment/source-publication evidence; `CanonicalListingRepository.upsert` accepts the full payload without SQLAlchemy compile/runtime drift; repeated import is idempotent for listing media; fixtures cover sale, long-term rent, short-term rent, grouped/development blocked import, numeric-zero price converted to null plus status, and stale/unknown availability; `make verify-db-counts` passes when `DATABASE_URL` is available; tests pass without live-network dependencies.
- **Output**: migration/schema/model/repository/importer updates, `scripts/bd18_db_smoke_import.py`, tests, backend_developer JOURNEY.
- **Verifier**: debugger + data_analyst
- **Depends on**: DA-01, BD-11

### BD-19: QA evidence read model for dashboard/API truth
- **Status**: `TODO`
- **Priority**: HIGH
- **Read first**: `BD-18`, `DA-02`, `DA-05`, `docs/exports/action1-dataset-quality-gate.json`, `docs/exports/properties-deep-analytics-agent-handoff-2026-05-13.md`, `src/bgrealestate/api/routers/admin.py`, `src/bgrealestate/db/repositories.py`, `lib/types/listing.ts`
- **Do**:
  1. After `BD-18` proves DB-backed import, expose accepted, LOST, grouped/development, inactive, missing-description, missing-price, media-gap, and image-report-status counts through an admin/API read model.
  2. Keep file-backed analyst artifacts as source-of-truth until DB counts are verified by `INFRA-02`.
  3. Return source/bucket-scoped counts; do not collapse bad/lost and grouped dimensions into one denominator.
  4. Add DB-backed equivalents for DA-05 metrics: source and regional candidate counts, sale/rent medians, area and price-per-sqm summaries, image/gallery metrics, description depth, and textual tendency flags. Keep sale/rent and file-backed/DB-backed labels explicit.
- **Acceptance gate**: seeded/fixture DB tests prove read-model counts match analyst fixture artifacts; API returns 503 cleanly without DB; no live-network dependency.
- **Output**: API/repository updates, tests, backend_developer JOURNEY.
- **Verifier**: debugger + data_analyst + ux_ui_designer
- **Depends on**: BD-18, DA-02

### BD-20: First-party product analytics event intake
- **Status**: `TODO`
- **Priority**: HIGH
- **Read first**: `docs/analytics/user-event-taxonomy.md`, `UA-02`, `src/bgrealestate/api/main.py`, `src/bgrealestate/api/routers/analytics.py`, `sql/schema.sql`, `src/bgrealestate/db/models.py`, `src/bgrealestate/db/repositories.py`
- **Do**:
  1. Add first-party event intake for allowlisted product events only; do not install external analytics or forward payloads to third parties.
  2. Persist a minimal event envelope with schema version, event name, route pattern, surface, pseudonymous session/user hashes, coarse device/viewport buckets, and validated payload JSON.
  3. Reject or drop unsafe fields including raw search text, raw chat text, emails, phones, names, source URLs, image URLs, IP addresses, raw user agents, tokens, and admin private notes.
  4. Add retention and deletion hooks that align with auth/profile data once `BD-13` is live.
  5. Expose fixture-safe summary queries for the dashboard contract in `UA-03`.
- **Acceptance gate**: API/unit tests prove known events are accepted, unknown fields are rejected/dropped, unsafe payload examples fail, no external network is used, and API returns clean 503/disabled behavior without DB.
- **Output**: migration/schema/model/router/repository updates, tests, backend_developer JOURNEY.
- **Verifier**: debugger + user_analytics_agent
- **Depends on**: UA-02, BD-13, BD-17, BD-19

### BD-21: Entity-resolution candidate schema/API and import safety
- **Status**: `TODO`
- **Priority**: HIGH
- **Read first**: ER-01 output, ER-02 output when available, `BD-18`, `BD-19`, `src/bgrealestate/services/unification.py`, `scripts/import_scraped_listings.py`, `sql/schema.sql`, `src/bgrealestate/db/models.py`, `src/bgrealestate/db/repositories.py`, `src/bgrealestate/api/routers/admin.py`
- **Do**:
  1. Add a reviewable entity-resolution candidate layer independent from `property_entity` and `property_offer` (candidate, evidence, and review event persistence).
  2. Ensure scraped accepted source-publication import can persist source publications without automatically creating/updating `property_entity` or `property_offer` links unless an explicit reviewed merge path is invoked.
  3. Expose admin-only read/review API for candidates; keep candidates out of public `/properties` and buyer-facing exports.
  4. Persist score component JSON, conflict reasons, accepted-only filter evidence, and immutable source-publication snapshot references.
  5. Add fixture DB tests for idempotent candidate generation and review events; no live network dependency.
- **Acceptance gate**: grouped/development, pending QA, missing-status, `LOST`, inactive, and unknown rows cannot enter candidate scoring or property promotion; repeated candidate generation is idempotent; admin APIs are auth-gated; public APIs do not expose candidates.
- **Output**: migration/schema/model/repository/API updates, tests, backend_developer JOURNEY.
- **Verifier**: debugger + entity_resolution_agent + data_analyst
- **Depends on**: ER-01, BD-18, BD-19, DA-02

---

## ═══════════════════════════════════════════════════════
## SCRAPER_1 (tier-1 and tier-2 marketplace connectors)
## ═══════════════════════════════════════════════════════

**Mission**: Build **efficient, legal, buyer-trustworthy** tier-1/2 ingestion: **full galleries**, honest **bucket_key** classification, **single-unit** promotion rules, and **per-source/bucket** metrics. Connectors must work end-to-end: discover URLs → fetch pages → parse → persist evidence → refresh dashboards — with **no silent “pattern missing” states** (patterns live in code + `data/source_registry.json` + exports).

**Detective index (2026-04-30)**: read `docs/exports/detective-product-orchestration-2026-04-30.md` for stack truth, API/UI alignment notes, and OpenClaw execution gates.

**Current operator mandate (2026-04-09):** Do **not** stop for end-of-session idle after `S1-15` code lands — keep executing harvest + ingest iterations until **`S1-18` volume gate** is satisfied (≥100 listings × ≥5 sources), except for real blockers (legal gate, site outage, CAPTCHA) documented in `JOURNEY.md`.

### S1-01: Homes.bg connector + fixtures
- **Status**: `VERIFIED`
- **Read first**: `src/bgrealestate/connectors/homes_bg.py`, `tests/fixtures/homes_bg/*`
- **Do**: connector interface + discovery/detail parser + fixtures + tests
- **Acceptance gate**: `make test` passes; no live network in tests
- **Output**: connector, fixtures, tests
- **Verifier**: debugger
- **Depends on**: —

### S1-02: OLX.bg API connector + JSON fixtures
- **Status**: `VERIFIED`
- **Read first**: `src/bgrealestate/connectors/olx_bg.py`, `tests/fixtures/olx_bg/*`
- **Do**: dedicated API parser for OLX JSON structure; 3 fixture cases
- **Acceptance gate**: `make test` passes; parser handles blocked/missing-price cases
- **Output**: connector, fixtures, tests
- **Verifier**: debugger
- **Depends on**: —

### S1-03 through S1-09: Remaining tier-1 HTML connectors
- **Status**: `VERIFIED`
- **Sources**: alo.bg, imot.bg, BulgarianProperties, Address.bg, SUPRIMMO, LUXIMMO, property.bg
- **Acceptance gate**: `make test` — 44 tests pass, 0 failures
- **Verifier**: debugger
- **Depends on**: —

### S1-10: imoti.net stub (legal-gated)
- **Status**: `VERIFIED`
- **Do**: fixture parsing only; live HTTP blocked by `legal_mode=legal_review_required`
- **Acceptance gate**: `TestImotiNetLegalGate` passes; live fetch raises `LegalGateError`
- **Verifier**: debugger (Bugbot priority: legal gates)
- **Depends on**: —

### S1-11: Live-safe ingestion runner (small)
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08; CLI + tests added, golden-path command executed in skip-mode without DATABASE_URL)
- **Read first**: `src/bgrealestate/connectors/ingest.py`, `src/bgrealestate/connectors/factory.py`
- **Do**: CLI command that ingests 1 fixture into DB using `ingest.py`
- **Acceptance gate**: stats endpoints reflect the inserted record; `make golden-path` still passes
- **Output**: CLI command + test
- **Verifier**: debugger + backend_developer (DB round-trip)
- **Depends on**: BD-01, S1-01

### S1-12: Tier-2 connector stubs (fixture-only)
- **Status**: `VERIFIED` (2026-04-30; added Domaza development-page classification fixture; refreshed tier-2 stub fixture suite)
- **Read first**: `data/source_registry.json` (tier-2 sources), `src/bgrealestate/connectors/scaffold.py`
- **Do**: stub connectors + 1 fixture each for Bazar.bg, Domaza, Yavlena, Home2U (highest-value tier-2)
- **Acceptance gate**: `make test` passes; legal gates enforced for `licensing_required` sources
- **Output**: connectors, fixtures, tests
- **Verifier**: debugger
- **Depends on**: S1-03 (tier-1 pattern established)

### S1-13: Stage-1 scraping completion check (all product types)
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08; coverage matrix + assertions added)
- **Read first**: `data/source_registry.json`, `tests/fixtures/`, `src/bgrealestate/models.py`
- **Do**: ensure stage-1 scraping for tier-1/2 covers property intents/types used by MVP (`sale`, `long_term_rent`, `short_term_rent`, `land`, `new_build`) with fixture + ingest coverage matrix
- **Acceptance gate**: matrix report exists and `make test` passes with product-type coverage assertions
- **Output**: `docs/exports/stage1-product-type-coverage.md`, coverage tests
- **Verifier**: debugger + backend_developer
- **Depends on**: S1-12

### S1-14: Discovery pagination for ALL tier-1 sources
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08; discovery parsers + fixtures + tests added for all tier-1 sources)
- **Priority**: **CRITICAL** — scrapers can't run without discovery
- **Read first**: `src/bgrealestate/connectors/homes_bg.py` (has `parse_discovery_html`), all other tier-1 connectors in `src/bgrealestate/connectors/`
- **Do**:
  1. Implement `parse_discovery_html()` / `parse_discovery_json()` for every tier-1 source that doesn't already have it:
     - OLX.bg: paginate API search results (page parameter in API URL)
     - alo.bg: HTML pagination with next-page link
     - imot.bg: HTML pagination
     - BulgarianProperties: HTML pagination
     - Address.bg: HTML pagination
     - SUPRIMMO: HTML pagination
     - LUXIMMO: HTML pagination
     - property.bg: HTML pagination
  2. Each discovery parser returns list of `{url, external_id, preview_price, preview_intent}` per page
  3. Add discovery fixtures: `tests/fixtures/<source>/discovery_page/raw.html` + `expected.json` for each source
  4. Test: discovery returns correct count, handles last page, handles empty results
- **Acceptance gate**: every tier-1 source has working discovery; `make test` passes; fixtures exist for each
- **Output**: updated connector files, discovery fixtures, tests
- **Verifier**: debugger
- **Depends on**: S1-01 through S1-10

### S1-15: Live HTTP integration for tier-1 connectors
- **Status**: `IN_PROGRESS` (2026-04-21; strict pattern repairs promoted `Address.bg`, `BulgarianProperties`, `LUXIMMO`, `OLX.bg`, `property.bg`, `SUPRIMMO`, `Bazar.bg`, and `Yavlena` to `Patterned` from saved item evidence; DB proof is still blocked because no PostgreSQL server is running locally and Docker daemon/compose are unavailable in this environment; `alo.bg`/`Domaza`/`Home2U` still remain low-yield or zero-sample)
- **Priority**: **CRITICAL** — must actually hit real websites to populate database; **feeds `S1-18` volume gate**
- **Read first**: `src/bgrealestate/connectors/scaffold.py`, `src/bgrealestate/connectors/legal.py`, `src/bgrealestate/connectors/protocol.py`
- **Do**:
  1. Implement `httpx`-based live fetch in `HtmlPortalConnector.fetch_url()` with:
     - User-Agent rotation (realistic browser UAs)
     - Rate limiting (configurable per source, default 1 req/2sec)
     - Retry with exponential backoff (3 retries)
     - Proxy support (optional, configured via env var `HTTP_PROXY`)
     - Response caching in `raw_capture` table (raw HTML stored in S3/local, metadata in DB)
     - Legal gate check before every request (`assert_live_http_allowed`)
  2. Implement live discovery + detail fetch flow:
     - `discover_listing_urls(source, page)` → returns URL list from live site
     - `fetch_listing_detail(url)` → returns raw HTML → parse → canonical listing
  3. Integration test (separate from unit tests): `tests/test_live_integration.py` — skipped by default, runs only with `ENABLE_LIVE_TESTS=1`
  4. **Tests must remain fixture-only by default** — live tests are opt-in only
- **Acceptance gate**: `make test` still passes (no live network); with `ENABLE_LIVE_TESTS=1`, fetches 1 page from each tier-1 source and parses successfully; legal gates block restricted sources
- **Output**: updated connector base class, live fetch implementation, integration tests
- **Verifier**: debugger (legal gate enforcement) + backend_developer (DB storage)
- **Depends on**: S1-14, BD-01

**Continuation checklist (operator pause 2026-04-08 — resume here)**  
Bulk live harvesting was started outside the formal S1-15 acceptance gate; do **not** assume it is complete.

1. **Stabilize `scripts/live_scraper.py`**: fix remaining discovery URLs (alo.bg, address.bg, property.bg, home2u, SUPRIMMO/LUXIMMO home-only patterns); prefer each site’s real listing URL regex after a one-page probe; cap `--max-listings` per run to avoid hour-long jobs.
2. **Normalize media URLs everywhere**: protocol-relative `//cdn...` must become `https:` before `download_image` (partially done in live scraper; align with `ingest` / listing API if URLs are stored raw).
3. **Homes.bg volume**: use `/api/offers` with validated `city` / `offerType` params; confirm pagination until empty `result`; merge with connector `HomesBgConnector` so one code path owns discovery.
4. **Wire harvest → DB**: either extend `ingest_listing_detail_html` + crawl job runner or a dedicated “bulk import JSON” path so `data/scraped/*/listings/*.json` round-trips to `canonical_listing` + `listing_media` (not only on disk).
5. **Regenerate exports**: after a successful harvest, run `make scraping-inventory` and extend `scripts/generate_scraping_inventory.py` to ingest **live** counts from `data/scraped/**/scrape_stats.json` + `scrape_summary.json` (separate columns from fixture stats).
6. **Agent report MD + DOCX + PDF**: add `docs/exports/scraper-1-tier12-status.md` and a small script (or Makefile target) to render DOCX/PDF from that markdown (reuse `reportlab` / `python-docx` patterns from inventory script).
7. **Opt-in live tests**: keep `make test` fixture-only; add `ENABLE_LIVE_TESTS=1` smoke that hits **one** URL per source (as in original S1-15 spec).
8. **Then**: mark `S1-15` `DONE_AWAITING_VERIFY` only when live fetch + parse + **persistence path** (via `BD-11`) works; immediately continue **`S1-18`** until volume gate met → then `S1-16` tier-2 expansion → `S1-17` Playwright for JS-heavy portals.

### S1-18: Tier-1/2 live volume gate (≥100 listings × ≥5 sources) — NON-STOP
- **Status**: `TODO`
- **Priority**: **CRITICAL** — primary success metric for the current execution wave
- **Read first**: `S1-15`, `BD-11`, `data/source_registry.json` (tier 1–2 rows), `docs/exports/stage1-product-type-coverage.md`
- **Do**:
  1. After live HTTP + ingest work (`S1-15` + `BD-11`), run **repeated** discovery → detail → persist cycles for tier-1 and tier-2 sources allowed by `legal_mode` / `access_mode`.
  2. **Stop condition:** at least **5** distinct `source_name` values (from the registry, tier 1 or 2) each have **≥100** rows in **`canonical_listing`** (count distinct `reference_id` or equivalent unique key per source). If Postgres is temporarily unavailable, document **interim** counts from an agreed export under `data/scraped/` in `docs/exports/tier12-live-volume-report.md` and still treat the gate as **not met** until DB counts match.
  3. **Non-stop rule:** do not mark this slice `DONE_AWAITING_VERIFY` until the numeric gate is hit or **`BLOCKED`** with a concrete reason (e.g. `LegalGateError`, sustained HTTP 403, missing partner contract). Rotate sources if one is blocked; prefer Homes.bg, OLX.bg, imot.bg, alo.bg, property.bg as the default “first five” unless the registry forbids live fetch.
  4. Update **`docs/exports/tier12-live-volume-report.md`** after each major run: timestamp, per-source counts, sample `reference_id`s, and command lines used.
- **Current analysis artifact (2026-04-20)**: `docs/dashboard/scrape-status.html` is the operator dashboard for per-source service/property coverage, field capture, image/text readiness, and next steps across all tier-1/2 sources.
- **Website inventory artifact (2026-04-20)**: `docs/exports/website-inventory-analysis.json` and `docs/exports/website-inventory-analysis.md` now persist website-side totals, category-level count evidence, count method, count gaps, and estimate conflicts for each tier-1/2 source; `scrape-status.html` renders those inside each website block and should be extended after every live counting pass.
- **Interim evidence (2026-04-09)**: `data/scraped/` already contains ≥100 parsed listings for **5** sources (`Bazar.bg`, `BulgarianProperties`, `imot.bg`, `OLX.bg`, `Yavlena`), and the continuation wave added live on-disk corpus for `Address.bg` (43), `LUXIMMO` (15), `property.bg` (15), and `SUPRIMMO` (12). The gate is still **not met** until those rows land in PostgreSQL `canonical_listing`.
- **Gemma/OpenClaw analysis note (2026-04-27)**: `docs/exports/gemma4-openclaw-run-analysis-2026-04-27.md` shows 1,549 file-backed tier-1/2 items, 18,707 remote photo references, 5,376 local photos, and no completed apartment image-description reports. Treat this as the handoff baseline for `S1-21` and the `S1-22A` / `S1-22B` / `S1-22C` action sequence.
- **Pattern audit note (2026-04-21)**:
  1. Current strict `Patterned` set from saved sample evidence is `Address.bg`, `BulgarianProperties`, `Homes.bg`, `imot.bg`, `LUXIMMO`, `OLX.bg`, `property.bg`, `SUPRIMMO`, `Bazar.bg`, `Yavlena`.
  2. Current remaining non-patterned tier-1/2 sources split into:
     - no saved sample proof yet: `alo.bg`, `ApartmentsBulgaria.com`, `Domaza`, `Holding Group Real Estate`, `Home2U`, `Indomio.bg`, `Lions Group`, `Pochivka.bg`, `realestates.bg`, `Realistimo`, `Rentica.bg`, `Svobodni-kvartiri.com`, `Unique Estates`, `Vila.bg`
     - legal/authorization review required: `imoti.net`, `Imoteka.bg`, `Imoti.info`
  3. DB persistence proof is currently blocked by environment runtime, not parser code: `psql` and Python DB deps are present, but `localhost:5432` is not running and Docker daemon/socket are unavailable here.
- **Follow-up planning note (2026-04-14)**:
  1. Use `docs/exports/tier12-source-analysis.md` and `docs/exports/tier12-source-analysis.xlsx` as the source-by-source runbook for the next tier-1/2 continuation wave.
  2. Recover the zero-yield or weak-yield set first: `alo.bg`, `Domaza`, `Home2U`, then deepen `Homes.bg` apartment coverage and re-run `imot.bg` media downloads.
  3. After that, promote remaining tier-2 implementation in this order: `Rentica.bg`, `Svobodni-kvartiri.com`, `Holding Group Real Estate`, `Unique Estates`, `Realistimo`.
  4. Apply the new local skills when relevant:
     - `agent-skills/browser-scrape-ops/SKILL.md`
     - `agent-skills/image-media-pipeline/SKILL.md`
     - `agent-skills/postgres-ops-psql/SKILL.md`
- **Research and setup note (2026-04-20)**:
  1. Use `docs/exports/scraping-tools-market-radar-2026-04-20.md` as the dated tool-market reference before expanding new complex-source strategies.
  2. Use `docs/exports/universal-agent-scrape-setup-2026-04-20.md` to keep Codex and Claude-agent runs on the same runtime, env-var, and escalation policy.
  3. Apply the newer local skills when a source becomes expensive or brittle:
     - `agent-skills/hybrid-scrape-stack/SKILL.md`
     - `agent-skills/managed-scrape-platforms/SKILL.md`
     - `agent-skills/universal-agent-scrape-setup/SKILL.md`
  4. For each property item, treat media completeness as part of completeness:
     - identify the whole gallery on the detail page where possible
     - download all reachable listing photos, not only the first image
     - record readability/decode success for the full set and note partial or broken galleries
  5. Use `docs/exports/tier12-source-metrics-deep-dive.md` and `docs/exports/tier12-source-metrics-deep-dive.xlsx` as the per-source metric baseline:
     - declared site offering
     - estimated site scale
     - confirmed landed corpus
     - intent/category splits
     - progress percentages
     - method and automation recommendations
  6. Use `docs/exports/all-tier-source-pattern-audit-2026-04-30.md` and `docs/exports/all-tier-source-pattern-audit-2026-04-30.xlsx` as the current cross-tier audit for unpatterned sources and for the non-Action1 patterned-source universality check.
  7. Use `data/scrape_patterns/pattern_candidates/all-tier-unpatterned-source-patterns.json` and `docs/exports/all-tier-unpatterned-source-patterns-2026-04-30.md` as the durable proposed-pattern registry for still-unpatterned tier-1/2 sources.
  8. Current non-Action1 patterned universality verdict:
     - `OLX.bg`: broad schema coverage, not yet universally proven
     - `Bazar.bg`: not universally proven across rent/commercial templates
     - `Yavlena`: not universally proven across all property/service templates
- **Acceptance gate**: report shows ≥5 sources × ≥100 listings in `canonical_listing`; `make test` still passes (fixture-only); rate limits and legal gates respected
- **Output**: `docs/exports/tier12-live-volume-report.md`, crawl/job logs as needed, JOURNEY entries per run batch
- **Verifier**: debugger
- **Depends on**: `S1-15`, `BD-11`

### S1-21: Codex tier-1/2 scrape quality audit + pattern repair prep
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-29; exports refreshed; bucket_key backfilled on saved JSON for per-bucket reporting)
- **Priority**: **CRITICAL** — next operator-requested tier-1/2 run before Gemma resumes
- **2026-04-30 strict sample-proof update**: `alo.bg`, `Domaza`, and `Home2U` now have saved legal detail samples bound to `tests/fixtures/strict_sample_proof/*.json`, raw HTML under `data/scraped/<source>/raw/`, listing JSON under `data/scraped/<source>/listings/`, and full local galleries under `data/media/<reference_id>/`. `Home2U` selected sample has no description text in the source detail block, so the parser persists `source_attributes.description_status = absent_on_detail_page` and dashboards keep that caveat visible.
- **2026-04-30 debugger repair update**: Action1 seven-source parser defects were repaired and saved raw HTML was reparsed offline. Fixed: Address.bg full-gallery URL extraction, BulgarianProperties full-description extraction, Homes.bg sqm decimal parsing, property-family unit-area preference, and conservative Bulgaria coordinate rejection. Current remaining media backfill dry-run gaps: Address.bg 31078, BulgarianProperties 5027, Homes.bg 396, imot.bg 2115, LUXIMMO 2, property.bg 0, SUPRIMMO 0. DB geospatial QA is blocked until PostgreSQL/Docker are available.
- **2026-05-01 debugger quarantine update**: `scripts/action1_dataset_quality_gate.py` marks wrongly scraped rows as `LOST` and development/multi-unit pages as `GROUPED_PUBLICATION`. Default frontend export and DB import now exclude `LOST` plus grouped publications unless explicitly overridden. Current Action1 file-backed QA: Address.bg 5203 LOST, BulgarianProperties 1612 LOST / 279 grouped, Homes.bg 67 LOST / 10 grouped, imot.bg 383 LOST / 603 grouped, LUXIMMO 430 LOST / 105 grouped, property.bg 0 LOST, SUPRIMMO 39 LOST / 42 grouped. Main remaining work is source-specific media backfill, active-URL rechecks, and development-page splitting only when unit-level evidence exists.
- **2026-05-04 debugger hardening update**: A1 pattern-depth review added route/bucket context hardening, immediate source-publication status, QA-eligible pattern proof, inactive-row import/export blocking, and `--limit-per-source` smoke QA for OpenClaw. See `docs/exports/a1-pattern-depth-reliability-review-2026-05-04.md`.
- **Read first**: `docs/exports/gemma4-openclaw-run-analysis-2026-04-27.md`, `docs/exports/source-item-photo-coverage.json`, `docs/exports/tier12-pattern-status.md`, `docs/dashboard/scrape-status.html`, `scripts/live_scraper.py`, `data/scraped/*/listings/*.json`
- **Do**:
  1. Audit every tier-1/2 source with saved rows for: item count, `photo_count_remote`, `photo_count_local`, `full_gallery_downloaded`, local file existence/decodability, description length, price, area, city, property type, rooms/floor/phones.
  2. Produce per-source and per-property failure tables: missing images, partial galleries, thin descriptions, missing price/area/city/type, suspicious one-photo galleries, and missing image-description reports.
  3. Improve source-specific parsing patterns in code, not only generated JSON. Current priority repairs after the 2026-04-30 debugger pass: `imot_bg` remaining price/area edge cases, `yavlena` zero-price/on-request handling, broader multi-unit/development flags for `imot_bg`, `yavlena`, `homes_bg`, `olx_bg`, and operator-approved media backfill for repaired `Address.bg`, `BulgarianProperties`, `Homes.bg`, `imot.bg`, and `LUXIMMO` galleries.
  4. Regenerate all affected listing JSON, photo coverage exports, pattern-status exports, `docs/dashboard/scrape-status.html`, and frontend scraped-listing seed data.
  5. Keep legal gates intact and keep tests fixture-only.
  6. Treat `Address.bg`, `BulgarianProperties`, `Homes.bg`, `imot.bg`, `LUXIMMO`, `property.bg`, and `SUPRIMMO` as the current priority four-bucket tier-1/2 pattern set. Each must keep explicit `buy_personal`, `buy_commercial`, `rent_personal`, and `rent_commercial` bucket instructions; where the website exposes a mixed route, accept rows only after card/detail category classification.
  7. **Same-location grouping contract (required)**: ensure the website “Aggregate” filter groups only when a **useful address** exists (address text is not just city/district). Group key must be \(city :: district :: useful_address\). This prevents the “dummy address” placeholder from collapsing whole districts into one group.
- **Acceptance gate**: parser regression tests pass; dashboards show source-by-source and item-by-item media/field completeness; every source gap is mapped to either fixed, legal/runtime blocked, or queued for Gemma image reporting.
- **Output**: updated parser code/tests, refreshed dashboards/exports, `docs/exports/s1-21-tier12-quality-audit-2026-04-29.md`, updated `docs/agents/scraper_1/JOURNEY.md`
- **Verifier**: debugger
- **Depends on**: S1-18 file-backed corpus evidence, S1-20 all-Bulgaria runner

### S1-22A: Gemma/OpenClaw Action0 — local-gallery property image reports
- **Status**: `TODO`
- **Priority**: **CRITICAL** — runs after Action1 when operator commands it
- **Read first**: `docs/exports/taskforgema.md`, `docs/exports/s1-21-gemma-action0-eligible.json`, `docs/exports/s1-21-tier12-quality-audit-2026-04-29.md`, `docs/exports/property-quality-and-building-contract.md`, `docs/exports/source-item-photo-coverage.json`, `data/scraped/*/listings/*.json`, `data/media/`
- **Do**:
  1. Process only rows in `docs/exports/s1-21-gemma-action0-eligible.json`.
  2. Work property item by property item; use all listed `local_image_files` in saved order.
  3. Generate one Markdown and one JSON report per property under `docs/exports/property-image-reports/<source_key>/`.
  4. Include one ordered description per image: scene type, style, layout clues, visible objects/equipment/tools, colors/materials, condition, defects/risks, usefulness, confidence, and uncertainty.
  5. Include one whole-property report: scraped title/description, source links, price/area/category/address, visual summary, planning evidence, requirements, photo-description match, price/size plausibility, identity flags, building-match status, and human-review gaps.
  6. Treat each row as a source publication first. Flag mixed/development/multi-unit pages as `suspected_multi_unit_publication` unless unit-level URL, price, area, and media evidence proves one unit.
  7. Do not run live scraping, do not analyze remote URLs unless explicitly marked as a gap, and do not invent unseen rooms, colors, tools, damage, floorplans, or equipment.
- **Acceptance gate**: every Action0 eligible row has a report or precise skip reason; every completed report references existing local files only; `docs/exports/property-image-reports/index.md` and `index.json` summarize source totals, reports, images, skips, warnings, and fields needing human review.
- **Output**: `docs/exports/property-image-reports/`, optional compatibility mirror to `docs/exports/apartment-image-reports/`, refreshed dashboards, updated `docs/agents/scraper_1/JOURNEY.md`
- **Verifier**: debugger
- **Depends on**: `S1-21` complete; operator **`Action0 now`** after Action1 completion (or explicit parallel waiver in `docs/agents/scraper_1/JOURNEY.md`). OpenClaw must still **load** Action0+1+2 contracts whenever Action1 is active, but must **not write** Action0 outputs before `Action0 now` unless waived.

**Operator / OpenClaw trigger (Telegram-safe)**:

- If you want Gemma4 to draft reports and post progress to Telegram, run this from your host shell:

```bash
openclaw --profile codex gateway probe
openclaw --profile codex channels status
ollama list | grep -i gemma4

openclaw --profile codex agent --agent main \
  --message "Execute S1-22A (Action0) exactly per docs/exports/taskforgema.md using docs/exports/s1-21-gemma-action0-eligible.json. Write outputs under docs/exports/property-image-reports/ and update index.md/index.json. Use ONLY local_image_files; no remote fetch. Post progress updates to Telegram chat 181488201." \
  --deliver --reply-channel telegram --reply-to 181488201 --timeout 3600 --json
```

Notes:
- The authoritative report contract is `docs/exports/taskforgema.md` (do not invent new fields).
- If Gemma4 times out, increase `models.providers.ollama.timeoutSeconds` in OpenClaw config and restart the gateway (see `docs/openclaw/README.md`).

### S1-22B: Gemma/OpenClaw Action1 — seven-source all-Bulgaria scrape/backfill
- **Status**: `IN_PROGRESS` (detached run; monitor `data/runs/action1_20260429_171309.log`)
- **Priority**: **CRITICAL** — **first live OpenClaw execution after operator `Action1 ACCEPT`**
- **Read first**: `docs/exports/taskforgema.md`, `docs/exports/tier12-four-bucket-pattern-handoff-2026-04-28.md`, `docs/exports/tier12-pattern-status.md`, `data/source_registry.json`, `data/scrape_patterns/regions/varna/sections.json`, `scripts/live_scraper.py`, `src/bgrealestate/scraping/`
- **Scope**: `Address.bg`, `BulgarianProperties`, `Homes.bg`, `imot.bg`, `LUXIMMO`, `property.bg`, `SUPRIMMO`
- **Buckets**: `buy_personal`, `buy_commercial`, `rent_personal`, `rent_commercial`
- **Do**:
  1. Run all-Bulgaria scrape/backfill only for the seven scoped sources and only through legal/source-registry gates.
  2. Resume from persisted file/log state, not chat. Use `data/runs/action1_scrape_uncapped_*`, `data/runs/scrape_metrics.jsonl`, and source listing JSON counts to determine the last useful progress point.
  3. For backlog completion, run with `SCRAPER_PAGE_ORDER=oldest_first` and the Action1 uncapped runner so the scraper scans older pages in the current window before newer pages, then widens by wave. This is the current reliable approximation of "oldest to newest" on portals that expose newest-first pagination; exact chronological cursors are source-specific follow-up work.
  4. For every source and bucket, use the saved route/pattern if present; if a portal exposes a mixed route, classify each row from card/detail text before saving it to a bucket.
  5. Save source URL, title, full description, combined text, structured attributes, price/currency or explicit price status, area, rooms, floor, type, service type, residential/commercial class, city/district/address, coordinates/geocoding evidence, all remote image URLs, all downloaded local image files, parse warnings, and local file validity.
  6. Preserve source-publication identity. Group duplicates/same-property publications conservatively by useful address plus city/district; city-only or district-only placeholders must not create aggregate groups.
  7. After each batch, run or queue the quality gate: `python3 scripts/action1_dataset_quality_gate.py --limit-per-source 20 --output docs/exports/action1-dataset-quality-gate-dryrun.json` for smoke, full run when practical. Rows marked `LOST`, grouped/development, or inactive do not count as accepted properties.
  8. Refresh source/item photo coverage, pattern-status exports, `docs/dashboard/scrape-status.html`, and website seed data after the run.
- **Acceptance gate**: all seven sources are attempted in all four buckets; each source/bucket has saved/skipped/error/parser-warning counts; every accepted row has photo counts, description coverage, source-link evidence, bucket evidence, and media status; `data_analyst` DA-01 and `debugger` DBG-08 have either verified or blocked the Action1 completion claim.
- **Output**: refreshed `data/scraped/`, `data/media/`, `docs/exports/source-item-photo-coverage.json`, `docs/dashboard/scrape-status.html`, source/bucket logs, updated `docs/agents/scraper_1/JOURNEY.md`
- **Verifier**: debugger
- **Depends on**: operator **`Action1 ACCEPT`** posted to Telegram (or echoed in the OpenClaw operator message). `S1-22A` is **not** a hard prerequisite anymore; Action0 is sequenced by operator `Action0 now` after Action1 unless waived in `JOURNEY.md`.

**Operator / OpenClaw trigger (Action1 now)**:

When the operator says **`Action1 ACCEPT`** (or legacy **`Action1 now`**), treat this as a **live scrape operator command**. Use the repo’s Make targets and publish progress to Telegram.

**Telegram cadence (required)**: after every **+100 net new** saved listing JSON rows across the seven Action1 sources, send one Telegram message with a **7 sources × 4 buckets** bullet or markdown table (counts + full-gallery % + avg description chars when available). Host shortcut: `make action1-matrix-snapshot`.

Dry-run first:

```bash
make scrape-all-full EXTRA_ARGS="--dry-run --parallel-sources 4 --target-per-source 100"
```

Then live run:

```bash
make scrape-all-full EXTRA_ARGS="--parallel-sources 4 --max-pages 8 --max-waves 3 --target-per-source 100 --refresh-dashboard"
make dashboard-doc
```

Telegram progress pings (operator):

```bash
openclaw --profile codex message send --channel telegram --target 181488201 --message "Action1: <your update>" --json
```

If you want OpenClaw+Gemma4 to *drive* the run (and narrate progress), use:

```bash
openclaw --profile codex agent --agent main \
  --message "Operator sent Action1 ACCEPT. Load docs/exports/taskforgema.md (full Action0+1+2 contract) but EXECUTE only S1-22B Action1: dry-run then detached live make scrape-all-full per docs/agents/TASKS.md. After every +100 net new saves, run: make action1-matrix-snapshot | send to Telegram 181488201 as 7x4 matrix + errors. Do NOT start Action0 file writes until operator sends Action0 now; do NOT start Action2 until Action2 now." \
  --deliver --reply-channel telegram --reply-to 181488201 --timeout 3600 --json
```

### S1-23: Scraper repair from DA-01 scrape database audit
- **Status**: `TODO` (2026-05-13 scraper-side source context prepared; no live scrape started)
- **Priority**: **CRITICAL**
- **Read first**: `docs/exports/scrape-database-quality-audit-2026-05-13.md`, `docs/exports/scrape-database-quality-audit-2026-05-13.json`, `docs/exports/data-quality-deep-review-2026-05-13.md`, `docs/exports/properties-deep-analytics-agent-handoff-2026-05-13.md`, `docs/dashboard/data-quality-dashboard.html`, `docs/dashboard/properties-database.html`, `scripts/action1_dataset_quality_gate.py`, `scripts/live_scraper.py`, `data/source_registry.json`, A1 listing JSON for the seven sources.
- **2026-05-14 planner lock**: this is the next execution slice after prompt-pack reconciliation. Start here before entity-resolution execution, DB/operator proof, Action0, or Action2.
- **Do**:
  1. Treat DA-01 findings as the current scraper issue list. Do not widen Action2 until Action1 QA repair is complete or explicitly waived.
  2. Re-run/apply quality gate after every continuation so accepted rows are not left as `PENDING_QA`.
  3. For `Address.bg`, repair missing city/address extraction, one-photo suspects, oversized area suspects, and noisy phones.
  4. For `BulgarianProperties`, fix local-gallery completeness and unit-area parsing; keep development pages grouped.
  5. For `Homes.bg`, expand beyond sale apartments, remove duplicate URL rows, confirm active status, and download all offer JSON gallery images.
  6. For `imot.bg`, preserve the strong accepted corpus but repair partial galleries, missing area, category precision, grouped pages, and thin/mojibake descriptions.
  7. For `LUXIMMO`, `property.bg`, and `SUPRIMMO`, deduplicate gallery size variants, fix missing/oversized area, classify development pages separately, and reduce thin descriptions/low sale-price warnings.
  8. Normalize phones using source-specific contact blocks only; reject dates, IDs, counters, and JS numeric fragments.
  9. Default import/export must exclude `PENDING_QA`, missing QA state, `LOST`, grouped/development, and inactive rows.
  10. Use this source-specific analyst-support map before coding:
      - `Address.bg`: parser gap = city/address + oversized area; media gap = one-photo suspects/high-resolution gallery evidence; grouped = none in current DA rollup; provenance = bucket/source URL/QA state must be applied; price-state = preserve missing/on-request as non-numeric.
      - `BulgarianProperties`: parser gap = unit-area semantics; media gap = large partial-local-gallery backlog; grouped = development pages stay grouped unless unit URL + price/status + area + media exist; provenance = preserve registry/source-domain evidence and bucket route; price-state = preserve on-request/undefined.
      - `Homes.bg`: parser gap = sale-apartment bias, duplicate detail URLs, active-state evidence; media gap = offer JSON/API gallery; grouped = keep mixed pages grouped; provenance = offer id, active marker, bucket route; price-state = explicit missing/on-request only.
      - `imot.bg`: parser gap = missing area, category precision, mojibake/thin descriptions; media gap = partial gallery; grouped = separate development pages from strong single-unit corpus; provenance = `adParams`, detail URL, active marker, route bucket; price-state = missing price becomes provenance, not zero.
      - `LUXIMMO` / `property.bg` / `SUPRIMMO`: parser gap = missing/oversized unit area and thin/low-price warnings; media gap = gallery size-variant de-duplication before local-vs-remote counts; grouped = development/project pages stay source publications; provenance = labeled unit fields + source-family route evidence; price-state = low or absent price requires status/review.
      - Non-A1 tier-1/2 (`alo.bg`, `Bazar.bg`, `Domaza`, `Home2U`, `OLX.bg`, `Yavlena`, and other legal public sources) remains Action2/A12 context only until Action1 QA and operator `Action2 now`; blocked/legal sources (`imoti.net`, `Imoteka.bg`, `Imoti.info`) stay excluded.
  11. Use `docs/exports/data-quality-deep-review-2026-05-13.md` source drilldowns for per-source bad-scrape examples and fixture selection; do not treat raw saved row counts as accepted property counts.
  12. Use DA-05 deep source analytics to prioritize source repairs: weak candidate rate, bad price-per-sqm/area sanity, thin/duplicated descriptions, one-photo/partial gallery rows, duplicate image URLs, and grouped/development textual signals.
- **Acceptance gate**: `python3 scripts/audit_scrape_database_quality.py` and `python3 scripts/action1_dataset_quality_gate.py --limit-per-source 20 --output docs/exports/action1-dataset-quality-gate-dryrun.json` run cleanly; the seven-source bucket matrix shows no unreviewed accepted imports; grouped/development counts use one documented definition; source-specific parser regressions cover each fixed pattern, including Address.bg city/address/contact/gallery, BulgarianProperties local-gallery/unit-area/development separation, Homes.bg duplicate URL/active-status/full-gallery handling, imot.bg area/category/mojibake/grouped handling, LUXIMMO/property.bg/SUPRIMMO gallery variant de-duplication and unit-area selection, zero-price-to-status handling, and source-specific contact extraction that rejects dates, IDs, counters, and JavaScript fragments.
- **Output**: parser/media/contact fixes, refreshed quality/dashboard exports, scraper_1 JOURNEY.
- **Verifier**: data_analyst + debugger
- **Depends on**: DA-01, S1-22B

### S1-24: Analyst-queued Action1 repair waves
- **Status**: `TODO`
- **Priority**: **CRITICAL**
- **Read first**: `S1-23`, latest `DA-02` / `DA-03` outputs, `docs/exports/action1-lost-rescrape-queue.json`, `docs/exports/action1-multi-unit-publications.json`, `scripts/live_scraper.py`, `tests/test_action1_parser_regressions.py`
- **2026-05-14 planner lock**: run only after `S1-23` repairs/tests identify bounded waves. Do not widen source scope or start Action2.
- **Do**:
  1. Execute bounded parser/media/contact repairs from data_analyst queues only; do not widen source scope to Action2.
  2. For each source/bucket wave, record before/after accepted, LOST, grouped, inactive, description, price, area, local-gallery, and phone-noise counts.
  3. Add fixture/regression coverage for each repaired source pattern before any live rerun.
  4. Refresh quality gates after each wave and hand off to data_analyst/debugger.
- **Acceptance gate**: bounded `action1_dataset_quality_gate` and scraper parser regressions pass; per-source/bucket delta report shows reduced unreviewed/bad states or a named blocker.
- **Output**: parser/media/contact fixes, refreshed quality exports, `docs/exports/action1-repair-wave-YYYY-MM-DD.md`, scraper_1 JOURNEY.
- **Verifier**: data_analyst + debugger
- **Depends on**: S1-23, DA-02

### S1-25: Wave 2 parser repair for clean titles, area, categories, and location evidence
- **Status**: `TODO` (Wave 2; wait for Wave 1 evidence)
- **Priority**: **CRITICAL**
- **Read first**: `DA-08` output, `UX-25` output, `S1-23`, `S1-24`, `scripts/live_scraper.py`, `tests/test_action1_parser_regressions.py`, `data/source_registry.json`, sample Action1 listing JSON for the seven sources.
- **Do**:
  1. Add or repair extraction for clean buyer-facing title, source listing ID, source title, area sqm, rooms, floor, source category, city, district, address, geocode text, and source-derived filter categories.
  2. Preserve source IDs and source labels in provenance fields, not public title fields.
  3. Add parser tests for `objava`/ID-noise title cleanup, decimal/comma area parsing, oversized/sub-2-sqm area rejection, grouped/development page detection, and city/district/address evidence.
  4. Do not widen beyond Action1 sources unless operator explicitly starts Action2.
  5. Keep price `0` as null plus price-status provenance.
- **Acceptance gate**: focused parser regression tests pass; quality-gate sample shows clean title and area evidence for repaired patterns; grouped/development rows stay non-public; no live-network dependency is added to tests.
- **Output**: parser/test patch, refreshed dry-run quality sample or repair report, scraper_1 JOURNEY entry.
- **Verifier**: data_analyst + debugger + ux_ui_designer
- **Depends on**: DA-08, UX-25, S1-23

### S1-26: Codex Spark active source-link freshness audit and bounded rescrape staging
- **Status**: `BLOCKED_LOW_DISK` and **SUPERSEDED BY `S1-27`** for the full-dataset cleanup/rescrape goal (2026-05-15; queue-only output, no live URL checks)
- **Priority**: **CRITICAL**
- **Model**: `5.3-codex-spark`
- **Read first**: `docs/exports/scraper-active-link-review-codex-spark-prompt-2026-05-15.md`, `docs/agents/communication/2026-05-15-triagent-active-link-er-debugger.md`, `DA-08` output, `UX-25` output, `S1-23`, `S1-25`, `docs/agents/roles/scraper_1.md`, `data/source_registry.json`, `scripts/live_scraper.py`, `tests/test_action1_parser_regressions.py`, sample Action1 listing JSON for the seven sources.
- **Do**:
  1. Build a resumable audit queue from existing saved Action1/A1 source-publication rows only: `Address.bg`, `BulgarianProperties`, `Homes.bg`, `imot.bg`, `LUXIMMO`, `property.bg`, and `SUPRIMMO`.
  2. Check only existing source/detail URLs on the original website to classify `active`, `inactive`, `unknown_blocked`, `active_changed`, and exact `duplicate_candidate` rows.
  3. Compare live page evidence against saved variables where available: source ID, URL, title, price/price-status, area, rooms, floor, category, city, district, address/geocode text, description, contact presence, remote image count, and grouped/development signals.
  4. For rows classified `active_changed` or visibly wrong, re-fetch only the same original detail URL into a staging export; do not overwrite corpus files or DB rows.
  5. Report image/media evidence as metadata: remote image count, existing local image count, local availability/readability if already present, duplicate URL/hash if already present, and missing image-description flag. Do not run semantic image reports unless operator sends `Action0 now`.
  6. Do not delete, merge, canonicalize, mutate DB rows, download media, crawl category pages, start Action0, start Action2, or add non-A1 sources.
  7. Stop before live checks if Mac free disk is `<= 50GB`; otherwise keep disk use minimal and write reports only.
- **Acceptance gate**: queue counts are reproducible; disk preflight is recorded; legal/access gates are enforced from `data/source_registry.json`; report separates FACT / INTERPRETATION / HYPOTHESIS / GAP; inactive and duplicate rows are candidate actions only; bounded rescrape staging is same-detail-URL only; no corpus deletion or DB mutation occurs; focused parser tests pass if code changes; `git diff --check` passes for changed docs/scripts.
- **Output**: `docs/exports/s1-26-active-link-audit-2026-05-15.md`, `.json`, queue CSV, `docs/exports/s1-26-rescrape-staging-2026-05-15.json`, scraper_1 JOURNEY entry, communication note, and debugger/data-analyst verifier handoff.
- **Verifier**: data_analyst + debugger
- **Depends on**: DA-08, UX-25

### S1-27: Full-dataset active-link audit, verified cleanup, and patterned background rescrape
- **Status**: `BLOCKED_LOW_DISK` (2026-05-15; preflight found 22GB free, below required `>50GB`; no live checks/rescrape started)
- **Priority**: **CRITICAL**
- **Model**: `5.3-codex-spark`
- **Read first**: `docs/exports/triagent-full-dataset-active-audit-clean-rescrape-prompts-2026-05-15.md`, `docs/agents/communication/2026-05-15-full-dataset-audit-clean-rescrape.md`, `S1-26` outputs, `DA-08` output, `UX-25` output, `S1-23`, `S1-25`, `docs/agents/roles/scraper_1.md`, `data/source_registry.json`, `scripts/live_scraper.py`, `tests/test_action1_parser_regressions.py`, saved listing JSON under `data/scraped/*/listings/`.
- **Do**:
  1. Treat `S1-26` as incomplete queue-only evidence: it did not live-check links because disk free space was below `50GB`.
  2. Build a full saved-corpus audit queue from every `data/scraped/*/listings/*.json` row, not only the public export.
  3. For each saved source-publication detail URL, check the original website and classify: `active_same_publication`, `active_changed`, `inactive_removed`, `wrong_property_reused_url`, `redirect_not_listing`, `grouped_development_not_unit`, `source_duplicate`, or `unknown_blocked`.
  4. Explain the gap between roughly 30k saved rows and roughly 1.6k public rows with row-level/source-level status counts.
  5. Produce a reversible cleanup manifest for inactive, wrong-property, non-property, grouped/development, and duplicate rows; do not physically delete or mutate DB/corpus before debugger PASS.
  6. Stage same-detail-URL rescrape output for active changed rows without overwriting corpus files or DB rows.
  7. After full audit coverage, cleanup manifest, debugger PASS, and free disk `>50GB`, run long-running background patterned rescrape with logs/PID/checkpoints/resume.
  8. Patterned legal rescrape source set: `Address.bg`, `alo.bg`, `Bazar.bg`, `BulgarianProperties`, `Domaza`, `Home2U`, `Homes.bg`, `imot.bg`, `LUXIMMO`, `property.bg`, `SUPRIMMO`, `Yavlena`; `OLX.bg` only through official API/approved route.
  9. Rescrape each source by category: buy residential, buy commercial, rent residential, rent commercial; save source-publication rows first; preserve price-status, grouped/development flags, media counts, and provenance.
  10. Do not start Action0 image descriptions, unsafe private/social sources, CAPTCHA bypass, mass account creation, KYC bypass, or live-network tests.
- **Acceptance gate**: whole saved corpus is accounted for; disk and source legal gates are recorded; no broad rescrape begins before audit/cleanup PASS; cleanup is reversible and reason-coded; inactive/wrong/duplicate rows are removed only from active/public candidate corpus after verification; patterned rescrape outputs per-source/per-category counts and blockers; parser tests pass if code changes; `git diff --check` passes for changed docs/scripts.
- **Output**: `docs/exports/s1-27-full-dataset-active-link-audit-2026-05-15.md`, `.json`, queue CSV, cleanup candidates JSON, same-detail rescrape staging JSON, patterned rescrape plan/status artifacts, scraper_1 JOURNEY entry, communication note, and debugger/data-analyst verifier handoff.
- **Verifier**: data_analyst + debugger
- **Depends on**: DA-08, UX-25, S1-26 queue artifacts for failure context; final rescrape depends on `DBG-32` audit/cleanup PASS and disk `>50GB`.

### S1-22C: Gemma/OpenClaw Action2 — remaining legal tier-1/2 expansion
- **Status**: `TODO`
- **Priority**: **HIGH** — run only after Action1 QA
- **Read first**: `docs/exports/taskforgema.md`, `data/source_registry.json`, `docs/exports/tier12-pattern-status.md`, `docs/exports/s1-21-tier12-quality-audit-2026-04-29.md`
- **Do**:
  1. Expand the Action1 process to remaining legal tier-1/2 sources in `data/source_registry.json`.
  2. Exclude sources with `legal_review_required`, `licensing_required`, private/social/messenger-only access, missing authorization, or blocked `access_mode` until a separate operator/legal approval exists.
  3. For each newly included source, create or repair reusable patterns before widening volume, then repeat full-gallery media capture and Action0-style image-report generation for complete local-gallery rows.
  4. Keep source-publication identity, duplicate grouping, price-status handling, area sanity checks, and dashboard refresh rules identical to Action1.
- **Acceptance gate**: every eligible remaining source is either attempted with logs and refreshed metrics or explicitly blocked with legal/runtime reason; debugger signs off before any public claim of completeness.
- **Output**: updated patterns, refreshed scrape/media exports, refreshed dashboards, updated `docs/agents/scraper_1/JOURNEY.md`
- **Verifier**: debugger
- **Depends on**: `S1-22B` debugger QA notes + operator **`Action2 now`**

**Operator / OpenClaw trigger (after QA)**:

Action2 is the same execution pattern as Action1, but the **allowed source set** is “remaining legal tier-1/2 in `data/source_registry.json`”.

Start by backfilling media gaps for older rows (dry-run optional):

```bash
make backfill-scraped-media EXTRA_ARGS="--source bulgarianproperties"
make backfill-scraped-media EXTRA_ARGS="--source imot_bg"
make backfill-scraped-media EXTRA_ARGS="--source property_bg"
make backfill-scraped-media EXTRA_ARGS="--source suprimmo"
make dashboard-doc
```

### S1-20: Stage 1 controlled production prep — Varna-only region-first control plane (no live crawl)
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-23; control-plane widened to all tier-1/2 sources, per-source/segment readiness matrix, threshold summary, queue status, manual control worker, pause/unpause command, and manual activation runbook; operator must still run migrations locally and decide when to enqueue)
- **Priority**: **HIGH** — prerequisite for passive background scraping and per-segment “100 valid listings” gates without auto-starting crawls
- **Read first**: `migrations/versions/20260423_0003_stage1_scrape_control_plane.py`, `docs/stage1-controlled-production-architecture.md`, `data/scrape_patterns/regions/varna/sections.json`, `src/bgrealestate/scraping/*`
- **Do**:
  1. Keep **only** `region_key = varna` in schema, manifests, and CHECK constraints; do not add other regions in implementation until an explicit schema/policy change.
  2. Persist layered patterns per **source → section → list_page → detail_page → media_gallery** in `source_section` + `source_section_pattern`; segment keys must include `buy_personal`, `buy_commercial`, `rent_personal`, `rent_commercial` where applicable.
  3. Wire operator commands: `make scrape-validate-manifest`, `make scrape-sync-sections-dry`, `make scrape-sync-sections` (needs `DATABASE_URL`), `make scrape-threshold-summary`, `make scrape-queue-status`, `make scrape-control-worker-once`, `make scrape-runner-unpause`, and `make scrape-runner-once` (enqueue only after manual unpause).
  4. Provide a manual control-worker path that can process queued `discover` and `threshold_check` tasks without auto-starting HTTP scraping; keep fetch/detail/media execution operator-controlled in this stage.
  5. **Do not** start live HTTP collection as part of this slice; Stage 2 activates “100 valid listings per Varna source/segment bucket” after operator approval.
- **Acceptance gate**: `make test` passes; `alembic upgrade head` applies `20260423_0003` on Postgres; manifest validates; architecture doc + operator checklist exist; `scrape_runner_state.global_pause` remains default **true** until operator clears it; queue status + control-worker preview commands stay read-only unless `--apply` is passed
- **Output**: migration, ORM models, `src/bgrealestate/scraping/`, manifest generator, threshold planner, queue status + control worker, Makefile/CLI targets, `docs/stage1-controlled-production-architecture.md`, `docs/exports/varna-controlled-crawl-matrix.{json,md}`, `agent-skills/stage1-scrape-control-plane/SKILL.md`
- **Verifier**: debugger + backend_developer
- **Depends on**: BD-01 (migrations baseline)

### S1-16: Remaining tier-2 connectors (full set)
- **Status**: `TODO`
- **Priority**: HIGH — more sources = more complete database (**start only after `S1-18` is `VERIFIED`** unless operator reprioritizes)
- **Read first**: `data/source_registry.json` (all tier-2 sources), `src/bgrealestate/connectors/tier2_stubs.py`
- **Do**: Implement fixture-backed connectors for remaining tier-2 sources:
  - Imoti.info, realestates.bg, Indomio.bg, Realistimo
  - Holding Group, Rentica, Svobodni-kvartiri
  - Pochivka (vacation focus), Vila (rural/villa focus)
  - ApartmentsBulgaria (English-market)
  - Unique Estates, Lions Group, Imoteka
  - Each: discovery + detail parsing + 2 fixtures (basic + edge case)
- **Acceptance gate**: `make test` passes; each source has working parser + fixtures; legal gates enforced where applicable
- **Output**: expanded tier-2 connectors, fixtures, tests
- **Verifier**: debugger
- **Depends on**: S1-12, S1-14, **S1-18**

### S1-17: Playwright connectors for headless-required sources
- **Status**: `TODO`
- **Priority**: MEDIUM — some sites require JS rendering
- **Read first**: `data/source_registry.json` (sources with `access_mode: "headless"`), `agent-skills/scraper-connector-builder/SKILL.md`
- **Do**: For sources that require browser rendering (imoti.net after legal review, any tier-2 with heavy JS):
  1. Create `src/bgrealestate/connectors/playwright_base.py` — base class using Playwright for JS-rendered pages
  2. Implement headless connector for specific sources
  3. Fixture capture: use Playwright to save rendered HTML as fixture files
  4. Test with saved fixtures (no live browser in CI)
- **Acceptance gate**: headless connector parses rendered HTML fixtures correctly; Playwright only runs in live mode; `make test` passes without Playwright installed
- **Output**: Playwright base connector, source-specific implementations, fixtures, tests
- **Verifier**: debugger
- **Depends on**: S1-15, **S1-18**

---

## ═══════════════════════════════════════════════════════
## SCRAPER_T3 (historical tier-3 lane — no new assignments)
## ═══════════════════════════════════════════════════════

**Mission status after 2026-05-05 reset**: retained for historical JOURNEY evidence only. New tier-3 work is owned by `scraper_sm` under the **S&M** mission. Do not add new `scraper_t3` slices; migrate open follow-ups to S&M.

**2026-04-09:** Do **not** expand **live** tier-3 work until **`S1-18`** is `VERIFIED` (or operator explicitly reprioritizes). Fixture slices awaiting **`DBG-06`** stay in queue behind the tier-1/2 volume wave.

### T3-01: Tier-3 ingestion policy and integration contracts
- **Status**: `VERIFIED` (2026-04-08; debugger policy + fixture contract review)
- **Read first**: `data/source_registry.json` (tier-3 sources), `AGENTS.md` (guardrails), `deep-research-report.md`
- **Do**: define what's allowed per source and the integration pattern for each
- **Acceptance gate**: policy doc reviewed by debugger; integration pattern defined per source; fixture format defined
- **Output**: `docs/agents/scraper_t3/tier3-ingestion-policy.md`, fixture templates under `tests/fixtures/`
- **Verifier**: debugger (legal gates + Bugbot priority)
- **Depends on**: —

### T3-02: AirDNA / Airbtics licensed data importer (fixture-first)
- **Status**: `DONE_AWAITING_VERIFY`
- **Read first**: T3-01 policy, `src/bgrealestate/connectors/protocol.py`, vendor API docs
- **Do**: connector that maps licensed STR analytics data → `canonical_listing` or dedicated STR analytics table; fixture-backed tests with sample JSON
- **Acceptance gate**: `make test` passes; no live vendor API calls in tests; fixture contains realistic STR metrics
- **Output**: connector, fixtures, tests, STR data model helpers
- **Verifier**: debugger + backend_developer (DB round-trip)
- **Depends on**: T3-01, BD-01

### T3-03: BCPEA property auctions connector (fixture-first)
- **Status**: `DONE_AWAITING_VERIFY`
- **Read first**: T3-01 policy, `data/source_registry.json` (BCPEA entry), `src/bgrealestate/connectors/scaffold.py`
- **Do**: HTML connector for BCPEA forced-sale auction listings; parse starting price, area, address, court, bailiff, dates; fixture-backed
- **Acceptance gate**: `make test` passes; no live network in tests; legal gates enforced
- **Output**: connector, fixtures, tests
- **Verifier**: debugger
- **Depends on**: T3-01

### T3-04: Partner feed stub connectors (Airbnb/Booking.com/Vrbo)
- **Status**: `DONE_AWAITING_VERIFY`
- **Read first**: T3-01 policy, partner API documentation (when available)
- **Do**: stub connector classes with fixture parsing for partner feed JSON format; actual API integration blocked until partner contracts are signed
- **Acceptance gate**: `make test` passes; connector raises `PartnerContractRequired` on live calls; fixtures demonstrate expected feed structure
- **Output**: stub connectors, fixtures, tests
- **Verifier**: debugger (legal gate enforcement)
- **Depends on**: T3-01

### T3-05: Official register query wrappers (Property Register / KAIS Cadastre)
- **Status**: `DONE_AWAITING_VERIFY`
- **Read first**: T3-01 policy, official e-service documentation
- **Do**: query wrappers for official e-services; manual/consent mode only; fixture-backed for parser tests; live queries require explicit operator authorization
- **Acceptance gate**: `make test` passes; no automated queries without operator consent; fixtures contain redacted sample responses
- **Output**: query wrappers, fixtures, tests, consent enforcement
- **Verifier**: debugger + backend_developer
- **Depends on**: T3-01, BD-01

### T3-06: Varna-focused enrichment handoff (post stage-1 gate)
- **Status**: `BLOCKED` (2026-04-08: dependency gates not yet verified)
- **Read first**: DBG-05 verification output, T3-02..T3-05 outputs
- **Do**: define tier-3 enrichment payloads prioritized for Varna region market depth (STR/vendor/official overlays) without unauthorized scraping
- **Acceptance gate**: enrichment handoff spec consumed by backend + UX tasks
- **Output**: `docs/agents/scraper_t3/varna-enrichment-handoff.md`
- **Verifier**: debugger + backend_developer
- **Depends on**: DBG-05, T3-02, T3-05
- **Blocker**: `DBG-05` remains `TODO`, and `T3-02`/`T3-05` are still `DONE_AWAITING_VERIFY` (not `VERIFIED`), so slice cannot start under dependency rules.
- **Mapped follow-up slices**: `DBG-06` (verify T3-02/T3-03/T3-04/T3-05) and `DBG-05` (stage-1 quality gate).

### T3-07: BCPEA live scraper (public auctions are legal to crawl)
- **Status**: `DONE_AWAITING_VERIFY`
- **Priority**: HIGH — BCPEA is public data and can be crawled immediately
- **Read first**: T3-03 output, `src/bgrealestate/connectors/tier3.py`
- **Do**: implement live HTTP fetch for BCPEA auction listings (public_crawl_with_review legal mode); discovery pagination + detail parsing + storage; respect rate limits
- **Acceptance gate**: live scraper fetches real auction listings; stores in DB; `make test` still passes (fixture-only)
- **Output**: live BCPEA connector (`src/bgrealestate/connectors/tier3.py`), CLI command (`scrape-bcpea`), Makefile targets, realistic fixtures, 7 new tests (156 total pass)
- **Verifier**: debugger
- **Depends on**: T3-03, BD-15
- **Completion notes (2026-04-08)**: Parsed real BCPEA HTML structure from sales.bcpea.org; discovery pagination (`?perpage=36&p=N`), detail parsing (property type, area, price, court, bailiff, dates, photos, descriptions, scanned documents), rate limiting (1.5s default). Successfully scraped 180 real auction listings with full detail. CLI: `make scrape-bcpea`.

### T3-08: STR analytics API integration (AirDNA/Airbtics — when licensed)
- **Status**: `TODO`
- **Priority**: MEDIUM — requires license subscription first
- **Read first**: T3-02 output, vendor API documentation
- **Do**: implement actual API client for AirDNA and/or Airbtics; pull Varna STR metrics (occupancy, revenue, ADR by property type/area); store in dedicated analytics table; expose via `GET /analytics/str-metrics`
- **Acceptance gate**: with valid API key, fetches real STR data; without key, returns mock/fixture data; `make test` passes
- **Output**: API client, analytics table migration, API endpoint, tests
- **Verifier**: debugger + backend_developer
- **Depends on**: T3-02, BD-14

---

## ═══════════════════════════════════════════════════════
## SCRAPER_SM / S&M (tier-3 + tier-4 intelligence overlays)
## ═══════════════════════════════════════════════════════

**Mission**: Operate as **S&M**: scraper + monitor for intelligence overlays. Own tier-3 vendor/partner/official routes and tier-4 social/messenger overlays. All outputs are source publications, CRM leads, analytics overlays, or review candidates first — not primary marketplace listings unless legal gates, consent gates, and single-property evidence pass.

**2026-05-05 reset:** S&M does not execute Action1 A1 marketplace scraping. S&M may monitor OpenClaw/reporting state and prepare tier-3/tier-4 fixture-first work, but live tier-3/tier-4 expansion remains blocked unless operator/legal approval exists and Action1 priority is not impacted.

### SM-00: S&M mission consolidation and OpenClaw monitor handoff
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-05)
- **Priority**: **CRITICAL**
- **Read first**: `docs/agents/TASKS.md`, `docs/agents/scraper_t3/JOURNEY.md`, `docs/agents/scraper_sm/JOURNEY.md`, `docs/openclaw/ACTION1_AGENT_BOOTSTRAP.md`, `docs/openclaw/OPENCLAW_S_AND_M_AGENT.md`
- **Do**:
  1. Treat tier-3 partner/vendor/official and tier-4 social/messenger work as one S&M intelligence lane.
  2. Keep all private/social/messenger scraping consent-gated; no private groups, DMs, unofficial sessions, or KYC/CAPTCHA bypass.
  3. While Action1 runs, S&M may monitor reports and prepare QA/rescrape prompts, but must not widen Action1 source scope.
  4. After Action1 QA, S&M supports Action0 media-quality reports and Action2 legal tier-1/2 expansion only as monitor/analyst support, not by overriding `scraper_1`.
- **Acceptance gate**: S&M instructions are explicit, tier-3 historical work is not lost, and OpenClaw can distinguish A1 marketplace scraping from S&M intelligence overlays.
- **Output**: updated TASKS, S&M JOURNEY, OpenClaw S&M instruction doc.
- **Verifier**: debugger
- **Depends on**: PLAN-01

### SM-01: Social ingestion contract (policy + fixtures)
- **Status**: `VERIFIED` (2026-04-08; debugger consent + fixture review)
- **Read first**: `data/source_registry.json` (tier-4 sources), `AGENTS.md` (guardrails), `sql/schema.sql` (CRM tables)
- **Do**: define what's allowed per platform
- **Acceptance gate**: policy doc reviewed by debugger; consent checklist complete; fixture format defined
- **Output**: `docs/agents/scraper_sm/social-ingestion-policy.md`, fixture templates, detailed contract
- **Verifier**: debugger (consent checklist + Bugbot priority: legal gates)
- **Depends on**: —

### SM-02: Telegram public channel connector (fixture-first)
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08: acceptance gate passed)
- **Read first**: SM-01 policy, `src/bgrealestate/connectors/protocol.py`, CRM tables
- **Do**: connector that maps Telegram channel messages → `lead_message` + `lead_thread`; NLP extraction
- **Acceptance gate**: `make test` passes; fixtures contain redacted posts; no live Telegram calls
- **Output**: `src/bgrealestate/connectors/telegram_public.py`, tests, NLP extraction
- **Verifier**: debugger + backend_developer
- **Depends on**: SM-01, BD-01

### SM-03: X (Twitter) public monitor connector (fixture-first)
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08: acceptance gate passed)
- **Read first**: SM-01 policy, `data/source_registry.json` (X entry)
- **Do**: connector for X API JSON → lead extraction; fixture-backed
- **Acceptance gate**: `make test` passes; no live API calls
- **Output**: `src/bgrealestate/connectors/x_public.py`, tests, fixtures
- **Verifier**: debugger
- **Depends on**: SM-01

### SM-04: Social lead-to-property mapping for AI chat context
- **Status**: `TODO`
- **Read first**: SM-01 policy, `src/bgrealestate/connectors/social_parser.py`, chat/API contracts
- **Do**: provide social lead mapping format so chat can show related properties and map-filter suggestions from social signals
- **Acceptance gate**: fixture-backed mapping examples pass tests; no live social calls
- **Output**: mapping schema + fixtures + parser update tasks
- **Verifier**: debugger + ux_ui_designer
- **Depends on**: SM-02, UX-05

### SM-05: Social collection options research (decision matrix)
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08)
- **Read first**: `docs/agents/scraper_sm/social-ingestion-policy.md`, `data/source_registry.json` (tier-4)
- **Do**: research reliable options for Telegram/X/Facebook/Instagram/Viber/WhatsApp collection; document pros/cons/pricing/legality per platform; present decision matrix for operator
- **Acceptance gate**: decision matrix doc exists with all platforms covered; no code written
- **Output**: `docs/agents/scraper_sm/social-collection-options.md`
- **Verifier**: lead agent
- **Depends on**: SM-01
- **Verification evidence**: decision matrix added with all 7 tier-4 channels, cost bands, legality path, and rollout recommendation.

### SM-06: Telegram live connector (Telegram Bot API or MTProto)
- **Status**: `TODO`
- **Priority**: HIGH — Telegram is the most active social channel for BG real estate
- **Read first**: SM-02 output, SM-05 decision matrix, `src/bgrealestate/connectors/telegram_public.py`
- **Do**:
  1. Implement live Telegram public channel monitoring using official Bot API (or Telethon for MTProto if approved)
  2. Subscribe to 5-10 known Bulgarian real estate Telegram channels (public only)
  3. Parse new messages → extract real estate leads → store as `lead_thread` + `lead_message`
  4. NLP extraction: intent (sell/rent/buy), property type, price, area, city, phone (redacted)
  5. Run as background worker alongside scraper runner
  6. **No private channels, no private messages, no user DMs**
- **Acceptance gate**: live connector receives messages from public channels; leads appear in CRM; `make test` still passes (fixture-only)
- **Output**: live Telegram connector, channel list config, worker integration, tests
- **Verifier**: debugger (consent + legal gate) + backend_developer
- **Depends on**: SM-02, SM-05, BD-14

### SM-07: Facebook public group scraper (consent-gated)
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08: implementation deferred by legal decision)
- **Priority**: MEDIUM — Facebook groups are very active but heavily restricted
- **Read first**: SM-01 policy, SM-05 decision matrix
- **Do**: research and implement if legal: monitor public Facebook real estate groups via Graph API (official) or RSS; only public posts; consent-gated; redaction enforced
- **Acceptance gate**: if implemented, fixture-backed tests pass; no private data accessed; legal review documented
- **Output**: decision doc `docs/agents/scraper_sm/facebook-public-groups-decision.md` (manual/consent path, autonomous scrape deferred)
- **Verifier**: debugger (legal gate)
- **Depends on**: SM-05

### SM-08: Messenger publication candidates for Telegram, WhatsApp, and Viber
- **Status**: `TODO`
- **Priority**: HIGH — requested source deepening, but must stay consent/API/manual only
- **Read first**: `docs/agents/scraper_sm/messenger-publication-entity-plan-2026-04-29.md`, `src/bgrealestate/connectors/social_parser.py`, `src/bgrealestate/connectors/telegram_public.py`, `data/source_registry.json`
- **Do**:
  1. Implement fixture-first candidate mapper for Telegram public-channel messages, WhatsApp manual/Cloud API webhook payloads, and Viber manual/bot webhook payloads.
  2. Redact phone/email/name/private profile fields before persistence.
  3. Classify each message as `lead_only`, `candidate_single_unit`, `suspected_multi_unit`, or `noise`.
  4. Preserve `consent_status`, `redaction_applied`, channel/message IDs, media traceability, and promotion blockers.
  5. Do not run live WhatsApp/Viber/private-channel scraping; no private groups, no user DMs, no unofficial session scraping.
- **Acceptance gate**: fixture-backed tests prove candidate extraction, redaction, and promotion blocking; no live network dependency in tests; debugger verifies legal gates.
- **Output**: candidate schema/mapper, Telegram/WhatsApp/Viber fixtures, tests, refreshed tier-4 exports.
- **Verifier**: debugger + backend_developer
- **Depends on**: SM-01, SM-02, SM-05

### SM-09: Approved messenger candidate persistence into source-publication pipeline
- **Status**: `TODO`
- **Priority**: MEDIUM — start only after SM-08 review schema is verified
- **Read first**: SM-08 outputs, `src/bgrealestate/connectors/ingest.py`, `src/bgrealestate/services/unification.py`, BD-17
- **Do**: persist approved messenger candidates as source publications first; promote to `property_entity` only when single-unit evidence gate passes; otherwise keep CRM lead/thread evidence.
- **Acceptance gate**: approved fixture candidate creates source publication + review status; unapproved/noise/private messages do not create property entities; `make test` passes.
- **Output**: persistence adapter, tests, admin review notes.
- **Verifier**: debugger
- **Depends on**: SM-08, BD-11, BD-17

### SM-10: Tier-3/tier-4 intelligence path matrix
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-13)
- **Priority**: HIGH — prepares safe evidence paths while data analyst work continues
- **Read first**: `docs/agents/TASKS.md`, `docs/agents/roles/scraper_sm.md`, `data/source_registry.json`, `docs/agents/scraper_sm/social-ingestion-policy.md`, `docs/agents/scraper_sm/social-collection-options.md`
- **Do**:
  1. Define only legal, consent, partner, official API, licensed, or manual routes for tier-3/tier-4 intelligence.
  2. Record legal/consent blockers for Airbnb, Booking.com, Vrbo, Flat Manager, Menada, AirDNA, Airbtics, BCPEA, KAIS, Property Register, Telegram, X, Facebook, Instagram, Threads, Viber, and WhatsApp.
  3. Keep S&M evidence separate from canonical listings: source publications, CRM leads, review candidates, or analytics overlays only.
  4. Produce follow-up slices that can complement data analyst findings without widening Action1 or scraping private/social/messenger channels.
- **Acceptance gate**: path matrix exists; no unsafe scraping route is proposed; blocker language matches `source_registry` legal/access modes; follow-up tasks are explicit.
- **Output**: `docs/agents/scraper_sm/tier3-tier4-intelligence-paths-2026-05-13.md`, S&M JOURNEY entry, TASKS follow-ups.
- **Verifier**: debugger + data_analyst
- **Depends on**: PLAN-03

### SM-11: Official/register evidence queue
- **Status**: `TODO`
- **Priority**: HIGH — official evidence can complement accepted marketplace rows without private/social scraping
- **Read first**: `docs/agents/scraper_sm/tier3-tier4-intelligence-paths-2026-05-13.md`, `data/source_registry.json` entries for BCPEA/KAIS/Property Register, `docs/exports/scrape-database-quality-audit-2026-05-13.md`, latest data analyst reports
- **Do**:
  1. Define fixture schemas and review states for BCPEA auction source publications.
  2. Define manual/consent-only evidence envelopes for KAIS parcel/building checks and Property Register ownership checks.
  3. Specify comparison fields for data analyst: source URL/reference, geography, address fragments, area, price/opening bid, document dates, confidence, and review blocker.
  4. Block autonomous KAIS/Property Register querying; require operator/manual consent and permitted export evidence.
  5. Keep all official evidence outside canonical listings until single-unit evidence and review gates pass.
- **Acceptance gate**: queue spec separates auction/public-crawl evidence from consent/manual register checks; no official-service automation bypass is proposed.
- **Output**: official/register evidence queue spec, fixture templates if needed, S&M JOURNEY entry.
- **Verifier**: debugger + data_analyst
- **Depends on**: SM-10

### SM-12: Vendor/partner intelligence readiness
- **Status**: `TODO`
- **Priority**: HIGH — STR and partner evidence can explain supply/price gaps after data analyst baseline
- **Read first**: `docs/agents/scraper_sm/tier3-tier4-intelligence-paths-2026-05-13.md`, `data/source_registry.json` tier-3 vendor/partner entries, T3-02/T3-04 historical outputs, latest data analyst reports
- **Do**:
  1. Define fixture contracts for AirDNA/Airbtics licensed STR metric snapshots; do not model them as listings.
  2. Define partner-feed readiness checklists for Airbnb, Booking.com, Vrbo, Flat Manager, and Menada.
  3. Keep live API/feed calls hard-blocked without license, partner contract, API docs, credentials, and debugger approval.
  4. Map outputs to analytics overlays, channel capability evidence, partner inventory candidates, or publishing eligibility evidence.
  5. Identify which fields can later help data analyst compare marketplace inventory against STR/vendor supply signals.
- **Acceptance gate**: every vendor/partner route has an allowed path, blocker list, output class, and fixture-first test expectation; no crawl-first OTA route is proposed.
- **Output**: vendor/partner readiness spec, fixture TODOs, S&M JOURNEY entry.
- **Verifier**: debugger + data_analyst
- **Depends on**: SM-10

### SM-13: Social-overlay evidence queue and data analyst handoff
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-13)
- **Priority**: MEDIUM — use public/consented social signals as lead evidence only
- **Read first**: `docs/agents/scraper_sm/tier3-tier4-intelligence-paths-2026-05-13.md`, `docs/agents/scraper_sm/social-ingestion-policy.md`, `docs/agents/scraper_sm/social-collection-options.md`, SM-02/SM-03 outputs, latest data analyst reports
- **Do**:
  1. Define review queue states for Telegram/X official API signals and Facebook/Instagram/Threads manual-consent signals.
  2. Define consented/manual or official business/bot webhook envelopes for Viber and WhatsApp; block private groups, DMs, unofficial sessions, and mass account workflows.
  3. Define redaction, provenance, channel/message IDs, extracted intent, location hints, price hints, and confidence fields.
  4. Define handoff metrics for data analyst: lead-only, candidate-single-unit, suspected-multi-unit, noise, missing-price, redaction failure, and promotion-blocked counts.
  5. Keep social evidence out of canonical listings until SM-09-style persistence and review gates are verified.
- **Acceptance gate**: queue spec proves S&M signals remain separate from marketplace completeness; no unsafe social or messenger scraping path is introduced.
- **Output**: `docs/agents/scraper_sm/social-overlay-evidence-queue-2026-05-13.md`, `docs/agents/scraper_sm/social-media-source-discovery-2026-05-13.md`, `data/social_media_intelligence_candidates.json`, S&M JOURNEY entry.
- **Verifier**: debugger + data_analyst
- **Depends on**: SM-10, SM-02, SM-03

### SM-14: Telegram public candidate validation and fixture expansion
- **Status**: `TODO`
- **Priority**: HIGH — highest-confidence automated social overlay path
- **Read first**: `data/social_media_intelligence_candidates.json`, `docs/agents/scraper_sm/social-overlay-evidence-queue-2026-05-13.md`, `src/bgrealestate/connectors/telegram_public.py`, `tests/test_telegram_public_connector.py`
- **Do**:
  1. Validate public status, channel type, activity, and duplicate risk for the top Telegram candidates.
  2. Add redacted fixtures for at least four high-priority candidates: `rentvarna`, `varnarents`, `kvartirivarna`, and `addressbg`, if public/allowed samples are available.
  3. Extend classifier fixtures for source-link candidates, lead-only messages, suspected multi-unit messages, and noise.
  4. Do not run a live worker or store live data until token/session, rate limits, redaction, and debugger approval exist.
- **Acceptance gate**: fixture tests pass offline; every candidate has route/status; no live Telegram dependency in tests.
- **Output**: Telegram candidate validation notes, fixtures, parser tests, S&M JOURNEY entry.
- **Verifier**: debugger + data_analyst
- **Depends on**: SM-13

### SM-15: Meta Facebook/Instagram manual/API route pilot
- **Status**: `TODO`
- **Priority**: MEDIUM — high signal but high compliance friction
- **Read first**: `data/social_media_intelligence_candidates.json`, `docs/agents/scraper_sm/social-media-source-discovery-2026-05-13.md`, Meta/Instagram API docs, SM-13 queue spec
- **Do**:
  1. Split Facebook Groups, Facebook Pages, and Instagram profiles into route-specific queues.
  2. Define manual operator capture templates for groups.
  3. Define Graph API/Page and Instagram Business Discovery approval checklist for pages/professional profiles.
  4. Add redacted manual fixtures only; no login-gated scraping or unofficial profile scraping.
- **Acceptance gate**: manual/API route spec exists; fixture examples are redacted; unsafe scraping remains blocked.
- **Output**: Meta route pilot spec, fixture templates, S&M JOURNEY entry.
- **Verifier**: debugger + data_analyst
- **Depends on**: SM-13

### SM-16: WhatsApp/Viber opt-in business intake design
- **Status**: `TODO`
- **Priority**: MEDIUM — useful as inbound CRM, not source scraping
- **Read first**: `data/social_media_intelligence_candidates.json`, `docs/agents/scraper_sm/social-media-source-discovery-2026-05-13.md`, Viber Bot API docs, WhatsApp Business Platform docs, SM-13 queue spec
- **Do**:
  1. Define Viber commercial bot/manual opt-in evidence envelope.
  2. Define WhatsApp Business webhook evidence envelope for owner/agent opt-in conversations.
  3. Define consent proof, unsubscribe/delete handling, redaction, and retention requirements.
  4. Block arbitrary community/group/DM scraping.
- **Acceptance gate**: opt-in intake spec exists; no group scraping route is proposed; debugger verifies consent and redaction.
- **Output**: WhatsApp/Viber intake spec, fixture templates, S&M JOURNEY entry.
- **Verifier**: debugger + backend_developer + data_analyst
- **Depends on**: SM-13

---

## ═══════════════════════════════════════════════════════
## UX_UI_DESIGNER (frontend)
## ═══════════════════════════════════════════════════════

**Mission**: Build the buyer-trust **LUN.ua-style** marketplace UI: map-driven, mobile-responsive, honest loading states, **liquid-glass** polish (motion + glass surfaces without hiding data gaps), and AI chat — always aligned to real API field names (`lib/types/listing.ts`) and the `/api/backend/*` proxy when DB mode is on.

**Detective index (2026-04-30)**: `docs/exports/detective-product-orchestration-2026-04-30.md` (UI↔API notes).

**2026-04-09:** Do **not** start **new** large UX slices (`UX-04`+) until **`S1-18`** is `VERIFIED`; finish **`DBG-06`** promotion for UX-02/03/06 when debugger runs the batch pass.

### UX-01: Operator dashboard UI plan
- **Status**: `VERIFIED` (2026-04-08; debugger contract check)
- **Read first**: `PLAN.md` §8, `src/bgrealestate/api/routers/`, BD-02 API outputs
- **Do**: define `/admin` UX layout and data model
- **Acceptance gate**: markdown spec + component breakdown reviewed by debugger
- **Output**: `docs/agents/ux_ui_designer/admin-ui-spec.md`
- **Verifier**: debugger
- **Depends on**: BD-02

### UX-02: Beta main page — map + listings + category picker
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08)
- **Read first**: `PLAN.md` §8, `src/bgrealestate/api/routers/listings.py`
- **Do**: Build split-view main page with MapLibre map (left) + scrollable listing feed (right) + intent toggle + category picker + search + source badges
- **Acceptance gate**: page loads with mock/seeded data; category/intent filters work; map renders with pins; responsive mobile stacking
- **Output**: `app/(main)/page.tsx`, `components/listings/*`, `components/map/*`, `lib/types/listing.ts`, `lib/mock/listings.ts`
- **Verifier**: debugger
- **Depends on**: UX-01

### UX-03: Wire listings feed to live `/listings` API
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08)
- **Read first**: `src/bgrealestate/api/routers/listings.py`, `lib/server/fetch-backend.ts`
- **Do**: Replace mock data with TanStack Query fetch; add infinite scroll; fallback to mock if API unreachable
- **Acceptance gate**: page fetches from FastAPI; pagination works; fallback to mock if API unreachable
- **Output**: updated `ListingFeed.tsx`, new `lib/hooks/useListings.ts`
- **Verifier**: debugger
- **Depends on**: UX-02, BD-02, BD-03

### UX-04: Nationwide Bulgaria LUN-style map + listings experience
- **Status**: `TODO` (website seed updated 2026-04-28 with grouped map markers, aggregate filter, search-mode toggle, scrollable all-card list, and foldable descriptions; full UX-04 still waits on backend/filter gates)
- **Read first**: `PLAN.md` §8, `docs/agents/ux_ui_designer/operator-dashboard-spec.md`, LUN-style reference notes
- **Do**: shape homepage UX to LUN-like split flow (map + feed + filters) for **all of Bulgaria**: default viewport and filters are **country-wide**; users can narrow by region/city/bbox. Optional **Varna preset** is allowed for demos or 3D pilot (UX-07) but must not be the only mode. Keep the scraped-property evidence fields visible where useful: local/remote photo counts, full-gallery flag, description quality, scrape quality score, and image-report status.
- **2026-04-28 lead note**: homepage seed now has MapLibre + OpenStreetMap raster base, deterministic nationwide coordinates for scraped rows without lat/lon, at most 20 grouped city/district map points, smooth zoom-settled recentering toward the largest nearby aggregate while the visible frame still represents more than 20 properties, synchronized map/list selection, selected-property right panel, selected-card pinning, scrollable full-card list, aggregate duplicate-source filter, region/description search modes, foldable descriptions, and source buttons. Full UX-04 still needs backend filter contracts, viewport-driven clustering, and real geocoding/building entities before verification.
- **2026-04-29 lead note**: homepage map/list row is now a bounded two-panel layout on desktop with a 70% map / 30% property panel split, same-height blocks, internal property-panel scrolling, smaller property cards, 2D default view, and a 3D toggle. The map keeps visible grouped DOM pins even if remote map tiles or projection readiness are delayed.
- **2026-04-29 viewport-group note**: map grouping is now client viewport-driven, not pre-baked by city/district. Each rendered map view shows at most 20 markers; 21-39 visible properties merge nearest neighbors until 20 markers remain, and 40+ visible properties use a 20-cell viewport grid. Selecting a group filters the right panel to only that group; selecting one property pins it first inside the same scrollable list. Below desktop width, the map stacks above the property panel instead of disappearing or overlapping.
- **2026-04-27 product note**: property detail pages now expose `Marketed by sources` / `Source links` buttons using conservative source-link matching. Current source is always shown; cross-source links are only added when same-property evidence is strong enough and never inferred from neighboring listings on the same source.
- **Acceptance gate**: prototype demonstrates Bulgaria-wide browse (no hard-coded Varna-only lock), map filters + listing cards + synchronized selection; spec calls out optional Varna shortcut vs default nationwide
- **Output**: UX spec/update doc + component task breakdown
- **Verifier**: debugger + backend_developer
- **Depends on**: UX-03, BD-06, DBG-05

### UX-05: AI chat panel with property/map-aware context
- **Status**: `TODO`
- **Read first**: `app/(main)/page.tsx`, chat API contracts, `PLAN.md` chat sections
- **Do**: define and implement persistent chat panel connected to AI chat API, always aware of selected property and active map filters
- **Acceptance gate**: chat can reference current property card + filtered map state
- **Output**: frontend chat-panel implementation
- **Verifier**: debugger
- **Depends on**: UX-04, BD-07

### UX-06: Product UX structure spec (LUN-style buyer marketplace)
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-08)
- **Read first**: `docs/business/product-ux-structure.md`, `docs/business/unit-economics-market-analysis.md`
- **Do**: review and refine the product UX structure spec; create wireframe descriptions for each page; define component tree + mobile responsive strategy
- **Acceptance gate**: refined spec exists with component breakdown for all pages
- **Output**: `docs/agents/ux_ui_designer/product-ux-structure-refined.md`
- **Verifier**: debugger + lead agent
- **Depends on**: UX-01

### UX-07: 3D map integration with building layer (MapLibre)
- **Status**: `TODO`
- **Read first**: `docs/business/varna-3d-osm-integration.md`, `components/map/MapCanvas.tsx`
- **Do**: implement MapLibre 3D building extrusion layer using PMTiles from BD-08; building click shows listing drawer; 2D/3D toggle
- **2026-04-28 lead note**: temporary synthetic property/building extrusions were removed from the homepage path. The UI should only claim building-level highlighting after BD-08 provides real PMTiles/OSM/PostGIS building footprints and address-based matches.
- **Acceptance gate**: 3D buildings render in Varna viewport; building click opens drawer; 2D fallback works
- **Output**: updated MapCanvas component + BuildingLayer + BuildingSummaryDrawer
- **Verifier**: debugger + backend_developer
- **Depends on**: UX-04, BD-08

### UX-08: Shop view — full property feed with advanced filters (like LUN.ua)
- **Status**: `TODO`
- **Priority**: **CRITICAL** — this is the main user-facing page
- **Read first**: `docs/business/product-ux-structure.md` (§3.1, §3.2), `components/listings/ListingFeed.tsx`, `components/listings/ListingCard.tsx`, BD-12 API spec
- **Do**:
  1. **Filter sidebar/panel** (collapsible on mobile):
     - Intent toggle: Buy / Rent / Short-term / Auction / Land
     - Category chips: Apartment / House / Villa / Studio / Penthouse / Office / Shop / Land / Garage
     - Price range slider (min–max, €)
     - Area range slider (min–max, m²)
     - Rooms dropdown (1, 2, 3, 4, 5+)
     - Floor range (min–max)
     - Year built (min–max)
     - Construction type checkboxes (brick, panel, EPK, monolith)
     - Amenities checkboxes (parking, balcony, elevator, furnished, sea view)
     - Source filter (show only from: imot.bg, Homes.bg, etc.)
     - Sort: Newest / Price ↑ / Price ↓ / Area ↑
  2. **Listing cards** (per `docs/business/product-ux-structure.md` §3.2):
     - Photo carousel (swipeable, 3–5 photos)
     - Price + price/m² prominently
     - Location (city, district)
     - Key facts: rooms, area, floor/total_floors, year
     - Source badges (which portals list this property)
     - Freshness indicator (updated X hours ago)
     - Save/favorite button (requires login)
     - "Owner representative" label (never "agent")
  3. **Infinite scroll** with cursor-based pagination from BD-12
  4. **Map synchronization**: hover card → highlight pin; click pin → scroll to card; drag map → filter feed to visible area; draw polygon → filter to custom area
  5. **Empty state**: "No properties match your filters" with suggestions
  6. **Loading skeleton**: shimmer cards while fetching
  7. All filters send API params to `GET /properties` (from BD-12)
- **Acceptance gate**: filters work with live API; map sync works; infinite scroll loads next page; mobile responsive; all filter combinations compose correctly
- **Output**: updated ListingFeed, FilterPanel, ListingCard, map sync hooks
- **Verifier**: debugger + backend_developer
- **Depends on**: UX-04, BD-12

### UX-09: Property detail page — LUN.ua style (like lun.ua item page)
- **Status**: `TODO`
- **Priority**: **CRITICAL** — each property needs a rich detail page
- **Read first**: `docs/business/product-ux-structure.md` (§3.3), `app/(main)/properties/[id]/page.tsx`, BD-11 API
- **Do**: Rebuild `/properties/[id]` to match LUN.ua detail page spec:
  1. **Photo gallery**: fullscreen capable, swipeable, zoom, lightbox, photo count badge
  2. **Price box**: price, price/m², price history chart (if available), currency toggle (EUR/BGN)
  3. **Facts grid**: type, rooms, area, floor/total_floors, year, construction type, Act 16 status, amenities
  4. **Description**: expandable, with machine translation toggle (BG ↔ EN)
  5. **Contact panel**: owner/representative name, phone (click-to-call), message button, agency logo if applicable
  6. **Mini map**: property location + nearby properties (3–5 pins)
  7. **Source links panel**: "Listed on: imot.bg, Homes.bg, alo.bg" with links and dates
  8. **Similar properties**: 3–6 cards based on same district + similar price/area
  9. **AI chat context**: "Ask about this property" → opens chat with property pre-loaded
  10. **Breadcrumb**: Home > Varna > Chaika > 2-bed apartment
  11. **Share button**: copy link, share to social
  12. **Save/favorite button** (requires login)
- **Acceptance gate**: detail page renders with all sections from live API; photo gallery works; contact info displayed; similar properties shown; mobile responsive
- **Output**: rebuilt `properties/[id]/page.tsx`, PhotoGallery, PriceBox, FactsGrid, ContactPanel, SimilarProperties components
- **Verifier**: debugger
- **Depends on**: UX-08, BD-11

### UX-10: User profile cabinet — buyer/renter/seller mode switching
- **Status**: `TODO`
- **Priority**: **HIGH** — all users need account management
- **Read first**: `docs/business/product-ux-structure.md` (§3.7), BD-13 auth API
- **Do**:
  1. **Header mode switcher**: visible toggle in top navigation — "I'm Buying" / "I'm Renting" / "I'm Selling"
     - Switching mode changes: navigation items, dashboard data, available actions
     - Mode persists in user profile (not just frontend state)
  2. **Registration page** `/auth/register`: email, password, name, preferred mode
  3. **Login page** `/auth/login`: email + password → JWT stored in httpOnly cookie
  4. **Settings page** `/settings`:
     - Profile: name, email, phone, avatar, preferred language (BG/EN)
     - Mode preferences: default mode, notification channels
     - Saved searches: list of saved filter combinations with alert toggles
     - Alert preferences: email/push/SMS frequency
  5. **Buyer/Renter dashboard** (when mode = buyer or renter):
     - Saved properties (grid of favorited listings)
     - Recent searches
     - Price alerts ("Property X dropped by 5%")
     - Recommended properties (based on saved search criteria)
  6. **Seller dashboard** (when mode = seller):
     - My listings (with status: active/pending/expired)
     - View count per listing
     - Inquiries/leads received
     - "Post new listing" CTA → `/post` wizard
  7. **Post listing wizard** `/post` (seller mode only):
     - Step 1: Property type + intent (sell/rent)
     - Step 2: Location (address input + pin on map)
     - Step 3: Details (area, rooms, floor, year, amenities — checkboxes)
     - Step 4: Photos (upload 5–20, drag to reorder, crop)
     - Step 5: Price + description (with Bulgarian/English toggle)
     - Step 6: Contact method (phone, chat, email)
     - Step 7: Review + submit
  8. **Auth guard**: protect `/settings`, `/post`, save actions — redirect to login if unauthenticated
- **Acceptance gate**: registration + login works; mode switcher changes navigation; saved properties persist; listing wizard submits to API; mobile responsive
- **Output**: auth pages, settings page, dashboard views, post wizard, mode switcher component
- **Verifier**: debugger + backend_developer (API integration)
- **Depends on**: UX-08, BD-13

### UX-11: Vercel deployment — frontend
- **Status**: `TODO`
- **Priority**: **CRITICAL** — the frontend must be publicly accessible
- **Read first**: `next.config.ts`, `package.json`, `lib/config.ts`, BD-14 Railway output
- **Do**:
  1. Configure Vercel project for Next.js 15 deployment
  2. Set environment variables: `NEXT_PUBLIC_API_URL` pointing to Railway backend (`https://bgrealestate-api.up.railway.app`)
  3. Configure custom domain (optional) or use default `*.vercel.app`
  4. Set up auto-deploy from `main` branch
  5. Configure headers: CORS, security headers, caching for static assets
  6. Verify API proxy route `app/api/backend/[...path]/route.ts` works with Railway backend
  7. Add `vercel.json` if custom config needed
  8. Test: all pages render, API calls work, map loads, images load
- **Acceptance gate**: `https://bgrealestate.vercel.app` loads homepage with map + listings; property detail pages work; API proxy reaches Railway backend
- **Output**: `vercel.json` (if needed), deployment docs, environment variable list
- **Verifier**: debugger
- **Depends on**: UX-08, BD-14

### UX-12: Admin dashboard — live operator panel
- **Status**: `TODO`
- **Priority**: HIGH — operators need to monitor scraper health and data quality
- **Read first**: `docs/agents/ux_ui_designer/admin-ui-spec.md`, `docs/agents/ux_ui_designer/operator-dashboard-spec.md`, `src/bgrealestate/api/routers/admin.py`
- **Do**: Build full admin dashboard at `/admin`:
  1. **Source health table**: all sources with status (active/error/stale), last crawl time, listing count, error rate
  2. **Crawl jobs table**: recent jobs with status, duration, records processed
  3. **Parser failure queue**: failed parses with raw HTML preview + error message + retry button
  4. **Duplicate review queue**: suspected duplicates with side-by-side comparison + merge/dismiss actions
  5. **System metrics**: total listings, total properties, active sources, daily ingestion rate chart
  6. **User management**: list users, roles, API keys
  7. Auth: admin-only access (requires `admin:read` scope)
- **Acceptance gate**: dashboard shows real data from admin API; tables paginate; charts render; admin auth enforced
- **Output**: admin page components, admin hooks, admin types
- **Verifier**: debugger + backend_developer
- **Depends on**: UX-11, BD-03

### UX-13: Design system — colors, typography, spacing tokens
- **Status**: `TODO`
- **Priority**: HIGH — consistent visual identity across all pages
- **Read first**: `docs/business/product-ux-structure.md` (§6 Design System Tokens), `tailwind.config.ts`, `app/globals.css`
- **Do**:
  1. Implement design tokens from product-ux-structure.md §6 in Tailwind config:
     - Colors: primary (#4361ee), accent (#e94560), success (#16c79a), warning (#f9c74f), dark (#1a1a2e), light (#f5f5f5)
     - Typography: Inter/system-ui for body, JetBrains Mono for prices/IDs
     - Spacing: 4px grid
     - Border radius: card (12px), button (8px)
     - Shadows: card elevation
  2. Create reusable component primitives: Button, Badge, Card, Input, Select, Slider, Modal, Drawer, Toast
  3. Apply design system to all existing components
  4. Dark mode support (optional, low priority)
- **Acceptance gate**: all pages use consistent tokens; no hardcoded colors/fonts; components match design spec
- **Output**: updated `tailwind.config.ts`, `app/globals.css`, `components/ui/*` primitives
- **Verifier**: debugger
- **Depends on**: UX-02

### UX-14: Account cabinet, liked properties, and property chat UX
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-29: `/settings`, `/chat`, and global chat bar now align to BD-17 contracts)
- **Priority**: HIGH — user account and liked-property workflows are core marketplace behavior
- **Read first**: BD-17, `app/(main)/settings/page.tsx`, `app/(main)/chat/page.tsx`, `components/chat/ChatBar.tsx`
- **Do**:
  1. Reframe `/settings` as a profile/account cabinet with buyer/renter/seller mode, liked properties, saved searches, and chat entry points.
  2. Reframe `/chat` around search threads and property threads.
  3. Connect chat surfaces through the Next backend proxy so model keys stay masked on the backend.
  4. Keep demo/local state until auth cookies and live user session wiring are complete.
- **Acceptance gate**: frontend typecheck passes; chat requests post to `/api/backend/api/v1/chat`; account surface shows liked-property and mode workflows without blocking Action1.
- **Output**: `components/account/AccountCabinet.tsx`, `components/chat/ChatWorkspace.tsx`, updated `/settings`, `/chat`, and `ChatBar`.
- **Verifier**: debugger + backend_developer
- **Depends on**: BD-17

### UX-15: Data-quality UX requirements from DA findings
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-13; requirements only, no public UI expansion)
- **Priority**: HIGH — operator truth before buyer-facing claims
- **Read first**: `docs/agents/roles/ux_ui_designer.md`, `docs/agents/roles/data_analyst.md`, `docs/exports/scrape-database-quality-audit-2026-05-13.md`, `docs/exports/action1-dataset-quality-gate.md`
- **Do**:
  1. Convert expected/current data-quality findings into UX/product requirements.
  2. Define UI handling for accepted vs pending QA, grouped/development publications, media gaps, confidence, duplicate candidates, and source provenance.
  3. Keep admin/operator UX tasks ahead of buyer-facing tasks.
  4. Hand debugger the assumptions that must be verified before implementation.
- **Acceptance gate**: decision notes separate FACT / INTERPRETATION / HYPOTHESIS / GAP; no public UI expansion is started; follow-up UX tasks are ordered admin/operator first, then buyer-facing.
- **Output**: `docs/agents/ux_ui_designer/data-quality-ui-decision-notes-2026-05-13.md`, updated UX task slices, ux_ui_designer JOURNEY entry.
- **Verifier**: debugger
- **Depends on**: DA-01 file-backed audit

### UX-16: Admin source-publication QA review queues
- **Status**: `TODO`
- **Priority**: HIGH — internal operator surface before public expansion
- **Read first**: `docs/agents/ux_ui_designer/data-quality-ui-decision-notes-2026-05-13.md`, `docs/agents/ux_ui_designer/admin-ui-spec.md`, `docs/agents/ux_ui_designer/operator-dashboard-spec.md`, `docs/exports/scrape-database-quality-audit-2026-05-13.md`, `BD-18` output, `BD-19` output when available
- **Do**:
  1. Extend `/admin` requirements and implementation with a source-publication QA queue.
  2. Show accepted, pending QA, `LOST`, inactive, grouped/development, media-gap, description-gap, parser-gap, and image-report states as separate filterable dimensions.
  3. Provide an evidence drawer with source URL, source key, source external ID, bucket/segment key, first/last seen, price/status, area, media counts, QA reasons, and source registry legal/risk/access modes.
  4. Add operator actions only when backed by API: accept, quarantine, grouped/development review, queue rescrape, queue media backfill, mark source-limited.
- **Acceptance gate**: admin queue never describes grouped/development rows as single properties; table/drawer labels match DA-02 metric definitions; no public route consumes these rows.
- **Output**: updated admin/operator spec and `/admin` component tasks or implementation.
- **Verifier**: debugger + data_analyst + backend_developer
- **Depends on**: DA-02, BD-18, BD-19

### UX-17: Admin duplicate, confidence, and provenance review UX
- **Status**: `TODO`
- **Priority**: HIGH — internal entity-resolution review before merge claims
- **Read first**: `docs/agents/ux_ui_designer/data-quality-ui-decision-notes-2026-05-13.md`, `ER-01` output, `ER-04` output when available, `BD-21` output when available, `src/bgrealestate/services/unification.py`, `docs/exports/action1-multi-unit-publications.json`
- **Do**:
  1. Define and build the operator duplicate-candidate queue after accepted source-publication import exists.
  2. Show side-by-side source-publication cards with confidence score, match signals, conflict fields, photos, price/status, area, contacts, source URLs, and first/last seen.
  3. Disable merge for grouped/development publications, low-confidence candidates, and records without unit-level evidence.
  4. Keep raw confidence internal; buyer-facing UI can later show verified source count/provenance only.
- **Acceptance gate**: grouped/development rows cannot be merged as one property; every merge/dismiss action is auditable; confidence language is internal and evidence-based.
- **Output**: duplicate/confidence/provenance UX spec update and admin task/component breakdown.
- **Verifier**: debugger + entity_resolution_agent + data_analyst
- **Depends on**: ER-01, BD-18, BD-19, BD-21, accepted source-publication import evidence

### UX-18: Buyer-facing accepted-only trust labels
- **Status**: `TODO`
- **Priority**: MEDIUM — do not start until public data gates pass
- **Read first**: `docs/agents/ux_ui_designer/data-quality-ui-decision-notes-2026-05-13.md`, `docs/business/product-ux-structure.md`, `lib/types/listing.ts`, `DA-02` output, `BD-18` output, `BD-19` output
- **Do**:
  1. Update listing cards and property details to show only accepted single-unit records by default.
  2. Translate pipeline evidence into buyer-safe labels: verified source, multiple sources, limited photos, price on request, location approximate.
  3. Keep source provenance visible as `Listed on` / `Marketed by sources` without exposing parser internals.
  4. Do not show grouped/development publications as normal property cards; reserve a future development/project surface until unit evidence exists.
- **Acceptance gate**: public feed/detail fixtures prove pending QA, missing-status, `LOST`, inactive, and grouped/development rows are excluded; labels are backed by verified fields; browser screenshots show no misleading data-quality copy.
- **Output**: buyer-facing trust-label component tasks or implementation after gates pass.
- **Verifier**: debugger + data_analyst
- **Depends on**: UX-16 verification, DA-02, BD-18, BD-19, public export accepted-only proof

### UX-19: Market positioning and source-coverage language
- **Status**: `TODO`
- **Priority**: MEDIUM
- **Read first**: `docs/exports/market-intelligence-2026-05-13.md`, `docs/agents/ux_ui_designer/data-quality-ui-decision-notes-2026-05-13.md`, `DA-02` output, `BD-19` output, `UX-18`
- **Do**:
  1. Define buyer-safe copy and UI labels for verified source provenance, limited media, approximate location, price on request, and accepted-only source coverage.
  2. Reserve "complete market", "95% coverage", city trend, and price-per-sqm labels until accepted-only DB-backed counts and price rollups exist.
  3. Map grouped/development publications to future project/new-build surfaces instead of normal property cards.
- **Acceptance gate**: UX language does not overstate coverage, does not expose parser internals to buyers, and cites accepted-only fields for every trust label.
- **Output**: UX copy/spec notes or implementation task breakdown.
- **Verifier**: debugger + market_intelligence_analyst + data_analyst
- **Depends on**: MI-01, UX-18, DA-02, BD-19

### UX-20: First-party analytics instrumentation hooks
- **Status**: `TODO`
- **Priority**: HIGH
- **Read first**: `docs/analytics/user-event-taxonomy.md`, `UA-02`, `BD-20`, `components/listings/MainExplorer.tsx`, `components/map/MapCanvas.tsx`, `components/listings/PhotoCarousel.tsx`, `app/(main)/properties/[id]/detail-client.tsx`, `components/chat/ChatBar.tsx`, `components/chat/ChatWorkspace.tsx`, `components/account/AccountCabinet.tsx`, `app/(main)/admin/page.tsx`
- **Do**:
  1. Add a small first-party analytics client wrapper only after `BD-20` intake exists; no external analytics package.
  2. Fire safe derived events for search/filter changes, listing impressions/selections, map marker/mode/view interactions, source link opens, save/contact/share intent, chat opens/messages/failures, profile mode/saved-search actions, admin queue/review actions, and media gallery navigation.
  3. Derive and send only taxonomy-approved buckets/enums; never send raw search text, raw chat text, contact details, source URLs, image URLs, or admin notes.
  4. Debounce/batch high-volume events: search changes, map moves, impressions, and media navigation.
- **Acceptance gate**: component tests or debug sink fixtures show expected event names/payloads for key flows; `rg` finds no external analytics dependency; unsafe text/url/contact fields are absent.
- **Output**: frontend analytics client/hooks, component wiring, UX JOURNEY entry, debugger handoff.
- **Verifier**: debugger + user_analytics_agent + backend_developer
- **Depends on**: UA-02, BD-20, UX-15

### UX-21: In-platform four-dashboard shell
- **Status**: `TODO`
- **Priority**: MEDIUM
- **Read first**: `PLAN-06`, `docs/dashboard/project-progress.html`, `docs/dashboard/properties-database.html`, `docs/dashboard/website.html`, `docs/dashboard/support.html`, `docs/exports/operational-dashboards.json`, `app/(main)/admin/page.tsx`, `app/(main)/dashboard/[...path]/route.ts`
- **Do**:
  1. Translate the static four-dashboard model into an authenticated operator/admin web-platform shell after `BD-19` exposes verified read models.
  2. Preserve the same four categories and expandable insight/details/action pattern; do not compress statuses into opaque aggregate cards.
  3. Show file-backed vs DB-backed badges for every count and hide public/release-ready labels until verifier gates pass.
  4. Keep support operations separate from public marketplace pages; support dashboard is for operator assistance, not buyer marketing.
- **Acceptance gate**: in-platform dashboard routes mirror the static dashboard semantics, use verified API/read-model data when available, and no public route displays raw QA or support data.
- **Output**: admin/dashboard component plan or implementation, UX JOURNEY entry, screenshot/browser verification handoff.
- **Verifier**: debugger + data_analyst + backend_developer
- **Depends on**: PLAN-06, DA-04, BD-19

### UX-22: Verified dashboard/read-model field consumption contract
- **Status**: `DONE_AWAITING_VERIFY` (2026-05-13; contract only, no buyer-facing implementation)
- **Priority**: **HIGH**
- **Read first**: `docs/agents/ux_ui_designer/verified-field-consumption-2026-05-13.md`, `docs/exports/properties-deep-analytics-agent-handoff-2026-05-13.md`, `DA-02`, `DA-05`, `BD-18`, `BD-19`, `UX-16`, `UX-18`, `UX-21`, `docs/dashboard/data-quality-dashboard.html`, `docs/dashboard/properties-database.html`
- **Do**:
  1. Consume only verified file-backed dashboard fields or DB-backed read-model fields.
  2. Label file-backed audit, quality-gate estimate, importer candidate, media-capture, and DB-blocked states explicitly in admin/operator surfaces.
  3. Keep buyer-facing cards/details/trust labels blocked until accepted-only DB/read-model proof, `BD-19`, and debugger verification exist.
  4. Preserve grouped/development, `LOST`, inactive, pending QA, and image-description-not-generated states as internal operator evidence only.
- **Acceptance gate**: UX contract names allowed fields, blocked fields, required labels, and dependent slices; no public route claims verified inventory or semantic image descriptions from file-backed operational dashboards alone.
- **Output**: `docs/agents/ux_ui_designer/verified-field-consumption-2026-05-13.md`, ux_ui_designer JOURNEY entry.
- **Verifier**: debugger + data_analyst + backend_developer
- **Depends on**: DA-02, BD-18, BD-19

---

## ═══════════════════════════════════════════════════════
## DEBUGGER (cross-agent verification + safety)
## ═══════════════════════════════════════════════════════

**Mission**: Verify every slice before it's marked complete: acceptance gates, **OpenClaw/Telegram gate compliance** (`Action1 ACCEPT`, +100 matrix pings), legal compliance, security spot checks, and **`make test` / `make validate`**. Be the quality gatekeeper — especially **file-backed vs DB-backed** metrics drift.

**Detective index (2026-04-30)**: `docs/exports/detective-product-orchestration-2026-04-30.md`.

**2026-04-09:** Prioritize **`DBG-06`** / **`DBG-05`** **after** **`S1-18`** live volume + **`BD-11`** ingest evidence; you may still **spot-check** `S1-14` promotion if asked.

### DBG-01: Golden path check
- **Status**: `VERIFIED`
- **Read first**: `scripts/golden_path_check.py`, `agent-skills/debugger-golden-path/SKILL.md`
- **Do**: `make golden-path` — migrate → sync → fixture ingest → stats → XLSX
- **Acceptance gate**: `make validate` passes; with DB, golden path ends OK
- **Output**: `scripts/golden_path_check.py`, skill, tests
- **Verifier**: self (via `make validate`)
- **Depends on**: —

### DBG-02: Verify all DONE_AWAITING_VERIFY slices
- **Status**: `VERIFIED` (2026-04-08 run; UX-01 verified)
- **Read first**: this file (scan for `DONE_AWAITING_VERIFY` status)
- **Do**: for each awaiting slice, run its acceptance gate commands; record PASS/FAIL
- **Acceptance gate**: every verified slice has a matching JOURNEY.md entry
- **Output**: verification entries in JOURNEY.md + status updates here
- **Verifier**: lead agent (spot checks)
- **Depends on**: —

### DBG-03: Cross-agent safety audit
- **Status**: `VERIFIED` (2026-04-08)
- **Read first**: `.cursor/BUGBOT.md`, `data/source_registry.json`, all `tests/test_*.py`
- **Do**: check all connectors for legal gate enforcement; check tests for live network; check fixtures for secrets/PII; check media storage
- **Acceptance gate**: zero violations found, or violations documented as blockers
- **Output**: audit entry in JOURNEY.md
- **Verifier**: lead agent
- **Depends on**: S1-01 through S1-10

### DBG-04: CI pipeline verification
- **Status**: `VERIFIED` (2026-04-08)
- **Read first**: `.gitlab-ci.yml`, `Makefile`, `Dockerfile`
- **Do**: verify CI runs `make test`, `make lint`, `make validate`, `make golden-path`
- **Acceptance gate**: pipeline green on fixture-only tests
- **Output**: verification entry in JOURNEY.md
- **Verifier**: self
- **Depends on**: BD-05

### DBG-05: Verify stage-1 scraping before expanding 3D / building-depth geo
- **Status**: `TODO`
- **Read first**: `docs/exports/stage1-product-type-coverage.md`, `docs/exports/tier12-live-volume-report.md` (once exists), `scripts/golden_path_check.py`, `/admin/source-stats`
- **Do**: verify stage-1 **fixture** product-type completeness **and** (when available) **live** volume evidence from `S1-18`; confirm inputs for **Varna 3D / building-mesh pilot** and broader **building-match** rollout. **Note:** nationwide **map + listings browse** (`UX-04`) is not Varna-limited; this gate still matters for data trust before **3D** and **multi-city building** investment.
- **Acceptance gate**: required product types covered per coverage doc; golden path passes; live volume report meets `S1-18` thresholds or waiver is documented
- **Output**: verification entry in `docs/agents/debugger/JOURNEY.md`
- **Verifier**: lead agent
- **Depends on**: S1-13, BD-01, **S1-18** (live portion)

### DBG-08: Verify Codex tier-1/2 quality audit and Gemma readiness
- **Status**: `TODO`
- **Priority**: **CRITICAL** — verifier for the Action0/Action1/Action2 Gemma/OpenClaw sequence
- **Read first**: `S1-21`, `S1-22A`, `S1-22B`, `S1-22C`, `docs/exports/taskforgema.md`, `docs/openclaw/gemma4-agent.md`, `docs/exports/s1-21-gemma-action0-eligible.json`, `docs/dashboard/scrape-status.html`
- **Do**: verify source-by-source completeness tables, parser tests, local image file evidence, property-image-report completeness, Action1 source/bucket logs, frontend scraped-listing seed generation, and refreshed dashboards after each action.
- **Acceptance gate**: Action0 has report-or-skip coverage for every eligible row; Action1 has attempted all seven sources in all four buckets with saved/skipped/error counts; every high-priority source gap has a fix, test, blocker, or queued Action2 follow-up; no ambiguous Varna-only instruction remains.
- **Output**: verification entry in `docs/agents/debugger/JOURNEY.md`, updated TASKS statuses
- **Verifier**: lead agent
- **Depends on**: S1-21, S1-22A, S1-22B as applicable

### DBG-06: Verify all pending DONE_AWAITING_VERIFY slices (batch 2)
- **Status**: `TODO`
- **Priority**: **CRITICAL** — many slices await verification (**scheduled after `S1-18` + `BD-11` live ingest proof** per 2026-04-09 wave; early spot-checks allowed if operator requests)
- **Read first**: this file — scan all `DONE_AWAITING_VERIFY` slices
- **Do**: systematically verify each pending slice:
  1. BD-04 (Auth/RBAC): test 401/403 responses, API key scope enforcement
  2. BD-05 (Temporal): verify worker/scheduler stubs, test restart behavior
  3. S1-11 (Ingestion runner): run fixture ingest, check DB round-trip
  4. S1-12 (Tier-2 stubs): verify all 4 tier-2 connectors parse correctly
  5. S1-13 (Stage-1 coverage): verify coverage matrix is complete
  6. T3-02 (AirDNA/Airbtics): verify STR metrics parsing
  7. T3-03 (BCPEA): verify auction parsing
  8. T3-04 (Partner stubs): verify `PartnerContractRequired` enforcement
  9. T3-05 (Official registers): verify consent enforcement
  10. SM-02 (Telegram): verify lead extraction + redaction
  11. SM-03 (X): verify lead extraction + redaction
  12. UX-02 (Beta main page): verify map + listings + filters render
  13. UX-03 (Live API wiring): verify TanStack Query fetch + fallback
  - For each: run `make test`, run specific acceptance gate, record PASS/FAIL
- **Acceptance gate**: all slices either promoted to `VERIFIED` or documented as `BLOCKED` with specific failure reason
- **Output**: batch verification report in `docs/agents/debugger/JOURNEY.md`, updated statuses in TASKS.md
- **Verifier**: lead agent
- **Depends on**: **S1-18**, **BD-11** (live rows or documented waiver)

### DBG-07: End-to-end website smoke test
- **Status**: `TODO`
- **Priority**: **CRITICAL** — must verify the full stack works before launch
- **Read first**: BD-14, UX-11 outputs, all API endpoints
- **Do**: after Railway + Vercel deployment, run full smoke test:
  1. `GET /api/v1/ready` returns 200 (Railway)
  2. Homepage loads with map + listings (Vercel)
  3. Click a listing → property detail page loads
  4. Apply filters → feed updates
  5. Map pan → feed updates to visible area
  6. Register new user → login → save a property → verify saved
  7. Switch to seller mode → post a listing (if implemented)
  8. Admin dashboard loads with real data
  9. Scraper status shows recent crawl times
  10. Mobile responsive check (viewport resize)
- **Acceptance gate**: all 10 smoke tests pass; screenshot evidence in JOURNEY.md
- **Output**: smoke test checklist + results in `docs/agents/debugger/JOURNEY.md`
- **Verifier**: lead agent
- **Depends on**: BD-14, UX-11

### DBG-08: Security audit — auth, injection, XSS, CORS
- **Status**: `TODO`
- **Priority**: HIGH — public website must be secure
- **Read first**: all API routes, auth middleware, frontend forms
- **Do**:
  1. SQL injection audit: verify all queries use parameterized statements
  2. XSS audit: verify all user content is escaped in frontend
  3. Auth audit: verify JWT validation, session handling, password hashing
  4. CORS audit: verify only allowed origins can access API
  5. Rate limiting: verify API has rate limiting on auth endpoints
  6. Secrets audit: no API keys, passwords, or tokens in code or fixtures
  7. HTTPS: verify all traffic is encrypted
- **Acceptance gate**: zero critical vulnerabilities; medium issues documented with fix plan
- **Output**: security audit report in `docs/agents/debugger/JOURNEY.md`
- **Verifier**: lead agent
- **Depends on**: BD-14, BD-13

### DBG-09: End-of-run verification sweep
- **Status**: `TODO`
- **Priority**: HIGH — every non-debugger agent run must end with queued verification
- **Read first**: `docs/agents/README.md`, latest entries in `docs/agents/*/JOURNEY.md`, all `DONE_AWAITING_VERIFY` slices in this file
- **Do**:
  1. After each backend, scraper, or UX run, scan for the latest slice updates and match them to their acceptance gates.
  2. Execute the relevant verification immediately when the gate is runnable, or record an explicit deferred reason in `docs/agents/debugger/JOURNEY.md`.
  3. Keep a short pass/fail queue so no agent run ends without a debugger follow-up.
- **Acceptance gate**: every new non-debugger JOURNEY entry has a corresponding debugger verification note or an explicit deferral reason
- **Output**: rolling handoff log in `docs/agents/debugger/JOURNEY.md`, status updates here when verification completes
- **Verifier**: lead agent
- **Depends on**: —

### DBG-10: Fixture-only test hardening for live scraper/media side effects
- **Status**: `TODO`
- **Priority**: HIGH — guardrail enforcement
- **Read first**: `tests/test_scrape_stage1.py`, `tests/test_live_scraper_source_parsers.py`, `tests/test_media_pipeline.py`, `scripts/live_scraper.py`, `src/bgrealestate/services/media.py`
- **Do**: identify why `make test` can emit live HTTP/image-download log lines and modify `data/scraper.log`; convert the path to fixture/mocked clients or isolate log output to a temp file during tests.
- **Acceptance gate**: `make test` leaves `data/scraper.log` unchanged and no test performs external HTTP unless explicitly enabled by an opt-in env var.
- **Output**: tests/mocks/logging isolation patch plus verifier note.
- **Verifier**: lead agent
- **Depends on**: —

### DBG-14: Verify DA-01 scrape database quality audit
- **Status**: `VERIFIED` (2026-05-13; file-backed DA-01 passed, DB-backed counts blocked)
- **Priority**: **HIGH**
- **Read first**: `docs/exports/scrape-database-quality-audit-2026-05-13.md`, `scripts/audit_scrape_database_quality.py`, `docs/agents/data_analyst/JOURNEY.md`, `docs/agents/TASKS.md`
- **Do**:
  1. Re-run `python3 scripts/audit_scrape_database_quality.py` and compare report totals with the committed JSON.
  2. Verify the report separates FACT / INTERPRETATION / GAP and covers seven Action1 sources across four buckets.
  3. Verify `S1-23` and `BD-18` are queued with concrete acceptance gates.
  4. Record DB/import blockers (`DATABASE_URL` missing and SQLAlchemy import dependency) without promoting DB-backed claims.
- **Acceptance gate**: report is reproducible; no public/DB completion claim is made without PostgreSQL evidence; follow-up tasks are actionable.
- **Output**: debugger JOURNEY verification entry and TASKS status update for DA-01.
- **Verifier**: debugger
- **Depends on**: DA-01

### DBG-22: Verify backend BD-18 contract prep
- **Status**: `TODO`
- **Priority**: **HIGH**
- **Read first**: `docs/agents/backend_developer/JOURNEY.md`, `BD-18`, `docs/exports/bd18-database-review-and-correction-spec-2026-05-13.md`, `scripts/import_scraped_listings.py`, `src/bgrealestate/models.py`, `src/bgrealestate/db/models.py`, `src/bgrealestate/db/repositories.py`, `src/bgrealestate/db/media_ids.py`, `src/bgrealestate/connectors/ingest.py`, `tests/test_backend_import_contract.py`
- **Do**:
  1. Confirm no live scraped data was imported or mutated by the backend prep run.
  2. Verify accepted-only import boundaries still reject unreviewed, LOST, grouped/development, and inactive rows by default.
  3. Verify all-Bulgaria bucket/provenance evidence is preserved outside the Varna-only `source_section_id` FK.
  4. Verify `CanonicalListingRepository.upsert` can accept the current `CanonicalListing` dataclass fields and repeated listing-media sync uses deterministic IDs.
  5. Defer DB-backed import/count claims until `DATABASE_URL` is available.
  6. Verify numeric price `0` cannot persist as a real price and default scraped import does not promote `property_entity` / `property_offer`.
- **Acceptance gate**: `python3 -m py_compile scripts/import_scraped_listings.py src/bgrealestate/db/media_ids.py src/bgrealestate/db/models.py src/bgrealestate/db/repositories.py src/bgrealestate/connectors/ingest.py src/bgrealestate/cli.py tests/test_backend_import_contract.py`; `PYTHONPATH=src python3 -m unittest tests.test_backend_import_contract -v`; DB-backed fixture import remains blocked unless a real PostgreSQL URL is supplied.
- **Output**: debugger JOURNEY verification entry and TASKS status update for `BD-18` prep.
- **Verifier**: debugger
- **Depends on**: BD-18

### DBG-15: Verify data-analyst-centered planner handoff
- **Status**: `VERIFIED` (2026-05-13; protocol pass, DB/dashboard verification deferred to BD-18/INFRA-02/DA-03)
- **Priority**: **CRITICAL**
- **Read first**: `PLAN-04`, `docs/agents/TASKS.md`, `docs/agents/planner/JOURNEY.md`, `docs/agents/README.md`, `docs/agents/AGENT_LOOP_AND_CADENCE.md`
- **Do**:
  1. Verify the active dependency map keeps `data_analyst` as evidence owner.
  2. Verify backend, scraper_1, UX, infra, and knowledge slices each have a concrete next step, dependency, output, and verifier.
  3. Verify planner did not touch scraped DB/corpus artifacts.
- **Acceptance gate**: no active slice can claim Action1 completion, DB import success, or public UI data truth without analyst/debugger evidence.
- **Output**: debugger JOURNEY entry; TASKS status update for `PLAN-04`.
- **Verifier**: debugger
- **Depends on**: PLAN-04

### DBG-16: Verify DA-dependent implementation queue
- **Status**: `TODO`
- **Priority**: HIGH
- **Read first**: `BD-18`, `BD-19`, `S1-23`, `S1-24`, `UX-15`, `INFRA-02`, latest `DA-02` / `DA-03` outputs
- **Do**:
  1. Verify each DA-dependent implementation slice uses analyst artifacts as inputs, not chat summaries.
  2. Run focused acceptance gates when a producing agent marks a slice `DONE_AWAITING_VERIFY`.
  3. Record deferred verification reasons when `DATABASE_URL`, dashboard fast mode, or live credentials are missing.
- **Acceptance gate**: every DA-dependent slice has PASS/FAIL/deferred debugger notes and no unresolved verifier handoff.
- **Output**: debugger JOURNEY entries and TASKS status updates.
- **Verifier**: debugger
- **Depends on**: DA-02, DA-03 as applicable

### DBG-23: Verify four-dashboard operating model
- **Status**: `TODO`
- **Priority**: **CRITICAL**
- **Read first**: `PLAN-06`, `scripts/generate_operational_dashboards.py`, `docs/exports/operational-dashboards.json`, `docs/dashboard/index.html`, `docs/dashboard/project-progress.html`, `docs/dashboard/properties-database.html`, `docs/dashboard/website.html`, `docs/dashboard/support.html`
- **Do**:
  1. Run `python3 -m py_compile scripts/generate_operational_dashboards.py` and `python3 scripts/generate_operational_dashboards.py`.
  2. Verify the four dashboard pages exist and each stat block is a `<details open>` item with insight/details/action text.
  3. Verify the Project Progress dashboard includes all current agent lanes and does not lose new support agents.
  4. Verify the Properties Database dashboard labels file-backed audit, quality-gate, scrape-status, and DB-blocked counts separately.
  5. Verify the Website and Support dashboards do not claim public data readiness, deployment readiness, DB parity, or media report completion without upstream gates.
- **Acceptance gate**: dashboards regenerate deterministically from file-backed artifacts, no scraped DB/corpus is touched, and unresolved DA-02/DA-03/BD-18/INFRA-02 gates remain visible.
- **Output**: debugger JOURNEY entry and TASKS status update for `PLAN-06`.
- **Verifier**: debugger + data_analyst + ux_ui_designer
- **Depends on**: PLAN-06

### DBG-24: Verify DA-02/BD-18 deep handoff
- **Status**: `VERIFIED` (2026-05-13; file-backed handoff and code-contract checks passed, DB proof blocked by missing `DATABASE_URL`)
- **Priority**: **CRITICAL**
- **Read first**: `docs/exports/debugger-da02-bd18-handoff-verification-2026-05-13.md`, `docs/exports/data-quality-deep-review-2026-05-13.md`, `docs/exports/bd18-database-review-and-correction-spec-2026-05-13.md`, `docs/dashboard/data-quality-dashboard.html`, `scripts/import_scraped_listings.py`, `scripts/bd18_db_smoke_import.py`, `src/bgrealestate/db/models.py`, `src/bgrealestate/db/repositories.py`, `src/bgrealestate/connectors/ingest.py`, `tests/test_backend_import_contract.py`
- **Do**:
  1. Verify DA-02 dashboard/report outputs are file-backed and do not claim DB parity.
  2. Verify BD-18 table/model/repository/import-smoke changes compile and preserve accepted-only source-publication import behavior.
  3. Run focused backend import contract tests.
  4. Record `make verify-db-counts` and `make bd18-db-smoke-import` as blocked until `DATABASE_URL` exists.
- **Acceptance gate**: debugger report separates PASS file-backed/code-contract readiness from BLOCKED DB-backed migration/import/count proof, and names backend/infra/UX next owners.
- **Output**: `docs/exports/debugger-da02-bd18-handoff-verification-2026-05-13.md`, debugger JOURNEY entry.
- **Verifier**: debugger
- **Depends on**: DA-02, BD-18

### DBG-17: Verify scraper_1 analyst-support handoff
- **Status**: `TODO`
- **Priority**: **HIGH**
- **Read first**: latest `docs/agents/scraper_1/JOURNEY.md`, `S1-23`, `docs/exports/scrape-database-quality-audit-2026-05-13.md`, `docs/exports/action1-dataset-quality-gate.md`, `data/source_registry.json`
- **Do**:
  1. Verify scraper_1 did not start live scraping or widen Action2.
  2. Check that source-specific next actions cover parser gaps, media gaps, grouped/development handling, missing provenance, and price-state handling for all seven A1 sources.
  3. Confirm Action1 -> Action0 -> Action2 gate remains intact and non-A1 sources are context only.
- **Acceptance gate**: debugger can map every DA-01 source finding to a scraper repair, data_analyst follow-up, or blocked/legal state without contradicting source-registry gates.
- **Output**: debugger JOURNEY verification entry and any required TASKS status update.
- **Verifier**: debugger
- **Depends on**: S1-23, DA-01

### DBG-18: Verify vision media QA readiness and gates
- **Status**: `TODO`
- **Priority**: HIGH
- **Read first**: `VM-01`, `VM-02`, `VM-03`, `VM-04`, `docs/exports/vision-media-action0-readiness-2026-05-13.md`, `docs/agents/vision_media_agent/JOURNEY.md`, `docs/exports/s1-21-gemma-action0-eligible.json`, `docs/exports/action1-dataset-quality-gate.json`
- **Do**:
  1. Verify VM-01 did not run image processing and kept Action0 execution blocked until operator `Action0 now`.
  2. Verify media QA tasks cover gallery completeness, per-image semantics, room/condition/equipment/style evidence, whole-property consistency, and uncertainty.
  3. Verify buyer-facing display and promotion gates exclude pending QA, `LOST`, inactive, grouped/development, partial-gallery, and no-report rows unless explicitly source-limited.
  4. Verify dashboard handoff warns against using stale media-coverage accepted counters before DA-02.
- **Acceptance gate**: debugger can approve the media-evidence plan without any semantic image output being treated as canonical fact; any missing schema/gate requirement is mapped back to VM-02/VM-03/VM-04.
- **Output**: debugger JOURNEY verification entry and TASKS status update for VM-01.
- **Verifier**: debugger
- **Depends on**: VM-01

### DBG-21: Verify data-analysis release hygiene gate
- **Status**: `TODO`
- **Priority**: **CRITICAL**
- **Read first**: `OPS-02`, `docs/agents/ops_release_manager/JOURNEY.md`, `.gitignore`, latest `data_analyst` outputs, staged diff if a release is later prepared
- **Do**:
  1. Verify OPS-02 did not stage, push, or promote counts while data analyst work was still running.
  2. Confirm release notes require reproducible DA artifacts and separate file-backed, DB-backed, accepted, LOST, grouped/development, inactive, media-gap, and dashboard denominator claims.
  3. If a staged release exists later, run unsafe-path and secret scans against the staged diff and block raw dumps, logs, DB dumps, secrets, local runtime state, archives, caches, and unreviewed corpus batches.
  4. Record whether tracked `data/scraper.log` changed; treat unexpected log churn as a release blocker until DBG-10 resolves log isolation.
- **Acceptance gate**: debugger records PASS/FAIL/deferred release-hygiene result; no data-analysis-driven release proceeds with unsafe files or unsupported data claims.
- **Output**: debugger JOURNEY entry and TASKS status update.
- **Verifier**: debugger
- **Depends on**: OPS-02, DA-02/DA-03 as applicable

### DBG-19: Verify privacy-safe analytics instrumentation
- **Status**: `TODO`
- **Priority**: HIGH
- **Read first**: `docs/analytics/user-event-taxonomy.md`, `UA-02`, `BD-20`, `UX-20`, tests for analytics payloads
- **Do**:
  1. Verify no external analytics dependencies, scripts, pixels, or outbound third-party telemetry endpoints were added.
  2. Verify event payload tests reject raw search text, raw chat text, emails, phones, names, source URLs, image URLs, IP addresses, raw user agents, tokens, and admin notes.
  3. Verify debounced/batched events do not over-log high-frequency search, map, impression, or media actions.
  4. Verify dashboard queries use first-party event tables only.
- **Acceptance gate**: focused tests and `rg` scans pass; debugger records PASS/FAIL with any unsafe field paths.
- **Output**: debugger JOURNEY verification entry and TASKS status updates.
- **Verifier**: debugger
- **Depends on**: BD-20, UX-20, UA-03

### DBG-20: Verify entity-resolution accepted-only/no-promotion gate
- **Status**: `TODO`
- **Priority**: HIGH
- **Read first**: ER-01 output, ER-02/ER-03 outputs when available, `BD-21` output when available, `src/bgrealestate/services/unification.py`, `scripts/import_scraped_listings.py`, `docs/exports/action1-multi-unit-publications.json`, `docs/exports/scrape-database-quality-audit-2026-05-13.md`
- **Do**:
  1. Verify ER planning and later implementation consume accepted source-publication evidence, not chat summaries or raw scrape volume.
  2. Verify pending QA, missing-status, `LOST`, inactive, grouped/development, unknown, and conflicting-evidence rows cannot enter duplicate scoring or property promotion.
  3. Verify candidate generation, when implemented, writes reviewable candidate/evidence/review rows only until an explicit reviewed merge path exists.
  4. Verify fixtures cover single-unit, grouped/development, unknown, duplicate, and conflicting-evidence cases.
  5. Verify public `/properties` and buyer-facing exports do not expose ER candidates.
- **Acceptance gate**: no ER slice creates or mutates `property_entity` / `property_offer` without reviewed accepted-only evidence; fixture tests and docs prove grouped/development rows cannot auto-merge as one property.
- **Output**: debugger JOURNEY verification entry and TASKS status updates for ER/BD handoffs.
- **Verifier**: debugger + data_analyst
- **Depends on**: ER-01; implementation verification depends on ER-02, ER-03, BD-21

---

## ═══════════════════════════════════════════════════════
## LEAD AGENT — Business, Strategy & Monitoring
## ═══════════════════════════════════════════════════════

**Mission**: Keep the project on track. Monitor dashboards, update architecture docs, resolve blockers, and ensure all agents are making progress toward the working website goal.

### LEAD-01: Unit economics, TAM/SAM/SOM, market analysis
- **Status**: `VERIFIED` (2026-04-08; created and generated)
- **Output**: `docs/business/unit-economics-market-analysis.md`
- **Verifier**: lead agent (self)
- **Depends on**: —

### LEAD-02: Investor presentation PDF with charts
- **Status**: `VERIFIED` (2026-04-08; generated with matplotlib + reportlab)
- **Output**: `output/pdf/investor-presentation-2026-04-08.pdf` (12 slides, 411 KB)
- **Generator**: `scripts/generate_investor_presentation.py`
- **Verifier**: lead agent (self)
- **Depends on**: LEAD-01

### LEAD-03: Product UX structure plan (LUN-style)
- **Status**: `VERIFIED` (2026-04-08; spec complete)
- **Output**: `docs/business/product-ux-structure.md`
- **Verifier**: lead agent (self)
- **Depends on**: —

### LEAD-04: Varna 3D OSM building integration plan
- **Status**: `VERIFIED` (2026-04-08; plan complete)
- **Output**: `docs/business/varna-3d-osm-integration.md`
- **Verifier**: lead agent (self)
- **Depends on**: —

### LEAD-05: Dashboard monitoring + architecture refresh (recurring)
- **Status**: `TODO` (recurring)
- **Priority**: HIGH — lead agent's primary ongoing responsibility
- **Read first**: `docs/exports/progress-dashboard.json`, all JOURNEY.md files, this file
- **Do**: On each activation:
  1. Read all JOURNEY.md files — identify progress since last check
  2. Update `docs/exports/progress-dashboard.json` with current slice statuses
  3. Run `make dashboard-doc` to regenerate dashboard HTML
  4. Identify blocked agents and propose unblock actions
  5. Update dependency graph if new slices were added
  6. Verify agent slices are being completed in priority order (CRITICAL first)
  7. Report: % complete toward working website, estimated remaining slices, top blockers
- **Acceptance gate**: dashboard is current; no agent has been stuck on same slice for >2 activations without blocker documented
- **Output**: updated dashboard, blocker notes, progress report

### LEAD-07: OpenClaw/Gemma run analysis and next-run preparation
- **Status**: `DONE_AWAITING_VERIFY` (2026-04-27)
- **Priority**: HIGH
- **Read first**: `docs/exports/gemma4-openclaw-run-analysis-2026-04-27.md`, `docs/openclaw/gemma4-agent.md`, `docs/exports/taskforgema.md`
- **Do**: analyze what Gemma/OpenClaw produced, update only relevant agent tasks, prepare the next Codex quality-audit prompt path and the following Gemma image-report path, update website seed data with scraped property evidence, refresh dashboards, and run the website locally.
- **Acceptance gate**: analysis doc exists; `S1-21`, `S1-22A`, `S1-22B`, `S1-22C`, and `DBG-08` are queued; website can show scraped items with media/quality metadata; dashboards are regenerated.
- **Output**: updated task queue, dashboards, frontend scraped-listing seed, run notes
- **Verifier**: self
- **Depends on**: —

### LEAD-06: GitLab CI/CD pipeline setup
- **Status**: `TODO`
- **Priority**: HIGH — automated testing and deployment
- **Read first**: `Makefile`, `Dockerfile`, `pyproject.toml`, `package.json`
- **Do**:
  1. Create `.gitlab-ci.yml` with stages: lint → test → build → deploy
  2. Lint stage: `make lint` + `make typecheck`
  3. Test stage: `make test` + `make golden-path` (with PostgreSQL service container)
  4. Build stage: Docker build for backend + Next.js build for frontend
  5. Deploy stage: trigger Railway deploy (backend) + Vercel deploy (frontend) on `main` branch
  6. Add branch protection: require CI pass before merge
- **Acceptance gate**: CI pipeline runs on every push; all stages green; auto-deploy works
- **Output**: `.gitlab-ci.yml`, CI documentation
- **Verifier**: debugger
- **Depends on**: BD-14, UX-11

---

## ═══════════════════════════════════════════════════════
## PRIORITY EXECUTION ORDER (Critical Path to Working Website)
## ═══════════════════════════════════════════════════════

The critical path to a working website, in order (**2026-04-09 operator wave**):

```
Phase A — Tier-1/2 live volume (scraper_1 + minimal backend) — DO FIRST:
  S1-14   →  Discovery pagination (DONE_AWAITING_VERIFY — debugger promotes when ready)
  S1-15   →  Live HTTP integration (httpx, rate limits, legal gates)
  BD-11   →  Unified DB ingest path MUST be live for volume counting
  S1-18   →  NON-STOP until ≥100 listings × ≥5 tier-1/2 sources in canonical_listing

Phase B — Backend core (backend_developer) — AFTER S1-18 VERIFIED:
  BD-12   →  Shop-style filter API
  BD-13   →  User profile + auth system (remaining items)
  BD-14   →  Railway deployment
  BD-15   →  Scraper orchestration loop (production cadence)

Phase C — Debugger consolidation:
  DBG-06  →  Batch-verify all pending DONE_AWAITING_VERIFY slices
  DBG-05  →  Stage-1 + live volume quality gate

Phase D — Other scrapers (parked until S1-18 done unless unblocker):
  T3-07   →  BCPEA live scraper
  (tier-3/tier-4 expansion per TASKS)

Phase E — Frontend (ux_ui_designer):
  UX-13   →  Design system tokens
  UX-08   →  Shop view with filters
  UX-09   →  Property detail page (LUN-style)
  UX-10   →  User profile cabinet + mode switching
  UX-11   →  Vercel deployment

Phase F — Polish (all agents):
  UX-04   →  Nationwide Bulgaria LUN-style map + listings experience
  UX-07   →  3D map with buildings
  BD-08   →  Varna OSM 3D data
  UX-05   →  AI chat panel
  BD-07   →  Chat API bridge
  UX-12   →  Admin dashboard
  DBG-07  →  End-to-end smoke test
  DBG-08  →  Security audit

Phase G — Growth:
  S1-16   →  Remaining tier-2 connectors
  S1-17   →  Playwright connectors
  SM-06   →  Telegram live connector
  T3-08   →  STR analytics API
  BD-16   →  Real-time updates (SSE)
  BD-09   →  Analytics views
  BD-10   →  Photo classification
```

---

## Dependency summary (what blocks what)

```
BD-01 ──► BD-02 ──► BD-03
  │         │         │
  │         │         ▼
  │         │       UX-02 ──► UX-03
  │         │
  │         ├──► BD-04 ──► BD-13 (user auth)
  │         ├──► BD-05 ──► BD-15 (scraper loop)
  │         ├──► BD-08 (Varna OSM buildings)
  │         ├──► BD-09 (property analytics)
  │         ├──► BD-10 (photo classification)
  │         ├──► BD-11 (unified DB) ──► S1-18 (live volume) ──► BD-12 (shop filter API)
  │         │                          ──► UX-08 (shop view)
  │         │                          ──► UX-09 (detail page)
  │         └──► UX-01
  │
  ├──► S1-11 (needs DB for ingest)
  ├──► T3-02 (needs DB for STR data)
  ├──► T3-05 (needs DB for register data)
  ├──► SM-02 (needs CRM tables)
  └──► BD-14 (Railway deploy) ──► UX-11 (Vercel deploy)
                                ──► BD-15 (scraper on Railway)
                                ──► DBG-07 (E2E smoke test)

S1-01..S1-10 ──► S1-14 (discovery pagination)
               ──► S1-15 (live HTTP) ──► BD-11 ──► S1-18 (≥100×5 volume) ──► S1-16 (tier-2 expansion)
               ──► S1-12 (tier-2 stubs)
               ──► S1-13 (product-type check)
               ──► DBG-03 (audit)

S1-18 ──► DBG-06 (batch verify) / DBG-05 (stage-1 + live gate)

S1-13 ──► DBG-05 (stage-1 quality gate)
       ──► BD-06 (map/search APIs, nationwide default)
       ──► UX-04 (Bulgaria map/feed)

BD-06 ──► BD-07 (chat API) ──► UX-05 (chat panel)
      ──► BD-12 (shop filter API)
      └──► UX-04 ──► UX-07 (3D map)
                  └──► UX-05

BD-11 ──► BD-12 ──► UX-08 (shop view)
BD-13 ──► UX-10 (user profiles)
BD-14 ──► UX-11 ──► DBG-07

T3-01 ──► T3-02..T3-05 ──► T3-06 (Varna enrichment)
      ──► T3-07 (BCPEA live)
      ──► T3-08 (STR analytics)

SM-01 ──► SM-02 ──► SM-03
      ──► SM-05 ──► SM-06 (Telegram live)
      ──► SM-07 (Facebook)
                 └──► SM-04 (social-to-property mapping)

UX-13 (design system) ──► UX-08 (shop view)
                       ──► UX-09 (detail page)
                       ──► UX-10 (user profiles)
                       ──► UX-12 (admin dashboard)

LEAD-05 (monitoring) ──► ongoing, no dependencies
LEAD-06 (CI/CD) ──► BD-14, UX-11
```
