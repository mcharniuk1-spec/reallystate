from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...db.ids import new_id
from ...db.models import AppUserModel
from ...services.user_auth import (
    VALID_USER_MODES,
    create_jwt,
    hash_password,
    verify_password,
)
from ..deps import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: str = Field(min_length=5)
    password: str = Field(min_length=6)
    display_name: str = Field(min_length=1)
    user_mode: str = "buyer"


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user_id: str
    email: str
    display_name: str
    user_mode: str


@router.post("/register", response_model=AuthResponse)
def register(
    body: RegisterRequest,
    session: Annotated[Session, Depends(get_db)],
) -> AuthResponse:
    if body.user_mode not in VALID_USER_MODES:
        raise HTTPException(400, detail=f"invalid user_mode; must be one of {sorted(VALID_USER_MODES)}")

    existing = session.scalar(
        select(AppUserModel).where(AppUserModel.email == body.email.lower().strip())
    )
    if existing is not None:
        raise HTTPException(409, detail="email_already_registered")

    now = datetime.now(timezone.utc)
    user = AppUserModel(
        user_id=new_id("usr"),
        email=body.email.lower().strip(),
        display_name=body.display_name.strip(),
        password_hash=hash_password(body.password),
        user_mode=body.user_mode,
        status="active",
        created_at=now,
        last_login_at=now,
    )
    session.add(user)
    session.flush()

    token = create_jwt(user.user_id, user.email, user.user_mode)
    return AuthResponse(
        token=token,
        user_id=user.user_id,
        email=user.email,
        display_name=user.display_name,
        user_mode=user.user_mode,
    )


@router.post("/login", response_model=AuthResponse)
def login(
    body: LoginRequest,
    session: Annotated[Session, Depends(get_db)],
) -> AuthResponse:
    user = session.scalar(
        select(AppUserModel).where(AppUserModel.email == body.email.lower().strip())
    )
    if user is None or not user.password_hash:
        raise HTTPException(401, detail="invalid_credentials")
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(401, detail="invalid_credentials")
    if user.status != "active":
        raise HTTPException(403, detail="account_disabled")

    user.last_login_at = datetime.now(timezone.utc)
    token = create_jwt(user.user_id, user.email, user.user_mode)
    return AuthResponse(
        token=token,
        user_id=user.user_id,
        email=user.email,
        display_name=user.display_name,
        user_mode=user.user_mode,
    )
