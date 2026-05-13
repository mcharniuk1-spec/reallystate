"""Action1: explicit --sources must not be filtered by pattern-status."""

from __future__ import annotations

import unittest

from bgrealestate.scraping.varna_full_scrape import resolve_explicit_source_keys


class TestResolveExplicitSources(unittest.TestCase):
    def test_action1_seven_names(self) -> None:
        labels = [
            "Address.bg",
            "BulgarianProperties",
            "Homes.bg",
            "imot.bg",
            "LUXIMMO",
            "property.bg",
            "SUPRIMMO",
        ]
        keys = resolve_explicit_source_keys(labels)
        self.assertEqual(
            keys,
            [
                "address_bg",
                "bulgarianproperties",
                "homes_bg",
                "imot_bg",
                "luximmo",
                "property_bg",
                "suprimmo",
            ],
        )

    def test_mixed_keys_and_names(self) -> None:
        keys = resolve_explicit_source_keys(["homes_bg", "OLX.bg"])
        self.assertIn("homes_bg", keys)
        self.assertIn("olx_bg", keys)
