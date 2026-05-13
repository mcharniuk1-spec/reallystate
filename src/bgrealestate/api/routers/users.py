from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...db.ids import new_id
from ...db.models import (
    AppUserModel,
    LeadMessageModel,
    LeadThreadModel,
    LeadThreadPropertyLinkModel,
    OrganizationAccountModel,
    PropertyEntityModel,
    SavedPropertyModel,
    SavedPropertyStatusEventModel,
    UserPropertyChatModel,
)
from ...services.chat_service import run_chat_completion
from ...services.user_auth import VALID_USER_MODES, TokenPayload
from ..deps import get_db
from ..user_deps import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


class UpdateProfileRequest(BaseModel):
    display_name: str | None = None
    user_mode: str | None = None
    avatar_url: str | None = None


class SavePropertyRequest(BaseModel):
    property_id: str
    listing_reference_id: str | None = None
    notes: str | None = None


class CreatePropertyChatRequest(BaseModel):
    property_id: str
    initial_message: str | None = Field(default=None, max_length=8_000)
    context: dict[str, Any] = Field(default_factory=dict)


class SendPropertyChatMessageRequest(BaseModel):
    body_text: str = Field(min_length=1, max_length=16_000)
    model: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    ai_assist: bool = True


def _serialize_user(u: AppUserModel) -> dict[str, Any]:
    return {
        "user_id": u.user_id,
        "email": u.email,
        "display_name": u.display_name,
        "avatar_url": u.avatar_url,
        "user_mode": u.user_mode,
        "status": u.status,
        "created_at": u.created_at.isoformat() if u.created_at else None,
        "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None,
    }


def _serialize_saved(s: SavedPropertyModel) -> dict[str, Any]:
    return {
        "saved_id": s.saved_id,
        "property_id": s.property_id,
        "listing_reference_id": s.listing_reference_id,
        "status": s.status,
        "notes": s.notes,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
    }


def _serialize_message(m: LeadMessageModel) -> dict[str, Any]:
    return {
        "message_id": m.message_id,
        "thread_id": m.thread_id,
        "direction": m.direction,
        "sender_type": m.sender_type,
        "sender_id": m.sender_id,
        "body_text": m.body_text,
        "sent_at": m.sent_at.isoformat() if m.sent_at else None,
        "received_at": m.received_at.isoformat() if m.received_at else None,
        "delivery_status": m.delivery_status,
        "metadata": dict(m.metadata_jsonb or {}),
    }


def _serialize_property_chat(c: UserPropertyChatModel) -> dict[str, Any]:
    return {
        "chat_id": c.chat_id,
        "thread_id": c.thread_id,
        "property_id": c.property_id,
        "status": c.status,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        "last_message_at": c.last_message_at.isoformat() if c.last_message_at else None,
        "metadata": dict(c.metadata_jsonb or {}),
    }


def _record_saved_status_event(
    session: Session,
    *,
    saved: SavedPropertyModel,
    actor_user_id: str,
    action: str,
    from_status: str | None,
    to_status: str,
    details: dict[str, Any] | None = None,
) -> None:
    session.add(
        SavedPropertyStatusEventModel(
            event_id=new_id("spevt"),
            saved_id=saved.saved_id,
            user_id=saved.user_id,
            property_id=saved.property_id,
            actor_user_id=actor_user_id,
            action=action,
            from_status=from_status,
            to_status=to_status,
            details_jsonb=details or {},
            created_at=datetime.now(timezone.utc),
        )
    )


def _default_account_id() -> str:
    return os.getenv("CRM_DEFAULT_ACCOUNT_ID", "acct_default")


def _ensure_default_account(session: Session) -> str:
    account_id = _default_account_id()
    account = session.get(OrganizationAccountModel, account_id)
    if account is None:
        session.add(
            OrganizationAccountModel(
                account_id=account_id,
                name="Default Property Chat Account",
                account_type="operator",
                billing_status="trial",
                default_locale="en",
                timezone="Europe/Sofia",
                created_at=datetime.now(timezone.utc),
            )
        )
    return account_id


def _append_user_property_message(
    session: Session,
    *,
    chat: UserPropertyChatModel,
    user_id: str,
    body_text: str,
    metadata: dict[str, Any] | None = None,
) -> LeadMessageModel:
    now = datetime.now(timezone.utc)
    msg = LeadMessageModel(
        message_id=new_id("lmsg"),
        thread_id=chat.thread_id,
        direction="inbound",
        sender_type="user",
        sender_id=user_id,
        external_message_id=None,
        body_text=body_text,
        body_html=None,
        language=None,
        sent_at=None,
        received_at=now,
        delivery_status="stored",
        metadata_jsonb={"kind": "property_chat", "property_id": chat.property_id, **(metadata or {})},
    )
    session.add(msg)
    chat.last_message_at = now
    chat.updated_at = now
    thread = session.get(LeadThreadModel, chat.thread_id)
    if thread is not None:
        thread.last_message_at = now
    return msg


