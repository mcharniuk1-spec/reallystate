# Agent Skills Index

Canonical skill files live under `agent-skills/<skill-name>/SKILL.md`.

| Skill | Primary Use |
| --- | --- |
| `real-estate-source-registry` | Source inventory, tiering, legal mode, MVP phase |
| `scraper-connector-builder` | One connector at a time, legal-gated, fixture-backed |
| `parser-fixture-qa` | Offline fixtures and parser regression suite |
| `postgres-postgis-schema` | Database schema, indexes, migrations, repositories |
| `workflow-runtime` | Temporal workflows, scheduler, retries, idempotency |
| `dedupe-entity-resolution` | Property/contact/media duplicate scoring and review |
| `geo-map-3d` | Geocoding, building matching, 2D/3D map APIs |
| `crm-chat-inbox` | Lead threads, messages, reminders, templates, channel adapters |
| `publishing-compliance` | Channel capabilities, dry-run publishing, compliance blocks |
| `frontend-pages` | `/listings`, `/properties/[id]`, `/map`, `/chat`, `/settings`, `/admin` |
| `docs-export` | Markdown, Mermaid, DOCX, PDF exports |
| `qa-review-release` | Tests, gates, release checks, step reports |
| `daily-orchestration` | Daily review, roadmap alignment, slicing for agents |
| `stage1-scrape-control-plane` | Passive scrape queue/control-plane setup plus operator-approved Varna and all-Bulgaria full scrape runners |
| `runtime-compliance-evaluator` | Enforce legal/risk/access gates at runtime |
| `db-sync-and-seeding` | Sync `data/source_registry.json` into PostgreSQL |
| `debugger-golden-path` | Migrate → sync → fixture ingest → stats → XLSX (optional DB) |
| `skill-discovery` | Discover/create project skills and avoid duplication |
| `browser-scrape-ops` | Browser tracing, JS pagination mapping, and Playwright recovery planning |
| `hybrid-scrape-stack` | Layered scraper design from HTTP-first extraction through replay and managed fallback |
| `image-media-pipeline` | Download, validate, analyze, and compress listing media safely |
| `managed-scrape-platforms` | Evaluate Browserbase, Firecrawl, and Zyte as escalation layers |
| `postgres-ops-psql` | Practical `psql` operations for exports, bulk loads, and ingest verification |
| `universal-agent-scrape-setup` | Shared Codex/Claude scrape runtime, env, and agent-role setup |
| `openclaw-ollama-gemma4` | OpenClaw local-model role: offline QA, SQL drafting, and report drafting via Ollama |
| `fullstack-coding` | End-to-end coding across scraper/backend/API/UI contracts |
| `backend-data-engineering` | Data pipelines, persistence reliability, and reporting aggregates |
| `ux-dashboard-design` | Operator dashboard UX for source health and stage progress |
| `visual-3d-map` | 2D/3D map visualization behavior and graceful fallbacks |
| `software-architecture` | Architecture boundaries, dependency direction, and execution sequencing |
| `subagent-driven-development` | Parallel subagent dispatch, checkpoints, and verifier handoffs |
| `claude-opus-planner` | Planning policy: use Opus-level reasoning for architecture/plans |
| `deep-research-workflow` | Evidence-backed source/legal/technical research workflow |
| `postgres-analysis` | PostgreSQL schema/query/index diagnostics and reporting SQL reviews |
| `wordpress-development` | WordPress theme/plugin/REST/security implementation workflow |
| `web-frontend-nextjs` | Next.js/React UI execution and API-contract-first component flow |
| `dashboard-visual-ops` | KPI/kanban/operator dashboard visual design and drill-down behavior |
| `web-performance-accessibility` | Frontend performance and accessibility quality checks |
| `investor-pitch-yc` | Y Combinator style investor narrative and slide flow |
| `presentation-pdf-reportlab` | Polished PDF slide deck generation with layout QA |
| `presentation-powerpoint-pptx` | Microsoft PowerPoint deck generation using python-pptx |
| `google-slides-handoff` | Google Slides import readiness and collaboration handoff |
| `project-progress-dashboard-web` | Full-flow project progress dashboard enhancement |
| `context-engineering` | Context window management and progressive disclosure for agent prompts |
| `prompt-engineering` | Systematic prompt design with Anthropic best practices |
| `multi-agent-patterns` | Supervisor, peer, and hierarchical multi-agent coordination patterns |
| `test-generator` | Fixture-first test generation for connectors, APIs, and pipelines |
| `security-audit` | Security audit checklist: legal gates, secrets, injection, compliance |
| `vercel-nextjs-deploy` | Vercel deployment for Next.js frontend applications |
| `railway-deploy` | Railway deployment for Python backend with PostgreSQL and workers |
| `ci-cd-pipeline` | CI/CD pipeline design with lint, typecheck, test, and deploy stages |
| `agent-architecture-governance` | Multi-agent ownership, prompt-to-slice conversion, verifier loops, and dependency control |
| `ops-release-management` | Safe git staging, secret scans, commits, pushes, release notes, and rollback handoffs |
| `infra-db-migration` | PostgreSQL/PostGIS backup, restore, transfer, and count verification for server migration |
| `market-intelligence` | Market/rival analysis, source prioritization, pricing/supply signals, and product implications |
| `user-analytics-instrumentation` | Privacy-safe event taxonomy, funnels, UX telemetry, and analytics dashboards |

Every agent should state the skills used in its closeout.

## Role-to-Skill Mapping

| Agent | Core Skills |
| --- | --- |
| `planner` | `agent-architecture-governance`, `software-architecture`, `subagent-driven-development`, `context-engineering`, `prompt-engineering` |
| `ops_release_manager` | `ops-release-management`, `qa-review-release`, `security-audit`, `ci-cd-pipeline` |
| `infra_db_operator` | `infra-db-migration`, `postgres-ops-psql`, `postgres-postgis-schema`, `railway-deploy` |
| `backend_developer` | `backend-data-engineering`, `postgres-postgis-schema`, `workflow-runtime`, `fullstack-coding` |
| `data_analyst` | `postgres-analysis`, `dashboard-visual-ops`, `test-generator` |
| `market_intelligence_analyst` | `market-intelligence`, `deep-research-workflow` |
| `user_analytics_agent` | `user-analytics-instrumentation`, `dashboard-visual-ops`, `web-performance-accessibility` |
| `scraper_1` | `scraper-connector-builder`, `browser-scrape-ops`, `hybrid-scrape-stack`, `parser-fixture-qa`, `runtime-compliance-evaluator` |
| `scraper_sm` | `publishing-compliance`, `runtime-compliance-evaluator`, `deep-research-workflow`, `scraper-connector-builder` |
| `vision_media_agent` | `image-media-pipeline`, `managed-scrape-platforms` |
| `entity_resolution_agent` | `dedupe-entity-resolution`, `postgres-analysis` |
| `ux_ui_designer` | `web-frontend-nextjs`, `frontend-pages`, `geo-map-3d`, `visual-3d-map`, `web-performance-accessibility` |
| `debugger` | `debugger-golden-path`, `qa-review-release`, `security-audit`, `test-generator` |
| `knowledge_context_agent` | `context-engineering`, `docs-export`, `skill-discovery` |
