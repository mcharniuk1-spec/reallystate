from __future__ import annotations

import json
import unittest

from bgrealestate.connectors.fixtures import fixture_dir, read_json, read_text
from bgrealestate.connectors.olx_bg import parse_olx_discovery_json
from bgrealestate.connectors.scaffold import parse_discovery_html


class TestTier1HtmlDiscovery(unittest.TestCase):
    def test_discovery_page_for_each_tier1_html_source(self) -> None:
        cases = [
            ("alo_bg", "alo.bg", "https://www.alo.bg"),
            ("imot_bg", "imot.bg", "https://www.imot.bg"),
            ("bulgarianproperties", "BulgarianProperties", "https://www.bulgarianproperties.bg"),
            ("address_bg", "Address.bg", "https://address.bg"),
            ("suprimmo", "SUPRIMMO", "https://suprimmo.bg"),
            ("luximmo", "LUXIMMO", "https://luximmo.bg"),
            ("property_bg", "property.bg", "https://property.bg"),
        ]
        for fixture_key, source_name, base_url in cases:
            with self.subTest(source=source_name):
                case_dir = fixture_dir(fixture_key) / "discovery_page"
                html = read_text(case_dir / "raw.html")
                expected = read_json(case_dir / "expected.json")
                entries, next_cursor = parse_discovery_html(source_name, html, base_url=base_url)
                self.assertEqual(expected["entries"], entries)
                self.assertEqual(expected["next_cursor"], next_cursor)

    def test_html_discovery_handles_last_and_empty(self) -> None:
        last_page_html = '<a class="listing-link" href="/listing/X1" data-ext-id="X1" data-price="1" data-intent="sale">x</a>'
        entries, next_cursor = parse_discovery_html("demo", last_page_html, base_url="https://example.com")
        self.assertEqual(1, len(entries))
        self.assertIsNone(next_cursor)

        empty_html = "<html><body><div class='results'></div></body></html>"
        entries, next_cursor = parse_discovery_html("demo", empty_html, base_url="https://example.com")
        self.assertEqual([], entries)
        self.assertIsNone(next_cursor)


class TestOlxDiscovery(unittest.TestCase):
    def _run_case(self, case: str) -> None:
        case_dir = fixture_dir("olx_bg") / case
        payload = json.loads(read_text(case_dir / "raw.json"))
        expected = read_json(case_dir / "expected.json")
        entries, next_cursor = parse_olx_discovery_json(payload)
        self.assertEqual(expected["entries"], entries)
        self.assertEqual(expected["next_cursor"], next_cursor)

    def test_discovery_page(self) -> None:
        self._run_case("discovery_page")

    def test_discovery_last_page(self) -> None:
        self._run_case("discovery_last_page")

    def test_discovery_empty(self) -> None:
        self._run_case("discovery_empty")


if __name__ == "__main__":
    unittest.main()
