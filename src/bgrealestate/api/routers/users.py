from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from ...db.ids import new_id
from ...db.models import AppUserModel, SavedPropertyModel
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
        .where(SavedPropertyModel.user_id == current_user.user_id)
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
            .order_by(SavedPropertyModel.created_at.desc())
            .limit(200)
        )
        .all()
    )
    items = [
        {
            "saved_id": s.saved_id,
            "property_id": s.property_id,
            "listing_reference_id": s.listing_reference_id,
            "notes": s.notes,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in rows
    ]
    return {"count": len(items), "items": items}


@router.post("/me/saved", status_code=201)
def save_property(
    body: SavePropertyRequest,
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    stmt = (
        insert(SavedPropertyModel)
        .values(
            saved_id=new_id("saved"),
            user_id=current_user.user_id,
            property_id=body.property_id,
            listing_reference_id=body.listing_reference_id,
            notes=body.notes,
            created_at=now,
        )
        .on_conflict_do_update(
            index_elements=[SavedPropertyModel.user_id, SavedPropertyModel.property_id],
            set_={"notes": body.notes, "listing_reference_id": body.listing_reference_id},
        )
        .returning(SavedPropertyModel.saved_id)
    )
    saved_id = str(session.execute(stmt).scalar_one())
    return {"saved_id": saved_id, "property_id": body.property_id}


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
        session.delete(row)


@router.get("/me/dashboard")
def user_dashboard(
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    from sqlalchemy import func

    saved_count = session.scalar(
        select(func.count(SavedPropertyModel.saved_id)).where(
            SavedPropertyModel.user_id == current_user.user_id
        )
    ) or 0

    return {
        "user_id": current_user.user_id,
        "user_mode": current_user.user_mode,
        "saved_count": saved_count,
    }
