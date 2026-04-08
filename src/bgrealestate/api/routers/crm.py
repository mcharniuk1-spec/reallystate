from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...db.repositories import CrmRepository
from ..deps import get_db

router = APIRouter(prefix="/crm", tags=["crm"])


def _iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt is not None else None


def _thread_row(t: Any) -> dict[str, Any]:
    return {
        "thread_id": t.thread_id,
        "account_id": t.account_id,
        "channel_account_id": t.channel_account_id,
        "external_thread_id": t.external_thread_id,
        "lead_contact_id": t.lead_contact_id,
        "status": t.status,
        "stage": t.stage,
        "assignee_user_id": t.assignee_user_id,
        "priority": t.priority,
        "unread_count": t.unread_count,
        "last_message_at": _iso(t.last_message_at),
        "follow_up_due_at": _iso(t.follow_up_due_at),
        "created_at": _iso(t.created_at),
    }


def _message_row(m: Any) -> dict[str, Any]:
    return {
        "message_id": m.message_id,
        "thread_id": m.thread_id,
        "direction": m.direction,
        "sender_type": m.sender_type,
        "sender_id": m.sender_id,
        "external_message_id": m.external_message_id,
        "body_text": m.body_text,
        "body_html": m.body_html,
        "language": m.language,
        "sent_at": _iso(m.sent_at),
        "received_at": _iso(m.received_at),
        "delivery_status": m.delivery_status,
        "metadata": dict(m.metadata_jsonb or {}),
    }


class AppendMessageBody(BaseModel):
    body_text: str = Field(min_length=1, max_length=16_000)


@router.get("/threads")
def list_threads(
    session: Annotated[Session, Depends(get_db)],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    account_id: str | None = None,
) -> dict[str, Any]:
    repo = CrmRepository(session)
    rows = repo.list_threads(limit=limit, offset=offset, account_id=account_id)
    return {"count": len(rows), "items": [_thread_row(t) for t in rows]}


@router.get("/threads/{thread_id}/messages")
def list_messages(thread_id: str, session: Annotated[Session, Depends(get_db)]) -> dict[str, Any]:
    repo = CrmRepository(session)
    if repo.get_thread(thread_id) is None:
        raise HTTPException(status_code=404, detail="thread_not_found")
    rows = repo.list_messages(thread_id)
    return {"thread_id": thread_id, "count": len(rows), "items": [_message_row(m) for m in rows]}


@router.post("/threads/{thread_id}/messages")
def append_message(
    thread_id: str,
    body: AppendMessageBody,
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    repo = CrmRepository(session)
    try:
        msg = repo.append_operator_message(thread_id, body.body_text)
    except ValueError as exc:
        if str(exc) == "thread_not_found":
            raise HTTPException(status_code=404, detail="thread_not_found") from exc
        raise
    return {"ok": True, "message": _message_row(msg)}
