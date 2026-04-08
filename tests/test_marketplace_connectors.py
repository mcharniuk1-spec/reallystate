from __future__ import annotations

import unittest
from pathlib import Path

from bgrealestate.connectors.factory import build_connector, is_marketplace_source, marketplace_sources
from bgrealestate.connectors.legal import (
    LegalGateError,
    assert_live_http_allowed,
    derive_default_legal_rule,
)
from bgrealestate.enums import SourceFamily
from bgrealestate.source_registry import SourceRegistry


class TestMarketplaceScope(unittest.TestCase):
    def test_excludes_social_and_messenger(self) -> None:
        root = Path(__file__).resolve().parents[1]
        registry = SourceRegistry.from_file(root / "data" / "source_registry.json")
        market = marketplace_sources(registry)
        self.assertEqual(len(market), 37)
        for entry in market:
            self.assertNotIn(
                entry.source_family,
                (SourceFamily.SOCIAL_PUBLIC_CHANNEL, SourceFamily.PRIVATE_MESSENGER),
            )

    def test_is_marketplace_source(self) -> None:
        root = Path(__file__).resolve().parents[1]
        registry = SourceRegistry.from_file(root / "data" / "source_registry.json")
        fb = registry.by_name("Facebook public groups/pages")
        self.assertIsNotNone(fb)
        assert fb is not None
        self.assertFalse(is_marketplace_source(fb))


class TestLegalDerivation(unittest.TestCase):
    def test_partner_blocks_scrape(self) -> None:
        root = Path(__file__).resolve().parents[1]
        registry = SourceRegistry.from_file(root / "data" / "source_registry.json")
        airbnb = registry.by_name("Airbnb")
        self.assertIsNotNone(airbnb)
        assert airbnb is not None
        rule = derive_default_legal_rule(airbnb)
        self.assertTrue(rule.blocks_live_scrape)
        self.assertTrue(rule.requires_contract)
        with self.assertRaises(LegalGateError):
            assert_live_http_allowed(airbnb)

    def test_public_crawl_allows_http_gate(self) -> None:
        root = Path(__file__).resolve().parents[1]
        registry = SourceRegistry.from_file(root / "data" / "source_registry.json")
        homes = registry.by_name("Homes.bg")
        self.assertIsNotNone(homes)
        assert homes is not None
        rule = derive_default_legal_rule(homes)
        self.assertFalse(rule.blocks_live_scrape)
        assert_live_http_allowed(homes)

    def test_licensing_blocks_ingestion(self) -> None:
        root = Path(__file__).resolve().parents[1]
        registry = SourceRegistry.from_file(root / "data" / "source_registry.json")
        imoti = registry.by_name("Imoti.info")
        self.assertIsNotNone(imoti)
        assert imoti is not None
        rule = derive_default_legal_rule(imoti)
        self.assertFalse(rule.allowed_for_ingestion)
        self.assertTrue(rule.blocks_live_scrape)


class TestConnectorFactory(unittest.TestCase):
    def test_homes_uses_specialized_class(self) -> None:
        root = Path(__file__).resolve().parents[1]
        registry = SourceRegistry.from_file(root / "data" / "source_registry.json")
        c = build_connector("Homes.bg", registry)
        self.assertEqual(c.source_name, "Homes.bg")
        self.assertEqual(type(c).__name__, "HomesBgConnector")

    def test_other_uses_scaffold(self) -> None:
        root = Path(__file__).resolve().parents[1]
        registry = SourceRegistry.from_file(root / "data" / "source_registry.json")
        c = build_connector("imot.bg", registry)
        self.assertEqual(c.source_name, "imot.bg")
        self.assertEqual(type(c).__name__, "HtmlPortalConnector")


if __name__ == "__main__":
    unittest.main()
