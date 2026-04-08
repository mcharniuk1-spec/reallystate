from __future__ import annotations

import unittest

from bgrealestate.connectors.fixtures import fixture_dir, read_json, read_text
from bgrealestate.connectors.homes_bg import parse_discovery_html


class TestHomesBgDiscovery(unittest.TestCase):
    """Fixture-backed tests for Homes.bg discovery (search result page parsing)."""

    def _run(self, case: str) -> None:
        case_dir = fixture_dir("homes_bg") / case
        html = read_text(case_dir / "raw.html")
        expected = read_json(case_dir / "expected.json")

        urls, next_cursor = parse_discovery_html(html)

        self.assertEqual(urls, expected["urls"])
        self.assertEqual(next_cursor, expected["next_cursor"])

    def test_discovery_page_with_pagination(self) -> None:
        self._run("discovery_page")

    def test_discovery_last_page(self) -> None:
        self._run("discovery_last_page")

    def test_discovery_empty(self) -> None:
        self._run("discovery_empty")


if __name__ == "__main__":
    unittest.main()
