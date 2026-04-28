"""Build controlled crawl plans from DB state without triggering live HTTP."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

from ..db.ids import new_id
from .region import ONLY_REGION_KEY
from .validity import media_present_where, valid_listing_where


@dataclass(frozen=True)
class PlannedTask:
    task_type: str
    idempotency_key: str
    section_id: str
    payload: dict[str, Any]


def fetch_runner_pause(engine: Engine) -> bool:
    with engine.connect() as conn:
        row = conn.execute(
            text("select global_pause from scrape_runner_state where singleton_id = 'global'")
        ).first()
        return True if row is None else bool(row[0])


def set_runner_pause(engine: Engine, *, paused: bool, note: str | None = None) -> dict[str, Any]:
    now = datetime.now(tz=timezone.utc)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                insert into scrape_runner_state (singleton_id, global_pause, notes, updated_at)
                values ('global', :paused, :note, :ts)
                on conflict (singleton_id) do update set
                    global_pause = excluded.global_pause,
                    notes = excluded.notes,
                    updated_at = excluded.updated_at
                """
            ),
            {"paused": paused, "note": note, "ts": now},
        )
    return {"paused": paused, "note": note, "updated_at": now.isoformat()}


def _section_query() -> str:
    return """
        select
            s.section_id,
            s.source_name,
            s.segment_key,
            s.vertical_key,
            s.section_label,
            s.entry_urls,
            s.active,
            coalesce(sf.target_valid_listings, 100) as target_valid_listings,
            sf.current_valid_listings,
            sf.current_total_listings,
            src.spec_jsonb as source_spec,
            sec.spec_jsonb as section_spec,
            lp.spec_jsonb as list_spec,
            dp.spec_jsonb as detail_spec,
            mg.spec_jsonb as media_spec
        from source_section s
        left join segment_fulfillment sf on sf.section_id = s.section_id
        left join source_section_pattern src on src.section_id = s.section_id and src.pattern_layer = 'source'
        left join source_section_pattern sec on sec.section_id = s.section_id and sec.pattern_layer = 'section'
        left join source_section_pattern lp on lp.section_id = s.section_id and lp.pattern_layer = 'list_page'
        left join source_section_pattern dp on dp.section_id = s.section_id and dp.pattern_layer = 'detail_page'
        left join source_section_pattern mg on mg.section_id = s.section_id and mg.pattern_layer = 'media_gallery'
        where s.region_key = :region_key
          and (:source_name is null or s.source_name = :source_name)
          and (:section_id is null or s.section_id = :section_id)
        order by s.source_name, s.segment_key
    """


def _count_section(conn: Any, *, section_id: str, source_name: str, segment_key: str, vertical_key: str) -> dict[str, int]:
    valid_where = valid_listing_where("cl")
    media_where = media_present_where("cl")
    sql = f"""
        with section_rows as (
            select *
            from canonical_listing cl
            where (
                cl.source_section_id = :section_id
                or (
                    cl.source_section_id is null
                    and cl.source_name = :source_name
                    and coalesce(cl.segment_key, '') = :segment_key
                    and coalesce(cl.vertical_key, 'all') = :vertical_key
                    and coalesce(cl.region_key, '') = :region_key
                )
            )
        )
        select
            count(*) filter (where removed_at is null) as total_count,
            count(*) filter (where {valid_where}) as valid_count,
            count(*) filter (where {valid_where} and {media_where}) as media_ready_count
        from section_rows cl
    """
    row = conn.execute(
        text(sql),
        {
            "section_id": section_id,
            "source_name": source_name,
            "segment_key": segment_key,
            "vertical_key": vertical_key,
            "region_key": ONLY_REGION_KEY,
        },
    ).mappings().one()
    return {
        "total_count": int(row["total_count"] or 0),
        "valid_count": int(row["valid_count"] or 0),
        "media_ready_count": int(row["media_ready_count"] or 0),
    }


def decide_section_action(
    *,
    active: bool,
    support_status: str,
    pattern_status: str,
    global_pause: bool,
    valid_count: int,
    target_valid_listings: int,
    skip_reason: str | None,
) -> tuple[str, str]:
    if support_status == "unsupported":
        return "skipped_unsupported", skip_reason or "This source/segment bucket is not supported."
    if support_status == "legal_blocked":
        return "skipped_legal_blocked", skip_reason or "Legal mode blocks activation for this source/segment."
    if support_status != "supported":
        return "skipped_pattern_incomplete", skip_reason or "Pattern is not complete enough for controlled activation."
    if pattern_status != "Patterned":
        return "skipped_pattern_incomplete", f"Source pattern status is {pattern_status!r}; controlled activation requires strict Patterned evidence."
    if valid_count >= target_valid_listings:
        return "threshold_reached", "Bucket already has enough valid records and should remain incremental-ready only."
    if not active:
        return "inactive", "Bucket is persisted but not active; keep it out of the activation wave until explicitly enabled."
    if global_pause:
        return "paused_pending_backfill", "Bucket is ready, but the global pause switch is still on."
    return "backfill_required", "Bucket is below threshold and eligible for discover/fetch/validate work."


