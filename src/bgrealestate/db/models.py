from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, ForeignKey, Integer, Numeric, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import UserDefinedType


class Geometry(UserDefinedType):
    cache_ok = True

    def __init__(self, geometry_type: str, srid: int = 4326) -> None:
        self.geometry_type = geometry_type
        self.srid = srid

    def get_col_spec(self, **_: Any) -> str:
        return f"geometry({self.geometry_type}, {self.srid})"


class Base(DeclarativeBase):
    pass


class SourceRegistryModel(Base):
    __tablename__ = "source_registry"

    source_name: Mapped[str] = mapped_column(Text, primary_key=True)
    tier: Mapped[int] = mapped_column(Integer, nullable=False)
    source_family: Mapped[str] = mapped_column(Text, nullable=False)
    owner_group: Mapped[str] = mapped_column(Text, nullable=False)
    access_mode: Mapped[str] = mapped_column(Text, nullable=False)
    risk_mode: Mapped[str] = mapped_column(Text, nullable=False)
    freshness_target: Mapped[str] = mapped_column(Text, nullable=False)
    publish_capable: Mapped[bool] = mapped_column(Boolean, nullable=False)
    dedupe_cluster_hint: Mapped[str] = mapped_column(Text, nullable=False)
    legal_mode: Mapped[str] = mapped_column(Text, nullable=False, default="public_or_contract_review")
    mvp_phase: Mapped[str] = mapped_column(Text, nullable=False, default="source_first_ingestion")
    best_extraction_method: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    primary_url: Mapped[str | None] = mapped_column(Text)
    related_urls: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    languages: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    listing_types: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)


class SourceEndpointModel(Base):
    __tablename__ = "source_endpoint"

    endpoint_id: Mapped[str] = mapped_column(Text, primary_key=True)
    source_name: Mapped[str] = mapped_column(ForeignKey("source_registry.source_name"), nullable=False)
    endpoint_kind: Mapped[str] = mapped_column(Text, nullable=False)
    base_url: Mapped[str] = mapped_column(Text, nullable=False)
    params_template: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    method: Mapped[str] = mapped_column(Text, nullable=False, default="GET")
    requires_headless: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    requires_auth: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rate_limit_policy: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class SourceLegalRuleModel(Base):
    __tablename__ = "source_legal_rule"

    rule_id: Mapped[str] = mapped_column(Text, primary_key=True)
    source_name: Mapped[str] = mapped_column(ForeignKey("source_registry.source_name"), nullable=False)
    allowed_for_ingestion: Mapped[bool] = mapped_column(Boolean, nullable=False)
    allowed_for_publishing: Mapped[bool] = mapped_column(Boolean, nullable=False)
    requires_contract: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    requires_consent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    blocks_live_scrape: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)


class CrawlJobModel(Base):
    __tablename__ = "crawl_job"

    job_id: Mapped[str] = mapped_column(Text, primary_key=True)
    source_name: Mapped[str] = mapped_column(ForeignKey("source_registry.source_name"), nullable=False)
    endpoint_id: Mapped[str | None] = mapped_column(Text)
    job_type: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cursor_key: Mapped[str | None] = mapped_column(Text)
    idempotency_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    metadata_jsonb: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)


class RawCaptureModel(Base):
    __tablename__ = "raw_capture"

    raw_capture_id: Mapped[str] = mapped_column(Text, primary_key=True)
    source_name: Mapped[str] = mapped_column(ForeignKey("source_registry.source_name"), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    storage_key: Mapped[str | None] = mapped_column(Text)
    sha256: Mapped[str | None] = mapped_column(Text)
    http_status: Mapped[int | None] = mapped_column(Integer)
    headers_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    parser_version: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_jsonb: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)


