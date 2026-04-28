"""Operator-callable controlled crawl runner (no live HTTP by default)."""

from __future__ import annotations

from sqlalchemy.engine import Engine

from .orchestrator import (
    create_crawl_run,
    enqueue_planned_tasks,
    fetch_runner_pause,
    plan_discover_and_threshold_tasks,
    refresh_fulfillment_counts,
    summarize_controlled_run,
)


def runner_once(
    engine: Engine,
    *,
    dry_run: bool = True,
    enqueue: bool = False,
    source_name: str | None = None,
    section_id: str | None = None,
    include_inactive: bool = False,
    include_unsupported: bool = True,
    max_sections: int | None = None,
    initiated_by: str | None = None,
) -> dict[str, object]:
    """Plan one controlled-crawl scheduler tick.

    Default behavior is read-only and returns a section-by-section summary.
    When ``dry_run=False`` the runner refreshes ``segment_fulfillment`` counts.
    When ``enqueue=True`` and the global pause switch is off, it also inserts
    discover/threshold queue tasks for below-threshold buckets.
    """
    summary = summarize_controlled_run(
        engine,
        source_name=source_name,
        section_id=section_id,
        include_inactive=include_inactive,
        include_unsupported=include_unsupported,
        max_sections=max_sections,
    )
    planned_tasks = plan_discover_and_threshold_tasks(summary)
    if dry_run:
        summary["planned_tasks"] = len(planned_tasks)
        summary["dry_run"] = True
        summary["note"] = "Read-only summary only. Use --apply to refresh fulfillment counts, and --enqueue after unpausing."
        return summary

    refresh_fulfillment_counts(engine, summary)
    summary["dry_run"] = False
    summary["planned_tasks"] = len(planned_tasks)
    if fetch_runner_pause(engine):
        summary["enqueued"] = 0
        summary["note"] = "Counts were refreshed, but the runner is paused. Clear global pause before enqueue."
        return summary
    if not enqueue:
        summary["enqueued"] = 0
        summary["note"] = "Counts were refreshed. enqueue=False, so no crawl_queue_task rows were written."
        return summary

    run_id = create_crawl_run(
        engine,
        initiated_by=initiated_by,
        source_name=source_name,
        section_id=section_id,
    )
    inserted = enqueue_planned_tasks(engine, planned_tasks, run_id=run_id)
    summary["run_id"] = run_id
    summary["enqueued"] = inserted
    summary["note"] = "Controlled activation queued discover + threshold_check tasks for below-threshold supported buckets."
    return summary