def _append_assistant_property_message(
    session: Session,
    *,
    chat: UserPropertyChatModel,
    body_text: str,
    provider: str,
    model: str | None,
) -> LeadMessageModel:
    now = datetime.now(timezone.utc)
    msg = LeadMessageModel(
        message_id=new_id("lmsg"),
        thread_id=chat.thread_id,
        direction="outbound",
        sender_type="assistant",
        sender_id="property_assistant",
        external_message_id=None,
        body_text=body_text,
        body_html=None,
        language=None,
        sent_at=now,
        received_at=None,
        delivery_status="stored",
        metadata_jsonb={
            "kind": "property_chat_assistant",
            "property_id": chat.property_id,
            "provider": provider,
            "model": model,
        },
    )
    session.add(msg)
    chat.last_message_at = now
    chat.updated_at = now
    thread = session.get(LeadThreadModel, chat.thread_id)
    if thread is not None:
        thread.last_message_at = now
    return msg


def _property_chat_prompt(prop: PropertyEntityModel, user_text: str, context: dict[str, Any]) -> list[dict[str, str]]:
    facts = [
        f"property_id={prop.property_id}",
        f"title={prop.canonical_title or ''}",
        f"city={prop.canonical_city or ''}",
        f"address={prop.canonical_address or ''}",
        f"confidence={prop.confidence_score if prop.confidence_score is not None else ''}",
    ]
    if context:
        facts.append(f"ui_context={context}")
    desc = (prop.canonical_description or "")[:1800]
    system = (
        "You are the Bulgaria real-estate property assistant. "
        "Answer from the supplied property facts and project context only. "
        "If facts are missing, say what must be checked by the operator. "
        + "\n".join(facts)
        + (f"\ndescription={desc}" if desc else "")
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user_text}]


