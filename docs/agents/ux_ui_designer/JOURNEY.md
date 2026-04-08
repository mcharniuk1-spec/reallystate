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

---

### Task 3 — UX-01 formal task completion (task-queue protocol)

**Date**: 2026-04-08  
**Slice**: `UX-01` in `docs/agents/TASKS.md`  
**What**: Completed the queue-defined operator dashboard deliverable in the required output path and moved UX-01 status to `DONE_AWAITING_VERIFY` for debugger verification.

**Changed files**:
- `docs/agents/ux_ui_designer/admin-ui-spec.md` (new, required output file)
- `docs/agents/TASKS.md` (UX-01 status set to `DONE_AWAITING_VERIFY`)
- `docs/agents/ux_ui_designer/JOURNEY.md` (this appended entry)

**Verification**:
- Confirmed output file exists at required path.
- Confirmed UX-01 task status transition recorded in `docs/agents/TASKS.md`.

**Commands run**: none  
**Tests run**: none (documentation slice)  
**Extensions/libraries used**: none

### After Task 3

- Keep `operator-dashboard-spec.md` as the deep-dive version and `admin-ui-spec.md` as the task-tracked contract file.
- Next implementation slice should remain blocked until debugger verifies API contract alignment per UX-01 acceptance gate.

---

### Task 4 — UX-02: Beta main page (map + listings + category picker)

**Date**: 2026-04-08  
**Slice**: `UX-02` in `docs/agents/TASKS.md`  
**What**: Built the beta product page — a split-view combining an interactive MapLibre GL JS map with a scrollable listing feed and category/intent filter controls, all on one screen. Uses 12 mock listings matching the `canonical_listing` API schema from `src/bgrealestate/api/routers/listings.py`.

**Design decisions**:
- **Split layout**: map takes left ~60% on desktop, listing feed takes right ~40%. On mobile they stack vertically (map 280px → listings below).
- **Filter bar**: intent toggle (All / Buy / Rent / Short-term / Auction) + search input + category picker chips (All types / Apartment / House / Studio / Villa / Penthouse / Office / Shop / Land / Garage). All client-side filtering — no API call yet.
- **Map**: MapLibre GL JS with OpenStreetMap raster tiles, bounded to Bulgaria, navigation controls. Green dot pins for each listing with coordinates. Pins scale up on card hover. Clicking a pin scrolls the listing panel to that card.
- **Listing card**: Photo placeholder (shows source name), price with intent-aware formatting (EUR/mo for rentals), location, property type, area, room count, description excerpt, source badge, relative time.
- **Bi-directional highlight**: hovering a card highlights its map pin; clicking a map pin scrolls to and highlights the card.
- **Compact header**: reduced nav height to maximize viewport for map+list content. "Beta" badge.
- **`/listings` route**: redirects to `/` (the main page IS the listings view now).
- **`/map` route**: dedicated full-screen map view with all listings.

**Changed files**:
- `lib/types/listing.ts` (new — `Listing`, `ListingIntent`, `PropertyCategory`, `CATEGORIES`, `INTENTS`)
- `lib/mock/listings.ts` (new — 12 seeded listings: Sofia, Varna, Burgas, Bansko, Plovdiv, Sozopol, Nessebar, Sunny Beach)
- `components/listings/CategoryPicker.tsx` (new — `IntentToggle` + `CategoryPicker`)
- `components/listings/ListingCard.tsx` (new — `ListingCard` with price/location/facts/badges)
- `components/listings/ListingFeed.tsx` (new — split-view orchestrator: filters + map + scrollable list)
- `components/map/MapCanvas.tsx` (new — MapLibre GL JS with dynamic markers + hover highlight)
- `components/map/FullScreenMap.tsx` (new — standalone full-screen map page)
- `app/(main)/page.tsx` (rewritten — split-view main page replacing hero landing)
- `app/(main)/listings/page.tsx` (rewritten — redirects to `/`)
- `app/(main)/map/page.tsx` (rewritten — uses `FullScreenMap`)
- `docs/agents/TASKS.md` (UX-02 status → `DONE_AWAITING_VERIFY`; UX-03 added)
- `docs/agents/ux_ui_designer/JOURNEY.md` (this entry)

