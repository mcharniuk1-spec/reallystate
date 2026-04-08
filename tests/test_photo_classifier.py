"""Tests for the photo classification stub."""

from __future__ import annotations

import unittest

from bgrealestate.analytics.photo_classifier import (
    PhotoClassification,
    classify_batch,
    classify_image,
)


class TestClassifyImage(unittest.TestCase):
    def test_returns_classification_dataclass(self) -> None:
        result = classify_image("https://example.com/photo.jpg")
        self.assertIsInstance(result, PhotoClassification)
        self.assertEqual(result.method, "heuristic_v1")

    def test_detects_kitchen_from_url(self) -> None:
        result = classify_image("https://cdn.example.com/photos/kitchen_01.jpg")
        self.assertEqual(result.room_type, "kitchen")

    def test_detects_bathroom_from_url(self) -> None:
        result = classify_image("https://cdn.example.com/photos/bathroom_main.jpg")
        self.assertEqual(result.room_type, "bathroom")

    def test_detects_bedroom_from_caption(self) -> None:
        result = classify_image(
            "https://cdn.example.com/abc123.jpg",
            metadata={"caption": "Master bedroom with sea view"},
        )
        self.assertEqual(result.room_type, "bedroom")

    def test_detects_living_room_bulgarian(self) -> None:
        result = classify_image(
            "https://cdn.example.com/abc123.jpg",
            metadata={"caption": "хол с камина"},
        )
        self.assertEqual(result.room_type, "living_room")

    def test_detects_exterior(self) -> None:
        result = classify_image(
            "https://cdn.example.com/facade_photo.jpg",
        )
        self.assertTrue(result.is_exterior)

    def test_detects_floorplan(self) -> None:
        result = classify_image(
            "https://cdn.example.com/floor_plan_2br.png",
        )
        self.assertTrue(result.is_floorplan)

    def test_floorplan_bulgarian(self) -> None:
        result = classify_image(
            "https://cdn.example.com/abc.jpg",
            metadata={"alt_text": "Разпределение на апартамент"},
        )
        self.assertTrue(result.is_floorplan)

    def test_unknown_returns_none_room_type(self) -> None:
        result = classify_image("https://cdn.example.com/img_0042.jpg")
        self.assertIsNone(result.room_type)
        self.assertFalse(result.is_exterior)
        self.assertFalse(result.is_floorplan)

    def test_quality_score_high_for_large_images(self) -> None:
        result = classify_image(
            "https://cdn.example.com/photo.jpg",
            metadata={"width": 2000, "height": 1500},
        )
        self.assertGreaterEqual(result.quality_score, 0.9)

    def test_quality_score_medium_for_small_images(self) -> None:
        result = classify_image(
            "https://cdn.example.com/photo.jpg",
            metadata={"width": 800, "height": 600},
        )
        self.assertLessEqual(result.quality_score, 0.5)

    def test_quality_default_when_no_dimensions(self) -> None:
        result = classify_image("https://cdn.example.com/photo.jpg")
        self.assertEqual(result.quality_score, 0.5)

    def test_confidence_higher_when_classified(self) -> None:
        classified = classify_image("https://cdn.example.com/kitchen_01.jpg")
        unknown = classify_image("https://cdn.example.com/img_0042.jpg")
        self.assertGreater(classified.confidence, unknown.confidence)


class TestClassifyBatch(unittest.TestCase):
    def test_batch_processes_multiple(self) -> None:
        items = [
            ("https://cdn.example.com/kitchen.jpg", None),
            ("https://cdn.example.com/bathroom.jpg", {"caption": "Modern bathroom"}),
            ("https://cdn.example.com/exterior.jpg", {"alt_text": "Building facade"}),
        ]
        results = classify_batch(items)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].room_type, "kitchen")
        self.assertEqual(results[1].room_type, "bathroom")
        self.assertTrue(results[2].is_exterior)


if __name__ == "__main__":
    unittest.main()
