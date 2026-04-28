"""Manual queue worker for the Stage 2 controlled crawl."""

from __future__ import annotations

from typing import Any

from sqlalchemy.engine import Engine

from .control_queue import (
    claim_next_task,
    complete_task,
    fail_task,
    insert_followup_tasks,
    peek_next_task,
)
from .orchestrator import refresh_fulfillment_counts, summarize_controlled_run
from .region import ONLY_REGION_KEY


def build_fetch_list_tasks(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Expand a discover payload into concrete list-fetch tasks.

    This stage remains operator-driven. The generated tasks preserve enough
    metadata for a later HTTP/list executor without starting any network work.
    """
    section_id = str(payload["section_id"])
    source_name = str(payload["source_name"])
    source_spec = dict(payload.get("source_spec") or {})
    list_spec = dict(payload.get("list_spec") or {})
    source_key = source_spec.get("source_key")
    section_label = payload.get("section_label") or section_id
    templates = dict(list_spec.get("discovery_templates") or {})
    entry_urls = list(payload.get("entry_urls") or list_spec.get("entry_urls") or [])

    out: list[dict[str, Any]] = []
    for index, url in enumerate(entry_urls, start=1):
        out.append(
            {
                "section_id": section_id,
                "task_type": "fetch_list",
                "priority": 90,
                "idempotency_key": f"fetch_list:url:{section_id}:{index}:{url}",
                "payload": {
                    **payload,
                    "section_label": section_label,
                    "source_key": source_key,
                    "list_target": {
                        "kind": "entry_url",
                        "url": url,
                        "page": 1,
                    },
                    "execution_hint": {
                        "mode": "manual_or_worker_http_fetch",
                        "runtime_source_key": source_key,
                        "region_key": ONLY_REGION_KEY,
                    },
                },
            }
        )
    for index, template in enumerate(templates.get("api_templates") or [], start=1):
        out.append(
            {
                "section_id": section_id,
                "task_type": "fetch_list",
                "priority": 80,
                "idempotency_key": f"fetch_list:api:{section_id}:{index}:{template}",
                "payload": {
                    **payload,
                    "section_label": section_label,
                    "source_key": source_key,
                    "list_target": {
                        "kind": "api_template",
                        "template": template,
                        "page": 1,
                    },
                    "execution_hint": {
                        "mode": "manual_or_worker_http_fetch",
                        "runtime_source_key": source_key,
                        "region_key": ONLY_REGION_KEY,
                    },
                },
            }
        )
    for index, template in enumerate(templates.get("list_templates") or [], start=1):
        out.append(
            {
                "section_id": section_id,
                "task_type": "fetch_list",
                "priority": 85,
                "idempotency_key": f"fetch_list:list_template:{section_id}:{index}:{template}",
                "payload": {
                    **payload,
                    "section_label": section_label,
                    "source_key": source_key,
                    "list_target": {
                        "kind": "list_template",
                        "template": template,
                        "page": 1,
                    },
                    "execution_hint": {
                        "mode": "manual_or_worker_http_fetch",
                        "runtime_source_key": source_key,
                        "region_key": ONLY_REGION_KEY,
                    },
                },
            }
        )
    return out


def _execute_threshold_check(
    engine: Engine,
    *,
    task: dict[str, Any],
) -> dict[str, Any]:
    section_id = str((task.get("payload") or {}).get("section_id") or task["section_id"])
    summary = summarize_controlled_run(
        engine,
        section_id=section_id,
        include_inactive=True,
        include_unsupported=True,
        max_sections=1,
    )
    refresh_fulfillment_counts(engine, summary)
    row = summary["rows"][0] if summary["rows"] else None
    return {
        "task_id": task["task_id"],
        "task_type": task["task_type"],
        "section_id": section_id,
        "refreshed": True,
        "section_action": row["action"] if row else "missing",
        "current_valid_listings": row["current_valid_listings"] if row else 0,
        "target_valid_listings": row["target_valid_listings"] if row else None,
    }


def _execute_discover(
    engine: Engine,
    *,
    task: dict[str, Any],
) -> dict[str, Any]:
    payload = dict(task.get("payload") or {})
    followups = build_fetch_list_tasks(payload)
    inserted = insert_followup_tasks(engine, tasks=followups, run_id=task.get("run_id"))
    return {
        "task_id": task["task_id"],
        "task_type": task["task_type"],
        "section_id": task["section_id"],
        "generated_fetch_list_tasks": len(followups),
        "inserted_fetch_list_tasks": inserted,
    }


def worker_once(
    engine: Engine,
    *,
    dry_run: bool = True,
    allowed_task_types: list[str] | None = None,
    source_name: str | None = None,
    section_id: str | None = None,
    lease_seconds: int = 300,
) -> dict[str, Any]:
    """Process one queue task for the controlled crawl.

    Default mode is read-only so the operator can inspect what would happen
    before mutating queue state.
    """
    allowed = allowed_task_types or ["discover", "threshold_check"]
    if dry_run:
        task = peek_next_task(
            engine,
            allowed_task_types=allowed,
            source_name=source_name,
            section_id=section_id,
        )
        if not task:
            return {
                "dry_run": True,
                "allowed_task_types": allowed,
                "task_found": False,
                "note": "No eligible queue task matched the current filter.",
            }
        out = {
            "dry_run": True,
            "allowed_task_types": allowed,
            "task_found": True,
            "next_task": task,
        }
        if task["task_type"] == "discover":
            out["preview_followups"] = build_fetch_list_tasks(dict(task.get("payload") or {}))
        return out

    task = claim_next_task(
        engine,
        allowed_task_types=allowed,
        source_name=source_name,
        section_id=section_id,
        lease_seconds=lease_seconds,
    )
    if not task:
        return {
            "dry_run": False,
            "allowed_task_types": allowed,
            "task_claimed": False,
            "note": "No eligible queue task matched the current filter.",
        }

    try:
        if task["task_type"] == "threshold_check":
            result = _execute_threshold_check(engine, task=task)
            complete_task(engine, task_id=task["task_id"], note="Threshold summary refreshed.")
            return {
                "dry_run": False,
                "task_claimed": True,
                "completed": True,
                "result": result,
            }
        if task["task_type"] == "discover":
            result = _execute_discover(engine, task=task)
            complete_task(engine, task_id=task["task_id"], note="Expanded discover task into fetch_list tasks.")
            return {
                "dry_run": False,
                "task_claimed": True,
                "completed": True,
                "result": result,
            }
        message = f"Task type {task['task_type']!r} is not implemented in the manual control worker yet."
        fail_task(
            engine,
            task_id=task["task_id"],
            phase="control_worker",
            message=message,
            detail={"allowed_task_types": allowed},
            retry_delay_seconds=900,
        )
        return {
            "dry_run": False,
            "task_claimed": True,
            "completed": False,
            "result": {
                "task_id": task["task_id"],
                "task_type": task["task_type"],
                "status": "failed_unimplemented",
                "message": message,
            },
        }
    except Exception as exc:  # noqa: BLE001
        fail_task(
            engine,
            task_id=task["task_id"],
            phase="control_worker",
            message=str(exc),
            detail={"task_type": task["task_type"]},
            retry_delay_seconds=900,
        )
        return {
            "dry_run": False,
            "task_claimed": True,
            "completed": False,
            "result": {
                "task_id": task["task_id"],
                "task_type": task["task_type"],
                "status": "failed_exception",
                "message": str(exc),
            },
        }

