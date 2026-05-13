# All-Agent Execution Plan

Generated: 2026-05-13 14:22:31Z

## Critical Path

- FACT: `data_analyst` owns current Action1 evidence and dashboard denominator truth.
- INTERPRETATION: execute `DA-02`/`DA-03` before public dashboard claims, then `BD-18`/`BD-19`, then `INFRA-02`, then UX/admin/public surfaces.
- GAP: DB-backed proof and operator-gated media execution remain unavailable.

## Agent Next Actions

### Planner

- `PLAN-03` (DONE_AWAITING_VERIFY): Self-development architecture rebuild — Keep existing core lanes: planner, backend_developer, data_analyst, scraper_1, scraper_sm, ux_ui_designer, debugger.; Add support lanes: ops_release_manager, infra_db_operator, market_intelligence_analyst, user_analytics_agent, vision_media_agent, entity_resolution_agent, knowledge_context_agent.; Define constant vs triggered cadence and review loop.
- `CONST-01` (TODO): Activation sync + dashboard refresh — latest run updates TASKS.md, docs/exports/operational-dashboards.json, and dashboard HTML timestamps; if full make dashboard-doc is blocked by corpus scan performance, run the operational dashboard generator and keep DA-03 blocker visible.
- `CONST-02` (TODO): Cross-agent note propagation — each blocker has at least one mapped follow-up slice with dependency, and scraper-facing follow-ups keep the full-item/full-gallery requirement visible
- `PLAN-01` (DONE_AWAITING_VERIFY): Agent reset and OpenClaw Action1 control reset — Keep exactly these active lanes: planner, backend_developer, data_analyst, scraper_1, scraper_sm/S&M, ux_ui_designer, debugger.; Keep scraper_t3 historical only; move new tier-3 work into S&M.; Ensure OpenClaw reads Action0 + Action1 + Action2 but executes only the operator-approved next action.

### Backend Developer

- `BD-04` (DONE_AWAITING_VERIFY): Auth / RBAC on CRM and listings routes — unauthenticated requests return 401/403; make test passes with auth fixtures
- `BD-05` (DONE_AWAITING_VERIFY): Temporal workflow wiring — jobs survive worker restart; cursors persist; make test passes
- `BD-06` (TODO): Map/search + chat context APIs (geo scope configurable) — API contract tests prove (a) default/nationwide listing queries return Bulgaria-wide results when data exists, (b) optional Varna scope filter works when requested, (c) chat context returns selected property + active filters
- `BD-07` (TODO): AI chat API bridge for property-aware search assistant — chat endpoint returns responses that include referenced property IDs and active filter echo; tests cover fallback/error states

### Data Analyst

- `DA-03` (TODO): Dashboard source/photo coverage generator performance repair — make dashboard-doc completes without manual kill, or a documented fast dashboard target exists for task/JOURNEY-only changes.
- `DA-04` (TODO): Four-dashboard denominator certification — Certify which dashboard counts are file-backed audit counts, quality-gate counts, scrape-status operational counts, importer default candidates, or future DB counts.; Add a short denominator note for every Properties Database dashboard metric that can be misread as accepted property count.; Reconcile source-level differences between DA audit, action1 quality gate, and scrape-status export; preserve unresolved overlap as explicit GAP, not hidden adjustment.

### Scraper 1

- `S1-11` (DONE_AWAITING_VERIFY): Live-safe ingestion runner (small) — stats endpoints reflect the inserted record; make golden-path still passes
- `S1-13` (DONE_AWAITING_VERIFY): Stage-1 scraping completion check (all product types) — matrix report exists and make test passes with product-type coverage assertions
- `S1-14` (DONE_AWAITING_VERIFY): Discovery pagination for ALL tier-1 sources — Implement parse_discovery_html() / parse_discovery_json() for every tier-1 source that doesn't already have it:; OLX.bg: paginate API search results (page parameter in API URL); alo.bg: HTML pagination with next-page link
- `S1-15` (IN_PROGRESS): Live HTTP integration for tier-1 connectors — Implement httpx-based live fetch in HtmlPortalConnector.fetch_url() with:; User-Agent rotation (realistic browser UAs); Rate limiting (configurable per source, default 1 req/2sec)

