from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha1
from typing import Any

from ..models import RawCapture
from .social_parser import extract_social_lead

PARSER_VERSION = "x_public_v1"


def _stable_id(prefix: str, value: str) -> str:
    return f"{prefix}_{sha1(value.encode('utf-8')).hexdigest()[:18]}"


def _parse_posted_at(value: str) -> datetime:
    return datetime.fromisoformat(value)


@dataclass(frozen=True)
class XPublicLeadPayload:
    lead_thread: dict[str, Any]
    lead_message: dict[str, Any]
    raw_capture: RawCapture
    extracted: dict[str, Any]


class XPublicConnector:
    """Fixture-first mapper for X public accounts/search posts.

    This connector is intentionally offline for tests and does not perform
    live network calls.
    """

    source_name = "X public search/accounts"
    _allowed_consent_statuses = {"public_profile_via_official_api"}

    def map_post_to_lead(
        self,
        raw_post: dict[str, Any],
        *,
        account_id: str,
        channel_account_id: str | None = None,
    ) -> XPublicLeadPayload:
        source_name = str(raw_post.get("source_name", ""))
        if source_name != self.source_name:
            raise ValueError(f"unexpected source_name={source_name!r}")
        if not bool(raw_post.get("redaction_applied", False)):
            raise ValueError("redaction_applied must be true for X fixtures")

        consent_status = str(raw_post.get("consent_status", ""))
        if consent_status not in self._allowed_consent_statuses:
            raise ValueError(f"unsupported consent_status={consent_status!r} for X connector")

        account_handle = str(raw_post.get("account_id", "")).strip()
        message_id = str(raw_post.get("message_id", "")).strip()
        if not account_handle or not message_id:
            raise ValueError("account_id and message_id are required")

        posted_at = _parse_posted_at(str(raw_post.get("posted_at")))
        raw_text = str(raw_post.get("raw_text", ""))
        media_urls = list(raw_post.get("media_urls", []))
        extracted = extract_social_lead(raw_post)

        thread_external_id = f"x:{account_handle}"
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
            "sender_id": f"x:{account_handle}",
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
                "account_id": account_handle,
                "consent_status": consent_status,
                "redaction_applied": True,
                "media_urls": media_urls,
                "extracted": extracted,
            },
        }

        raw_capture = RawCapture(
            source_name=self.source_name,
            url=f"https://x.com/{account_handle}/status/{message_id}",
            content_type="application/json",
            body=json.dumps(raw_post, ensure_ascii=False),
            fetched_at=posted_at,
            parser_version=PARSER_VERSION,
            metadata={
                "account_id": account_handle,
                "message_id": message_id,
                "consent_status": consent_status,
                "redaction_applied": True,
            },
        )

        return XPublicLeadPayload(
            lead_thread=lead_thread,
            lead_message=lead_message,
            raw_capture=raw_capture,
            extracted=extracted,
        )

