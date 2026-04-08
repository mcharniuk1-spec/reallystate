from __future__ import annotations

import json
import os
from typing import Any

import httpx
import structlog

log = structlog.get_logger(__name__)


def _last_user_text(messages: list[dict[str, Any]]) -> str:
    for m in reversed(messages):
        if m.get("role") == "user" and isinstance(m.get("content"), str):
            return m["content"]
    return ""


def _stub_reply(messages: list[dict[str, Any]]) -> str:
    text = _last_user_text(messages).strip()
    if not text:
        return (
            "Stub assistant: send a message to continue. "
            "Set CHAT_PROVIDER=openai and OPENAI_API_KEY for live LLM replies."
        )
    return f"Stub assistant (local/dev): I received: {text[:2000]}"


def _openai_chat_completion(
    messages: list[dict[str, Any]],
    *,
    model: str,
    api_key: str,
    timeout_s: float,
) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    payload = {"model": model, "messages": messages, "temperature": 0.3}
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    with httpx.Client(timeout=timeout_s) as client:
        res = client.post(url, headers=headers, content=json.dumps(payload))
        res.raise_for_status()
        data = res.json()
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError("openai_response_missing_choices")
    msg = choices[0].get("message") or {}
    content = msg.get("content")
    if not isinstance(content, str):
        raise RuntimeError("openai_response_missing_content")
    return content


def run_chat_completion(
    messages: list[dict[str, Any]],
    *,
    model: str | None = None,
    timeout_s: float = 60.0,
) -> tuple[str, str]:
    """Return (assistant_text, provider_used)."""
    provider = os.getenv("CHAT_PROVIDER", "stub").strip().lower()
    key = os.getenv("OPENAI_API_KEY", "").strip()
    mdl: str = (model or os.getenv("OPENAI_CHAT_MODEL") or "gpt-4o-mini").strip()

    if provider == "openai" and key:
        try:
            text = _openai_chat_completion(messages, model=mdl, api_key=key, timeout_s=timeout_s)
            return text, "openai"
        except Exception as exc:  # noqa: BLE001 — surface as stub fallback for resilience
            log.warning("openai_chat_failed", error=str(exc))
            return _stub_reply(messages) + f"\n\n(OpenAI error; fell back to stub: {exc})", "stub"

    return _stub_reply(messages), "stub"