### S&M / Social + Vendor

- `SM-00` (DONE_AWAITING_VERIFY): S&M mission consolidation and OpenClaw monitor handoff — Treat tier-3 partner/vendor/official and tier-4 social/messenger work as one S&M intelligence lane.; Keep all private/social/messenger scraping consent-gated; no private groups, DMs, unofficial sessions, or KYC/CAPTCHA bypass.; While Action1 runs, S&M may monitor reports and prepare QA/rescrape prompts, but must not widen Action1 source scope.
- `SM-02` (DONE_AWAITING_VERIFY): Telegram public channel connector (fixture-first) — make test passes; fixtures contain redacted posts; no live Telegram calls
- `SM-03` (DONE_AWAITING_VERIFY): X (Twitter) public monitor connector (fixture-first) — make test passes; no live API calls
- `SM-04` (TODO): Social lead-to-property mapping for AI chat context — fixture-backed mapping examples pass tests; no live social calls

### Scraper T3 (historical)

- `T3-02` (DONE_AWAITING_VERIFY): AirDNA / Airbtics licensed data importer (fixture-first) — make test passes; no live vendor API calls in tests; fixture contains realistic STR metrics
- `T3-03` (DONE_AWAITING_VERIFY): BCPEA property auctions connector (fixture-first) — make test passes; no live network in tests; legal gates enforced
- `T3-04` (DONE_AWAITING_VERIFY): Partner feed stub connectors (Airbnb/Booking.com/Vrbo) — make test passes; connector raises PartnerContractRequired on live calls; fixtures demonstrate expected feed structure
- `T3-05` (DONE_AWAITING_VERIFY): Official register query wrappers (Property Register / KAIS Cadastre) — make test passes; no automated queries without operator consent; fixtures contain redacted sample responses

### UX/UI Designer

- `UX-02` (DONE_AWAITING_VERIFY): Beta main page — map + listings + category picker — page loads with mock/seeded data; category/intent filters work; map renders with pins; responsive mobile stacking
- `UX-03` (DONE_AWAITING_VERIFY): Wire listings feed to live /listings API — page fetches from FastAPI; pagination works; fallback to mock if API unreachable
- `UX-04` (TODO): Nationwide Bulgaria LUN-style map + listings experience — prototype demonstrates Bulgaria-wide browse (no hard-coded Varna-only lock), map filters + listing cards + synchronized selection; spec calls out optional Varna shortcut vs default nationwide
- `UX-05` (TODO): AI chat panel with property/map-aware context — chat can reference current property card + filtered map state

### Debugger

- `DBG-13` (TODO): Verify Plan 13.05 architecture reset and release gate — unsafe files are absent from staged diff; role docs and task board have clear owners/verifiers; dashboard refresh blocker is recorded as DA-03 if unresolved.
- `DBG-05` (TODO): Verify stage-1 scraping before expanding 3D / building-depth geo — required product types covered per coverage doc; golden path passes; live volume report meets S1-18 thresholds or waiver is documented
- `DBG-08` (TODO): Verify Codex tier-1/2 quality audit and Gemma readiness — Action0 has report-or-skip coverage for every eligible row; Action1 has attempted all seven sources in all four buckets with saved/skipped/error counts; every high-priority source gap has a fix, test, blocker, or queued Action2 follow-up; no ambiguous Varna-only instruction remains.
- `DBG-06` (TODO): Verify all pending DONE_AWAITING_VERIFY slices (batch 2) — BD-04 (Auth/RBAC): test 401/403 responses, API key scope enforcement; BD-05 (Temporal): verify worker/scheduler stubs, test restart behavior; S1-11 (Ingestion runner): run fixture ingest, check DB round-trip

### Ops Release Manager

