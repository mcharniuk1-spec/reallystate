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
| `runtime-compliance-evaluator` | Enforce legal/risk/access gates at runtime |
| `db-sync-and-seeding` | Sync `data/source_registry.json` into PostgreSQL |
| `debugger-golden-path` | Migrate → sync → fixture ingest → stats → XLSX (optional DB) |
| `skill-discovery` | Discover/create project skills and avoid duplication |
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

Every agent should state the skills used in its closeout.