def _task_payload(row: dict[str, Any], *, counts: dict[str, int], global_pause: bool) -> dict[str, Any]:
    target = int(row["target_valid_listings"] or 100)
    remaining = max(0, target - counts["valid_count"])
    return {
        "section_id": row["section_id"],
        "source_name": row["source_name"],
        "segment_key": row["segment_key"],
        "vertical_key": row["vertical_key"],
        "target_valid_listings": target,
        "current_valid_listings": counts["valid_count"],
        "current_total_listings": counts["total_count"],
        "current_media_ready_listings": counts["media_ready_count"],
        "remaining_needed": remaining,
        "global_pause": global_pause,
        "entry_urls": row.get("entry_urls") or [],
        "source_spec": row.get("source_spec") or {},
        "section_spec": row.get("section_spec") or {},
        "list_spec": row.get("list_spec") or {},
        "detail_spec": row.get("detail_spec") or {},
        "media_spec": row.get("media_spec") or {},
    }


def _update_fulfillment_counts(
    conn: Any,
    *,
    section_id: str,
    counts: dict[str, int],
    status: str,
    threshold_reached: bool,
    note: str | None = None,
) -> None:
    conn.execute(
        text(
            """
            update segment_fulfillment
            set current_valid_listings = :valid_count,
                current_total_listings = :total_count,
                last_counted_at = :ts,
                last_status = :status,
                incremental_ready = :incremental_ready,
                threshold_reached_at = case
                    when :threshold_reached then coalesce(threshold_reached_at, :ts)
                    else threshold_reached_at
                end,
                notes = :note
            where section_id = :section_id
            """
        ),
        {
            "section_id": section_id,
            "valid_count": counts["valid_count"],
            "total_count": counts["total_count"],
            "status": status,
            "incremental_ready": threshold_reached,
            "threshold_reached": threshold_reached,
            "note": note,
            "ts": datetime.now(tz=timezone.utc),
        },
    )


def summarize_controlled_run(
    engine: Engine,
    *,
    source_name: str | None = None,
    section_id: str | None = None,
    include_inactive: bool = False,
    include_unsupported: bool = False,
    max_sections: int | None = None,
) -> dict[str, Any]:
    global_pause = fetch_runner_pause(engine)
    rows_out: list[dict[str, Any]] = []
    with engine.connect() as conn:
        query_rows = conn.execute(
            text(_section_query()),
            {
                "region_key": ONLY_REGION_KEY,
                "source_name": source_name,
                "section_id": section_id,
            },
        ).mappings().all()
        for raw in query_rows:
            counts = _count_section(
                conn,
                section_id=str(raw["section_id"]),
                source_name=str(raw["source_name"]),
                segment_key=str(raw["segment_key"]),
                vertical_key=str(raw["vertical_key"]),
            )
            source_spec = dict(raw["source_spec"] or {})
            section_spec = dict(raw["section_spec"] or {})
            support_status = str(section_spec.get("support_status") or source_spec.get("support_status") or "pattern_incomplete")
            pattern_status = str(source_spec.get("pattern_status") or "Unknown")
            action, reason = decide_section_action(
                active=bool(raw["active"]),
                support_status=support_status,
                pattern_status=pattern_status,
                global_pause=global_pause,
                valid_count=counts["valid_count"],
                target_valid_listings=int(raw["target_valid_listings"] or 100),
                skip_reason=section_spec.get("skip_reason"),
            )
            if not include_inactive and action == "inactive":
                continue
            if not include_unsupported and action.startswith("skipped_"):
                continue
            rows_out.append(
                {
                    "section_id": raw["section_id"],
                    "source_name": raw["source_name"],
                    "segment_key": raw["segment_key"],
                    "vertical_key": raw["vertical_key"],
                    "section_label": raw["section_label"],
                    "active": bool(raw["active"]),
                    "pattern_status": pattern_status,
                    "support_status": support_status,
                    "target_valid_listings": int(raw["target_valid_listings"] or 100),
                    "current_valid_listings": counts["valid_count"],
                    "current_total_listings": counts["total_count"],
                    "current_media_ready_listings": counts["media_ready_count"],
                    "entry_urls": raw["entry_urls"] or [],
                    "action": action,
                    "reason": reason,
                    "source_spec": source_spec,
                    "section_spec": section_spec,
                    "list_spec": dict(raw["list_spec"] or {}),
                    "detail_spec": dict(raw["detail_spec"] or {}),
                    "media_spec": dict(raw["media_spec"] or {}),
                }
            )
            if max_sections is not None and len(rows_out) >= max_sections:
                break
    summary = {
        "region_key": ONLY_REGION_KEY,
        "global_pause": global_pause,
        "section_count": len(rows_out),
        "counts": {
            "backfill_required": sum(1 for row in rows_out if row["action"] == "backfill_required"),
            "paused_pending_backfill": sum(1 for row in rows_out if row["action"] == "paused_pending_backfill"),
            "threshold_reached": sum(1 for row in rows_out if row["action"] == "threshold_reached"),
            "inactive": sum(1 for row in rows_out if row["action"] == "inactive"),
            "skipped": sum(1 for row in rows_out if str(row["action"]).startswith("skipped_")),
        },
        "rows": rows_out,
    }
    return summary


