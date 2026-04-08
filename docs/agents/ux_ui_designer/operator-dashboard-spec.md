# Operator Dashboard UI Plan

**Slice**: Operator dashboard UI plan  
**Status**: Delivered — design spec only. Next.js implementation blocked until FastAPI stats endpoints stabilize.  
**Date**: 2026-04-08  
**Author**: ux_ui_designer agent

---

## 1. Design intent

The `/admin` surface is for **operators only** — people running the ingestion platform, not end-users browsing listings. Every decision should optimise for:

- **Rapid triage**: know at a glance which sources are broken or stale.
- **Drill-down without leaving the page**: expand rows inline; open side drawers; do not navigate away unless necessary.
- **Actionability over decoration**: each number has a linked action (retry, suppress, review, export).
- **Low visual weight**: the design tokens from the app shell (paper/sea/line palette, Outfit + Newsreader fonts) carry over; no additional libraries needed.

Public-facing listing/map/CRM pages are **out of scope** here per `AGENTS.md` phase gates.

---

## 2. Page-level layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  Header: AppShell nav (Operator context badge, no public links)     │
├─────────────────────────────────────────────────────────────────────┤
│  [A] Status bar  — system health strip (Postgres / Redis / API)     │
├─────────────────────────────────────────────────────────────────────┤
│  [B] Metrics row — 4 summary KPI cards                              │
├──────────────────────┬──────────────────────────────────────────────┤
│  [C] Left sidebar    │  [D] Main pane — active queue/table          │
│  Tab nav (6 queues)  │                                              │
│                      │  Switches based on sidebar selection         │
│  · Source health     │                                              │
│  · Crawl jobs        │                                              │
│  · Parser failures   │                                              │
│  · Duplicate review  │                                              │
│  · Geocode review    │                                              │
│  · Compliance        │                                              │
│  · Publish queue     │                                              │
└──────────────────────┴──────────────────────────────────────────────┘
```

The sidebar is collapsible to an icon strip on small viewports (md breakpoint).  
The main pane stacks below on mobile.

---

## 3. Zone A — System health strip

A full-width horizontal bar pinned beneath the app header. Always visible.

### Data model

Source: `GET /api/v1/ready`

```ts
type ReadyCheck = {
  name: "postgres" | "redis";
  ok: boolean | null;  // null = env var not set
  detail: string;
};

type ReadyPayload = {
  status: "ok" | "degraded";
  checks: ReadyCheck[];
};
```

### Components

| Component | Description |
|---|---|
| `SystemHealthStrip` | Container bar, green/amber/red background tint |
| `HealthPill` | One pill per check: dot + label + detail on hover |
| `ApiVersionBadge` | Shows `version` from `GET /` or package constant |

### States

- **ok** (all checks pass) — sea-green tint, "All systems operational"
- **degraded** (≥1 check failed) — amber tint, lists failing service names
- **unconfigured** (ok = null) — mist tint, "DATABASE_URL not set — run make dev-up"

### Refresh

Poll every 30 s via TanStack Query `refetchInterval`. No WebSocket needed at this stage.

---

## 4. Zone B — Metrics row (4 KPI cards)

Source: `GET /admin/source-stats` (aggregated)

```ts
type SourceStatRow = {
  source_name: string;
  canonical_listings: number;
  raw_captures: number;
  with_description: number;
};

type SourceStatsPayload = {
  ok: boolean;
  count: number;
  rows: SourceStatRow[];
};
```

Derived metrics for KPI cards:

| Card | Calculation | Icon |
|---|---|---|
| **Active sources** | `count` from `/admin/source-stats` | pulse dot |
| **Canonical listings** | `sum(canonical_listings)` | list icon |
| **Raw captures** | `sum(raw_captures)` | database icon |
| **With description** | `sum(with_description)` | text icon |

### Component

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  44          │  │  1,204       │  │  3,820       │  │  876         │
│  Sources     │  │  Canonical   │  │  Captures    │  │  Described   │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

`MetricsRow` → four `KpiCard` instances. Each card shows:
- Large numeral (font-display, 36px)
- Label (text-mist, uppercase, 11px)
- Delta badge (future: compares to 24 h ago)

---

## 5. Zone C — Sidebar queue nav

Seven items. Each item shows:
- Icon (18px, outlined)
- Label
- Badge count (red if non-zero errors/items)

```
  [●] Source health        44
  [↻] Crawl jobs           12
  [⚠] Parser failures       3
  [⊙] Duplicate review      0
  [◎] Geocode review        0
  [⛔] Compliance            1
  [↑] Publish queue         0
