"""Unified listing database — merge scraper outputs into canonical property store.

Takes raw scraper output from any tier-1/2/3 connector and writes through the
source_listing → parsed_listing → canonical_listing pipeline, then deduplicates
into property_entity records.

The deduplication strategy:
1. Compute a dedupe_key from (city, normalized_address, area_sqm bucket)
2. If a property_entity with the same dedupe_key already exists, link to it
3. Otherwise create a new property_entity
4. Merge best data: highest-quality photos, most complete description, latest price
5. Compute confidence_score based on number of cross-source matches
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha1

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from ..db.ids import new_id
from ..db.models import (
    CanonicalListingModel,
    PropertyEntityModel,
    PropertyOfferModel,
)


@dataclass(frozen=True)
class UnificationResult:
    property_id: str
    is_new: bool
    linked_listings: int
    confidence_score: float


def _normalize_address(address: str | None) -> str:
    if not address:
        return ""
    addr = address.lower().strip()
    addr = re.sub(r"\s+", " ", addr)
    addr = re.sub(r"[.,;:!?\"'()\[\]{}]", "", addr)
    return addr


def _compute_dedupe_key(
    city: str | None,
    address_text: str | None,
    area_sqm: float | None,
) -> str:
    components = [
        (city or "").lower().strip(),
        _normalize_address(address_text),
        str(round(area_sqm or 0.0, 0)),
    ]
    return sha1("|".join(components).encode("utf-8")).hexdigest()


def unify_listing(
    session: Session,
    reference_id: str,
) -> UnificationResult | None:
    """Link a single canonical_listing to a property_entity, creating if needed."""
    listing = session.get(CanonicalListingModel, reference_id)
    if listing is None:
        return None

    dedupe_key = _compute_dedupe_key(
        listing.city, listing.address_text, listing.area_sqm
    )

    existing = session.scalar(
        select(PropertyEntityModel).where(
            PropertyEntityModel.dedupe_key == dedupe_key
        )
    )

    if existing is None:
        is_new = True
        prop = PropertyEntityModel(
            property_id=new_id("prop"),
            dedupe_key=dedupe_key,
            entity_type=listing.property_category or "unknown",
            canonical_title=listing.description[:200] if listing.description else None,
            canonical_description=listing.description,
            canonical_address=listing.address_text,
            canonical_city=listing.city,
            canonical_building_name=None,
            latitude=listing.latitude,
            longitude=listing.longitude,
            geom=None,
            confidence_score=0.0,
            review_status="needs_review",
        )
        session.add(prop)
        session.flush()
        property_id = prop.property_id
    else:
        is_new = False
        property_id = existing.property_id

    offer_exists = session.scalar(
        select(PropertyOfferModel.offer_id).where(
            PropertyOfferModel.property_id == property_id,
            PropertyOfferModel.listing_reference_id == reference_id,
        )
    )
    if offer_exists is None:
        now = datetime.now(timezone.utc)
        offer = PropertyOfferModel(
            offer_id=new_id("offer"),
            property_id=property_id,
            source_listing_id=None,
            listing_reference_id=reference_id,
            intent=listing.listing_intent or "mixed",
            offer_status="active" if listing.removed_at is None else "removed",
            price_amount=listing.price,
            currency=listing.currency,
            available_from=None,
            last_changed_at=now,
        )
        session.add(offer)

    linked_count = _count_linked_listings(session, property_id)
    confidence = _compute_confidence(session, property_id, linked_count)

    entity = session.get(PropertyEntityModel, property_id)
    if entity is not None:
        entity.confidence_score = confidence
        _merge_best_data(session, entity, property_id)

    return UnificationResult(
        property_id=property_id,
        is_new=is_new,
        linked_listings=linked_count,
        confidence_score=confidence,
    )


def unify_all_pending(session: Session, *, batch_size: int = 500) -> list[UnificationResult]:
    """Find canonical_listings that have no property_offer link and unify them."""
    subq = select(PropertyOfferModel.listing_reference_id)
    stmt = (
        select(CanonicalListingModel.reference_id)
        .where(
            CanonicalListingModel.removed_at.is_(None),
            ~CanonicalListingModel.reference_id.in_(subq),
        )
        .limit(batch_size)
    )
    ref_ids = list(session.scalars(stmt).all())
    results: list[UnificationResult] = []
    for ref_id in ref_ids:
        r = unify_listing(session, ref_id)
        if r is not None:
            results.append(r)
    return results


def _count_linked_listings(session: Session, property_id: str) -> int:
    return session.scalar(
        select(func.count(PropertyOfferModel.offer_id)).where(
            PropertyOfferModel.property_id == property_id
        )
    ) or 0


def _compute_confidence(session: Session, property_id: str, linked_count: int) -> float:
    """Confidence grows with cross-source matches. 1 source = 0.2, 2 = 0.5, 3+ = 0.8+."""
    if linked_count == 0:
        return 0.0

    distinct_sources = session.scalar(
        text("""
            SELECT count(DISTINCT cl.source_name)
            FROM property_offer po
            JOIN canonical_listing cl ON cl.reference_id = po.listing_reference_id
            WHERE po.property_id = :pid
        """),
        {"pid": property_id},
    ) or 0

    if distinct_sources >= 3:
        return min(0.8 + 0.05 * (distinct_sources - 3), 1.0)
    if distinct_sources == 2:
        return 0.5
    return 0.2


def _merge_best_data(session: Session, entity: PropertyEntityModel, property_id: str) -> None:
    """Pick the best title/description/location from all linked listings."""
    rows = session.execute(
        text("""
            SELECT cl.reference_id, cl.description, cl.address_text, cl.city,
                   cl.latitude, cl.longitude, cl.image_urls, cl.price,
                   cl.last_seen, cl.property_category,
                   jsonb_array_length(cl.image_urls) AS photo_count
            FROM property_offer po
            JOIN canonical_listing cl ON cl.reference_id = po.listing_reference_id
            WHERE po.property_id = :pid
            ORDER BY jsonb_array_length(cl.image_urls) DESC, cl.last_seen DESC
        """),
        {"pid": property_id},
    ).fetchall()

    if not rows:
        return

    best = rows[0]
    entity.canonical_description = best.description
    entity.canonical_address = best.address_text
    entity.canonical_city = best.city
    entity.entity_type = best.property_category or entity.entity_type

    if best.latitude is not None and best.longitude is not None:
        entity.latitude = best.latitude
        entity.longitude = best.longitude

    for row in rows:
        if row.description and (not entity.canonical_description or len(row.description) > len(entity.canonical_description)):
            entity.canonical_description = row.description
            entity.canonical_title = row.description[:200]
