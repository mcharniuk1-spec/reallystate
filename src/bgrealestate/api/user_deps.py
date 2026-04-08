"""FastAPI dependencies for JWT-based user authentication."""

from __future__ import annotations

from typing import Annotated

from fastapi import Header, HTTPException

from ..services.user_auth import TokenPayload, decode_jwt


def get_current_user(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> TokenPayload:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, detail="missing_token")
    token = authorization[7:].strip()
    if not token:
        raise HTTPException(401, detail="missing_token")
    payload = decode_jwt(token)
    if payload is None:
        raise HTTPException(401, detail="invalid_or_expired_token")
    return payload
