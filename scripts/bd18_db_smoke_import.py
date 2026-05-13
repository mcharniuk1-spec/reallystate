#!/usr/bin/env python3
"""BD-18 PostgreSQL smoke import for accepted source-publication evidence.

This is intentionally tiny and fixture-backed. It proves that an accepted
source publication can persist QA evidence, listing media, and canonical row
data without default property/entity promotion.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))


def main() -> int:
    if not os.getenv("DATABASE_URL"):
        print("DATABASE_URL is required")
        return 2

    from sqlalchemy import func, select

    from bgrealestate.connectors.ingest import persist_listing_bundle
    from bgrealestate.db.models import ListingMediaModel, PropertyOfferModel, SourcePublicationQAReviewModel
    from bgrealestate.db.repositories import SourceRegistryRepository
    from bgrealestate.db.session import create_db_engine, session_scope
    from bgrealestate.source_registry import SourceRegistry
    from scripts.import_scraped_listings import _build_models

    registry = SourceRegistry.from_file(REPO / "data" / "source_registry.json")
    source = registry.by_name("imot.bg")
    if source is None:
        raise RuntimeError("imot.bg missing from source registry")

    listing = {
        "source_name": "imot.bg",
        "listing_url": "https://example.test/bd18-smoke",
        "external_id": "bd18-smoke",
        "reference_id": "imot.bg:bd18-smoke",
        "listing_intent": "sale",
        "property_category": "apartment",
        "title": "BD-18 smoke accepted apartment",
        "city": "Sofia",
        "district": "Center",
        "address_text": "Sofia, Center",
        "price": 125000,
        "currency": "EUR",
        "area_sqm": 80,
        "scraped_at": "2026-05-13T13:00:00+00:00",
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
        "image_urls": [
            "https://example.test/media/bd18-smoke-1.jpg",
            "https://example.test/media/bd18-smoke-2.jpg",
        ],
        "local_image_storage_keys": [
            "data/media/imot.bg_bd18-smoke/0000.jpg",
            "data/media/imot.bg_bd18-smoke/0001.jpg",
        ],
        "image_report_status": "missing",
    }
    listing_file = REPO / "tests" / "fixtures" / "bd18_smoke" / "imot_bg_bd18_smoke.json"
    raw_capture, parsed, canonical = _build_models(
        source_name=source.source_name,
        owner_group=source.owner_group,
        listing=listing,
        raw_body="<html><title>BD-18 smoke</title></html>",
        raw_suffix=".html",
        listing_file=listing_file,
    )

    engine = create_db_engine()
    with session_scope(engine) as session:
        SourceRegistryRepository(session).upsert_source(source)

    result = persist_listing_bundle(
        engine=engine,
        source=source,
        raw_capture=raw_capture,
        parsed=parsed,
        canonical=canonical,
        unify=False,
        download_images=False,
        source_payload={"smoke": "bd18"},
    )

    with session_scope(engine) as session:
        qa_count = session.scalar(
            select(func.count())
            .select_from(SourcePublicationQAReviewModel)
            .where(SourcePublicationQAReviewModel.listing_reference_id == canonical.reference_id)
            .where(SourcePublicationQAReviewModel.import_eligible.is_(True))
        )
        media_count = session.scalar(
            select(func.count())
            .select_from(ListingMediaModel)
            .where(ListingMediaModel.listing_reference_id == canonical.reference_id)
        )
        offer_count = session.scalar(
            select(func.count())
            .select_from(PropertyOfferModel)
            .where(PropertyOfferModel.listing_reference_id == canonical.reference_id)
        )

    if qa_count != 1:
        raise RuntimeError(f"expected 1 eligible QA review, got {qa_count}")
    if media_count != 2:
        raise RuntimeError(f"expected 2 listing media rows, got {media_count}")
    if offer_count != 0:
        raise RuntimeError(f"expected no property offer without promotion, got {offer_count}")

    print(f"reference_id={result['reference_id']}")
    print(f"source_listing_id={result['source_listing_id']}")
    print(f"qa_reviews={qa_count}")
    print(f"listing_media={media_count}")
    print("property_offer_promotion=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
