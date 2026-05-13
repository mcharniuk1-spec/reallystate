from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from action1_dataset_quality_gate import classify_multi_unit, local_reasons  # noqa: E402
from live_scraper import _apply_bucket_context, parse_homes_detail, parse_listing_html  # noqa: E402


def raw(source_key: str, filename: str) -> str:
    return (ROOT / "data" / "scraped" / source_key / "raw" / filename).read_text(encoding="utf-8", errors="replace")


class Action1ParserRegressionTests(unittest.TestCase):
    def test_address_bg_extracts_full_detail_gallery_not_single_og_image(self) -> None:
        row = parse_listing_html(
            raw("address_bg", "Address.bg_001a3d0d094d.html"),
            "https://address.bg/offers/example",
            "Address.bg",
        )
        self.assertIsNotNone(row)
        assert row is not None
        self.assertGreaterEqual(len(row["image_urls"]), 10)
        self.assertTrue(all("/1000x666/" in url for url in row["image_urls"]))

    def test_bulgarianproperties_uses_full_description_from_detail_payload(self) -> None:
        row = parse_listing_html(
            raw("bulgarianproperties", "BulgarianProperties_00306e455332.html"),
            "https://www.bulgarianproperties.com/example.html",
            "BulgarianProperties",
        )
        self.assertIsNotNone(row)
        assert row is not None
        self.assertGreater(len(row.get("description") or ""), 1000)
        self.assertGreaterEqual(len(row["image_urls"]), 20)

    def test_homes_bg_title_area_is_not_decimal_shifted(self) -> None:
        row = parse_homes_detail(
            raw("homes_bg", "Homes.bg_1247316.html"),
            "https://www.homes.bg/offer/apartment-for-sale/example",
        )
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["area_sqm"], 165.0)
        self.assertEqual(row["city"], "София")
        self.assertIn("Изток", row["district"])

    def test_suprimmo_prefers_unit_area_over_complex_land_area(self) -> None:
        row = parse_listing_html(
            raw("suprimmo", "SUPRIMMO_094a13604c7e.html"),
            "https://www.suprimmo.bg/example.html",
            "SUPRIMMO",
        )
        self.assertIsNotNone(row)
        assert row is not None
        self.assertAlmostEqual(float(row["area_sqm"]), 205.12, places=2)
        self.assertLess(float(row["area_sqm"]), 1000)
        self.assertGreater(float((row.get("source_attributes") or {}).get("raw_max_area_sqm") or 0), 100000)

    def test_outside_bulgaria_jsonld_coordinates_are_rejected(self) -> None:
        html = """
        <html><head><script type="application/ld+json">
        {"@type":"Product","name":"Bad geo","geo":{"@type":"GeoCoordinates","latitude":44.42,"longitude":26.10}}
        </script></head><body><h1>Апартамент в София</h1></body></html>
        """
        row = parse_listing_html(html, "https://example.test/bad", "imot.bg")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertIsNone(row.get("latitude"))
        self.assertIsNone(row.get("longitude"))

    def test_bucket_context_overrides_generic_detail_text_drift(self) -> None:
        row = {
            "listing_intent": "sale",
            "property_category": "unknown",
            "source_section_id": "",
        }
        _apply_bucket_context(row, "rent_land", "https://example.test/naem/parcels")
        self.assertEqual(row["listing_intent"], "long_term_rent")
        self.assertEqual(row["property_category"], "land")
        self.assertEqual(row["source_section_id"], "rent_land")

    def test_quality_gate_honors_persisted_grouped_and_inactive_status(self) -> None:
        row = {
            "source_publication_type": "multi_unit_or_development",
            "listing_url": "https://www.imot.bg/obiava-example",
            "title": "Жилищна сграда с апартаменти",
            "description": "Valid enough description for grouped page with several units and prices.",
            "price": 100000,
            "area_sqm": 100,
            "city": "София",
            "image_urls": ["https://imotstatic.example/1.jpg", "https://imotstatic.example/2.jpg"],
            "local_image_files": ["data/media/a/1.jpg", "data/media/a/2.jpg"],
            "listing_status": "inactive",
        }
        grouped, reason = classify_multi_unit(row)
        self.assertTrue(grouped)
        self.assertEqual(reason, "persisted_multi_unit_publication")
        lost, warnings, _multi, _multi_reason = local_reasons("imot_bg", row)
        self.assertIn("inactive_listing_status", lost)
        self.assertTrue(any(item.startswith("multi_unit_publication") for item in warnings))


if __name__ == "__main__":
    unittest.main()