```

Badge counts come from the same stat payloads (initially hardcoded to 0 for queues without live data).

Active item gets `border-l-2 border-sea bg-sea/5` highlight. Non-active items are plain text-mist.

---

## 6. Zone D — Queue panels (main pane)

### 6.1 Source health panel

**API**: `GET /admin/source-stats`  
**Default sort**: `canonical_listings DESC`

#### Layout

- **Filter bar** (top): tier selector (all / 1 / 2 / 3 / 4), risk mode selector, search box for source name.
- **Table** below.

#### Table columns

| Column | Field | Notes |
|---|---|---|
| Source | `source_name` | Bold, links to source URL |
| Tier | derived from registry | Tier badge pill |
| Canonical | `canonical_listings` | Numeric |
| Raw captures | `raw_captures` | Numeric |
| Coverage bar | `with_description / canonical_listings` | `CoverageBar` component (see §7) |
| Legal | from registry | `legal_mode` pill |
| Risk | from registry | `risk_mode` pill |
| Actions | — | "Sync", "View jobs" buttons |

#### Source data enrichment

The source registry data (`tier`, `legal_mode`, `risk_mode`, `access_mode`) is available client-side from `GET /sources` (dev API) or `GET /api/v1/sources` (FastAPI, to be added). Join by `source_name`.

#### Empty state

"No sources loaded. Run `make dev-up && make db-init && make validate` then re-check `DATABASE_URL`."

---

### 6.2 Crawl jobs panel

**API**: `GET /crawl-jobs?limit=50&offset=0`

```ts
type CrawlJob = {
  job_id: string;
  source_name: string;
  endpoint_id: string | null;
  job_type: string;
  status: "pending" | "running" | "success" | "failed" | "retrying";
  priority: number;
  scheduled_for: string | null;
  started_at: string | null;
  finished_at: string | null;
  attempt_count: number;
  cursor_key: string | null;
  idempotency_key: string | null;
  metadata: Record<string, unknown>;
};
```

#### Layout

- **Filter bar**: status filter (all / pending / running / failed), source name search, date range picker.
- **Table** with pagination (50 per page, load-more).

#### Table columns

| Column | Field | Notes |
|---|---|---|
| Job ID | `job_id` | Monospace, truncated, copy button |
| Source | `source_name` | — |
| Type | `job_type` | Pill |
| Status | `status` | `StatusBadge` (see §7) |
| Attempts | `attempt_count` | Number; amber if > 1, red if > 3 |
| Scheduled | `scheduled_for` | Relative time |
| Duration | `finished_at - started_at` | "—" if not finished |
| Actions | — | "Retry" (POST /crawl-jobs/{id}/retry), "Inspect" |

"Retry" button is disabled if status ≠ `failed`. "Inspect" opens metadata drawer.

#### Metadata drawer

Slides in from the right. Shows raw `metadata` JSON in a scrollable `<pre>` block plus all timestamps formatted as local datetime.

---

### 6.3 Parser failures panel

**API**: pending — `GET /admin/parser-failures` not yet implemented.

#### Placeholder state

Show a card: "Parser failure API not available yet. Tracked via [`docs/project-status-roadmap.md`]."

#### Target design (for when endpoint exists)

Fields expected:
```ts
type ParserFailure = {
  failure_id: string;
  source_name: string;
  raw_capture_id: string;
  error_type: string;
  error_message: string;
  captured_at: string;
  fixture_path: string | null;
};
```

Table columns: Source, Error type, Error message (truncated, expand on click), Capture ID (link), Fixture (if saved).

Inline action: "Save as fixture" → writes to `tests/fixtures/<source>/` path via backend.

---

### 6.4 Duplicate review queue

**API**: pending — dedupe graph not yet implemented.

#### Placeholder state

Card: "Dedupe graph ships in Stage 6. This queue will show property pairs with confidence < 0.9 awaiting manual merge/split decisions."

#### Target design fields

```ts
type DuplicateCandidate = {
  candidate_id: string;
  property_a_id: string;
  property_b_id: string;
  confidence: number;       // 0.0–1.0
  signals: string[];        // ["address", "phone", "area"]
  status: "pending" | "merged" | "split" | "dismissed";
};
```

Table: confidence bar, signals chips, side-by-side mini-cards for the two properties, Merge / Split / Dismiss actions.

---

### 6.5 Geocode review queue

**API**: pending — geo enrichment not yet implemented.

#### Placeholder state

Card: "Geocode/building review ships in Stage 7. This queue will list listings with geocode confidence < 0.7 needing manual address correction."

#### Target design fields

```ts
type GeoReviewItem = {
  listing_id: string;
  raw_address: string;
  geocoded_lat: number | null;
  geocoded_lon: number | null;
  confidence: number;
  suggested_address: string | null;
};
```

Actions: "Accept suggestion", "Set manually" (opens address editor with map pin), "Skip".

---

### 6.6 Compliance panel

**API**: pending — `GET /admin/compliance-flags` not yet implemented.

#### Placeholder state

Card: "Compliance gate API ships alongside legal-mode enforcement. This queue shows sources or jobs that tripped a `legal_mode` or `risk_mode` blocker."

#### Target design fields

```ts
type ComplianceFlag = {
  flag_id: string;
  source_name: string;
  flag_type: "legal_mode_blocked" | "risk_mode_blocked" | "access_violation" | "manual";
  reason: string;
  raised_at: string;
  resolved: boolean;
};
```

Table: Source, Flag type (color-coded pill), Reason, Raised at, Status. Action: "Acknowledge" / "Suppress (24 h)".

---

### 6.7 Publish queue

**API**: pending — publishing control plane not yet implemented.

#### Placeholder state

Card: "Publish queue ships in Stage 10. Only official, authorized, or assisted-manual routes will appear here."

#### Target design fields

```ts
type PublishJob = {
  publish_job_id: string;
  source_listing_id: string;
  channel: string;
  status: "pending" | "dry_run" | "published" | "failed" | "blocked";
  block_reason: string | null;
  created_at: string;
  last_attempt_at: string | null;
};
```

Table: Channel, Listing, Status, Block reason (if any), Actions: "Run dry-run", "Publish" (disabled until dry-run passes).

---

## 7. Shared components

| Component | Props | Description |
|---|---|---|
| `CoverageBar` | `value: number` (0–1), `label?: string` | Slim progress bar; green >0.8, amber 0.4–0.8, red <0.4 |
| `StatusBadge` | `status: string`, `colorMap` | Pill with dot; maps status strings to color tokens |
| `TierBadge` | `tier: 1\|2\|3\|4` | Pill: Tier 1 = sea, Tier 2 = sand, Tier 3/4 = mist |
| `RiskBadge` | `risk: string` | Color coded: low = sea, medium = sand, high = warn |
| `LegalBadge` | `legal: string` | Pill per legal_mode value |
| `RelativeTime` | `iso: string` | "3 min ago", updates every 30 s |
| `MetadataDrawer` | `data: unknown`, `onClose` | Slide-in panel, `<pre>` JSON viewer |
| `InlineFilter` | `options`, `value`, `onChange` | Horizontal filter chip row |
| `EmptyStateCard` | `message`, `action?` | Centered card for unloaded states |
| `PlaceholderQueue` | `title`, `description`, `targetStage` | Blocked-queue card with stage note |

All components are Tailwind-only. No additional CSS library.

---

## 8. Data-fetching contracts

All panels use TanStack Query. Conventions:

| Pattern | Implementation |
|---|---|
| Query key | `["admin", panelName, ...filterParams]` |
| Stale time | 30 s for health/stats; 60 s for job tables |
| Refetch interval | 30 s for health strip; manual for job tables |
| Error boundary | `ErrorStateCard` shows API error message + retry button |
| Loading state | Skeleton rows matching column count |

Client-side requests go to **`/api/backend/*`** (the Next.js proxy introduced in the UI shell, `app/api/backend/[...path]/route.ts`). No direct browser-to-Python calls.

Example:

```ts
// In a panel component
const q = useQuery({
  queryKey: ["admin", "source-stats"],
  queryFn: () =>
    fetch("/api/backend/admin/source-stats").then((r) => r.json()),
  staleTime: 30_000,
  refetchInterval: 30_000,
});
```

---

## 9. Filter and sort data model

All table panels use this shared filter state shape:

```ts
type TableFilter = {
  search: string;
  status?: string;       // crawl jobs, publish queue
  tier?: number | null;  // source health
  riskMode?: string;     // source health
  dateFrom?: string;     // crawl jobs
  dateTo?: string;       // crawl jobs
  page: number;
  pageSize: 50 | 100 | 200;
};
```

Filters are stored in `useState` inside each panel; URL-synced in a future iteration (not required for internal MVP).

---

## 10. Accessibility and interaction standards

- All tables have `<caption>` for screen readers and keyboard-navigable rows.
- Actions inside rows are `<button>` elements, not div click handlers.
- Color alone is never the only signal (status badges use text labels + color).
- Drawers trap focus and close on `Escape`.
- All numbers have `aria-label` with full text ("1,204 canonical listings").

---

## 11. Implementation phases

| Phase | What to build | Backend dependency |
|---|---|---|
| **Phase A — now** | Layout scaffold, sidebar, health strip, metrics row | `GET /api/v1/ready`, `GET /admin/source-stats` |
| **Phase B** | Source health table with coverage bars, Crawl jobs table + drawer | `GET /admin/source-stats`, `GET /crawl-jobs` |
| **Phase C** | Parser failure queue (real) | `GET /admin/parser-failures` (to be added) |
| **Phase D** | Duplicate review + geocode review queues | Stage 6–7 APIs |
| **Phase E** | Compliance panel + publish queue | Stage 8–10 APIs |

**The current `app/(main)/admin/page.tsx` is the Phase A stub.** Phase B starts when `GET /admin/source-stats` is confirmed stable against a real Postgres instance (`make golden-path` exits 0).

---

## 12. Files to create during implementation

```
app/(main)/admin/
  page.tsx                         ← Phase A stub (exists)
  _components/
    AdminSidebar.tsx
    SystemHealthStrip.tsx
    MetricsRow.tsx
    KpiCard.tsx
    panels/
      SourceHealthPanel.tsx
      CrawlJobsPanel.tsx
      ParserFailuresPanel.tsx
      DuplicateReviewPanel.tsx
      GeocodeReviewPanel.tsx
      CompliancePanel.tsx
      PublishQueuePanel.tsx
components/shared/
  CoverageBar.tsx
  StatusBadge.tsx
  TierBadge.tsx
  RiskBadge.tsx
  LegalBadge.tsx
  RelativeTime.tsx
  MetadataDrawer.tsx
  InlineFilter.tsx
  EmptyStateCard.tsx
  PlaceholderQueue.tsx
```

No files created by this spec. Implementation follows Phase B gate.

---

## 13. Acceptance gate (when Phase B is implemented)

- [ ] Health strip shows green when `make run-api` and `make dev-up` are both running.
- [ ] Health strip shows amber when Postgres is missing.
- [ ] KPI cards load real counts from `/admin/source-stats`.
- [ ] Source health table lists all registry sources with coverage bars.
- [ ] Crawl jobs table shows recent jobs from `/crawl-jobs` with status badges.
- [ ] All tables are filterable and have working empty states.
- [ ] No direct backend URL is called from the browser (all via `/api/backend/*` proxy).
- [ ] Playwright smoke test: `admin` page loads without JS errors.
