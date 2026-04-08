---
name: project-progress-dashboard-web
description: Improve project progress dashboards with complete task visibility, process percentages, kanban flow, and status-color conventions. Use when users ask to enhance progress web pages.
---

# Project Progress Dashboard Web

## Use When

- Dashboard lacks complete task flow visibility.
- User requests clear done/current/next visualization.
- Need process-level percentages and comments.

## Required Views

1. Global stages with subtasks and color pills:
   - green done
   - amber current
   - blue next
   - red blocked
2. Kanban flow across full project statuses.
3. All-tasks table (owner, status, ID, title, details).
4. Per-process progress percentages.

## Data Rules

- Parse backlog from `docs/agents/TASKS.md`.
- Keep status normalization consistent.
- Regenerate outputs via `make dashboard-doc`.

## Output

```text
Views updated:
Status mapping:
Progress formula:
Generated artifacts:
```
