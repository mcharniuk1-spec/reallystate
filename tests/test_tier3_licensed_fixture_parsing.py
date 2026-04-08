from __future__ import annotations

import unittest
from pathlib import Path

from bgrealestate.connectors.fixtures import fixture_dir, read_json, read_text
from bgrealestate.connectors.tier3 import LicensedStrDataConnector
from bgrealestate.source_registry import SourceRegistry


class TestTier3LicensedFixtureParsing(unittest.TestCase):
    def test_licensed_metrics_templates_for_airdna_and_airbtics(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        registry = SourceRegistry.from_file(repo_root / "data" / "source_registry.json")
        case_dir = fixture_dir("tier3_templates") / "licensed_data"
        raw_json_text = read_text(case_dir / "raw.json")
        expected = read_json(case_dir / "expected.json")

        for source_name in ("AirDNA", "Airbtics"):
            with self.subTest(source_name=source_name):
                connector = LicensedStrDataConnector(source_name, registry)
                metrics = connector.parse_metrics_payload(json_text=raw_json_text)
                actual = connector.metrics_to_dict(metrics)
                expected_for_source = dict(expected)
                expected_for_source["source_name"] = source_name
                self.assertEqual(expected_for_source, actual)


if __name__ == "__main__":
    unittest.main()
