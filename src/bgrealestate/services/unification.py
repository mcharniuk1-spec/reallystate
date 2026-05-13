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
from urllib.parse import urlparse

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


def _normalize_title(title: str | None) -> str:
    if not title:
        return ""
    t = title.lower().strip()
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"[.,;:!?\"'()\[\]{}]", "", t)
    return t


def _compute_dedupe_key(
    city: str | None,
    address_text: str | None,
    area_sqm: float | None,
) -> str:
    # Legacy fallback: (city, address, rounded area) for sparse pages.
    components = [(city or "").lower().strip(), _normalize_address(address_text), str(round(area_sqm or 0.0, 0))]
    return sha1("|".join(components).encode("utf-8")).hexdigest()


def _compute_dedupe_key_v2(
    *,
    city: str | None,
    address_text: str | None,
    title: str | None,
    area_sqm: float | None,
) -> str:
    """Primary dedupe: identical title+address (cross-source). Fallback: legacy key."""
    addr = _normalize_address(address_text)
    tit = _normalize_title(title)
    if addr and tit:
        components = [(city or "").lower().strip(), addr, tit]
        return sha1("|".join(components).encode("utf-8")).hexdigest()
    return _compute_dedupe_key(city, address_text, area_sqm)


def _url_key(url: str | None) -> str:
    if not url:
        return ""
    try:
        p = urlparse(url)
        # normalize: host + path without query
        return f"{p.netloc.lower()}{p.path}".rstrip("/")
    except Exception:
        return url.strip().lower()


def _image_overlap(a: list[str] | None, b: list[str] | None) -> float:
    """Return Jaccard overlap of normalized image URL keys."""
    if not a or not b:
        return 0.0
    sa = {_url_key(x) for x in a if x}
    sb = {_url_key(x) for x in b if x}
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / max(1, len(sa | sb))


def _is_strict_identical_listing(a: CanonicalListingModel, b: CanonicalListingModel) -> bool:
    """Completely identical except for link: title/address/price/area/images."""
    if (a.city or "").strip().lower() != (b.city or "").strip().lower():
        return False
    if _normalize_address(a.address_text) != _normalize_address(b.address_text):
        return False
    if _normalize_title(getattr(a, "title", None)) != _normalize_title(getattr(b, "title", None)):
        return False
    if (a.price or None) != (b.price or None):
        return False
    if (a.area_sqm or None) != (b.area_sqm or None):
        return False
    return _image_overlap(list(a.image_urls or []), list(b.image_urls or [])) >= 0.98


