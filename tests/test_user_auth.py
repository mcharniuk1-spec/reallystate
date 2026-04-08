"""Tests for user authentication service — pure functions (no DB required)."""

from __future__ import annotations

import os
import sys
import time
import unittest


class TestPasswordHashing(unittest.TestCase):
    def test_hash_and_verify(self) -> None:
        from bgrealestate.services.user_auth import hash_password, verify_password

        pw = "my-secure-password-123"
        h = hash_password(pw)
        self.assertTrue(h.startswith("pbkdf2:sha256:100000$"))
        self.assertTrue(verify_password(pw, h))

    def test_wrong_password_fails(self) -> None:
        from bgrealestate.services.user_auth import hash_password, verify_password

        h = hash_password("correct-password")
        self.assertFalse(verify_password("wrong-password", h))

    def test_different_hashes_for_same_password(self) -> None:
        from bgrealestate.services.user_auth import hash_password

        h1 = hash_password("same-pw")
        h2 = hash_password("same-pw")
        self.assertNotEqual(h1, h2)

    def test_verify_garbage_hash_returns_false(self) -> None:
        from bgrealestate.services.user_auth import verify_password

        self.assertFalse(verify_password("anything", "not-a-valid-hash"))
        self.assertFalse(verify_password("anything", ""))


class TestJWT(unittest.TestCase):
    def setUp(self) -> None:
        self._prev_secret = os.environ.get("JWT_SECRET")
        os.environ["JWT_SECRET"] = "test-secret-for-unit-tests"

    def tearDown(self) -> None:
        if self._prev_secret is None:
            os.environ.pop("JWT_SECRET", None)
        else:
            os.environ["JWT_SECRET"] = self._prev_secret

    def test_create_and_decode(self) -> None:
        from bgrealestate.services.user_auth import create_jwt, decode_jwt

        import bgrealestate.services.user_auth as mod
        mod.JWT_SECRET = "test-secret-for-unit-tests"

        token = create_jwt("usr_abc", "test@example.com", "buyer")
        self.assertIsInstance(token, str)
        parts = token.split(".")
        self.assertEqual(len(parts), 3)

        payload = decode_jwt(token)
        self.assertIsNotNone(payload)
        assert payload is not None
        self.assertEqual(payload.user_id, "usr_abc")
        self.assertEqual(payload.email, "test@example.com")
        self.assertEqual(payload.user_mode, "buyer")
        self.assertGreater(payload.exp, int(time.time()))

    def test_tampered_token_rejected(self) -> None:
        from bgrealestate.services.user_auth import create_jwt, decode_jwt
        import bgrealestate.services.user_auth as mod
        mod.JWT_SECRET = "test-secret-for-unit-tests"

        token = create_jwt("usr_abc", "test@example.com", "buyer")
        tampered = token[:-5] + "XXXXX"
        self.assertIsNone(decode_jwt(tampered))

    def test_expired_token_rejected(self) -> None:
        from bgrealestate.services.user_auth import decode_jwt
        import bgrealestate.services.user_auth as mod
        mod.JWT_SECRET = "test-secret-for-unit-tests"

        old_expiry = mod.JWT_EXPIRY_SECONDS
        mod.JWT_EXPIRY_SECONDS = -10
        try:
            from bgrealestate.services.user_auth import create_jwt
            token = create_jwt("usr_abc", "test@example.com", "buyer")
            self.assertIsNone(decode_jwt(token))
        finally:
            mod.JWT_EXPIRY_SECONDS = old_expiry

    def test_garbage_token_returns_none(self) -> None:
        from bgrealestate.services.user_auth import decode_jwt

        self.assertIsNone(decode_jwt("not.a.jwt"))
        self.assertIsNone(decode_jwt(""))
        self.assertIsNone(decode_jwt("single-part"))


class TestUserModes(unittest.TestCase):
    def test_valid_modes(self) -> None:
        from bgrealestate.services.user_auth import VALID_USER_MODES

        self.assertIn("buyer", VALID_USER_MODES)
        self.assertIn("renter", VALID_USER_MODES)
        self.assertIn("seller", VALID_USER_MODES)
        self.assertIn("agent", VALID_USER_MODES)
        self.assertNotIn("admin", VALID_USER_MODES)


def _fastapi_available() -> bool:
    if sys.version_info < (3, 10):
        return False
    try:
        from fastapi.testclient import TestClient  # noqa: F401
        return True
    except ImportError:
        return False


@unittest.skipUnless(_fastapi_available(), "fastapi runtime checks require fastapi on Python 3.10+")
class TestAuthEndpointRegistration(unittest.TestCase):
    """Verify that auth/user routes are registered."""

    def setUp(self) -> None:
        from bgrealestate.api.main import create_app
        from fastapi.testclient import TestClient

        self._prev = {
            "DATABASE_URL": os.environ.pop("DATABASE_URL", None),
            "API_KEYS_JSON": os.environ.pop("API_KEYS_JSON", None),
        }
        os.environ["API_KEYS_JSON"] = '{"admin-key":["admin:read","listings:read"]}'
        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        for key, val in self._prev.items():
            if val is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = val

    def test_register_returns_503_without_db(self) -> None:
        from bgrealestate.api import deps as deps_mod
        deps_mod._engine = None
        r = self.client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "secure123",
            "display_name": "Test User",
        })
        self.assertEqual(r.status_code, 503)

    def test_login_returns_503_without_db(self) -> None:
        from bgrealestate.api import deps as deps_mod
        deps_mod._engine = None
        r = self.client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "secure123",
        })
        self.assertEqual(r.status_code, 503)

    def test_profile_requires_bearer_token(self) -> None:
        r = self.client.get("/users/me")
        self.assertEqual(r.status_code, 401)

    def test_saved_requires_bearer_token(self) -> None:
        r = self.client.get("/users/me/saved")
        self.assertEqual(r.status_code, 401)

    def test_dashboard_requires_bearer_token(self) -> None:
        r = self.client.get("/users/me/dashboard")
        self.assertEqual(r.status_code, 401)


if __name__ == "__main__":
    unittest.main()