@router.get("/me")
def get_profile(
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    user = session.get(AppUserModel, current_user.user_id)
    if user is None:
        raise HTTPException(404, detail="user_not_found")
    saved_count = session.scalar(
        select(SavedPropertyModel.saved_id)
        .where(SavedPropertyModel.user_id == current_user.user_id, SavedPropertyModel.status == "liked")
        .limit(1)
    )
    profile = _serialize_user(user)
    profile["has_saved_properties"] = saved_count is not None
    return {"user": profile}


@router.patch("/me")
def update_profile(
    body: UpdateProfileRequest,
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    user = session.get(AppUserModel, current_user.user_id)
    if user is None:
        raise HTTPException(404, detail="user_not_found")
    if body.display_name is not None:
        user.display_name = body.display_name.strip()
    if body.user_mode is not None:
        if body.user_mode not in VALID_USER_MODES:
            raise HTTPException(400, detail=f"invalid user_mode; must be one of {sorted(VALID_USER_MODES)}")
        user.user_mode = body.user_mode
    if body.avatar_url is not None:
        user.avatar_url = body.avatar_url.strip() or None
    return {"user": _serialize_user(user)}


@router.get("/me/saved")
def list_saved(
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    rows = (
        session.scalars(
            select(SavedPropertyModel)
            .where(SavedPropertyModel.user_id == current_user.user_id)
            .where(SavedPropertyModel.status == "liked")
            .order_by(SavedPropertyModel.created_at.desc())
            .limit(200)
        )
        .all()
    )
    items = [_serialize_saved(s) for s in rows]
    return {"count": len(items), "items": items}


@router.get("/me/liked")
def list_liked(
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    return list_saved(current_user, session)


@router.post("/me/saved", status_code=201)
def save_property(
    body: SavePropertyRequest,
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    if session.get(PropertyEntityModel, body.property_id) is None:
        raise HTTPException(404, detail="property_not_found")
    now = datetime.now(timezone.utc)
    saved = session.scalar(
        select(SavedPropertyModel).where(
            SavedPropertyModel.user_id == current_user.user_id,
            SavedPropertyModel.property_id == body.property_id,
        )
    )
    old_status = saved.status if saved is not None else None
    if saved is None:
        saved = SavedPropertyModel(
            saved_id=new_id("saved"),
            user_id=current_user.user_id,
            property_id=body.property_id,
            listing_reference_id=body.listing_reference_id,
            status="liked",
            notes=body.notes,
            created_at=now,
            updated_at=now,
        )
        session.add(saved)
    else:
        saved.listing_reference_id = body.listing_reference_id
        saved.notes = body.notes
        saved.status = "liked"
        saved.updated_at = now
    if old_status != "liked":
        _record_saved_status_event(
            session,
            saved=saved,
            actor_user_id=current_user.user_id,
            action="like_property",
            from_status=old_status,
            to_status="liked",
        )
    return {"saved_id": saved.saved_id, "property_id": body.property_id, "status": saved.status}


@router.delete("/me/saved/{property_id}", status_code=204)
def unsave_property(
    property_id: str,
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
) -> None:
    row = session.scalar(
        select(SavedPropertyModel).where(
            SavedPropertyModel.user_id == current_user.user_id,
            SavedPropertyModel.property_id == property_id,
        )
    )
    if row is not None:
        old_status = row.status
        if old_status != "unliked":
            row.status = "unliked"
            row.updated_at = datetime.now(timezone.utc)
            _record_saved_status_event(
                session,
                saved=row,
                actor_user_id=current_user.user_id,
                action="unlike_property",
                from_status=old_status,
                to_status="unliked",
            )


@router.get("/me/dashboard")
def user_dashboard(
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    from sqlalchemy import func

    saved_count = session.scalar(
        select(func.count(SavedPropertyModel.saved_id)).where(
            SavedPropertyModel.user_id == current_user.user_id,
            SavedPropertyModel.status == "liked",
        )
    ) or 0

    return {
        "user_id": current_user.user_id,
        "user_mode": current_user.user_mode,
        "saved_count": saved_count,
    }


@router.get("/me/property-chats")
def list_property_chats(
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    rows = (
        session.scalars(
            select(UserPropertyChatModel)
            .where(UserPropertyChatModel.user_id == current_user.user_id)
            .order_by(UserPropertyChatModel.updated_at.desc())
            .limit(100)
        )
        .all()
    )
    return {"count": len(rows), "items": [_serialize_property_chat(c) for c in rows]}


@router.post("/me/property-chats", status_code=201)
def create_property_chat(
    body: CreatePropertyChatRequest,
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    if session.get(PropertyEntityModel, body.property_id) is None:
        raise HTTPException(404, detail="property_not_found")
    chat = session.scalar(
        select(UserPropertyChatModel).where(
            UserPropertyChatModel.user_id == current_user.user_id,
            UserPropertyChatModel.property_id == body.property_id,
        )
    )
    created = False
    now = datetime.now(timezone.utc)
    if chat is None:
        account_id = _ensure_default_account(session)
        thread = LeadThreadModel(
            thread_id=new_id("lthr"),
            account_id=account_id,
            channel_account_id=None,
            external_thread_id=f"property_chat:{current_user.user_id}:{body.property_id}",
            lead_contact_id=None,
            status="open",
            stage="property_chat",
            assignee_user_id=None,
            priority="normal",
            unread_count=0,
            last_message_at=None,
            follow_up_due_at=None,
            created_at=now,
        )
        session.add(thread)
        session.add(
            LeadThreadPropertyLinkModel(
                link_id=new_id("ltpl"),
                thread_id=thread.thread_id,
                property_id=body.property_id,
                source_listing_id=None,
                offer_id=None,
                relationship_type="user_property_chat",
            )
        )
        chat = UserPropertyChatModel(
            chat_id=new_id("upchat"),
            user_id=current_user.user_id,
            property_id=body.property_id,
            thread_id=thread.thread_id,
            status="open",
            created_at=now,
            updated_at=now,
            last_message_at=None,
            metadata_jsonb={"context": body.context},
        )
        session.add(chat)
        created = True
    if body.initial_message:
        _append_user_property_message(
            session,
            chat=chat,
            user_id=current_user.user_id,
            body_text=body.initial_message,
            metadata={"initial": True, "context": body.context},
        )
    return {"created": created, "chat": _serialize_property_chat(chat)}


@router.get("/me/property-chats/{chat_id}/messages")
def list_property_chat_messages(
    chat_id: str,
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    chat = session.get(UserPropertyChatModel, chat_id)
    if chat is None or chat.user_id != current_user.user_id:
        raise HTTPException(404, detail="property_chat_not_found")
    rows = (
        session.scalars(
            select(LeadMessageModel)
            .where(LeadMessageModel.thread_id == chat.thread_id)
            .order_by(LeadMessageModel.received_at.asc().nullsfirst(), LeadMessageModel.sent_at.asc().nullsfirst())
            .limit(200)
        )
        .all()
    )
    return {"chat": _serialize_property_chat(chat), "count": len(rows), "items": [_serialize_message(m) for m in rows]}


@router.post("/me/property-chats/{chat_id}/messages", status_code=201)
def send_property_chat_message(
    chat_id: str,
    body: SendPropertyChatMessageRequest,
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    chat = session.get(UserPropertyChatModel, chat_id)
    if chat is None or chat.user_id != current_user.user_id:
        raise HTTPException(404, detail="property_chat_not_found")
    prop = session.get(PropertyEntityModel, chat.property_id)
    if prop is None:
        raise HTTPException(404, detail="property_not_found")

    user_msg = _append_user_property_message(
        session,
        chat=chat,
        user_id=current_user.user_id,
        body_text=body.body_text,
        metadata={"context": body.context},
    )
    assistant_msg = None
    provider = None
    if body.ai_assist:
        reply, provider = run_chat_completion(
            _property_chat_prompt(prop, body.body_text, body.context),
            model=body.model,
        )
        assistant_msg = _append_assistant_property_message(
            session,
            chat=chat,
            body_text=reply,
            provider=provider,
            model=body.model,
        )

    return {
        "chat": _serialize_property_chat(chat),
        "user_message": _serialize_message(user_msg),
        "assistant_message": _serialize_message(assistant_msg) if assistant_msg else None,
        "provider": provider,
    }
