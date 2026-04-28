"""Queue helpers for the operator-driven Stage 2 controlled crawl."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

from ..db.ids import new_id


def queue_status_summary(
    engine: Engine,
    *,
    source_name: str | None = None,
    section_id: str | None = None,
) -> dict[str, Any]:
    """Return queue/task counts for the controlled crawl pipeline."""
    filters = {
        "source_name": source_name,
        "section_id": section_id,
    }
    status_sql = text(
        """
        select
            q.task_type,
            q.status,
            count(*) as task_count
        from crawl_queue_task q
        join source_section s on s.section_id = q.section_id
        where (:source_name is null or s.source_name = :source_name)
          and (:section_id is null or q.section_id = :section_id)
        group by q.task_type, q.status
        order by q.task_type, q.status
        """
    )
    section_sql = text(
        """
        select
            s.source_name,
            q.section_id,
            count(*) filter (where q.status = 'pending') as pending_count,
            count(*) filter (where q.status = 'leased') as leased_count,
            count(*) filter (where q.status = 'done') as done_count,
            count(*) filter (where q.status = 'failed') as failed_count
        from crawl_queue_task q
        join source_section s on s.section_id = q.section_id
        where (:source_name is null or s.source_name = :source_name)
          and (:section_id is null or q.section_id = :section_id)
        group by s.source_name, q.section_id
        order by s.source_name, q.section_id
        """
    )
    next_sql = text(
        """
        select
            q.task_id,
            s.source_name,
            q.section_id,
            q.task_type,
            q.status,
            q.priority,
            q.attempt_count,
            q.max_attempts,
            q.next_attempt_at
        from crawl_queue_task q
        join source_section s on s.section_id = q.section_id
        where q.status in ('pending', 'failed')
          and (q.next_attempt_at is null or q.next_attempt_at <= now())
          and (:source_name is null or s.source_name = :source_name)
          and (:section_id is null or q.section_id = :section_id)
        order by q.priority asc, q.created_at asc
        limit 10
        """
    )
    with engine.connect() as conn:
        by_status = [dict(row) for row in conn.execute(status_sql, filters).mappings().all()]
        by_section = [dict(row) for row in conn.execute(section_sql, filters).mappings().all()]
        next_tasks = [dict(row) for row in conn.execute(next_sql, filters).mappings().all()]
    return {
        "source_name": source_name,
        "section_id": section_id,
        "task_counts": by_status,
        "section_counts": by_section,
        "next_tasks": next_tasks,
    }


def peek_next_task(
    engine: Engine,
    *,
    allowed_task_types: list[str],
    source_name: str | None = None,
    section_id: str | None = None,
) -> dict[str, Any] | None:
    sql = text(
        """
        select
            q.task_id,
            q.run_id,
            s.source_name,
            q.section_id,
            q.task_type,
            q.status,
            q.priority,
            q.payload
        from crawl_queue_task q
        join source_section s on s.section_id = q.section_id
        where q.task_type = any(:allowed_task_types)
          and q.status in ('pending', 'failed')
          and q.attempt_count < q.max_attempts
          and (q.next_attempt_at is null or q.next_attempt_at <= now())
          and (:source_name is null or s.source_name = :source_name)
          and (:section_id is null or q.section_id = :section_id)
        order by q.priority asc, q.created_at asc
        limit 1
        """
    )
    with engine.connect() as conn:
        row = conn.execute(
            sql,
            {
                "allowed_task_types": allowed_task_types,
                "source_name": source_name,
                "section_id": section_id,
            },
        ).mappings().first()
    return dict(row) if row else None


def claim_next_task(
    engine: Engine,
    *,
    allowed_task_types: list[str],
    source_name: str | None = None,
    section_id: str | None = None,
    lease_seconds: int = 300,
) -> dict[str, Any] | None:
    """Lease a single pending task for manual worker execution."""
    candidate = peek_next_task(
        engine,
        allowed_task_types=allowed_task_types,
        source_name=source_name,
        section_id=section_id,
    )
    if not candidate:
        return None
    now = datetime.now(tz=timezone.utc)
    lease_until = now + timedelta(seconds=lease_seconds)
    with engine.begin() as conn:
        updated = conn.execute(
            text(
                """
                update crawl_queue_task
                set status = 'leased',
                    attempt_count = attempt_count + 1,
                    lease_until = :lease_until,
                    updated_at = :ts
                where task_id = :task_id
                  and status in ('pending', 'failed')
                returning task_id, run_id, section_id, task_type, status, priority, payload
                """
            ),
            {
                "task_id": candidate["task_id"],
                "lease_until": lease_until,
                "ts": now,
            },
        ).mappings().first()
    return dict(updated) if updated else None


def insert_followup_tasks(
    engine: Engine,
    *,
    tasks: list[dict[str, Any]],
    run_id: str | None,
) -> int:
    if not tasks:
        return 0
    inserted = 0
    now = datetime.now(tz=timezone.utc)
    with engine.begin() as conn:
        for task in tasks:
            row = conn.execute(
                text(
                    """
                    insert into crawl_queue_task (
                        task_id,
                        run_id,
                        section_id,
                        task_type,
                        idempotency_key,
                        status,
                        priority,
                        payload,
                        attempt_count,
                        max_attempts,
                        created_at,
                        updated_at
                    ) values (
                        :task_id,
                        :run_id,
                        :section_id,
                        :task_type,
                        :idempotency_key,
                        'pending',
                        :priority,
                        cast(:payload as jsonb),
                        0,
                        :max_attempts,
                        :ts,
                        :ts
                    )
                    on conflict (idempotency_key) do nothing
                    returning task_id
                    """
                ),
                {
                    "task_id": new_id("ctsk"),
                    "run_id": run_id,
                    "section_id": task["section_id"],
                    "task_type": task["task_type"],
                    "idempotency_key": task["idempotency_key"],
                    "priority": int(task.get("priority", 100)),
                    "payload": json.dumps(task.get("payload") or {}),
                    "max_attempts": int(task.get("max_attempts", 5)),
                    "ts": now,
                },
            ).first()
            if row:
                inserted += 1
    return inserted


def complete_task(
    engine: Engine,
    *,
    task_id: str,
    note: str | None = None,
) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                update crawl_queue_task
                set status = 'done',
                    lease_until = null,
                    updated_at = :ts,
                    payload = payload || cast(:patch as jsonb)
                where task_id = :task_id
                """
            ),
            {
                "task_id": task_id,
                "ts": datetime.now(tz=timezone.utc),
                "patch": json.dumps({"worker_note": note} if note else {}),
            },
        )


def fail_task(
    engine: Engine,
    *,
    task_id: str,
    phase: str,
    message: str,
    detail: dict[str, Any] | None = None,
    retry_delay_seconds: int = 300,
) -> None:
    now = datetime.now(tz=timezone.utc)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                insert into crawl_error (error_id, task_id, phase, message, detail, created_at)
                values (:error_id, :task_id, :phase, :message, cast(:detail as jsonb), :ts)
                """
            ),
            {
                "error_id": new_id("cerr"),
                "task_id": task_id,
                "phase": phase,
                "message": message,
                "detail": json.dumps(detail or {}),
                "ts": now,
            },
        )
        conn.execute(
            text(
                """
                update crawl_queue_task
                set status = 'failed',
                    lease_until = null,
                    next_attempt_at = :next_attempt_at,
                    updated_at = :ts
                where task_id = :task_id
                """
            ),
            {
                "task_id": task_id,
                "next_attempt_at": now + timedelta(seconds=retry_delay_seconds),
                "ts": now,
            },
        )

