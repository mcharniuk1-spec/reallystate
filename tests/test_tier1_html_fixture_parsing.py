from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from bgrealestate.connectors.fixtures import canonical_to_subset, fixture_dir, read_json, read_text
from bgrealestate.connectors.scaffold import HtmlPortalConnector
from bgrealestate.source_registry import SourceRegistry


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY = SourceRegistry.from_file(REPO_ROOT / "data" / "source_registry.json")

TIER1_HTML_SOURCES = [
    ("alo.bg", "alo_bg"),
    ("imot.bg", "imot_bg"),
    ("BulgarianProperties", "bulgarianproperties"),
    ("Address.bg", "address_bg"),
    ("SUPRIMMO", "suprimmo"),
    ("LUXIMMO", "luximmo"),
    ("property.bg", "property_bg"),
    ("imoti.net", "imoti_net"),
]

FIXTURE_CASES = ["basic_listing", "blocked_page"]


class TestTier1HtmlFixtureParsing(unittest.TestCase):
    """Fixture-backed parser tests for all tier-1 HTML portal/agency sources."""

    def _run_cases(self, source_name: str, fixture_slug: str) -> None:
        connector = HtmlPortalConnector(source_name, REGISTRY)
        for case in FIXTURE_CASES:
            case_dir = fixture_dir(fixture_slug) / case
            if not case_dir.exists():
                continue
            with self.subTest(source=source_name, case=case):
                html = read_text(case_dir / "raw.html")
                expected = read_json(case_dir / "expected.json")
                seed_path = case_dir / "seed.json"
                seed = json.loads(read_text(seed_path)) if seed_path.exists() else None

                out = connector.parse_and_normalize_from_html(
                    url=expected["listing_url"],
                    html=html,
                    discovered_at=datetime(2026, 4, 8, tzinfo=timezone.utc),
                    seed=seed,
                )
                canonical = out["canonical_listing"]
                subset = canonical_to_subset(canonical)
                self.assertEqual(expected, subset)

    def test_alo_bg(self) -> None:
        self._run_cases("alo.bg", "alo_bg")

    def test_imot_bg(self) -> None:
        self._run_cases("imot.bg", "imot_bg")

    def test_bulgarianproperties(self) -> None:
        self._run_cases("BulgarianProperties", "bulgarianproperties")

    def test_address_bg(self) -> None:
        self._run_cases("Address.bg", "address_bg")

    def test_suprimmo(self) -> None:
        self._run_cases("SUPRIMMO", "suprimmo")

    def test_luximmo(self) -> None:
        self._run_cases("LUXIMMO", "luximmo")

    def test_property_bg(self) -> None:
        self._run_cases("property.bg", "property_bg")

    def test_imoti_net(self) -> None:
        self._run_cases("imoti.net", "imoti_net")


class TestImotiNetLegalGate(unittest.TestCase):
    """imoti.net is legal_review_required — assert live HTTP is blocked."""

    def test_imoti_net_blocks_live_http(self) -> None:
        from bgrealestate.connectors.legal import LegalGateError, assert_live_http_allowed

        entry = REGISTRY.by_name("imoti.net")
        self.assertIsNotNone(entry)
        assert entry is not None
        with self.assertRaises(LegalGateError):
            assert_live_http_allowed(entry)


if __name__ == "__main__":
    unittest.main()
