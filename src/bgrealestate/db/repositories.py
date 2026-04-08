from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from ..connectors.legal import DerivedLegalRule
from ..models import CanonicalListing, RawCapture, SourceRegistryEntry
from .ids import new_id
from .models import (
    CanonicalListingModel,
    CrawlJobModel,
    LeadMessageModel,
    LeadThreadModel,
    ListingMediaModel,
    PropertyEntityModel,
    PropertyOfferModel,
    RawCaptureModel,
    SourceEndpointModel,
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
                primary_url=(entry.primary_url or None) or None,
                related_urls=list(entry.related_urls or []),
                languages=list(entry.languages or []),
                listing_types=list(entry.listing_types or []),
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
                    "primary_url": (entry.primary_url or None) or None,
                    "related_urls": list(entry.related_urls or []),
                    "languages": list(entry.languages or []),
                    "listing_types": list(entry.listing_types or []),
                },
            )
        )
        self.session.execute(stmt)

    def upsert_legal_rule(self, rule: DerivedLegalRule, *, source_name: str) -> None:
        stmt = (
            insert(SourceLegalRuleModel)
            .values(
                rule_id=rule.rule_id,
                source_name=source_name,
                allowed_for_ingestion=rule.allowed_for_ingestion,
                allowed_for_publishing=rule.allowed_for_publishing,
                requires_contract=rule.requires_contract,
                requires_consent=rule.requires_consent,
                blocks_live_scrape=rule.blocks_live_scrape,
                reason=rule.reason,
            )
            .on_conflict_do_update(
                index_elements=[SourceLegalRuleModel.rule_id],
                set_={
                    "source_name": source_name,
                    "allowed_for_ingestion": rule.allowed_for_ingestion,
                    "allowed_for_publishing": rule.allowed_for_publishing,
                    "requires_contract": rule.requires_contract,
                    "requires_consent": rule.requires_consent,
                    "blocks_live_scrape": rule.blocks_live_scrape,
                    "reason": rule.reason,
                },
            )
        )
        self.session.execute(stmt)

    def upsert_endpoint(
        self,
        *,
        endpoint_id: str,
        source_name: str,
        endpoint_kind: str,
        base_url: str,
        params_template: dict[str, object],
        method: str,
        requires_headless: bool,
        requires_auth: bool,
        rate_limit_policy: dict[str, object],
    ) -> None:
        stmt = (
            insert(SourceEndpointModel)
            .values(
                endpoint_id=endpoint_id,
                source_name=source_name,
                endpoint_kind=endpoint_kind,
                base_url=base_url,
                params_template=params_template,
                method=method,
                requires_headless=requires_headless,
                requires_auth=requires_auth,
                rate_limit_policy=rate_limit_policy,
            )
            .on_conflict_do_update(
                index_elements=[SourceEndpointModel.endpoint_id],
                set_={
                    "source_name": source_name,
                    "endpoint_kind": endpoint_kind,
                    "base_url": base_url,
                    "params_template": params_template,
                    "method": method,
                    "requires_headless": requires_headless,
                    "requires_auth": requires_auth,
                    "rate_limit_policy": rate_limit_policy,
                },
            )
        )
        self.session.execute(stmt)

    def get_legal_rule(self, source_name: str) -> SourceLegalRuleModel | None:
        return self.session.scalar(select(SourceLegalRuleModel).where(SourceLegalRuleModel.source_name == source_name))


class CrawlJobRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_recent(self, *, limit: int = 50, offset: int = 0) -> list[CrawlJobModel]:
        stmt = (
            select(CrawlJobModel)
            .order_by(CrawlJobModel.scheduled_for.desc())
            .limit(min(limit, 500))
            .offset(offset)
        )
        return list(self.session.scalars(stmt).all())


class CrmRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_threads(self, *, limit: int = 50, offset: int = 0, account_id: str | None = None) -> list[LeadThreadModel]:
        stmt = select(LeadThreadModel).order_by(
            LeadThreadModel.last_message_at.desc().nulls_last(),
            LeadThreadModel.created_at.desc(),
        )
        if account_id:
            stmt = stmt.where(LeadThreadModel.account_id == account_id)
        stmt = stmt.limit(min(limit, 200)).offset(offset)
        return list(self.session.scalars(stmt).all())

    def get_thread(self, thread_id: str) -> LeadThreadModel | None:
        return self.session.get(LeadThreadModel, thread_id)

    def list_messages(self, thread_id: str) -> list[LeadMessageModel]:
        stmt = (
            select(LeadMessageModel)
            .where(LeadMessageModel.thread_id == thread_id)
            .order_by(LeadMessageModel.received_at.asc().nullsfirst(), LeadMessageModel.sent_at.asc().nullsfirst())
        )
        return list(self.session.scalars(stmt).all())

    def append_operator_message(self, thread_id: str, body_text: str) -> LeadMessageModel:
        thread = self.get_thread(thread_id)
        if thread is None:
            raise ValueError("thread_not_found")
        now = datetime.now(timezone.utc)
        msg = LeadMessageModel(
            message_id=new_id("lmsg"),
            thread_id=thread_id,
            direction="outbound",
            sender_type="operator",
            sender_id=None,
            external_message_id=None,
            body_text=body_text,
            body_html=None,
            language=None,
            sent_at=now,
            received_at=None,
            delivery_status="stored",
            metadata_jsonb={"kind": "manual_note"},
        )
        self.session.add(msg)
        thread.last_message_at = now
        return msg


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

    def list_recent(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        source_name: str | None = None,
        include_removed: bool = False,
    ) -> list[CanonicalListingModel]:
        stmt = select(CanonicalListingModel)
        if not include_removed:
            stmt = stmt.where(CanonicalListingModel.removed_at.is_(None))
        if source_name:
            stmt = stmt.where(CanonicalListingModel.source_name == source_name)
        stmt = stmt.order_by(CanonicalListingModel.last_seen.desc()).limit(min(limit, 200)).offset(offset)
        return list(self.session.scalars(stmt).all())

    def get(self, reference_id: str) -> CanonicalListingModel | None:
        return self.session.get(CanonicalListingModel, reference_id)


class PropertyEntityRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_properties(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        city: str | None = None,
        min_confidence: float | None = None,
    ) -> list[PropertyEntityModel]:
        stmt = select(PropertyEntityModel)
        if city:
            stmt = stmt.where(PropertyEntityModel.canonical_city == city)
        if min_confidence is not None:
            stmt = stmt.where(PropertyEntityModel.confidence_score >= min_confidence)
        stmt = (
            stmt.order_by(
                PropertyEntityModel.confidence_score.desc().nulls_last(),
            )
            .limit(min(limit, 200))
            .offset(offset)
        )
        return list(self.session.scalars(stmt).all())

    def get(self, property_id: str) -> PropertyEntityModel | None:
        return self.session.get(PropertyEntityModel, property_id)

    def get_offers(self, property_id: str) -> list[PropertyOfferModel]:
        stmt = (
            select(PropertyOfferModel)
            .where(PropertyOfferModel.property_id == property_id)
            .order_by(PropertyOfferModel.last_changed_at.desc())
        )
        return list(self.session.scalars(stmt).all())

    def get_linked_listings(self, property_id: str) -> list[CanonicalListingModel]:
        stmt = (
            select(CanonicalListingModel)
            .join(
                PropertyOfferModel,
                PropertyOfferModel.listing_reference_id == CanonicalListingModel.reference_id,
            )
            .where(PropertyOfferModel.property_id == property_id)
            .order_by(CanonicalListingModel.last_seen.desc())
        )
        return list(self.session.scalars(stmt).all())


class ListingMediaRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert_media(
        self,
        *,
        media_id: str,
        listing_reference_id: str,
        url: str,
        ordering: int = 0,
        content_hash: str | None = None,
        storage_key: str | None = None,
        mime_type: str | None = None,
        width: int | None = None,
        height: int | None = None,
        file_size: int | None = None,
        download_status: str = "pending",
    ) -> str:
        stmt = (
            insert(ListingMediaModel)
            .values(
                media_id=media_id,
                listing_reference_id=listing_reference_id,
                url=url,
                ordering=ordering,
                content_hash=content_hash,
                storage_key=storage_key,
                mime_type=mime_type,
                width=width,
                height=height,
                file_size=file_size,
                download_status=download_status,
            )
            .on_conflict_do_update(
                index_elements=[ListingMediaModel.media_id],
                set_={
                    "url": url,
                    "ordering": ordering,
                    "content_hash": content_hash,
                    "storage_key": storage_key,
                    "mime_type": mime_type,
                    "width": width,
                    "height": height,
                    "file_size": file_size,
                    "download_status": download_status,
                },
            )
        )
        self.session.execute(stmt)
        return media_id

    def list_for_listing(self, reference_id: str) -> list[ListingMediaModel]:
        stmt = (
            select(ListingMediaModel)
            .where(ListingMediaModel.listing_reference_id == reference_id)
            .order_by(ListingMediaModel.ordering.asc())
        )
        return list(self.session.scalars(stmt).all())

    def get(self, media_id: str) -> ListingMediaModel | None:
        return self.session.get(ListingMediaModel, media_id)

    def count_for_listing(self, reference_id: str) -> int:
        from sqlalchemy import func
        stmt = select(func.count()).where(ListingMediaModel.listing_reference_id == reference_id)
        return self.session.scalar(stmt) or 0

