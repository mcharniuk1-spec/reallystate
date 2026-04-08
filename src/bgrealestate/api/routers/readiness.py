from __future__ import annotations

import os
from typing import Any

import redis
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text

router = APIRouter(tags=["health"])


def _check_postgres() -> dict[str, Any]:
    url = os.getenv("DATABASE_URL")
    if not url:
        return {"name": "postgres", "ok": None, "detail": "DATABASE_URL not set"}
    try:
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"name": "postgres", "ok": True, "detail": "select_1_ok"}
    except Exception as exc:  # noqa: BLE001
        return {"name": "postgres", "ok": False, "detail": str(exc)}


def _check_redis() -> dict[str, Any]:
    url = os.getenv("REDIS_URL")
    if not url:
        return {"name": "redis", "ok": None, "detail": "REDIS_URL not set"}
    try:
        r = redis.Redis.from_url(url, socket_connect_timeout=2.0)
        if r.ping():
            return {"name": "redis", "ok": True, "detail": "ping_ok"}
        return {"name": "redis", "ok": False, "detail": "ping_false"}
    except Exception as exc:  # noqa: BLE001
        return {"name": "redis", "ok": False, "detail": str(exc)}


@router.get("/ready")
def ready() -> JSONResponse:
    """Dependency checks for orchestrators (K8s, Compose, load balancers)."""
    checks = [_check_postgres(), _check_redis()]
    failed = [c for c in checks if c.get("ok") is False]
    status = "degraded" if failed else "ok"
    # Fail readiness only when a configured dependency is explicitly down (ok is False).
    code = 503 if failed else 200
    body: dict[str, Any] = {"status": status, "checks": checks}
    return JSONResponse(content=body, status_code=code)
