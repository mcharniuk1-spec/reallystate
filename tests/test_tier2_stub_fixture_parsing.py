from __future__ import annotations

import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, ClassVar, cast

from bgrealestate.connectors.factory import build_connector
from bgrealestate.connectors.fixtures import canonical_to_subset, fixture_dir, read_json, read_text
from bgrealestate.connectors.legal import LegalGateError
from bgrealestate.connectors.tier2_stubs import BazarBgConnector, DomazaConnector, Home2UConnector, YavlenaConnector
from bgrealestate.source_registry import SourceRegistry


class TestTier2StubFixtures(unittest.TestCase):
    registry: ClassVar[SourceRegistry]

    @classmethod
    def setUpClass(cls) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        cls.registry = SourceRegistry.from_file(repo_root / "data" / "source_registry.json")

    def _run_case(self, source_name: str, fixture_key: str, case_name: str = "basic_listing") -> None:
        connector = cast(Any, build_connector(source_name, self.registry))
        case_dir = fixture_dir(fixture_key) / case_name
        html = read_text(case_dir / "raw.html")
        expected = read_json(case_dir / "expected.json")
        seed_path = case_dir / "seed.json"
        seed = read_json(seed_path) if seed_path.exists() else None
        out = connector.parse_and_normalize_from_html(
            url=expected["listing_url"],
            html=html,
            discovered_at=datetime(2026, 4, 8, tzinfo=timezone.utc),
            seed=seed,
        )
        self.assertEqual(expected, canonical_to_subset(out["canonical_listing"]))

    def test_bazar_bg_fixture(self) -> None:
        self._run_case("Bazar.bg", "bazar_bg")

    def test_domaza_fixture(self) -> None:
        self._run_case("Domaza", "domaza")

    def test_yavlena_fixture(self) -> None:
        self._run_case("Yavlena", "yavlena")

    def test_home2u_fixture(self) -> None:
        self._run_case("Home2U", "home2u")

    def test_bazar_bg_land_fixture(self) -> None:
        self._run_case("Bazar.bg", "bazar_bg", "land_listing")

    def test_yavlena_long_term_rent_fixture(self) -> None:
        self._run_case("Yavlena", "yavlena", "long_term_rent")

    def test_domaza_short_term_rent_fixture(self) -> None:
        self._run_case("Domaza", "domaza", "short_term_rent")

    def test_home2u_new_build_fixture(self) -> None:
        self._run_case("Home2U", "home2u", "new_build")

    def test_factory_returns_tier2_stub_classes(self) -> None:
        registry = self.registry
        self.assertIsInstance(build_connector("Bazar.bg", registry), BazarBgConnector)
        self.assertIsInstance(build_connector("Domaza", registry), DomazaConnector)
        self.assertIsInstance(build_connector("Yavlena", registry), YavlenaConnector)
        self.assertIsInstance(build_connector("Home2U", registry), Home2UConnector)


class TestTier2LegalGate(unittest.TestCase):
    def test_imoti_info_live_fetch_blocked(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        registry = SourceRegistry.from_file(repo_root / "data" / "source_registry.json")
        connector = build_connector("Imoti.info", registry)
        with self.assertRaises(LegalGateError):
            connector.fetch_listing_detail(
                url="https://imoti.info/ad/blocked",
                fetched_at=datetime(2026, 4, 8, tzinfo=timezone.utc),
            )


if __name__ == "__main__":
    unittest.main()
