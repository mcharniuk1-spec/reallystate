---
name: ux-dashboard-design
description: Use when designing operator dashboards for source health, scraping progress, stage execution, and report visibility.
---

# ux-dashboard-design

Use this skill for admin/operator dashboard design and information architecture.

## Read First
- `docs/agents/ux_ui_designer/operator-dashboard-spec.md`
- `docs/project-architecture-execution-guide.md`
- `src/bgrealestate/api/routers/admin.py`

## Workflow
1. Prioritize operator tasks: detect issues, review failures, verify coverage.
2. Show time-based progress: last run, stage progress, source counts.
3. Keep filters by source, tier, intent, and category.
4. Ensure dashboard can be served as static HTML for remote access.

## Acceptance
- Dashboard spec and data model align with admin APIs.
- UX communicates stage health and next actions clearly.