class SourceListingModel(Base):
    __tablename__ = "source_listing"
    __table_args__ = (UniqueConstraint("source_name", "external_id"),)

    source_listing_id: Mapped[str] = mapped_column(Text, primary_key=True)
    source_name: Mapped[str] = mapped_column(ForeignKey("source_registry.source_name"), nullable=False)
    external_id: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_url: Mapped[str] = mapped_column(Text, nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    current_snapshot_id: Mapped[str | None] = mapped_column(Text)
    source_reference: Mapped[str | None] = mapped_column(Text)
    source_payload_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class SourceListingSnapshotModel(Base):
    __tablename__ = "source_listing_snapshot"

    snapshot_id: Mapped[str] = mapped_column(Text, primary_key=True)
    source_listing_id: Mapped[str] = mapped_column(ForeignKey("source_listing.source_listing_id"), nullable=False)
    raw_capture_id: Mapped[str | None] = mapped_column(ForeignKey("raw_capture.raw_capture_id"))
    title: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    price_amount: Mapped[float | None] = mapped_column(Numeric)
    currency: Mapped[str | None] = mapped_column(Text)
    area_sqm: Mapped[float | None] = mapped_column(Float)
    rooms: Mapped[float | None] = mapped_column(Float)
    floor: Mapped[int | None] = mapped_column(Integer)
    total_floors: Mapped[int | None] = mapped_column(Integer)
    city: Mapped[str | None] = mapped_column(Text)
    district: Mapped[str | None] = mapped_column(Text)
    address_text: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    parsed_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CanonicalListingModel(Base):
    __tablename__ = "canonical_listing"

    reference_id: Mapped[str] = mapped_column(Text, primary_key=True)
    source_name: Mapped[str] = mapped_column(ForeignKey("source_registry.source_name"), nullable=False)
    owner_group: Mapped[str] = mapped_column(Text, nullable=False)
    listing_url: Mapped[str] = mapped_column(Text, nullable=False)
    external_id: Mapped[str] = mapped_column(Text, nullable=False)
    listing_intent: Mapped[str] = mapped_column(Text, nullable=False)
    property_category: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str | None] = mapped_column(Text)
    district: Mapped[str | None] = mapped_column(Text)
    resort: Mapped[str | None] = mapped_column(Text)
    region: Mapped[str | None] = mapped_column(Text)
    address_text: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    area_sqm: Mapped[float | None] = mapped_column(Float)
    rooms: Mapped[float | None] = mapped_column(Float)
    price: Mapped[float | None] = mapped_column(Numeric)
    currency: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    image_urls: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    removed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    parser_version: Mapped[str] = mapped_column(Text, nullable=False)
    crawl_provenance: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class PropertyEntityModel(Base):
    __tablename__ = "property_entity"

    property_id: Mapped[str] = mapped_column(Text, primary_key=True)
    dedupe_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    entity_type: Mapped[str] = mapped_column(Text, nullable=False, default="unknown")
    canonical_title: Mapped[str | None] = mapped_column(Text)
    canonical_description: Mapped[str | None] = mapped_column(Text)
    canonical_address: Mapped[str | None] = mapped_column(Text)
    canonical_city: Mapped[str | None] = mapped_column(Text)
    canonical_building_name: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    geom: Mapped[Any | None] = mapped_column(Geometry("Point", 4326))
    confidence_score: Mapped[float | None] = mapped_column(Float)
    review_status: Mapped[str] = mapped_column(Text, nullable=False, default="needs_review")


