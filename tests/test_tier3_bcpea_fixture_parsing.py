from __future__ import annotations

import unittest
from pathlib import Path

from bgrealestate.connectors.fixtures import fixture_dir, read_json, read_text
from bgrealestate.connectors.tier3 import BcpeaAuctionConnector
from bgrealestate.source_registry import SourceRegistry


class TestTier3BcpeaFixtureParsing(unittest.TestCase):
    def test_bcpea_template_parses_expected_fields(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        registry = SourceRegistry.from_file(repo_root / "data" / "source_registry.json")
        connector = BcpeaAuctionConnector(registry)
        case_dir = fixture_dir("tier3_templates") / "public_auction"
        html = read_text(case_dir / "raw.html")
        expected = read_json(case_dir / "expected.json")
        actual = connector.parse_auction_html(html=html)
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
