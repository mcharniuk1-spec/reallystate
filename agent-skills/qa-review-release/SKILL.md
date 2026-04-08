---
name: qa-review-release
description: Use for running tests, lint/typecheck checks, release gates, no-live-network checks, progress updates, and final agent closeout reporting.
---

# qa-review-release

Use this skill for test, review, release, and progress-gate checks.

## Read First
- `AGENTS.md`
- `PLAN.md`
- `tests/`

## Workflow
1. Run the smallest relevant tests first, then the full suite.
2. Run lint/typecheck when available.
3. Confirm no live-network tests were added.
4. Check source legal gates for new connectors or publishing adapters.
5. Update progress and record risks/blockers.

## Acceptance
- Required tests pass or failures are documented with cause.
- Every agent step reports changed files, commands, tests, outputs, risks, progress, and next step.