def unify_listing(
    session: Session,
    reference_id: str,
) -> UnificationResult | None:
    """Link a single canonical_listing to a property_entity, creating if needed."""
    listing = session.get(CanonicalListingModel, reference_id)
    if listing is None:
        return None

    dedupe_key = _compute_dedupe_key_v2(
        city=listing.city,
        address_text=listing.address_text,
        title=getattr(listing, "title", None),
        area_sqm=listing.area_sqm,
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
            canonical_title=(listing.title or (listing.description[:200] if listing.description else None)),
            canonical_description=listing.description,
            canonical_url=listing.listing_url,
            canonical_address=listing.address_text,
            canonical_city=listing.city,
            canonical_building_name=None,
            source_links=[],
            merged_image_urls=list(listing.image_urls or []),
            description_summary=None,
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

        # Photo-aware split: if title+address match but photos have zero overlap, keep separate property.
        # This prevents accidental merges where only a generic title/price matches.
        if existing.merged_image_urls and listing.image_urls:
            overlap = _image_overlap(list(existing.merged_image_urls), list(listing.image_urls or []))
            if overlap <= 0.01:
                dedupe_key = sha1(f"{dedupe_key}|split:{reference_id}".encode("utf-8")).hexdigest()
                prop = PropertyEntityModel(
                    property_id=new_id("prop"),
                    dedupe_key=dedupe_key,
                    entity_type=listing.property_category or "unknown",
                    canonical_title=(listing.title or (listing.description[:200] if listing.description else None)),
                    canonical_description=listing.description,
                    canonical_url=listing.listing_url,
                    canonical_address=listing.address_text,
                    canonical_city=listing.city,
                    canonical_building_name=None,
                    source_links=[],
                    merged_image_urls=list(listing.image_urls or []),
                    description_summary=None,
                    latitude=listing.latitude,
                    longitude=listing.longitude,
                    geom=None,
                    confidence_score=0.0,
                    review_status="needs_review",
                )
                session.add(prop)
                session.flush()
                property_id = prop.property_id
                is_new = True

    offer_exists = session.scalar(
        select(PropertyOfferModel.offer_id).where(
            PropertyOfferModel.property_id == property_id,
            PropertyOfferModel.listing_reference_id == reference_id,
        )
    )

    # If this listing is completely identical to an already-linked listing (except URL),
    # treat it as a duplicate: keep it for provenance, but don't create a new offer.
    if offer_exists is None and existing is not None:
        linked = session.scalars(
            select(CanonicalListingModel)
            .join(
                PropertyOfferModel,
                PropertyOfferModel.listing_reference_id == CanonicalListingModel.reference_id,
            )
            .where(PropertyOfferModel.property_id == property_id)
        ).all()
        for other in linked:
            if other.reference_id == reference_id:
                continue
            if _is_strict_identical_listing(listing, other) and _url_key(listing.listing_url) != _url_key(other.listing_url):
                listing.removed_at = listing.removed_at or datetime.now(timezone.utc)
                entity = session.get(PropertyEntityModel, property_id)
                if entity is not None:
                    links = list(entity.source_links or [])
                    if _url_key(listing.listing_url) not in {_url_key(x.get("listing_url")) for x in links if isinstance(x, dict)}:
                        links.append(
                            {
                                "reference_id": listing.reference_id,
                                "listing_url": listing.listing_url,
                                "first_seen": listing.first_seen.isoformat() if listing.first_seen else None,
                                "last_seen": listing.last_seen.isoformat() if listing.last_seen else None,
                                "note": "strict_duplicate_of",
                                "duplicate_of_reference_id": other.reference_id,
                            }
                        )
                        entity.source_links = links
                offer_exists = "__duplicate__"
                break

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
        _merge_best_data(session, entity, property_id, just_added_reference_id=reference_id)

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


def _merge_best_data(session: Session, entity: PropertyEntityModel, property_id: str, *, just_added_reference_id: str | None = None) -> None:
    """Pick the best title/description/location and aggregate sources + images from linked listings."""
    rows = session.execute(
        text("""
            SELECT cl.reference_id, cl.title, cl.description, cl.address_text, cl.city,
                   cl.latitude, cl.longitude, cl.image_urls, cl.price,
                   cl.last_seen, cl.first_seen, cl.listing_url, cl.property_category,
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
    entity.canonical_title = best.title or (best.description[:200] if best.description else entity.canonical_title)

    # Canonical URL: earliest first_seen among linked listings (stable primary link).
    try:
        earliest = min(rows, key=lambda r: r.first_seen or r.last_seen)
        entity.canonical_url = earliest.listing_url
    except Exception:
        entity.canonical_url = entity.canonical_url or None

    # Aggregate source links (unique by URL key).
    existing_links = list(entity.source_links or [])
    seen = {_url_key(item.get("listing_url")) for item in existing_links if isinstance(item, dict)}
    for r in rows:
        u = _url_key(r.listing_url)
        if not u or u in seen:
            continue
        existing_links.append(
            {
                "reference_id": r.reference_id,
                "listing_url": r.listing_url,
                "first_seen": r.first_seen.isoformat() if r.first_seen else None,
                "last_seen": r.last_seen.isoformat() if r.last_seen else None,
            }
        )
        seen.add(u)
    entity.source_links = existing_links

    # Merge images across sources.
    merged = []
    img_seen = set()
    for r in rows:
        for u in list(r.image_urls or []):
            k = _url_key(u)
            if not k or k in img_seen:
                continue
            img_seen.add(k)
            merged.append(u)
    entity.merged_image_urls = merged

    # Summarize descriptions from all linked listings (keep it short).
    descs = [r.description.strip() for r in rows if r.description and str(r.description).strip()]
    if descs:
        # Prefer the longest as canonical; summary includes up to 3 distinct descriptions.
        unique = []
        for d in sorted(descs, key=len, reverse=True):
            if all(d[:120] != u[:120] for u in unique):
                unique.append(d)
            if len(unique) >= 3:
                break
        summary = "\n\n---\n\n".join(unique)
        entity.description_summary = summary[:6000]

    if best.latitude is not None and best.longitude is not None:
        entity.latitude = best.latitude
        entity.longitude = best.longitude

    for row in rows:
        if row.description and (not entity.canonical_description or len(row.description) > len(entity.canonical_description)):
            entity.canonical_description = row.description
            entity.canonical_title = row.title or (row.description[:200] if row.description else entity.canonical_title)
