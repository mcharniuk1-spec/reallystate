from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from bgrealestate.connectors.x_public import XPublicConnector

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "x_public"


class TestXPublicConnector(unittest.TestCase):
    def setUp(self) -> None:
        self.connector = XPublicConnector()
        self.account_id = "acct_test_1"

    def _load_case(self, case: str) -> tuple[dict, dict]:
        case_dir = FIXTURES / case
        raw = json.loads((case_dir / "raw.json").read_text("utf-8"))
        expected = json.loads((case_dir / "expected.json").read_text("utf-8"))
        return raw, expected

    def test_maps_sale_post(self) -> None:
        raw, expected = self._load_case("sale_post")
        payload = self.connector.map_post_to_lead(raw, account_id=self.account_id)
        self.assertEqual(payload.extracted["intent"], expected["intent"])
        self.assertEqual(payload.extracted["property_type"], expected["property_type"])
        self.assertEqual(payload.extracted["city"], expected["city"])
        self.assertEqual(payload.extracted["district"], expected["district"])
        self.assertEqual(payload.extracted["price"], expected["price"])
        self.assertEqual(payload.extracted["currency"], expected["currency"])
        self.assertEqual(payload.extracted["is_noise"], expected["is_noise"])
        self.assertEqual(payload.lead_thread["external_thread_id"], "x:super_imoti")
        self.assertEqual(payload.lead_message["external_message_id"], "1891234567890000000")

    def test_maps_noise_post(self) -> None:
        raw, expected = self._load_case("noise_post")
        payload = self.connector.map_post_to_lead(raw, account_id=self.account_id)
        self.assertEqual(payload.extracted["intent"], expected["intent"])
        self.assertEqual(payload.extracted["property_type"], expected["property_type"])
        self.assertEqual(payload.extracted["city"], expected["city"])
        self.assertEqual(payload.extracted["district"], expected["district"])
        self.assertEqual(payload.extracted["price"], expected["price"])
        self.assertEqual(payload.extracted["currency"], expected["currency"])
        self.assertEqual(payload.extracted["is_noise"], expected["is_noise"])

    def test_rejects_non_redacted_fixture(self) -> None:
        raw, _ = self._load_case("sale_post")
        raw["redaction_applied"] = False
        with self.assertRaises(ValueError):
            self.connector.map_post_to_lead(raw, account_id=self.account_id)

    def test_fixture_has_no_raw_phone_numbers(self) -> None:
        phone_re = re.compile(r"\+\d[\d\s\-]{8,}|(?<!\d)\d{3}[\s\-]\d{3}[\s\-]\d{4}")
        for case in ("sale_post", "noise_post"):
            raw, _ = self._load_case(case)
            self.assertTrue(raw.get("redaction_applied", False))
            self.assertIsNone(phone_re.search(raw.get("raw_text", "")))


if __name__ == "__main__":
    unittest.main()

