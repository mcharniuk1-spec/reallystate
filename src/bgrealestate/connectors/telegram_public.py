from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha1
from typing import Any

from ..models import RawCapture
from .social_parser import extract_social_lead

PARSER_VERSION = "telegram_public_v1"


def _stable_id(prefix: str, value: str) -> str:
    return f"{prefix}_{sha1(value.encode('utf-8')).hexdigest()[:18]}"


def _parse_posted_at(value: str) -> datetime:
    return datetime.fromisoformat(value)


@dataclass(frozen=True)
class TelegramCrmPayload:
    lead_thread: dict[str, Any]
    lead_message: dict[str, Any]
    raw_capture: RawCapture
    extracted: dict[str, Any]


class TelegramPublicConnector:
    """Fixture-first Telegram public channel mapper for CRM ingestion.

    This connector does not perform any live network IO in MVP tests.
    It accepts already-fetched/redacted message payloads and maps them to
    CRM-ready thread/message payloads.
    """

    source_name = "Telegram public channels"

    def map_message_to_crm(
        self,
        raw_message: dict[str, Any],
        *,
        account_id: str,
        channel_account_id: str | None = None,
    ) -> TelegramCrmPayload:
        source_name = str(raw_message.get("source_name", ""))
        if source_name != self.source_name:
            raise ValueError(f"unexpected source_name={source_name!r}")
        if not bool(raw_message.get("redaction_applied", False)):
            raise ValueError("redaction_applied must be true for Telegram fixtures")
        if raw_message.get("consent_status") != "public_channel_broadcast":
            raise ValueError("Telegram connector accepts only public_channel_broadcast consent_status")

        channel_id = str(raw_message.get("channel_id", "")).strip()
        message_id = str(raw_message.get("message_id", "")).strip()
        if not channel_id or not message_id:
            raise ValueError("channel_id and message_id are required")

        posted_at = _parse_posted_at(str(raw_message.get("posted_at")))
        raw_text = str(raw_message.get("raw_text", ""))
        media_urls = list(raw_message.get("media_urls", []))
        extracted = extract_social_lead(raw_message)

        thread_external_id = f"telegram:{channel_id}"
        lead_thread = {
            "thread_id": _stable_id("lthr", f"{account_id}:{thread_external_id}"),
            "account_id": account_id,
            "channel_account_id": channel_account_id,
            "external_thread_id": thread_external_id,
            "lead_contact_id": None,
            "status": "new",
            "stage": "new",
            "assignee_user_id": None,
            "priority": "normal",
            "unread_count": 1,
            "last_message_at": posted_at,
            "follow_up_due_at": None,
            "created_at": posted_at,
        }

        lead_message = {
            "message_id": _stable_id("lmsg", f"{thread_external_id}:{message_id}"),
            "thread_id": lead_thread["thread_id"],
            "direction": "inbound",
            "sender_type": "lead",
            "sender_id": f"telegram:{channel_id}",
            "external_message_id": message_id,
            "body_text": raw_text,
            "body_html": None,
            "language": None,
            "sent_at": posted_at,
            "received_at": posted_at,
            "delivery_status": "stored",
            "metadata_jsonb": {
                "kind": "social_overlay",
                "source_name": self.source_name,
                "channel_id": channel_id,
                "consent_status": raw_message.get("consent_status"),
                "redaction_applied": True,
                "media_urls": media_urls,
                "extracted": extracted,
            },
        }

        raw_capture = RawCapture(
            source_name=self.source_name,
            url=f"https://t.me/{channel_id}/{message_id}",
            content_type="application/json",
            body=json.dumps(raw_message, ensure_ascii=False),
            fetched_at=posted_at,
            parser_version=PARSER_VERSION,
            metadata={
                "channel_id": channel_id,
                "message_id": message_id,
                "consent_status": raw_message.get("consent_status"),
                "redaction_applied": True,
            },
        )

        return TelegramCrmPayload(
            lead_thread=lead_thread,
            lead_message=lead_message,
            raw_capture=raw_capture,
            extracted=extracted,
        )

