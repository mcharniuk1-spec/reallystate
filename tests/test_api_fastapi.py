from __future__ import annotations

import os
import unittest

try:
    from fastapi.testclient import TestClient
except ImportError:  # pragma: no cover
    TestClient = None  # type: ignore[assignment,misc]


class TestFastAPIApp(unittest.TestCase):
    def setUp(self) -> None:
        if TestClient is None:
            self.skipTest("fastapi not installed in this environment")
        from bgrealestate.api.main import create_app

        self._prev = {
            "DATABASE_URL": os.environ.pop("DATABASE_URL", None),
            "REDIS_URL": os.environ.pop("REDIS_URL", None),
            "CHAT_PROVIDER": os.environ.pop("CHAT_PROVIDER", None),
            "OPENAI_API_KEY": os.environ.pop("OPENAI_API_KEY", None),
        }
        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        for key, val in self._prev.items():
            if val is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = val

    def test_health(self) -> None:
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data.get("status"), "ok")
        self.assertEqual(data.get("runtime"), "fastapi")

    def test_ready_without_deps(self) -> None:
        r = self.client.get("/api/v1/ready")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body.get("status"), "ok")

    def test_chat_stub(self) -> None:
        r = self.client.post(
            "/api/v1/chat",
            json={"messages": [{"role": "user", "content": "Hello from test"}]},
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data.get("provider"), "stub")
        self.assertIn("Hello from test", data.get("message", ""))

    def test_listings_returns_503_without_database_url(self) -> None:
        from bgrealestate.api import deps as deps_mod

        saved = os.environ.pop("DATABASE_URL", None)
        try:
            deps_mod._engine = None  # reset cached engine between env changes
            r = self.client.get("/listings")
            self.assertEqual(r.status_code, 503)
            self.assertIn("detail", r.json())
        finally:
            if saved is not None:
                os.environ["DATABASE_URL"] = saved
            deps_mod._engine = None

    def test_crm_threads_returns_503_without_database_url(self) -> None:
        from bgrealestate.api import deps as deps_mod

        saved = os.environ.pop("DATABASE_URL", None)
        try:
            deps_mod._engine = None
            r = self.client.get("/crm/threads")
            self.assertEqual(r.status_code, 503)
        finally:
            if saved is not None:
                os.environ["DATABASE_URL"] = saved
            deps_mod._engine = None
