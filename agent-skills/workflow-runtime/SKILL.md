---
name: workflow-runtime
description: Use when implementing Temporal workflows, schedulers, retries, idempotency, crawl cursors, worker behavior, and durable automation runtime.
---

# workflow-runtime

Use this skill when implementing durable jobs, schedulers, or worker logic.

## Read First
- `PLAN.md`
- `src/bgrealestate/pipeline.py`
- `data/source_registry.json`

## Workflow
1. Use Temporal workflows for discovery, detail fetch, enrichment, media, CRM sync, publishing, and docs export.
2. Add idempotency keys to every workflow/activity.
3. Respect per-source rate-limit and retry budgets.
4. Persist cursors and attempts.
5. Send failed parser/connector/publish work to reviewable dead-letter records.

## Acceptance
- Jobs survive worker restart.
- Retried jobs do not duplicate side effects.
- Source cadence can start hourly and promote to 10 minutes only after gates pass.
