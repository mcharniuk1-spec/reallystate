from __future__ import annotations

import json
import unittest
from pathlib import Path

from bgrealestate.connectors.telegram_public import TelegramPublicConnector

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "telegram_public"


class TestTelegramPublicConnector(unittest.TestCase):
    def setUp(self) -> None:
        self.connector = TelegramPublicConnector()
        self.account_id = "acct_test_1"

    def _load_raw(self, case: str) -> dict:
        return json.loads((FIXTURES / case / "raw.json").read_text("utf-8"))

    def test_maps_rent_listing_to_crm_payload(self) -> None:
        raw = self._load_raw("rent_listing")
        payload = self.connector.map_message_to_crm(raw, account_id=self.account_id)

        self.assertEqual(payload.lead_thread["external_thread_id"], "telegram:rentvarna")
        self.assertEqual(payload.lead_message["direction"], "inbound")
        self.assertEqual(payload.lead_message["external_message_id"], "42001")
        self.assertEqual(payload.extracted["intent"], "long_term_rent")
        self.assertEqual(payload.extracted["city"], "Варна")
        self.assertEqual(payload.extracted["district"], "Чайка")
        self.assertEqual(payload.extracted["price"], 400)
        self.assertEqual(payload.raw_capture.content_type, "application/json")

    def test_maps_sale_listing_to_crm_payload(self) -> None:
        raw = self._load_raw("sale_listing")
        payload = self.connector.map_message_to_crm(raw, account_id=self.account_id)

        self.assertEqual(payload.lead_thread["external_thread_id"], "telegram:real_estate_bg")
        self.assertEqual(payload.lead_message["external_message_id"], "18990")
        self.assertEqual(payload.extracted["intent"], "sale")
        self.assertEqual(payload.extracted["property_type"], "apartment")
        self.assertEqual(payload.extracted["city"], "София")
        self.assertEqual(payload.extracted["district"], "Лозенец")
        self.assertEqual(payload.extracted["price"], 185000)
        self.assertEqual(payload.extracted["currency"], "EUR")

    def test_maps_noise_message(self) -> None:
        raw = self._load_raw("noise_message")
        payload = self.connector.map_message_to_crm(raw, account_id=self.account_id)

        self.assertTrue(payload.extracted["is_noise"])
        self.assertIsNone(payload.extracted["intent"])
        self.assertIsNone(payload.extracted["property_type"])

    def test_rejects_non_redacted_fixture(self) -> None:
        raw = self._load_raw("rent_listing")
        raw["redaction_applied"] = False
        with self.assertRaises(ValueError):
            self.connector.map_message_to_crm(raw, account_id=self.account_id)


if __name__ == "__main__":
    unittest.main()