class PropertyOfferModel(Base):
    __tablename__ = "property_offer"

    offer_id: Mapped[str] = mapped_column(Text, primary_key=True)
    property_id: Mapped[str] = mapped_column(ForeignKey("property_entity.property_id"), nullable=False)
    source_listing_id: Mapped[str | None] = mapped_column(ForeignKey("source_listing.source_listing_id"))
    listing_reference_id: Mapped[str | None] = mapped_column(ForeignKey("canonical_listing.reference_id"))
    intent: Mapped[str] = mapped_column(Text, nullable=False)
    offer_status: Mapped[str] = mapped_column(Text, nullable=False)
    price_amount: Mapped[float | None] = mapped_column(Numeric)
    currency: Mapped[str | None] = mapped_column(Text)
    available_from: Mapped[date | None] = mapped_column(Date)
    last_changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class MediaAssetModel(Base):
    __tablename__ = "media_asset"

    media_id: Mapped[str] = mapped_column(Text, primary_key=True)
    source_url: Mapped[str | None] = mapped_column(Text)
    storage_key_original: Mapped[str | None] = mapped_column(Text)
    storage_key_web: Mapped[str | None] = mapped_column(Text)
    sha256: Mapped[str | None] = mapped_column(Text)
    perceptual_hash: Mapped[str | None] = mapped_column(Text)
    mime_type: Mapped[str | None] = mapped_column(Text)
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    bytes: Mapped[int | None] = mapped_column(BigInteger)
    download_status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class BuildingEntityModel(Base):
    __tablename__ = "building_entity"

    building_id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    footprint: Mapped[Any | None] = mapped_column(Geometry("MultiPolygon", 4326))
    centroid: Mapped[Any | None] = mapped_column(Geometry("Point", 4326))
    height_m: Mapped[float | None] = mapped_column(Float)
    levels: Mapped[int | None] = mapped_column(Integer)
    construction_year: Mapped[int | None] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    metadata_jsonb: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)


class AppUserModel(Base):
    __tablename__ = "app_user"

    user_id: Mapped[str] = mapped_column(Text, primary_key=True)
    external_auth_subject: Mapped[str | None] = mapped_column(Text, unique=True)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class OrganizationAccountModel(Base):
    __tablename__ = "organization_account"

    account_id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    account_type: Mapped[str] = mapped_column(Text, nullable=False, default="operator")
    billing_status: Mapped[str] = mapped_column(Text, nullable=False, default="trial")
    default_locale: Mapped[str] = mapped_column(Text, nullable=False, default="en")
    timezone: Mapped[str] = mapped_column(Text, nullable=False, default="Europe/Sofia")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class LeadThreadModel(Base):
    __tablename__ = "lead_thread"

    thread_id: Mapped[str] = mapped_column(Text, primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("organization_account.account_id"), nullable=False)
    channel_account_id: Mapped[str | None] = mapped_column(Text)
    external_thread_id: Mapped[str | None] = mapped_column(Text)
    lead_contact_id: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="new")
    stage: Mapped[str] = mapped_column(Text, nullable=False, default="new")
    assignee_user_id: Mapped[str | None] = mapped_column(ForeignKey("app_user.user_id"))
    priority: Mapped[str] = mapped_column(Text, nullable=False, default="normal")
    unread_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    follow_up_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class LeadMessageModel(Base):
    __tablename__ = "lead_message"

    message_id: Mapped[str] = mapped_column(Text, primary_key=True)
    thread_id: Mapped[str] = mapped_column(ForeignKey("lead_thread.thread_id"), nullable=False)
    direction: Mapped[str] = mapped_column(Text, nullable=False)
    sender_type: Mapped[str] = mapped_column(Text, nullable=False)
    sender_id: Mapped[str | None] = mapped_column(Text)
    external_message_id: Mapped[str | None] = mapped_column(Text)
    body_text: Mapped[str | None] = mapped_column(Text)
    body_html: Mapped[str | None] = mapped_column(Text)
    language: Mapped[str | None] = mapped_column(Text)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivery_status: Mapped[str] = mapped_column(Text, nullable=False, default="stored")
    metadata_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class PublishJobModel(Base):
    __tablename__ = "publish_job"

    publish_job_id: Mapped[str] = mapped_column(Text, primary_key=True)
    property_reference_id: Mapped[str] = mapped_column(ForeignKey("canonical_listing.reference_id"), nullable=False)
    channel: Mapped[str] = mapped_column(Text, nullable=False)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class PublishAttemptModel(Base):
    __tablename__ = "publish_attempt"

    attempt_id: Mapped[str] = mapped_column(Text, primary_key=True)
    publish_job_id: Mapped[str] = mapped_column(ForeignKey("publish_job.publish_job_id"), nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    request_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    response_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    error_code: Mapped[str | None] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
