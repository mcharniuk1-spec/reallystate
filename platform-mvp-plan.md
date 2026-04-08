# Bulgaria Real Estate Platform MVP Plan

This is the portable Cursor/Codex/Claude execution entrypoint. The full numbered plan is maintained in `PLAN.md`; this file points agents to the same source of truth and records the implementation foundation now present in the repo.

## Must-Read Files

1. `AGENTS.md`
2. `PLAN.md`
3. `deep-research-report.md`
4. `data/source_registry.json`
5. `sql/schema.sql`
6. `docs/cursor-agent-automation.md`
7. `agent-skills/*/SKILL.md`

## MVP Surfaces

1. `/listings`: scrolling apartment/listing feed.
2. `/properties/[id]`: canonical property detail with source links and photos.
3. `/map`: 2D/3D map with building grouping and fallback.
4. `/chat`: CRM chat folder with lead threads, messages, reminders, and property links.
5. `/settings`: personal info, team, API keys, connected channels, crawler and publishing settings.
6. `/admin`: source health, parser failures, duplicate/geocode/compliance review, and publishing queue.

## Source Policy

All market sources must be represented in `data/source_registry.json` with `legal_mode` and `mvp_phase`. The implementation order is tier 1 first, tier 2 after parser gates, tier 3 through official/vendor/partner routes, and tier 4 as lead-intelligence overlays only.

## Current Implementation Slice

This repo now includes:
- source registry with all documented source groups
- Cursor rules and agent setup files
- portable agent skill specifications
- Mermaid architecture source
- schema foundation for ingestion, property graph, CRM, users, map, and publishing

The next implementation slice should be persistence/migrations and a fixture-backed `Homes.bg` connector.