**Verification**:
- Linter: zero errors across all new/changed files (`ReadLints` clean).
- Build: not validated here (no Node/npm in this environment). Must run `npm install && npm run dev` locally.
- Design: responsive layout verified by Tailwind class logic (lg: split, sm: stacked).

**Commands run**: none (no Node available in sandbox)  
**Tests run**: none (UI components; Playwright tests deferred to UX-03)  
**Extensions/libraries used**: MapLibre GL JS (already in `package.json`), Tailwind CSS, TanStack Query (provider exists; not used in feed yet — deferred to live API wiring)

## Review comments (after each task)

### After Task 4

- Mock data covers 12 listings across 8 Bulgarian locations. When live API is wired (`UX-03`), delete `lib/mock/listings.ts` and switch `ListingFeed` to `useQuery` against `/api/backend/listings`.
- The map uses OSM raster tiles — lightweight and no API key needed. Switch to a vector tile source (e.g., MapTiler or self-hosted) when the tile budget is known.
- Category/intent filters run client-side over the full array. Once live API exists, push filters as query params (`?listing_intent=sale&property_category=apartment`) to the backend and let Postgres handle it.
- Photo placeholders show source name only. Wire `image_urls[0]` to `<Image>` once the media pipeline (Stage 6) stores real thumbnails.
- The `/listings` route now redirects to `/`. If a separate listings-only view (no map) is needed later, create `/listings-only` or add a view toggle.

---

### Task 5 — UX-03: Wire listings feed to live `/listings` API + property detail page

**Date**: 2026-04-08  
**Slice**: `UX-03` in `docs/agents/TASKS.md`  
**What**: Replaced hardcoded mock data in the listings feed with a TanStack Query `useInfiniteQuery` hook that calls the live FastAPI `GET /listings` endpoint via the `/api/backend/listings` proxy. Added automatic mock-data fallback when the API is unreachable. Added IntersectionObserver-based infinite scroll. Rewrote the `/properties/[id]` page to fetch from `GET /listings/{id}` with full detail display (price box, facts grid, description, source provenance, timeline, price-per-sqm calculation). Falls back to mock lookup when API is down.

**Changed files**:
- `lib/hooks/useListings.ts` (new — `useListings` hook with `useInfiniteQuery`, mock fallback, client-side filters)
- `components/listings/ListingFeed.tsx` (rewritten — uses `useListings` hook, loading spinner, "Demo data" badge, IntersectionObserver infinite scroll sentinel)
- `app/(main)/properties/[id]/page.tsx` (rewritten — server-side fetch from `/listings/{id}`, full detail layout with price/facts/description/provenance/timeline, mock fallback, dynamic metadata)

**Design decisions**:
- API call: `GET /api/backend/listings?limit=50&offset=N` → paginated via `useInfiniteQuery` `getNextPageParam`
- Fallback: on fetch error (API unreachable), switches to full `MOCK_LISTINGS` array and shows an amber "Demo data" pill
- Infinite scroll: sentinel `<div>` at the bottom of the list, observed with `IntersectionObserver` + 200px root margin
- Property detail: server component fetches directly from Python API base URL (server-side, no CORS); falls back to mock by `reference_id` match
- Intent/category/search filters still run client-side over fetched pages (backend doesn't expose filter params yet; will push to query params when backend adds them)

**Verification**:
- Linter: zero errors on all changed files
- Build: not validated (no Node in sandbox)

**Commands run**: none  
**Tests run**: linter only  
**Extensions/libraries used**: TanStack Query (`useInfiniteQuery`), IntersectionObserver API

### After Task 5

- When backend adds `listing_intent` and `property_category` query params to `GET /listings`, push those filters server-side and remove client-side filtering for those fields.
- The property detail page uses `<img>` for `image_urls[0]`; swap to Next.js `<Image>` with width/height once media pipeline stores known dimensions.
- "Create lead" button on detail page stays disabled until CRM API (`POST /crm/threads`) exists (BD-04 dependency).
- UX-04 (Varna-scoped LUN-style experience) is next but blocked on DBG-05 + BD-06 — no work to start until those gate.
