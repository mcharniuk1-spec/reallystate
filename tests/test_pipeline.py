import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bgrealestate.models import BuildingEntity
from bgrealestate.pipeline import DeduplicationScorer, StandardIngestionPipeline
from bgrealestate.source_registry import SourceRegistry


REGISTRY_PATH = Path(__file__).resolve().parents[1] / "data" / "source_registry.json"


SAMPLE_HTML = """
<html>
  <head>
    <title>For Rent Apartment Varna Center</title>
    <meta property="og:image" content="https://example.com/cover.jpg" />
    <script type="application/ld+json">
      {
        "@context": "https://schema.org",
        "@type": "Offer",
        "@id": "varna-apt-42",
        "name": "Sunny apartment near the sea",
        "description": "Two bedroom apartment in Varna Center.",
        "image": "https://example.com/apt-1.jpg",
        "priceCurrency": "EUR",
        "price": "950",
        "address": {
          "@type": "PostalAddress",
          "streetAddress": "15 Knyaz Boris I",
          "addressLocality": "Varna",
          "addressRegion": "Varna"
        },
        "geo": {
          "@type": "GeoCoordinates",
          "latitude": 43.2141,
          "longitude": 27.9147
        }
      }
    </script>
  </head>
  <body>
    <h1>Sunny apartment near the sea</h1>
    <p>Call +359 888 123 456 for details.</p>
  </body>
</html>
"""


class PipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = SourceRegistry.from_file(REGISTRY_PATH)
        self.pipeline = StandardIngestionPipeline()

    def test_pipeline_processes_apartment_detail_page(self) -> None:
        source = self.registry.by_name("Homes.bg")
        building = BuildingEntity(
            building_id="varna-center-1",
            name="Sea Residence",
            latitude=43.2142,
            longitude=27.9148,
            source="osm",
            confidence=0.97,
        )

        result = self.pipeline.process_listing_detail(
            source=source,
            url="https://example.com/listings/42",
            html=SAMPLE_HTML,
            captured_at=datetime(2026, 4, 6, 15, 0, 0),
            summary_fields={
                "listing_intent": "rent",
                "property_category": "apartment",
                "external_id": "42",
                "rooms": 3,
                "area_sqm": 110,
                "building_name": "Sea Residence",
                "image_urls": ["https://example.com/apt-2.jpg"]
            },
            buildings=[building],
        )

        canonical = result.canonical_listing
        self.assertEqual(canonical.reference_id, "Homes.bg:42")
        self.assertEqual(canonical.city, "Varna")
        self.assertAlmostEqual(canonical.price, 950.0)
        self.assertAlmostEqual(canonical.price_per_sqm, 8.64)
        self.assertIn("+359 888 123 456", canonical.phones)
        self.assertEqual(result.building_match.building_id, "varna-center-1")

    def test_dedupe_scorer_prefers_near_duplicate(self) -> None:
        source = self.registry.by_name("Homes.bg")
        left = self.pipeline.process_listing_detail(
            source=source,
            url="https://example.com/listings/42",
            html=SAMPLE_HTML,
            captured_at=datetime(2026, 4, 6, 15, 0, 0),
            summary_fields={"listing_intent": "rent", "property_category": "apartment", "external_id": "42", "area_sqm": 110},
        ).canonical_listing
        right = self.pipeline.process_listing_detail(
            source=source,
            url="https://example.com/listings/43",
            html=SAMPLE_HTML.replace("42", "43"),
            captured_at=datetime(2026, 4, 6, 15, 5, 0),
            summary_fields={"listing_intent": "rent", "property_category": "apartment", "external_id": "43", "area_sqm": 111},
        ).canonical_listing
        score = DeduplicationScorer.score(left, right)
        self.assertGreater(score, 0.6)


if __name__ == "__main__":
    unittest.main()

