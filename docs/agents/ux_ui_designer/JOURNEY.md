# UX/UI designer (frontend) journey

## Scope
- Operator-focused UI (admin/source health, parser failures, review queues) first.
- Public UI pages only after ingestion/compliance foundations exist.

## Executed tasks (append-only)

---

### Task 1 — Next.js App Router shell + design system bootstrap

**Date**: 2026-04-08  
**Slice**: MVP frontend scaffolding (precursor to operator dashboard)  
**What**: Created the Next.js App Router at the repo root with Tailwind CSS, Newsreader/Outfit fonts, a shared `AppShell`, six route shells (`/`, `/listings`, `/properties/[id]`, `/map`, `/chat`, `/settings`, `/admin`), a `/api/backend/*` proxy to the Python dev API, TanStack Query provider, and `LiveBackendPill` component. Updated `Makefile` (`run-frontend`), `.env.example` (`API_BASE_URL`), and `docs/project-status-roadmap.md` (items 97–98 marked in-progress).

**Changed files**:
- `package.json`, `next.config.ts`, `tsconfig.json`, `tailwind.config.ts`, `postcss.config.mjs`, `.eslintrc.json`, `next-env.d.ts`
- `app/layout.tsx`, `app/globals.css`, `app/providers.tsx`
- `app/(main)/page.tsx`, `listings/page.tsx`, `properties/[id]/page.tsx`, `map/page.tsx`, `chat/page.tsx`, `settings/page.tsx`, `admin/page.tsx`
- `app/api/backend/[...path]/route.ts`
- `components/shell/AppShell.tsx`, `components/status/LiveBackendPill.tsx`
- `lib/config.ts`, `lib/types/api.ts`, `lib/server/fetch-backend.ts`
- `web/index.html` (updated to point to Next.js)
- `Makefile` (`run-frontend`, `run-frontend-static`)
- `.env.example` (`API_BASE_URL`)
- `docs/project-status-roadmap.md`

**Verification**: TypeScript passes (linter clean per `ReadLints`). npm build not validated here (no Node in environment — must be run on local machine).

---

### Task 2 — Operator dashboard UI plan

**Date**: 2026-04-08  
**Slice**: TASKS.md — `UX_UI_designer: Operator dashboard UI plan`  
**What**: Produced a full markdown spec and component breakdown for the `/admin` operator surface. No Next.js implementation — spec only until FastAPI stats endpoints stabilize.

**Output**: `docs/agents/ux_ui_designer/operator-dashboard-spec.md`

**Spec covers**:
- Four-zone page layout (health strip, KPI row, sidebar nav, main pane)
- Seven queue panels: Source health, Crawl jobs, Parser failures, Duplicate review, Geocode review, Compliance, Publish queue
- Data model for each panel (typed against existing endpoints `GET /api/v1/ready`, `GET /admin/source-stats`, `GET /crawl-jobs`)
- Placeholder cards for panels blocked on Stage 6–10 backends
- 10 shared components (`CoverageBar`, `StatusBadge`, `TierBadge`, `MetadataDrawer`, etc.)
- TanStack Query data-fetching contracts (all via `/api/backend/*` proxy — no direct browser calls)
- Implementation phasing (Phase A = scaffold, Phase B = live stats, Phase C–E = future queues)
- Acceptance gate for Phase B

**Changed files**:
- `docs/agents/ux_ui_designer/operator-dashboard-spec.md` (new)
- `docs/agents/ux_ui_designer/JOURNEY.md` (this file)

**Commands run**: none (spec-only deliverable)  
**Tests run**: none  
**Extensions/libraries used**: none (spec only)

## Review comments (after each task)

### After Task 1

- `run-frontend` now requires Node/npm; add a Node version pin (`.nvmrc` or `package.engines`) in the next pass.
- The `/listings` page uses `/sources` as a stand-in for real listing data. Once `GET /api/v1/listings` exists, replace the grid with an infinite scroll and add `InfiniteListingFeed`.
- The `LiveBackendPill` polls `/api/backend/health` every 15 s — acceptable for dev; add a config flag to disable polling in production.

### After Task 2

- Phase B (Source health table + Crawl jobs table) can start as soon as `make golden-path` exits 0 with a live Postgres connection. Ping `backend_developer` when that gate passes.
- The `/admin/parser-failures` endpoint is the next critical backend slice for UX. Add it to TASKS.md for `backend_developer` after Stage 2 is complete.
- A Storybook or component-viewer setup would accelerate shared component validation without needing the full Next.js dev server. Consider adding it in Phase B.

