from __future__ import annotations

import unittest

from bgrealestate.matching import (
    classify_source_publication,
    fingerprint_from_mapping,
    rank_comparable_properties,
    score_property_pair,
)


class TestPropertyComparableSearch(unittest.TestCase):
    def _row(self, **overrides):
        row = {
            "source_name": "Address.bg",
            "reference_id": "Address.bg:1",
            "listing_url": "https://address.bg/property/1",
            "external_id": "1",
            "title": "Two-bedroom apartment in Varna Center",
            "description": "Bright apartment near the cathedral with balcony.",
            "listing_intent": "sale",
            "property_category": "apartment",
            "city": "Varna",
            "district": "Center",
            "address_text": "Varna Center, Cathedral",
            "latitude": 43.205,
            "longitude": 27.91,
            "price": 125000,
            "currency": "EUR",
            "area_sqm": 72,
            "rooms": 3,
            "image_urls": ["https://cdn.example.test/a.jpg", "https://cdn.example.test/b.jpg"],
            "phones": ["+359 888 111 222"],
            "source_publication_type": "single_unit_candidate",
            "scrape_status": "SCRAPED_OK",
            "scrape_acceptance_status": "accepted_single_entity_candidate",
            "listing_status": "active",
        }
        row.update(overrides)
        return row

    def test_single_unit_classification_requires_price_or_status(self) -> None:
        fp = fingerprint_from_mapping(self._row(price=None, price_status="on_request"))
        decision = classify_source_publication(fp)
        self.assertEqual(decision.classification, "single_unit_candidate")
        self.assertTrue(decision.is_single_unit_candidate)

        blocked = fingerprint_from_mapping(self._row(price=None, price_status=""))
        blocked_decision = classify_source_publication(blocked)
        self.assertFalse(blocked_decision.is_single_unit_candidate)
        self.assertIn("missing_price_or_explicit_price_status", blocked_decision.blockers)

    def test_grouped_publication_is_not_promoted(self) -> None:
        fp = fingerprint_from_mapping(
            self._row(
                source_publication_type="multi_unit_or_development",
                scrape_acceptance_status="not_single_entity",
            )
        )
        decision = classify_source_publication(fp)
        self.assertEqual(decision.classification, "source_publication_only")
        self.assertIn("grouped_or_development_publication", decision.blockers)

    def test_same_property_candidate_uses_cross_source_evidence(self) -> None:
        query = fingerprint_from_mapping(self._row(source_name="Address.bg"), source_tier=1)
        candidate = fingerprint_from_mapping(
            self._row(
                source_name="BulgarianProperties",
                reference_id="BulgarianProperties:9",
                listing_url="https://www.bulgarianproperties.bg/property/9",
                price=126000,
                image_urls=["https://cdn.example.test/a.jpg", "https://cdn.example.test/c.jpg"],
            ),
            source_tier=1,
        )
        result = score_property_pair(query, candidate)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.match_class, "same_property_candidate")
        self.assertGreaterEqual(result.score, 0.68)
        self.assertIn("same_normalized_address", result.evidence)

    def test_different_city_is_not_comparable(self) -> None:
        query = fingerprint_from_mapping(self._row(source_name="Address.bg"), source_tier=1)
        candidate = fingerprint_from_mapping(
            self._row(
                source_name="Homes.bg",
                reference_id="Homes.bg:2",
                listing_url="https://www.homes.bg/2",
                city="Sofia",
                district="Lozenets",
                address_text="Sofia Lozenets",
                latitude=42.67,
                longitude=23.32,
            ),
            source_tier=1,
        )
        result = score_property_pair(query, candidate)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertIn("city_mismatch", result.conflicts)
        self.assertEqual(result.match_class, "weak_candidate")

    def test_rank_excludes_same_source_by_default(self) -> None:
        query = fingerprint_from_mapping(self._row(source_name="Address.bg"), source_tier=1)
        same_source = fingerprint_from_mapping(
            self._row(reference_id="Address.bg:2", listing_url="https://address.bg/property/2"),
            source_tier=1,
        )
        other_source = fingerprint_from_mapping(
            self._row(
                source_name="imot.bg",
                reference_id="imot.bg:3",
                listing_url="https://www.imot.bg/pcgi/imot.cgi?act=5&adv=3",
            ),
            source_tier=1,
        )
        ranked = rank_comparable_properties(query, [same_source, other_source], min_score=0.1)
        self.assertEqual([item.candidate.source_name for item in ranked], ["imot.bg"])


if __name__ == "__main__":
    unittest.main()
