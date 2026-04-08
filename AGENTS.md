# Bulgaria Real Estate MVP Agent Instructions

This repository is the foundation for a Bulgaria real estate ingestion, map, CRM, and publishing MVP. Extend the existing scaffold; do not replace it wholesale.

## Mission

- Build source-first ingestion for Bulgarian portals, agencies, STR/vendor channels, official registers, and lead-intelligence overlays.
- Normalize all listings into one canonical real estate model with photos, descriptions, contacts, geospatial links, and lifecycle events.
- Add a map/search MVP with `/listings`, `/properties/[id]`, `/map`, `/chat`, `/settings`, and `/admin`.
- Add reverse publishing only through official, authorized, partner, vendor, or assisted-manual routes.

## Hard Guardrails

- Use `data/source_registry.json` as the authoritative source matrix.
- Enforce `legal_mode`, `risk_mode`, and `access_mode` before implementing any connector or publishing adapter.
- Do not add unsafe broad scraping for Airbnb, Booking.com, WhatsApp, Viber, private Facebook groups, or private Telegram groups.
- Do not automate mass account creation, KYC bypass, CAPTCHA bypass, or private-account access.
- Do not add live-network dependencies to tests; crawler tests must use fixtures.
- Do not start public UI work until ingestion, CRM, compliance, and operator review foundations exist.
- **Agent skills are version-controlled deliverables**: any new or updated skill must be saved under `agent-skills/<name>/SKILL.md` and included in the same change set as the code/docs it enables (so other agents can use it when the repo is cloned).
- If a Linear issue key is present in the task or branch context, keep implementation and status notes aligned with that issue.
- If Linear tools are unavailable in the session, use `docs/linear-integration.md` and `docs/exports/linear-import-roadmap.csv` as the fallback project-management source.

## Files To Read First

- `PLAN.md`
- `platform-mvp-plan.md` if present
- `deep-research-report.md`
- `data/source_registry.json`
- `sql/schema.sql`
- `README.md`
- `docs/linear-integration.md`
- `src/bgrealestate/*`
- `tests/*`

## Required Step Output

Every Cursor/Codex/Claude step must end with:

```text
Changed files:
Agent tools used:
Skills used:
Extensions/libraries used:
Commands run:
Tests run:
Outputs produced:
Risks / blockers:
Progress update:
Next step:
```

## Phase Gates

- Phase 1: docs, rules, source registry, and agent skills are present.
- Phase 2: persistence/migrations are working before live connectors.
- Phase 3: one connector is fixture-tested before adding more connectors.
- Phase 4: at least three tier-1 sources work end-to-end before tier-2 expansion.
- Phase 5: dedupe, geospatial confidence, and compliance gates exist before public UI.
- Phase 6: CRM and operator/admin workflows exist before launch.
- Phase 7: reverse publishing uses only official/authorized/vendor/assisted workflows.
