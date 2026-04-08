from __future__ import annotations

import unittest
from datetime import datetime, timezone
from pathlib import Path

from bgrealestate.connectors.fixtures import fixture_dir, read_json, read_text
from bgrealestate.connectors.tier3 import PartnerContractRequired, PartnerFeedStubConnector
from bgrealestate.source_registry import SourceRegistry


class TestTier3PartnerStubs(unittest.TestCase):
    def test_partner_payload_templates_for_ota_sources(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        registry = SourceRegistry.from_file(repo_root / "data" / "source_registry.json")
        case_dir = fixture_dir("tier3_templates") / "partner_feed"
        raw_json_text = read_text(case_dir / "raw.json")
        expected = read_json(case_dir / "expected.json")

        for source_name in ("Airbnb", "Booking.com", "Vrbo"):
            with self.subTest(source_name=source_name):
                connector = PartnerFeedStubConnector(source_name, registry)
                actual = connector.parse_partner_payload(json_text=raw_json_text)
                expected_for_source = dict(expected)
                expected_for_source["source_name"] = source_name
                expected_for_source["reference_id"] = f"{source_name}:{expected['external_id']}"
                self.assertEqual(expected_for_source, actual)

    def test_live_fetch_requires_partner_contract(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        registry = SourceRegistry.from_file(repo_root / "data" / "source_registry.json")
        connector = PartnerFeedStubConnector("Airbnb", registry)
        with self.assertRaises(PartnerContractRequired):
            connector.fetch_listing_detail(
                url="https://partner.example/listings/PARTNER-UNIT-123",
                fetched_at=datetime(2026, 4, 8, tzinfo=timezone.utc),
            )


if __name__ == "__main__":
    unittest.main()
