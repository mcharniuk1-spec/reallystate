from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...db.repositories import CrawlJobRepository
from ..auth import AuthPrincipal, require_scope
from ..deps import get_db

router = APIRouter(tags=["crawl"])


def _iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt is not None else None


def _job_row(j: Any) -> dict[str, Any]:
    return {
        "job_id": j.job_id,
        "source_name": j.source_name,
        "endpoint_id": j.endpoint_id,
        "job_type": j.job_type,
        "status": j.status,
        "priority": j.priority,
        "scheduled_for": _iso(j.scheduled_for),
        "started_at": _iso(j.started_at),
        "finished_at": _iso(j.finished_at),
        "attempt_count": j.attempt_count,
        "cursor_key": j.cursor_key,
        "idempotency_key": j.idempotency_key,
        "metadata": dict(j.metadata_jsonb or {}),
    }


@router.get("/crawl-jobs")
def list_crawl_jobs(
    _principal: Annotated[AuthPrincipal, Depends(require_scope("crawl:read"))],
    session: Annotated[Session, Depends(get_db)],
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    repo = CrawlJobRepository(session)
    rows = repo.list_recent(limit=limit, offset=offset)
    return {"count": len(rows), "items": [_job_row(j) for j in rows]}
