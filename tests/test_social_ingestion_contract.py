"""Tests for the social ingestion contract — legal gates + fixture parsing.

Validates:
1. All tier-4 social/messenger sources are blocked by assert_live_http_allowed.
2. Telegram public channel lead extraction works offline against fixtures.
3. Noise messages are correctly classified.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from bgrealestate.connectors.legal import LegalGateError, assert_live_http_allowed
from bgrealestate.connectors.social_parser import extract_social_lead
from bgrealestate.source_registry import SourceRegistry

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "telegram_public"
REGISTRY_PATH = Path(__file__).resolve().parent.parent / "data" / "source_registry.json"

SOCIAL_SOURCES = [
    "Facebook public groups/pages",
    "Instagram public profiles",
    "Telegram public channels",
    "Threads public profiles",
    "Viber opt-in communities",
    "WhatsApp opt-in groups",
    "X public search/accounts",
]


class TestSocialLegalGates(unittest.TestCase):
    """All social/messenger sources must be blocked by assert_live_http_allowed."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = SourceRegistry.from_file(REGISTRY_PATH)

    def test_all_social_sources_block_live_http(self) -> None:
        for name in SOCIAL_SOURCES:
            entry = self.registry.by_name(name)
            self.assertIsNotNone(entry, f"missing from registry: {name}")
            with self.assertRaises(LegalGateError, msg=f"should block: {name}"):
                assert_live_http_allowed(entry)


class TestTelegramFixtureParsing(unittest.TestCase):
    """Validate regex-based lead extraction against Telegram fixtures."""

    def _load(self, case: str) -> tuple[dict, dict]:
        case_dir = FIXTURES / case
        raw = json.loads((case_dir / "raw.json").read_text("utf-8"))
        expected = json.loads((case_dir / "expected.json").read_text("utf-8"))
        return raw, expected

    def test_rent_listing(self) -> None:
        raw, expected = self._load("rent_listing")
        result = extract_social_lead(raw)
        self.assertEqual(result["intent"], expected["intent"])
        self.assertEqual(result["property_type"], expected["property_type"])
        self.assertEqual(result["city"], expected["city"])
        self.assertEqual(result["district"], expected["district"])
        self.assertEqual(result["price"], expected["price"])
        self.assertEqual(result["currency"], expected["currency"])
        self.assertFalse(result["is_noise"])

    def test_sale_listing(self) -> None:
        raw, expected = self._load("sale_listing")
        result = extract_social_lead(raw)
        self.assertEqual(result["intent"], expected["intent"])
        self.assertEqual(result["property_type"], expected["property_type"])
        self.assertEqual(result["city"], expected["city"])
        self.assertEqual(result["district"], expected["district"])
        self.assertEqual(result["price"], expected["price"])
        self.assertEqual(result["currency"], expected["currency"])
        self.assertFalse(result["is_noise"])

    def test_noise_message(self) -> None:
        raw, expected = self._load("noise_message")
        result = extract_social_lead(raw)
        self.assertTrue(result["is_noise"])
        self.assertIsNone(result["intent"])
        self.assertIsNone(result["property_type"])


class TestRedactionContract(unittest.TestCase):
    """Verify that all stored fixtures have redaction applied."""

    def test_all_fixtures_have_redaction_flag(self) -> None:
        for case_dir in FIXTURES.iterdir():
            if not case_dir.is_dir():
                continue
            raw_path = case_dir / "raw.json"
            if not raw_path.exists():
                continue
            raw = json.loads(raw_path.read_text("utf-8"))
            self.assertTrue(
                raw.get("redaction_applied", False),
                f"fixture {case_dir.name} missing redaction_applied=true",
            )

    def test_no_raw_phone_numbers_in_fixtures(self) -> None:
        import re
        phone_re = re.compile(r"\+\d[\d\s\-]{8,}|(?<!\d)\d{3}[\s\-]\d{3}[\s\-]\d{4}")
        for case_dir in FIXTURES.iterdir():
            if not case_dir.is_dir():
                continue
            raw_path = case_dir / "raw.json"
            if not raw_path.exists():
                continue
            raw = json.loads(raw_path.read_text("utf-8"))
            text = raw.get("raw_text", "")
            for match in phone_re.finditer(text):
                self.fail(
                    f"fixture {case_dir.name} contains un-redacted phone: {match.group()}"
                )


if __name__ == "__main__":
    unittest.main()
