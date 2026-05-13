import json
import unittest
from pathlib import Path

from scripts.live_scraper import parse_listing_html


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "strict_sample_proof"


def _structured_count(row: dict) -> int:
    return sum(row.get(key) is not None for key in ("area_sqm", "rooms", "floor")) + (1 if row.get("phones") else 0)


class StrictSampleProofTest(unittest.TestCase):
    def test_saved_samples_have_full_gallery_and_reparse_from_raw(self):
        for fixture_path in sorted(FIXTURE_ROOT.glob("*.json")):
            with self.subTest(source=fixture_path.stem):
                fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
                listing_path = ROOT / fixture["listing_path"]
                raw_path = ROOT / fixture["raw_path"]
                saved = json.loads(listing_path.read_text(encoding="utf-8"))
                raw_html = raw_path.read_text(encoding="utf-8")
                reparsed = parse_listing_html(raw_html, saved["listing_url"], fixture["source_name"])

                self.assertIsNotNone(reparsed)
                self.assertEqual(saved["reference_id"], fixture["expected_reference_id"])
                self.assertEqual(saved["city"], fixture["expected_city"])
                self.assertEqual(saved["property_category"], fixture["expected_category"])
                self.assertGreaterEqual(saved["photo_count_remote"], fixture["min_remote_photos"])
                self.assertEqual(saved["photo_count_remote"], len(saved.get("image_urls") or []))
                self.assertGreaterEqual(saved["photo_count_local"], saved["photo_count_remote"])
                self.assertTrue(saved.get("full_gallery_downloaded"))
                self.assertEqual(saved["photo_count_local"], len(saved.get("local_image_files") or []))
                for relative_path in saved.get("local_image_files") or []:
                    self.assertTrue((ROOT / relative_path).is_file(), relative_path)

                self.assertEqual(reparsed["city"], fixture["expected_city"])
                self.assertEqual(reparsed["property_category"], fixture["expected_category"])
                self.assertGreaterEqual(len(reparsed.get("image_urls") or []), fixture["min_remote_photos"])
                self.assertIsNotNone(reparsed.get("price"))
                self.assertGreaterEqual(_structured_count(reparsed), fixture["min_structured_fields"])

                if fixture.get("description_required", True):
                    self.assertTrue(saved.get("description"))
                    self.assertTrue(reparsed.get("description"))
                else:
                    attrs = saved.get("source_attributes") or {}
                    self.assertEqual(attrs.get("description_status"), fixture.get("allowed_description_status"))


if __name__ == "__main__":
    unittest.main()
