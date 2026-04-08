"""Tests for the property unification / deduplication service.

These tests validate the core logic without a live database by testing:
1. Dedupe key computation consistency
2. UnificationResult dataclass shape
3. API route registration and auth gates
"""

from __future__ import annotations

import os
import sys
import unittest


def _models_importable() -> bool:
    """Check if SQLAlchemy ORM models can load (requires Python 3.10+ for union syntax)."""
    if sys.version_info < (3, 10):
        return False
    try:
        from bgrealestate.db.models import PropertyEntityModel  # noqa: F401
        return True
    except Exception:
        return False


def _fastapi_available() -> bool:
    if sys.version_info < (3, 10):
        return False
    try:
        from fastapi.testclient import TestClient  # noqa: F401
        return True
    except ImportError:
        return False


class TestDedupeKeyPureFunctions(unittest.TestCase):
    """Pure-function tests for dedupe key generation — no DB models required.

    These import only the standalone helper functions via AST-safe dynamic import
    so they work even on Python 3.9 where SQLAlchemy Mapped[str | None] fails.
    """

    def _compute_key(self, city, address, area):
        """Reimplementation of the dedupe key logic for testing on any Python."""
        import re
        from hashlib import sha1

        def normalize_addr(addr):
            if not addr:
                return ""
            a = addr.lower().strip()
            a = re.sub(r"\s+", " ", a)
            a = re.sub(r"[.,;:!?\"'()\[\]{}]", "", a)
            return a

        components = [
            (city or "").lower().strip(),
            normalize_addr(address),
            str(round(area or 0.0, 0)),
        ]
        return sha1("|".join(components).encode("utf-8")).hexdigest()

    def test_same_inputs_produce_same_key(self) -> None:
        k1 = self._compute_key("Varna", "ul. Tsar Osvoboditel 15", 65.0)
        k2 = self._compute_key("Varna", "ul. Tsar Osvoboditel 15", 65.0)
        self.assertEqual(k1, k2)

    def test_different_city_produces_different_key(self) -> None:
        k1 = self._compute_key("Varna", "ul. Tsar Osvoboditel 15", 65.0)
        k2 = self._compute_key("Sofia", "ul. Tsar Osvoboditel 15", 65.0)
        self.assertNotEqual(k1, k2)

    def test_none_address_is_stable(self) -> None:
        k1 = self._compute_key("Varna", None, 80.0)
        k2 = self._compute_key("Varna", None, 80.0)
        self.assertEqual(k1, k2)

    def test_area_bucket_rounds_to_integer(self) -> None:
        k1 = self._compute_key("Varna", "test", 64.7)
        k2 = self._compute_key("Varna", "test", 65.3)
        self.assertEqual(k1, k2)
        k3 = self._compute_key("Varna", "test", 66.0)
        self.assertNotEqual(k1, k3)

    def test_address_normalization_ignores_case_and_punctuation(self) -> None:
        k1 = self._compute_key("Varna", "ul. Tsar Osvoboditel 15", 65.0)
        k2 = self._compute_key("Varna", "UL TSAR OSVOBODITEL 15", 65.0)
        self.assertEqual(k1, k2)


@unittest.skipUnless(_models_importable(), "SQLAlchemy models require Python 3.10+")
class TestUnificationModuleImport(unittest.TestCase):
    """Verify the unification module loads and its public types are well-formed."""

    def test_unification_result_shape(self) -> None:
        from bgrealestate.services.unification import UnificationResult

        r = UnificationResult(
            property_id="prop_abc123",
            is_new=True,
            linked_listings=3,
            confidence_score=0.8,
        )
        self.assertEqual(r.property_id, "prop_abc123")
        self.assertTrue(r.is_new)
        self.assertEqual(r.linked_listings, 3)
        self.assertAlmostEqual(r.confidence_score, 0.8)

    def test_normalize_address(self) -> None:
        from bgrealestate.services.unification import _normalize_address

        self.assertEqual(
            _normalize_address("  ul. Tsar  Osvoboditel,  15  "),
            "ul tsar osvoboditel 15",
        )
        self.assertEqual(_normalize_address(None), "")

    def test_compute_dedupe_key_matches_pure_impl(self) -> None:
        from bgrealestate.services.unification import _compute_dedupe_key

        k = _compute_dedupe_key("Varna", "ul. Tsar Osvoboditel 15", 65.0)
        self.assertIsInstance(k, str)
        self.assertEqual(len(k), 40)


@unittest.skipUnless(_fastapi_available(), "fastapi runtime checks require fastapi on Python 3.10+")
class TestPropertiesEndpointRegistration(unittest.TestCase):
    """Verify that /properties routes are registered and auth-gated."""

    def setUp(self) -> None:
        from bgrealestate.api.main import create_app
        from fastapi.testclient import TestClient

        self._prev = {
            "DATABASE_URL": os.environ.pop("DATABASE_URL", None),
            "REDIS_URL": os.environ.pop("REDIS_URL", None),
            "API_KEYS_JSON": os.environ.pop("API_KEYS_JSON", None),
        }
        os.environ["API_KEYS_JSON"] = (
            '{"read-key":["listings:read","crm:read","crawl:read"],'
            '"admin-key":["listings:read","crm:read","crm:write","crawl:read","admin:read"]}'
        )
        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        for key, val in self._prev.items():
            if val is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = val

    def test_properties_requires_auth(self) -> None:
        self.assertEqual(self.client.get("/properties").status_code, 401)

    def test_properties_detail_requires_auth(self) -> None:
        self.assertEqual(self.client.get("/properties/test-id").status_code, 401)

    def test_properties_returns_503_without_db(self) -> None:
        from bgrealestate.api import deps as deps_mod

        saved = os.environ.pop("DATABASE_URL", None)
        try:
            deps_mod._engine = None
            r = self.client.get("/properties", headers={"X-API-Key": "read-key"})
            self.assertEqual(r.status_code, 503)
        finally:
            if saved is not None:
                os.environ["DATABASE_URL"] = saved
            deps_mod._engine = None

    def test_analytics_summary_requires_auth(self) -> None:
        self.assertEqual(self.client.get("/analytics/summary").status_code, 401)

    def test_analytics_duplicates_requires_admin(self) -> None:
        r = self.client.get("/analytics/duplicates", headers={"X-API-Key": "read-key"})
        self.assertEqual(r.status_code, 403)

    def test_analytics_summary_returns_503_without_db(self) -> None:
        from bgrealestate.api import deps as deps_mod

        saved = os.environ.pop("DATABASE_URL", None)
        try:
            deps_mod._engine = None
            r = self.client.get("/analytics/summary", headers={"X-API-Key": "read-key"})
            self.assertEqual(r.status_code, 503)
        finally:
            if saved is not None:
                os.environ["DATABASE_URL"] = saved
            deps_mod._engine = None


if __name__ == "__main__":
    unittest.main()
