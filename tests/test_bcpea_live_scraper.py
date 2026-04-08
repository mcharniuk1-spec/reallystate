"""Fixture-backed tests for the BCPEA live scraper (T3-07).

These tests parse real-structure HTML fixtures without any network calls.
"""
from __future__ import annotations

import unittest
from pathlib import Path

from bgrealestate.connectors.fixtures import fixture_dir, read_json, read_text
from bgrealestate.connectors.tier3 import (
    BcpeaAuctionConnector,
    parse_bcpea_detail_html,
    parse_bcpea_discovery_html,
)
from bgrealestate.source_registry import SourceRegistry


def _registry() -> SourceRegistry:
    repo = Path(__file__).resolve().parents[1]
    return SourceRegistry.from_file(repo / "data" / "source_registry.json")


class TestBcpeaDiscoveryParsing(unittest.TestCase):
    def test_discovery_page_extracts_all_items(self) -> None:
        html = read_text(fixture_dir("bcpea") / "discovery_page1" / "raw.html")
        result = parse_bcpea_discovery_html(html)

        self.assertEqual(len(result.listings), 3)
        self.assertEqual(result.total_results, 1224)
        self.assertEqual(result.next_page, 2)
        self.assertEqual(result.last_page, 102)

    def test_discovery_item_fields(self) -> None:
        html = read_text(fixture_dir("bcpea") / "discovery_page1" / "raw.html")
        expected = read_json(fixture_dir("bcpea") / "discovery_page1" / "expected.json")
        result = parse_bcpea_discovery_html(html)

        for i, item in enumerate(result.listings):
            exp = expected["listings"][i]
            with self.subTest(i=i, external_id=exp["external_id"]):
                self.assertEqual(item.external_id, exp["external_id"])
                self.assertEqual(item.url, exp["url"])
                self.assertEqual(item.property_type, exp["property_type"])
                self.assertAlmostEqual(item.area_sqm, exp["area_sqm"], places=1)
                self.assertAlmostEqual(item.price, exp["price"], places=1)
                self.assertEqual(item.currency, exp["currency"])
                self.assertEqual(item.city, exp["city"])
                self.assertEqual(item.court, exp["court"])
                self.assertEqual(item.bailiff, exp["bailiff"])
                self.assertEqual(item.has_image, exp["has_image"])

    def test_discovery_via_connector(self) -> None:
        registry = _registry()
        connector = BcpeaAuctionConnector(registry)
        html = read_text(fixture_dir("bcpea") / "discovery_page1" / "raw.html")
        result = connector.discover_page_from_html(html)

        self.assertEqual(len(result.listings), 3)
        self.assertEqual(result.listings[0].external_id, "87739")


class TestBcpeaDetailParsing(unittest.TestCase):
    def test_detail_page_parses_all_fields(self) -> None:
        html = read_text(fixture_dir("bcpea") / "detail_87739" / "raw.html")
        expected = read_json(fixture_dir("bcpea") / "detail_87739" / "expected.json")
        result = parse_bcpea_detail_html(html, "https://sales.bcpea.org/properties/87739")

        self.assertEqual(result["source_name"], expected["source_name"])
        self.assertEqual(result["external_id"], expected["external_id"])
        self.assertEqual(result["property_type"], expected["property_type"])
        self.assertEqual(result["listing_intent"], expected["listing_intent"])
        self.assertEqual(result["construction_type"], expected["construction_type"])
        self.assertEqual(result["amenities"], expected["amenities"])
        self.assertAlmostEqual(result["area_sqm"], expected["area_sqm"], places=1)
        self.assertEqual(result["city"], expected["city"])
        self.assertEqual(result["court"], expected["court"])
        self.assertEqual(result["bailiff"], expected["bailiff"])
        self.assertEqual(result["bailiff_reg_number"], expected["bailiff_reg_number"])
        self.assertEqual(result["auction_start_date"], expected["auction_start_date"])
        self.assertEqual(result["auction_end_date"], expected["auction_end_date"])
        self.assertEqual(result["announcement_datetime"], expected["announcement_datetime"])
        self.assertEqual(result["image_urls"], expected["image_urls"])
        self.assertEqual(result["scanned_documents"], expected["scanned_documents"])
        self.assertEqual(result["bailiff_phone"], expected["bailiff_phone"])
        self.assertEqual(result["bailiff_mobile"], expected["bailiff_mobile"])
        self.assertEqual(result["parser_version"], expected["parser_version"])

    def test_detail_via_connector(self) -> None:
        registry = _registry()
        connector = BcpeaAuctionConnector(registry)
        html = read_text(fixture_dir("bcpea") / "detail_87739" / "raw.html")
        result = connector.parse_detail_html(
            html=html, url="https://sales.bcpea.org/properties/87739"
        )

        self.assertEqual(result["external_id"], "87739")
        self.assertEqual(result["property_type"], "Къща")
        self.assertEqual(result["area_sqm"], 689.0)

    def test_description_snippet_extracted(self) -> None:
        html = read_text(fixture_dir("bcpea") / "detail_87739" / "raw.html")
        result = parse_bcpea_detail_html(html, "https://sales.bcpea.org/properties/87739")

        self.assertIsNotNone(result["description_snippet"])
        self.assertIn("21587.503.31", result["description_snippet"])


class TestBcpeaLegacyBackCompat(unittest.TestCase):
    """Verify the old T3-03 template parser still works."""

    def test_legacy_template_parser_still_works(self) -> None:
        html = read_text(fixture_dir("tier3_templates") / "public_auction" / "raw.html")
        expected = read_json(fixture_dir("tier3_templates") / "public_auction" / "expected.json")
        registry = _registry()
        connector = BcpeaAuctionConnector(registry)
        result = connector.parse_auction_html(html=html)
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
