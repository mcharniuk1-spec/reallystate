from __future__ import annotations

import logging
from dataclasses import asdict
from datetime import datetime
from typing import Any

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from ..models import CanonicalListing, ParsedListing, RawCapture
from ..source_registry import SourceRegistryEntry
from ..pipeline import GenericHtmlListingParser, StandardIngestionPipeline
from ..db.ids import new_id
from ..db.repositories import CanonicalListingRepository, ListingMediaRepository, ListingRepository, RawCaptureRepository
from ..db.session import session_scope
from ..services.unification import unify_listing

logger = logging.getLogger(__name__)


def _sync_listing_media(
    session: Session,
    reference_id: str,
    image_urls: list[str],
    *,
    download_images: bool = False,
) -> list[str]:
    """Create listing_media rows for each image URL.

    If download_images is True, also downloads images to local storage.
    Returns list of media_ids created.
    """
    media_repo = ListingMediaRepository(session)
    media_ids: list[str] = []

    for i, url in enumerate(image_urls):
        media_id = new_id("lmed")
        storage_key = None
        mime_type = None
        width = None
        height = None
        file_size = None
        content_hash = None
        dl_status = "pending"

        if download_images:
            try:
                from ..services.media import download_image
                result = download_image(url, reference_id=reference_id, ordering=i)
                if result.status == "downloaded":
                    storage_key = result.storage_key
                    mime_type = result.mime_type
                    width = result.width
                    height = result.height
                    file_size = result.file_size
                    content_hash = result.content_hash
                    dl_status = "downloaded"
                else:
                    dl_status = "failed"
                    logger.warning("Image download failed for %s: %s", url, result.error)
            except Exception as exc:
                dl_status = "failed"
                logger.warning("Image download error for %s: %s", url, exc)

        media_repo.upsert_media(
            media_id=media_id,
            listing_reference_id=reference_id,
            url=url,
            ordering=i,
            content_hash=content_hash,
            storage_key=storage_key,
            mime_type=mime_type,
            width=width,
            height=height,
            file_size=file_size,
            download_status=dl_status,
        )
        media_ids.append(media_id)

    return media_ids


def persist_listing_bundle(
    *,
    engine: Engine,
    source: SourceRegistryEntry,
    raw_capture: RawCapture,
    parsed: ParsedListing,
    canonical: CanonicalListing,
    status: str = "active",
    unify: bool = True,
    download_images: bool = False,
    source_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Persist an already-parsed listing bundle into the canonical pipeline."""
    with session_scope(engine) as session:
        raw_repo = RawCaptureRepository(session)
        listing_repo = ListingRepository(session)
        canon_repo = CanonicalListingRepository(session)

        raw_capture_id = raw_repo.insert(raw_capture)
        source_listing_id = listing_repo.upsert_source_listing(
            source_name=source.source_name,
            external_id=parsed.external_id,
            canonical_url=canonical.listing_url,
            seen_at=raw_capture.fetched_at,
            status=status,
            source_payload=source_payload or {},
            source_reference=canonical.reference_id,
        )
        snapshot_id = listing_repo.insert_snapshot(
            source_listing_id=source_listing_id,
            raw_capture_id=raw_capture_id,
            created_at=raw_capture.fetched_at,
            parsed=asdict(parsed),
        )
        listing_repo.set_current_snapshot(source_listing_id, snapshot_id)
        canon_repo.upsert(canonical)

        media_ids = _sync_listing_media(
            session,
            canonical.reference_id,
            canonical.image_urls,
            download_images=download_images,
        )

        property_id = None
        if unify:
            unification_result = unify_listing(session, canonical.reference_id)
            if unification_result is not None:
                property_id = unification_result.property_id

    return {
        "raw_capture_id": raw_capture_id,
        "source_listing_id": source_listing_id,
        "snapshot_id": snapshot_id,
        "reference_id": canonical.reference_id,
        "property_id": property_id,
        "media_ids": media_ids,
    }


def ingest_listing_detail_html(
    *,
    engine: Engine,
    source: SourceRegistryEntry,
    url: str,
    html: str,
    discovered_at: datetime,
    status: str = "active",
    unify: bool = True,
    download_images: bool = False,
) -> dict[str, Any]:
    pipeline = StandardIngestionPipeline(parser=GenericHtmlListingParser())
    result = pipeline.process_listing_detail(source=source, url=url, html=html, captured_at=discovered_at)

    raw_capture: RawCapture = result.raw_capture
    parsed: ParsedListing = result.parsed_listing
    canonical: CanonicalListing = result.canonical_listing

    return persist_listing_bundle(
        engine=engine,
        source=source,
        raw_capture=raw_capture,
        parsed=parsed,
        canonical=canonical,
        status=status,
        unify=unify,
        download_images=download_images,
        source_payload={"seed": parsed.raw_payload.get("seed", {})},
    )