- `OPS-01` (DONE_AWAITING_VERIFY): Safe git push gate for Plan 13.05 — Unstage unsafe existing index entries without modifying working files.; Stage only safe code/docs/config/skills/runbooks.; Exclude secrets, raw capture dirs, DB dumps, runtime logs, OpenClaw state, and unreviewed large scraped corpus.
- `OPS-02` (DONE_AWAITING_VERIFY): Data-analysis-driven release gate checklist — Treat data_analyst as the evidence owner for accepted/LOST/grouped/media/dashboard counts; release notes must cite reproducible artifact paths, not chat summaries.; Require DA-02 dashboard denominator semantics before any public count claim, and DA-03 or an explicit dashboard-refresh blocker note before broad validation claims.; Block DB-backed release claims until BD-18 import/schema alignment and INFRA-02 DB count verification succeed with a real DATABASE_URL / REMOTE_DATABASE_URL.

### Infra DB Operator

- `INFRA-01` (DONE_AWAITING_VERIFY): Server and DB migration readiness — Prepare backup/restore/count verification commands.; Document server prerequisites and provider recommendation.; Define transfer/restore/rollback steps.
- `INFRA-02` (BLOCKED): DB count verification execution gate — Once DATABASE_URL / REMOTE_DATABASE_URL exist, run backup/restore/count verification without committing dumps or runtime logs.; Compare DB counts with the latest data_analyst accepted/LOST/grouped/media artifacts.; Record mismatches as blockers for BD-18 or DA-02; do not reinterpret scrape quality.

### Market Intelligence

- `MI-01` (DONE_AWAITING_VERIFY): Weekly market and rival intelligence baseline — report separates FACT / INTERPRETATION / HYPOTHESIS / GAP and maps recommendations to planner tasks.
- `MI-02` (TODO): Next weekly market review scorecard — Build a weekly source scorecard from accepted-only evidence: source family, legal/access mode, website-total basis, landed rows, accepted rows, grouped rows, LOST rows, media/description coverage, city/district coverage, price-status coverage, and product role.; Identify strategic supply gaps by geography, intent, property type, and source family without using raw scraped volume as a market fact.; Separate marketable claims from internal hypotheses and blocked data needs.

### User Analytics

- `UA-01` (DONE_AWAITING_VERIFY): Website analytics event taxonomy — no PII-bearing payloads; frontend/backend tasks are explicit.
- `UA-02` (TODO): Privacy-safe instrumentation implementation plan — After account/chat/admin/read-model contracts stabilize, freeze the event dictionary, payload allowlists, sampling/debounce rules, retention windows, and dashboard metrics.; Confirm UX events use derived fields only: no raw search text, raw chat text, emails, phones, names, source URLs, IPs, user agents, tokens, or admin private notes.; Map each event to an owner component/API and a debugger verification fixture.
- `UA-03` (TODO): Product analytics dashboard contract — dashboard spec includes metric definitions, required events, denominator rules, privacy constraints, and example SQL/API query shapes using only first-party event data.

### Vision Media

- `VM-01` (DONE_AWAITING_VERIFY): Vision media agent readiness — Convert data analyst media gaps into semantic media QA tasks: gallery completeness, scene/room coverage, condition, equipment, style, photo-text consistency, and uncertainty.; Define the visual evidence threshold for buyer-facing display and stronger property promotion.; Define Action0 queue rules without running image processing; use only local files after operator Action0 now.
- `VM-02` (BLOCKED): Action0 semantic media QA execution queue — After operator Action0 now, process only rows from s1-21-gemma-action0-eligible.json or a debugger/data_analyst-approved successor queue.; Use only local_image_files; no remote fetch or gallery backfill inside semantic reporting.; Write one JSON and one Markdown report per property under docs/exports/property-image-reports/<source_key>/.
- `VM-03` (TODO): Visual evidence promotion gate — Turn the readiness report thresholds into product/DB/API fields: visual_evidence_status, semantic_report_status, missing_scene_warnings, human_review_required, and visual_promotion_blockers.; Separate buyer-facing display from promoted/enriched property use; promoted use needs a complete semantic report, not only local photos.; Keep grouped/development, LOST, inactive, pending-QA, partial-gallery, and no-report rows out of promoted property sets.
- `VM-04` (TODO): Media QA dashboard handoff — Define dashboard metrics for media capture completeness and semantic report completeness separately.; Track per-source/per-bucket counts for accepted rows with full local gallery, partial gallery, unreadable/duplicate images, semantic report complete, semantic report skipped, and human-review required.; Ensure source-item-photo-coverage.json is not used as the accepted-row denominator until DA-02 reconciles stored status vs quality-gate status.

