---
name: dashboard-visual-ops
description: Dashboard and visual operations skill for KPI design, kanban flows, alerting UX, and source-health visualization. Use when evolving operator dashboards and progress reporting UIs.
---

# Dashboard Visual Ops

## Use When

- Building or updating operator dashboards.
- Visualizing source health, progress, and queue status.
- Defining KPI and drill-down interactions.

## Workflow

1. Define operator decisions the dashboard must support.
2. Map KPIs to canonical API/reporting sources.
3. Design card/table/kanban views with drill-down paths.
4. Ensure status taxonomy is consistent across views.
5. Keep dashboard generation reproducible from repo data.

## Visual Rules

- Top strip: health and blockers first.
- KPI row: high-signal metrics only.
- Tables: sortable/filterable, stable columns.
- Kanban: explicit status transitions.

## Output

```text
Decision goals:
KPI definitions:
View layout:
Drill-down behavior:
Data sources:
Acceptance checks:
```
