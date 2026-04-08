from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Annotated

from fastapi import Header, HTTPException


@dataclass(frozen=True)
class AuthPrincipal:
    key_id: str
    scopes: frozenset[str]


def _load_key_map() -> dict[str, frozenset[str]]:
    """Load API keys and scopes from environment for MVP route protection.

    Supported formats:
    - API_KEYS_JSON={"key123":["listings:read","crm:write"],"adminkey":["admin:read"]}
    - READONLY_API_KEY=...
    - ADMIN_API_KEY=...
    """
    out: dict[str, frozenset[str]] = {}
    raw = os.getenv("API_KEYS_JSON", "").strip()
    if raw:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=500, detail=f"invalid API_KEYS_JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise HTTPException(status_code=500, detail="invalid API_KEYS_JSON: expected object")
        for key, scopes in data.items():
            if not isinstance(key, str):
                continue
            if isinstance(scopes, list):
                out[key] = frozenset(str(s) for s in scopes)
            else:
                out[key] = frozenset()

    ro = os.getenv("READONLY_API_KEY", "").strip()
    if ro:
        out.setdefault(
            ro,
            frozenset(
                {
                    "listings:read",
                    "crm:read",
                    "crawl:read",
                }
            ),
        )
    admin = os.getenv("ADMIN_API_KEY", "").strip()
    if admin:
        out.setdefault(
            admin,
            frozenset(
                {
                    "listings:read",
                    "crm:read",
                    "crm:write",
                    "crawl:read",
                    "admin:read",
                }
            ),
        )
    return out


def _extract_key(x_api_key: str | None, authorization: str | None) -> str | None:
    if x_api_key and x_api_key.strip():
        return x_api_key.strip()
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip() or None
    return None


def require_scope(scope: str):
    def _dep(
        x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
        authorization: Annotated[str | None, Header(alias="Authorization")] = None,
    ) -> AuthPrincipal:
        key = _extract_key(x_api_key, authorization)
        if not key:
            raise HTTPException(status_code=401, detail="missing_api_key")
        key_map = _load_key_map()
        scopes = key_map.get(key)
        if scopes is None:
            raise HTTPException(status_code=401, detail="invalid_api_key")
        if scope not in scopes:
            raise HTTPException(status_code=403, detail="forbidden")
        return AuthPrincipal(key_id=key[-6:] if len(key) >= 6 else key, scopes=scopes)

    return _dep

