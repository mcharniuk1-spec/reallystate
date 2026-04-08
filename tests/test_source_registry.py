import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bgrealestate.exporters import build_legal_risk_markdown, build_source_matrix_markdown
from bgrealestate.source_registry import SourceRegistry


REGISTRY_PATH = Path(__file__).resolve().parents[1] / "data" / "source_registry.json"


class SourceRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = SourceRegistry.from_file(REGISTRY_PATH)

    def test_registry_loads_expected_tiers(self) -> None:
        self.assertGreaterEqual(len(self.registry.by_tier(1)), 10)
        self.assertGreaterEqual(len(self.registry.by_tier(2)), 10)
        self.assertGreaterEqual(len(self.registry.by_tier(3)), 5)
        self.assertGreaterEqual(len(self.registry.by_tier(4)), 5)

    def test_registry_contains_key_priority_sources(self) -> None:
        self.assertIsNotNone(self.registry.by_name("OLX.bg"))
        self.assertIsNotNone(self.registry.by_name("Booking.com"))
        self.assertIsNotNone(self.registry.by_name("Telegram public channels"))
        self.assertIsNotNone(self.registry.by_name("Flat Manager"))
        self.assertIsNotNone(self.registry.by_name("Threads public profiles"))

    def test_registry_exposes_agent_planning_fields(self) -> None:
        booking = self.registry.by_name("Booking.com")
        self.assertEqual(booking.legal_mode, "official_partner_or_vendor_only")
        self.assertEqual(booking.mvp_phase, "reverse_publishing_and_str_intelligence")
        self.assertEqual(booking.primary_url, "https://www.booking.com/")

    def test_registry_filters_legal_review_queue(self) -> None:
        high_risk_names = {entry.source_name for entry in self.registry.legal_review_queue()}
        self.assertIn("Airbnb", high_risk_names)
        self.assertIn("WhatsApp opt-in groups", high_risk_names)
        self.assertIn("imoti.net", high_risk_names)

    def test_matrix_exports_include_seeded_sources(self) -> None:
        entries = self.registry.all()
        source_matrix = build_source_matrix_markdown(entries)
        legal_matrix = build_legal_risk_markdown(entries)
        self.assertIn("OLX.bg", source_matrix)
        self.assertIn("Booking.com", legal_matrix)


if __name__ == "__main__":
    unittest.main()
