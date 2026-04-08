from __future__ import annotations

import os
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from ..db.session import create_db_engine, create_session_factory

_engine: Engine | None = None


def has_database() -> bool:
    return bool(os.getenv("DATABASE_URL"))


def get_engine() -> Engine:
    """Shared engine for request-scoped sessions (lazy init)."""
    global _engine
    url = os.getenv("DATABASE_URL")
    if not url:
        raise HTTPException(status_code=503, detail="DATABASE_URL not configured")
    if _engine is None:
        _engine = create_db_engine(url)
    return _engine


def get_db(engine: Annotated[Engine, Depends(get_engine)]) -> Generator[Session, None, None]:
    factory = create_session_factory(engine)
    session = factory()
    try:
        yield session
        session.commit()
    except HTTPException:
        session.rollback()
        raise
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db_optional() -> Generator[Session | None, None, None]:
    """Return a DB session if DATABASE_URL is set, otherwise yield None."""
    url = os.getenv("DATABASE_URL")
    if not url:
        yield None
        return
    global _engine
    if _engine is None:
        _engine = create_db_engine(url)
    factory = create_session_factory(_engine)
    session = factory()
    try:
        yield session
        session.commit()
    except HTTPException:
        session.rollback()
        raise
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