def create_crawl_run(
    engine: Engine,
    *,
    initiated_by: str | None = None,
    source_name: str | None = None,
    section_id: str | None = None,
) -> str:
    run_id = new_id("crun")
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                insert into crawl_run (run_id, region_key, mode, status, initiated_by, metadata, created_at)
                values (:run_id, :region_key, 'manual_controlled_activation', 'planned', :initiated_by, cast(:metadata as jsonb), :ts)
                """
            ),
            {
                "run_id": run_id,
                "region_key": ONLY_REGION_KEY,
                "initiated_by": initiated_by,
                "metadata": json.dumps({"source_name": source_name, "section_id": section_id}),
                "ts": datetime.now(tz=timezone.utc),
            },
        )
    return run_id


def plan_discover_and_threshold_tasks(summary: dict[str, Any]) -> list[PlannedTask]:
    tasks: list[PlannedTask] = []
    stamp = datetime.now(tz=timezone.utc).date().isoformat()
    for row in summary["rows"]:
        if row["action"] != "backfill_required":
            continue
        payload = _task_payload(row, counts={
            "valid_count": row["current_valid_listings"],
            "total_count": row["current_total_listings"],
            "media_ready_count": row["current_media_ready_listings"],
        }, global_pause=bool(summary["global_pause"]))
        tasks.append(
            PlannedTask(
                task_type="discover",
                idempotency_key=f"discover:{row['section_id']}:{stamp}",
                section_id=row["section_id"],
                payload=payload,
            )
        )
        tasks.append(
            PlannedTask(
                task_type="threshold_check",
                idempotency_key=f"threshold:{row['section_id']}:{stamp}",
                section_id=row["section_id"],
                payload={
                    "section_id": row["section_id"],
                    "source_name": row["source_name"],
                    "segment_key": row["segment_key"],
                    "target_valid_listings": row["target_valid_listings"],
                    "validity_policy": "stage2_varna_minimal_validity_v1",
                },
            )
        )
    return tasks


def enqueue_planned_tasks(engine: Engine, tasks: list[PlannedTask], *, run_id: str | None = None) -> int:
    now = datetime.now(tz=timezone.utc)
    inserted = 0
    with engine.begin() as conn:
        for t in tasks:
            res = conn.execute(
                text(
                    """
                    insert into crawl_queue_task (
                        task_id, run_id, section_id, task_type, idempotency_key,
                        status, priority, payload, attempt_count, max_attempts, created_at, updated_at
                    ) values (
                        :task_id, :run_id, :section_id, :task_type, :idem,
                        'pending', 100, cast(:payload as jsonb), 0, 5, :ts, :ts
                    )
                    on conflict (idempotency_key) do nothing
                    returning task_id
                    """
                ),
                {
                    "task_id": new_id("ctsk"),
                    "run_id": run_id,
                    "section_id": t.section_id,
                    "task_type": t.task_type,
                    "idem": t.idempotency_key,
                    "payload": json.dumps(t.payload),
                    "ts": now,
                },
            )
            if res.fetchone():
                inserted += 1
    return inserted


def refresh_fulfillment_counts(engine: Engine, summary: dict[str, Any]) -> None:
    with engine.begin() as conn:
        for row in summary["rows"]:
            _update_fulfillment_counts(
                conn,
                section_id=row["section_id"],
                counts={
                    "valid_count": row["current_valid_listings"],
                    "total_count": row["current_total_listings"],
                    "media_ready_count": row["current_media_ready_listings"],
                },
                status=row["action"],
                threshold_reached=row["action"] == "threshold_reached",
                note=f"{row['action']}: {row['reason']}",
            )
