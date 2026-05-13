# Next Owner Prompts

Date: 2026-05-13

## Planner Prompt

Review DA-02 and BD-18 evidence. Keep `data_analyst` as evidence owner. Convert the handoff into executable slices for debugger, backend, infra, entity resolution, vision media, and UX. Do not touch scraped DB/corpus directly. Refresh operational dashboards and record wiki closeout.

## debugger

Verify the DA-02 / BD-18 handoff. Read `docs/exports/data-quality-deep-review-2026-05-13.md`, `docs/exports/bd18-database-review-and-correction-spec-2026-05-13.md`, `docs/dashboard/data-quality-dashboard.html`, importer code, DB models, migrations, and backend import contract tests. Run compile/tests. Confirm what is verified file-backed versus blocked DB-backed. Queue or update the next backend/infra blockers.

## backend_developer

Implement BD-18 DB tables and DB smoke import. Add first-class tables for source-publication QA review, status history, entity-resolution candidates/reviews, media descriptions, availability, viewing/inquiry requests, and external chat refs. Keep scraped import source-publication-first and accepted-only by default. Add a fixture-backed DB smoke script that proves QA evidence, listing media idempotency, and no default property/entity promotion.

## infra_db_operator

Provide a libpq-compatible `DATABASE_URL`, then run `make migrate`, `make bd18-db-smoke-import`, and `make verify-db-counts`. Record count parity or blockers. Do not reinterpret scrape quality; compare DB counts to analyst artifacts only.

## entity_resolution_agent

Design the accepted-only candidate layer. No candidate generation. Define accepted-only filters, candidate classes, score components, hard blockers, review actions, evidence snapshots, and backend/UX/debugger handoffs.

## vision_media_agent

Verify local gallery evidence before image descriptions. Use `source-item-photo-coverage.json` and DA-02 outputs only. Do not fetch remote images or generate semantic descriptions. Keep Action0 blocked until operator says `Action0 now`.

## ux_ui_designer

Consume only verified dashboard/read-model fields. File-backed data can appear in admin/operator surfaces with explicit labels. Buyer-facing views wait for accepted-only DB/read-model proof, BD-19, and debugger verification.
