from __future__ import annotations

import json
import os
import unittest
from typing import Any
from unittest.mock import patch


class _FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self.payload


class _FakeClient:
    calls: list[dict[str, Any]] = []

    def __init__(self, timeout: float) -> None:
        self.timeout = timeout

    def __enter__(self) -> "_FakeClient":
        return self

    def __exit__(self, *args: Any) -> None:
        return None

    def post(self, url: str, *, content: str, headers: dict[str, str]) -> _FakeResponse:
        self.calls.append({"url": url, "content": json.loads(content), "headers": headers, "timeout": self.timeout})
        return _FakeResponse({"message": {"content": "Ollama test response"}})


class TestChatService(unittest.TestCase):
    def setUp(self) -> None:
        self._prev = {
            "CHAT_PROVIDER": os.environ.get("CHAT_PROVIDER"),
            "OLLAMA_CHAT_MODEL": os.environ.get("OLLAMA_CHAT_MODEL"),
            "OLLAMA_BASE_URL": os.environ.get("OLLAMA_BASE_URL"),
        }
        os.environ["CHAT_PROVIDER"] = "ollama"
        os.environ["OLLAMA_CHAT_MODEL"] = "gemma4:26b"
        os.environ["OLLAMA_BASE_URL"] = "http://127.0.0.1:11434"
        _FakeClient.calls.clear()

    def tearDown(self) -> None:
        for key, val in self._prev.items():
            if val is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = val

    def test_ollama_provider_uses_local_chat_endpoint(self) -> None:
        from bgrealestate.services.chat_service import run_chat_completion

        with patch("bgrealestate.services.chat_service.httpx.Client", _FakeClient):
            text, provider = run_chat_completion([{"role": "user", "content": "hello"}], timeout_s=3)

        self.assertEqual(provider, "ollama")
        self.assertEqual(text, "Ollama test response")
        self.assertEqual(_FakeClient.calls[0]["url"], "http://127.0.0.1:11434/api/chat")
        self.assertEqual(_FakeClient.calls[0]["content"]["model"], "gemma4:26b")
        self.assertFalse(_FakeClient.calls[0]["content"]["stream"])

    def test_ollama_failure_falls_back_to_stub(self) -> None:
        from bgrealestate.services.chat_service import run_chat_completion

        with patch(
            "bgrealestate.services.chat_service._ollama_chat_completion",
            side_effect=RuntimeError("offline"),
        ):
            text, provider = run_chat_completion([{"role": "user", "content": "hello"}], timeout_s=3)

        self.assertEqual(provider, "stub")
        self.assertIn("hello", text)
        self.assertIn("Ollama unavailable", text)


if __name__ == "__main__":
    unittest.main()
