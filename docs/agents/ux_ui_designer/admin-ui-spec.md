# Admin UI Spec (`/admin`)

Slice: `UX-01`  
Status: `DONE_AWAITING_VERIFY` (awaiting debugger API-contract verification)  
Date: 2026-04-08

## Scope

Internal operator/admin surface only. No public UI work.

This spec defines the `/admin` UX layout and data model for:

- source health
- filters and coverage bars
- error/review queues
- crawl job visibility

## Page layout

1. **System health strip** (top, persistent)
2. **KPI row** (active sources, canonical listings, raw captures, described coverage)
3. **Left queue nav**
4. **Main queue panel** (table/drawer based on selected queue)

```
[Health strip]
[KPI cards]
[Sidebar queues] [Main panel: table + filters + actions]
```

## Queue model

- Source health
- Crawl jobs
- Parser failures
- Duplicate review
- Geocode review
- Compliance
- Publish queue

## API contracts used now

### 1) Readiness

Endpoint: `GET /api/v1/ready`

```ts
type ReadyPayload = {
  status: "ok" | "degraded";
  checks: Array<{ name: "postgres" | "redis"; ok: boolean | null; detail: string }>;
};
```

### 2) Source stats

Endpoint: `GET /admin/source-stats`

```ts
type SourceStatsPayload = {
  ok: boolean;
  count: number;
  rows: Array<{
    source_name: string;
    canonical_listings: number;
    raw_captures: number;
    with_description: number;
  }>;
};
```

### 3) Crawl jobs

Endpoint: `GET /crawl-jobs?limit=50&offset=0`

```ts
type CrawlJobsPayload = {
  count: number;
  items: Array<{
    job_id: string;
    source_name: string;
    job_type: string;
    status: "pending" | "running" | "success" | "failed" | "retrying";
    attempt_count: number;
    scheduled_for: string | null;
    started_at: string | null;
    finished_at: string | null;
    metadata: Record<string, unknown>;
  }>;
};
```

## Data model for Source Health panel

Source health table columns:

- Source (`source_name`)
- Tier (joined from source registry by `source_name`)
- Canonical listings (`canonical_listings`)
- Raw captures (`raw_captures`)
- Coverage bar (`with_description / canonical_listings`)
- Legal mode (joined)
- Risk mode (joined)
- Actions (`View jobs`, `Sync`)

Coverage formula:

```ts
const coverage = canonical_listings > 0 ? with_description / canonical_listings : 0;
```

## Filters

Shared filter object:

```ts
type AdminFilterState = {
  search: string;
  tier?: 1 | 2 | 3 | 4;
  riskMode?: string;
  status?: string;
  page: number;
  pageSize: 50 | 100;
};
```

Filtering controls:

- source name search
- tier selector
- risk selector
- crawl status selector

## Component breakdown

- `AdminPageShell`
- `SystemHealthStrip`
- `AdminKpiRow`
- `AdminQueueSidebar`
- `SourceHealthPanel`
- `CrawlJobsPanel`
- `ParserFailuresPanel` (placeholder until endpoint exists)
- `DuplicateReviewPanel` (placeholder)
- `GeocodeReviewPanel` (placeholder)
- `CompliancePanel` (placeholder)
- `PublishQueuePanel` (placeholder)
- shared: `CoverageBar`, `StatusBadge`, `MetadataDrawer`, `EmptyStateCard`

## Queue placeholders pending backend slices

Until APIs are implemented, show explicit placeholders for:

- parser failures
- duplicate review
- geocode review
- compliance
- publish queue

Each placeholder must include:

- missing endpoint name
- responsible slice dependency
- short operator note ("not available yet")

## Interaction and accessibility requirements

- Keyboard reachable filters/actions
- Status represented by text + color
- Drawer closable with Escape
- Tables include captions for screen readers

## Frontend data-fetching contract

Client calls only via Next proxy:

- `/api/backend/api/v1/ready`
- `/api/backend/admin/source-stats`
- `/api/backend/crawl-jobs`

No direct browser calls to Python base URL.

## Implementation gate

Do not move beyond admin/operator scope in this slice.

This is a spec deliverable only; implementation starts after verifier confirms API contract alignment.

## Related detailed plan

For expanded panel-by-panel detail, use:

- `docs/agents/ux_ui_designer/operator-dashboard-spec.md`
