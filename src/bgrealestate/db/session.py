from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is required (e.g. postgresql+psycopg://user:pass@localhost:5432/db)")
    return url


def create_db_engine(url: str | None = None) -> Engine:
    # Keep this sync-first for the MVP slice; connectors can still use httpx async
    # and persist via a background thread/worker later if needed.
    return create_engine(url or database_url(), pool_pre_ping=True)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


@contextmanager
def session_scope(engine: Engine) -> Iterator[Session]:
    factory = create_session_factory(engine)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

