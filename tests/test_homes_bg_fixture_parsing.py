from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from bgrealestate.connectors.fixtures import canonical_to_subset, fixture_dir, read_json, read_text
from bgrealestate.connectors.homes_bg import HomesBgConnector
from bgrealestate.source_registry import SourceRegistry


class TestHomesBgFixtureParsing(unittest.TestCase):
    def test_homes_bg_fixtures(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        registry = SourceRegistry.from_file(repo_root / "data" / "source_registry.json")
        connector = HomesBgConnector(registry)

        for case in [
            "basic_listing",
            "missing_geo",
            "missing_price",
            "blocked_page",
            "removed_404",
        ]:
            with self.subTest(case=case):
                case_dir = fixture_dir("homes_bg") / case
                html = read_text(case_dir / "raw.html")
                expected = read_json(case_dir / "expected.json")
                seed_path = case_dir / "seed.json"
                seed = json.loads(read_text(seed_path)) if seed_path.exists() else None

                out = connector.parse_and_normalize_from_html(
                    url=expected["listing_url"],
                    html=html,
                    discovered_at=datetime(2026, 4, 7, tzinfo=timezone.utc),
                    seed=seed,
                )
                canonical = out["canonical_listing"]
                subset = canonical_to_subset(canonical)
                self.assertEqual(expected, subset)


if __name__ == "__main__":
    unittest.main()

