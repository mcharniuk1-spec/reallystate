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

Every agent should state the skills used in its closeout.
