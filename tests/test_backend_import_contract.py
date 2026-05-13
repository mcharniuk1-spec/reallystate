from __future__ import annotations

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))


class TestBackendImportContract(unittest.TestCase):
    def test_canonical_listing_model_has_dataclass_fields(self) -> None:
        try:
            from bgrealestate.db.models import CanonicalListingModel
        except ModuleNotFoundError as exc:
            if exc.name == "sqlalchemy":
                self.skipTest("sqlalchemy not installed")
            raise
        from bgrealestate.models import CanonicalListing

        model_columns = {column.name for column in CanonicalListingModel.__table__.columns}
        missing = set(CanonicalListing.__dataclass_fields__) - model_columns
        self.assertEqual(missing, set())

    def test_stable_listing_media_id_is_idempotent(self) -> None:
        from bgrealestate.db.media_ids import stable_listing_media_id

        first = stable_listing_media_id("ref-001", "https://cdn.example.test/a.jpg")
        second = stable_listing_media_id("ref-001", "https://cdn.example.test/a.jpg")
        different = stable_listing_media_id("ref-001", "https://cdn.example.test/b.jpg")

        self.assertEqual(first, second)
        self.assertNotEqual(first, different)
        self.assertTrue(first.startswith("lmed_"))

    def test_import_models_preserve_qa_and_all_bulgaria_provenance(self) -> None:
        from scripts.import_scraped_listings import _build_models

        listing = {
            "source_name": "imot.bg",
            "listing_url": "https://example.test/listing/1",
            "external_id": "1",
            "reference_id": "imot.bg:1",
            "listing_intent": "sale",
            "property_category": "apartment",
            "city": "Sofia",
            "price": 125000,
            "currency": "EUR",
            "scraped_at": "2026-05-13T10:00:00+00:00",
            "crawl_provenance": {"price_status": "numeric"},
            "geo_scope": "all_bulgaria",
            "bucket_key": "buy_personal",
            "segment_key": "buy_personal",
            "source_publication_type": "single_unit_candidate",
            "scrape_status": "SCRAPED_OK",
            "scrape_acceptance_status": "accepted_single_entity_candidate",
            "single_entity_candidate": True,
            "listing_status": "active",
            "photo_count_remote": 2,
            "photo_count_local": 2,
            "local_image_storage_keys": ["imot.bg:1/0000.jpg", "imot.bg:1/0001.jpg"],
            "image_report_status": "missing",
        }
        listing_file = REPO_ROOT / "data" / "scraped" / "imot_bg" / "listings" / "imot_1.json"
        _, _, canonical = _build_models(
            source_name="imot.bg",
            owner_group="portal",
            listing=listing,
            raw_body="<html></html>",
            raw_suffix=".html",
            listing_file=listing_file,
        )

        provenance = canonical.crawl_provenance
        self.assertEqual(provenance["geo_scope"], "all_bulgaria")
        self.assertEqual(provenance["bucket_key"], "buy_personal")
        self.assertEqual(provenance["price_status"], "numeric")
        self.assertEqual(provenance["scrape_status"], "SCRAPED_OK")
        self.assertEqual(provenance["scrape_acceptance_status"], "accepted_single_entity_candidate")
        self.assertEqual(provenance["source_publication_type"], "single_unit_candidate")
        self.assertEqual(provenance["photo_count_local"], 2)
        self.assertEqual(provenance["image_report_status"], "missing")
        self.assertEqual(canonical.first_seen, datetime(2026, 5, 13, 10, 0, tzinfo=timezone.utc))

    def test_zero_price_is_null_with_status_provenance(self) -> None:
        from scripts.import_scraped_listings import _build_models

        listing = {
            "source_name": "bazar.bg",
            "listing_url": "https://example.test/listing/zero",
            "external_id": "zero",
            "reference_id": "bazar.bg:zero",
            "listing_intent": "sale",
            "property_category": "apartment",
            "price": 0,
            "currency": "EUR",
            "scraped_at": "2026-05-13T10:00:00+00:00",
            "crawl_provenance": {},
        }
        listing_file = REPO_ROOT / "data" / "scraped" / "bazar_bg" / "listings" / "zero.json"
        _, parsed, canonical = _build_models(
            source_name="bazar.bg",
            owner_group="portal",
            listing=listing,
            raw_body="{}",
            raw_suffix=".json",
            listing_file=listing_file,
        )

        self.assertIsNone(parsed.price)
        self.assertIsNone(canonical.price)
        self.assertEqual(canonical.crawl_provenance["price_status"], "undefined")
        self.assertTrue(canonical.crawl_provenance["price_zero_coerced_to_null"])

    def test_import_default_blocks_unsafe_quality_states(self) -> None:
        from scripts.import_scraped_listings import _skip_reason

        defaults = {
            "include_lost": False,
            "include_grouped": False,
            "include_inactive": False,
            "include_unreviewed": False,
        }
        self.assertEqual(_skip_reason({"scrape_status": "PENDING_QA"}, **defaults), "unreviewed_quality_state")
        self.assertEqual(_skip_reason({"scrape_status": "LOST"}, **defaults), "lost_rescrape_required")
        self.assertEqual(
            _skip_reason({"scrape_status": "SCRAPED_OK", "source_publication_type": "multi_unit_or_development"}, **defaults),
            "grouped_publication_not_single_entity",
        )
        self.assertEqual(
            _skip_reason({"scrape_status": "SCRAPED_OK", "suspected_multi_unit_publication": True}, **defaults),
            "grouped_publication_not_single_entity",
        )
        self.assertEqual(
            _skip_reason({"scrape_status": "SCRAPED_OK", "listing_status": "expired"}, **defaults),
            "inactive_source_listing",
        )

    def test_bd18_evidence_tables_are_mapped(self) -> None:
        try:
            from bgrealestate.db.models import (
                AvailabilityCalendarModel,
                AvailabilityObservationModel,
                AvailabilitySlotModel,
                EntityResolutionCandidateModel,
                EntityResolutionReviewEventModel,
                ExternalChatRefModel,
                MediaDescriptionModel,
                SourcePublicationQAReviewModel,
                StatusHistoryModel,
                ViewingInquiryRequestModel,
            )
        except ModuleNotFoundError as exc:
            if exc.name == "sqlalchemy":
                self.skipTest("sqlalchemy not installed")
            raise

        expected_tables = {
            SourcePublicationQAReviewModel.__tablename__,
            StatusHistoryModel.__tablename__,
            EntityResolutionCandidateModel.__tablename__,
            EntityResolutionReviewEventModel.__tablename__,
            MediaDescriptionModel.__tablename__,
            AvailabilityCalendarModel.__tablename__,
            AvailabilitySlotModel.__tablename__,
            AvailabilityObservationModel.__tablename__,
            ViewingInquiryRequestModel.__tablename__,
            ExternalChatRefModel.__tablename__,
        }
        self.assertEqual(
            expected_tables,
            {
                "source_publication_qa_review",
                "status_history",
                "entity_resolution_candidate",
                "entity_resolution_review_event",
                "media_description",
                "availability_calendar",
                "availability_slot",
                "availability_observation",
                "viewing_inquiry_request",
                "external_chat_ref",
            },
        )
        qa_columns = {column.name for column in SourcePublicationQAReviewModel.__table__.columns}
        self.assertTrue(
            {
                "qa_state",
                "import_eligible",
                "blocked_import_reason",
                "source_publication_type",
                "scrape_acceptance_status",
                "evidence_jsonb",
            }.issubset(qa_columns)
        )
        candidate_columns = {column.name for column in EntityResolutionCandidateModel.__table__.columns}
        self.assertTrue(
            {
                "candidate_type",
                "review_status",
                "confidence_score",
                "score_components_jsonb",
                "conflict_reasons_jsonb",
                "accepted_only_filter_jsonb",
                "evidence_snapshot_jsonb",
            }.issubset(candidate_columns)
        )

    def test_source_publication_import_eligibility(self) -> None:
        from bgrealestate.db.import_contract import import_eligibility_from_provenance

        eligible, reason, blocker = import_eligibility_from_provenance(
            {
                "scrape_status": "SCRAPED_OK",
                "scrape_acceptance_status": "accepted_single_entity_candidate",
                "source_publication_type": "single_unit_candidate",
                "listing_status": "active",
                "price_status": "numeric",
            }
        )
        self.assertTrue(eligible)
        self.assertEqual(reason, "accepted_single_entity_candidate")
        self.assertIsNone(blocker)

        eligible, reason, blocker = import_eligibility_from_provenance(
            {
                "scrape_status": "SCRAPED_OK",
                "scrape_acceptance_status": "not_single_entity",
                "source_publication_type": "multi_unit_or_development",
            }
        )
        self.assertFalse(eligible)
        self.assertEqual(reason, "blocked")
        self.assertEqual(blocker, "grouped_publication_not_single_entity")


if __name__ == "__main__":
    unittest.main()
