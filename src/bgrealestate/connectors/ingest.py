from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Any

from sqlalchemy.engine import Engine

from ..models import CanonicalListing, ParsedListing, RawCapture
from ..source_registry import SourceRegistryEntry
from ..pipeline import GenericHtmlListingParser, StandardIngestionPipeline
from ..db.repositories import CanonicalListingRepository, ListingRepository, RawCaptureRepository
from ..db.session import session_scope


def ingest_listing_detail_html(
    *,
    engine: Engine,
    source: SourceRegistryEntry,
    url: str,
    html: str,
    discovered_at: datetime,
    status: str = "active",
) -> dict[str, Any]:
    pipeline = StandardIngestionPipeline(parser=GenericHtmlListingParser())
    result = pipeline.process_listing_detail(source=source, url=url, html=html, captured_at=discovered_at)

    raw_capture: RawCapture = result.raw_capture
    parsed: ParsedListing = result.parsed_listing
    canonical: CanonicalListing = result.canonical_listing

    with session_scope(engine) as session:
        raw_repo = RawCaptureRepository(session)
        listing_repo = ListingRepository(session)
        canon_repo = CanonicalListingRepository(session)

        raw_capture_id = raw_repo.insert(raw_capture)
        source_listing_id = listing_repo.upsert_source_listing(
            source_name=source.source_name,
            external_id=parsed.external_id,
            canonical_url=url,
            seen_at=raw_capture.fetched_at,
            status=status,
            source_payload={"seed": parsed.raw_payload.get("seed", {})},
        )
        snapshot_id = listing_repo.insert_snapshot(
            source_listing_id=source_listing_id,
            raw_capture_id=raw_capture_id,
            created_at=raw_capture.fetched_at,
            parsed=asdict(parsed),
        )
        listing_repo.set_current_snapshot(source_listing_id, snapshot_id)
        canon_repo.upsert(canonical)

    return {
        "raw_capture_id": raw_capture_id,
        "source_listing_id": source_listing_id,
        "snapshot_id": snapshot_id,
        "reference_id": canonical.reference_id,
    }

