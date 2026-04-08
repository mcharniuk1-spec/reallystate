from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha1
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from .db.session import session_scope


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def _stable_id(prefix: str, *parts: Any) -> str:
    digest = sha1("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


@dataclass(frozen=True)
class SocialSeedPayload:
    thread: dict[str, Any]
    message: dict[str, Any]
    raw_capture: dict[str, Any]


def build_social_seed_payloads(*, account_id: str) -> list[SocialSeedPayload]:
    import json

    from .connectors.telegram_public import TelegramPublicConnector
    from .connectors.x_public import XPublicConnector

    root = _repo_root() / "tests" / "fixtures"
    out: list[SocialSeedPayload] = []
    captured_at = _utcnow()

    telegram = TelegramPublicConnector()
    tg_root = root / "telegram_public"
    if tg_root.exists():
        for case_dir in sorted(tg_root.iterdir()):
            raw_path = case_dir / "raw.json"
            if not case_dir.is_dir() or not raw_path.exists():
                continue
            raw = json.loads(raw_path.read_text(encoding="utf-8"))
            tg_payload = telegram.map_message_to_crm(raw, account_id=account_id)
            raw_capture = {
                "raw_capture_id": _stable_id("raw_tg", tg_payload.lead_message["message_id"]),
                "source_name": tg_payload.raw_capture.source_name,
                "url": tg_payload.raw_capture.url,
                "content_type": tg_payload.raw_capture.content_type,
                "body": tg_payload.raw_capture.body,
                "storage_key": None,
                "sha256": _stable_id("chk", tg_payload.lead_message["message_id"]),
                "http_status": 200,
                "headers_json": {},
                "fetched_at": tg_payload.raw_capture.fetched_at or captured_at,
                "parser_version": tg_payload.raw_capture.parser_version,
                "metadata_jsonb": tg_payload.raw_capture.metadata,
            }
            out.append(SocialSeedPayload(thread=tg_payload.lead_thread, message=tg_payload.lead_message, raw_capture=raw_capture))

    x_conn = XPublicConnector()
    x_root = root / "x_public"
    if x_root.exists():
        for case_dir in sorted(x_root.iterdir()):
            raw_path = case_dir / "raw.json"
            if not case_dir.is_dir() or not raw_path.exists():
                continue
            raw = json.loads(raw_path.read_text(encoding="utf-8"))
            x_payload = x_conn.map_post_to_lead(raw, account_id=account_id)
            raw_capture = {
                "raw_capture_id": _stable_id("raw_x", x_payload.lead_message["message_id"]),
                "source_name": x_payload.raw_capture.source_name,
                "url": x_payload.raw_capture.url,
                "content_type": x_payload.raw_capture.content_type,
                "body": x_payload.raw_capture.body,
                "storage_key": None,
                "sha256": _stable_id("chk", x_payload.lead_message["message_id"]),
                "http_status": 200,
                "headers_json": {},
                "fetched_at": x_payload.raw_capture.fetched_at or captured_at,
                "parser_version": x_payload.raw_capture.parser_version,
                "metadata_jsonb": x_payload.raw_capture.metadata,
            }
            out.append(SocialSeedPayload(thread=x_payload.lead_thread, message=x_payload.lead_message, raw_capture=raw_capture))

    return out


def _ensure_account(session: Session, *, account_id: str) -> None:
    from .db.models import OrganizationAccountModel

    existing = session.execute(select(OrganizationAccountModel.account_id).where(OrganizationAccountModel.account_id == account_id)).scalar_one_or_none()
    if existing:
        return
    session.add(
        OrganizationAccountModel(
            account_id=account_id,
            name="Tier4 Social Fixtures",
            account_type="agency",
            billing_status="trial",
            default_locale="en",
            timezone="Europe/Sofia",
            created_at=_utcnow(),
        )
    )


def seed_social_fixtures_to_db(engine: Engine, *, account_id: str) -> dict[str, int]:
    from .db.models import LeadMessageModel, LeadThreadModel, RawCaptureModel

    payloads = build_social_seed_payloads(account_id=account_id)
    with session_scope(engine) as session:
        _ensure_account(session, account_id=account_id)
        for payload in payloads:
            thread = LeadThreadModel(**payload.thread)
            message = LeadMessageModel(**payload.message)
            capture = RawCaptureModel(**payload.raw_capture)
            session.merge(thread)
            session.merge(message)
            session.merge(capture)
    return {"threads": len(payloads), "messages": len(payloads), "raw_captures": len(payloads)}