### Entity Resolution

- `ER-01` (DONE_AWAITING_VERIFY): Conservative entity-resolution queue plan — grouped/development publications cannot be auto-merged as single units; plan states no property_entity / property_offer promotion in ER planning; follow-up slices depend on BD-18/BD-19 accepted source-publication evidence.
- `ER-02` (DONE_AWAITING_VERIFY): Accepted-only duplicate candidate extraction contract — Define the exact accepted-only input query for source publications: SCRAPED_OK, accepted/single-entity state, not grouped/development, not LOST, not inactive/removed/expired, not pending/missing QA, and registry-backed source provenance.; Define candidate blocking keys and pair generation for exact source duplicates, strong cross-source same-unit candidates, weak same-building/project candidates, and conflict candidates.; Keep output as candidate rows/evidence only; do not create or update property_entity, property_offer, public /properties results, or buyer-facing labels.
- `ER-03` (TODO): Evidence scoring and case-classification matrix — Define score components for source URL/id, city/district/address/building/project, area, price/price-status, rooms/floor/unit clues, contacts, photo overlap, media counts, and lifecycle dates.; Define hard blockers that override any score: grouped/development, unknown QA state, inactive, LOST, same-source non-exact records, zero-price-as-real-price, contradictory area/price/media/unit evidence.; Separate review labels: single_unit, grouped_or_development, unknown, source_duplicate, same_unit_candidate, same_complex_only, and conflicting_evidence.
- `ER-04` (TODO): Source-publication relationship and conflict review policy — Define lifecycle for candidate review actions: link, dismiss, defer, mark_conflict, needs_unit_split, and needs_parser_repair.; Define audit fields for who/when/why plus immutable evidence snapshot.; Hand UX the operator-side wording for duplicate/confidence/provenance review without buyer-facing claims.

### Knowledge Context

- `KCA-01` (DONE_AWAITING_VERIFY): Data-analyst evidence capture and wiki closeout — Create a wiki run record for the data-analyst-centered loop after the current analyst/debugger outputs are stable.; Update project log, memory, and insights under the strict filters only.; Update docs/reporting index if a new durable artifact becomes source-of-truth.
- `KCA-02` (TODO): Four-dashboard knowledge capture — Record the four-dashboard operating model as a wiki run after debugger verifies PLAN-06.; Update project log and insights only for reusable conclusions: dashboard role split, accepted-only evidence chain, and verifier queue hygiene.; Update memory only if the dashboard/denominator blocker is a repeating future-run constraint.

### Lead Agent

- `LEAD-05` (TODO): Dashboard monitoring + architecture refresh (recurring) — Read all JOURNEY.md files — identify progress since last check; Update docs/exports/progress-dashboard.json with current slice statuses; Run make dashboard-doc to regenerate dashboard HTML
- `LEAD-07` (DONE_AWAITING_VERIFY): OpenClaw/Gemma run analysis and next-run preparation — analysis doc exists; S1-21, S1-22A, S1-22B, S1-22C, and DBG-08 are queued; website can show scraped items with media/quality metadata; dashboards are regenerated.
- `LEAD-06` (TODO): GitLab CI/CD pipeline setup — Create .gitlab-ci.yml with stages: lint → test → build → deploy; Lint stage: make lint + make typecheck; Test stage: make test + make golden-path (with PostgreSQL service container)
