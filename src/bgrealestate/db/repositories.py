from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from ..models import CanonicalListing, RawCapture, SourceRegistryEntry
from .ids import new_id
from .models import (
    CanonicalListingModel,
    RawCaptureModel,
    SourceLegalRuleModel,
    SourceListingModel,
    SourceListingSnapshotModel,
    SourceRegistryModel,
)


class SourceRegistryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert_source(self, entry: SourceRegistryEntry) -> None:
        stmt = (
            insert(SourceRegistryModel)
            .values(
                source_name=entry.source_name,
                tier=entry.tier,
                source_family=str(entry.source_family.value) if hasattr(entry.source_family, "value") else str(entry.source_family),
                owner_group=entry.owner_group,
                access_mode=str(entry.access_mode.value) if hasattr(entry.access_mode, "value") else str(entry.access_mode),
                risk_mode=str(entry.risk_mode.value) if hasattr(entry.risk_mode, "value") else str(entry.risk_mode),
                freshness_target=str(entry.freshness_target.value) if hasattr(entry.freshness_target, "value") else str(entry.freshness_target),
                publish_capable=entry.publish_capable,
                dedupe_cluster_hint=entry.dedupe_cluster_hint,
                legal_mode=entry.legal_mode,
                mvp_phase=entry.mvp_phase,
                best_extraction_method=entry.best_extraction_method or None,
                notes=entry.notes or None,
            )
            .on_conflict_do_update(
                index_elements=[SourceRegistryModel.source_name],
                set_={
                    "tier": entry.tier,
                    "source_family": str(entry.source_family.value) if hasattr(entry.source_family, "value") else str(entry.source_family),
                    "owner_group": entry.owner_group,
                    "access_mode": str(entry.access_mode.value) if hasattr(entry.access_mode, "value") else str(entry.access_mode),
                    "risk_mode": str(entry.risk_mode.value) if hasattr(entry.risk_mode, "value") else str(entry.risk_mode),
                    "freshness_target": str(entry.freshness_target.value) if hasattr(entry.freshness_target, "value") else str(entry.freshness_target),
                    "publish_capable": entry.publish_capable,
                    "dedupe_cluster_hint": entry.dedupe_cluster_hint,
                    "legal_mode": entry.legal_mode,
                    "mvp_phase": entry.mvp_phase,
                    "best_extraction_method": entry.best_extraction_method or None,
                    "notes": entry.notes or None,
                },
            )
        )
        self.session.execute(stmt)

    def get_legal_rule(self, source_name: str) -> SourceLegalRuleModel | None:
        return self.session.scalar(select(SourceLegalRuleModel).where(SourceLegalRuleModel.source_name == source_name))


class RawCaptureRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def insert(self, capture: RawCapture, *, raw_capture_id: str | None = None, sha256: str | None = None) -> str:
        raw_capture_id = raw_capture_id or new_id("raw")
        self.session.add(
            RawCaptureModel(
                raw_capture_id=raw_capture_id,
                source_name=capture.source_name,
                url=capture.url,
                content_type=capture.content_type,
                body=capture.body,
                storage_key=None,
                sha256=sha256,
                http_status=capture.metadata.get("http_status"),
                headers_json=capture.metadata.get("headers", {}),
                fetched_at=capture.fetched_at,
                parser_version=capture.parser_version,
                metadata_jsonb={k: v for k, v in capture.metadata.items() if k not in {"headers", "http_status"}},
            )
        )
        return raw_capture_id


class ListingRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert_source_listing(
        self,
        *,
        source_name: str,
        external_id: str,
        canonical_url: str,
        seen_at: datetime,
        status: str,
        source_payload: dict[str, Any] | None = None,
        source_reference: str | None = None,
    ) -> str:
        source_payload = source_payload or {}
        source_listing_id = new_id("slist")
        stmt = (
            insert(SourceListingModel)
            .values(
                source_listing_id=source_listing_id,
                source_name=source_name,
                external_id=external_id,
                canonical_url=canonical_url,
                first_seen_at=seen_at,
                last_seen_at=seen_at,
                status=status,
                current_snapshot_id=None,
                source_reference=source_reference,
                source_payload_jsonb=source_payload,
            )
            .on_conflict_do_update(
                index_elements=[SourceListingModel.source_name, SourceListingModel.external_id],
                set_={
                    "canonical_url": canonical_url,
                    "last_seen_at": seen_at,
                    "status": status,
                    "source_reference": source_reference,
                    "source_payload_jsonb": source_payload,
                },
            )
            .returning(SourceListingModel.source_listing_id)
        )
        return str(self.session.execute(stmt).scalar_one())

    def set_current_snapshot(self, source_listing_id: str, snapshot_id: str) -> None:
        self.session.execute(
            update(SourceListingModel)
            .where(SourceListingModel.source_listing_id == source_listing_id)
            .values(current_snapshot_id=snapshot_id)
        )

    def insert_snapshot(
        self,
        *,
        source_listing_id: str,
        raw_capture_id: str | None,
        created_at: datetime,
        parsed: dict[str, Any],
    ) -> str:
        snapshot_id = new_id("ssnap")
        self.session.add(
            SourceListingSnapshotModel(
                snapshot_id=snapshot_id,
                source_listing_id=source_listing_id,
                raw_capture_id=raw_capture_id,
                title=parsed.get("title"),
                description=parsed.get("description"),
                price_amount=parsed.get("price"),
                currency=parsed.get("currency"),
                area_sqm=parsed.get("area_sqm"),
                rooms=parsed.get("rooms"),
                floor=parsed.get("floor"),
                total_floors=parsed.get("total_floors"),
                city=parsed.get("city"),
                district=parsed.get("district"),
                address_text=parsed.get("address_text"),
                latitude=parsed.get("latitude"),
                longitude=parsed.get("longitude"),
                parsed_jsonb=parsed,
                created_at=created_at,
            )
        )
        return snapshot_id


class CanonicalListingRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert(self, listing: CanonicalListing) -> None:
        values = asdict(listing)
        # Enums serialize as objects in asdict; store their value/str.
        values["listing_intent"] = str(listing.listing_intent.value) if hasattr(listing.listing_intent, "value") else str(listing.listing_intent)
        values["property_category"] = (
            str(listing.property_category.value) if hasattr(listing.property_category, "value") else str(listing.property_category)
        )
        stmt = (
            insert(CanonicalListingModel)
            .values(**values)
            .on_conflict_do_update(
                index_elements=[CanonicalListingModel.reference_id],
                set_={
                    "listing_url": listing.listing_url,
                    "city": listing.city,
                    "district": listing.district,
                    "resort": listing.resort,
                    "region": listing.region,
                    "address_text": listing.address_text,
                    "latitude": listing.latitude,
                    "longitude": listing.longitude,
                    "area_sqm": listing.area_sqm,
                    "rooms": listing.rooms,
                    "price": listing.price,
                    "currency": listing.currency,
                    "description": listing.description,
                    "image_urls": listing.image_urls,
                    "last_seen": listing.last_seen,
                    "last_changed_at": listing.last_changed_at,
                    "removed_at": listing.removed_at,
                    "parser_version": listing.parser_version,
                    "crawl_provenance": listing.crawl_provenance,
                },
            )
        )
        self.session.execute(stmt)

