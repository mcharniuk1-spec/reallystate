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
    geocode_confidence: Mapped[float | None] = mapped_column(Float)
    building_name: Mapped[str | None] = mapped_column(Text)
    area_sqm: Mapped[float | None] = mapped_column(Float)
    rooms: Mapped[float | None] = mapped_column(Float)
    floor: Mapped[int | None] = mapped_column(Integer)
    total_floors: Mapped[int | None] = mapped_column(Integer)
    construction_type: Mapped[str | None] = mapped_column(Text)
    construction_year: Mapped[int | None] = mapped_column(Integer)
    stage: Mapped[str | None] = mapped_column(Text)
    act16_present: Mapped[bool | None] = mapped_column(Boolean)
    price: Mapped[float | None] = mapped_column(Numeric)
    currency: Mapped[str | None] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(Text)
    fees: Mapped[float | None] = mapped_column(Numeric)
    price_per_sqm: Mapped[float | None] = mapped_column(Numeric)
    broker_name: Mapped[str | None] = mapped_column(Text)
    agency_name: Mapped[str | None] = mapped_column(Text)
    owner_name: Mapped[str | None] = mapped_column(Text)
    developer_name: Mapped[str | None] = mapped_column(Text)
    phones: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    messenger_handles: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    outbound_channel_hints: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    description: Mapped[str | None] = mapped_column(Text)
    amenities: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    image_urls: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    removed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    parser_version: Mapped[str] = mapped_column(Text, nullable=False)
    crawl_provenance: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    # Stage 1 region-first (Varna-only) + full-detail pipeline fields (nullable for legacy rows)
    region_key: Mapped[str | None] = mapped_column(Text)
    segment_key: Mapped[str | None] = mapped_column(Text)
    vertical_key: Mapped[str | None] = mapped_column(Text)
    source_section_id: Mapped[str | None] = mapped_column(Text)
    list_page_url: Mapped[str | None] = mapped_column(Text)
    detail_url_canonical: Mapped[str | None] = mapped_column(Text)
    combined_text: Mapped[str | None] = mapped_column(Text)
    normalized_text: Mapped[str | None] = mapped_column(Text)
    structured_extra: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    raw_text_fallback: Mapped[str | None] = mapped_column(Text)
    raw_detail_storage_key: Mapped[str | None] = mapped_column(Text)


class PropertyEntityModel(Base):
    __tablename__ = "property_entity"

    property_id: Mapped[str] = mapped_column(Text, primary_key=True)
    dedupe_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    entity_type: Mapped[str] = mapped_column(Text, nullable=False, default="unknown")
    canonical_title: Mapped[str | None] = mapped_column(Text)
    canonical_description: Mapped[str | None] = mapped_column(Text)
    canonical_url: Mapped[str | None] = mapped_column(Text)
    canonical_address: Mapped[str | None] = mapped_column(Text)
    canonical_city: Mapped[str | None] = mapped_column(Text)
    canonical_building_name: Mapped[str | None] = mapped_column(Text)
    source_links: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    merged_image_urls: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    description_summary: Mapped[str | None] = mapped_column(Text)
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


class PersonContactModel(Base):
    __tablename__ = "person_contact"

    contact_id: Mapped[str] = mapped_column(Text, primary_key=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_name: Mapped[str | None] = mapped_column(Text)
    organization_id: Mapped[str | None] = mapped_column(Text)
    role: Mapped[str | None] = mapped_column(Text)
    language_codes: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    metadata_jsonb: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)


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
    room_type: Mapped[str | None] = mapped_column(Text)
    quality_score: Mapped[float | None] = mapped_column(Float)
    is_exterior: Mapped[bool | None] = mapped_column(Boolean)
    is_floorplan: Mapped[bool | None] = mapped_column(Boolean)


class ListingMediaModel(Base):
    __tablename__ = "listing_media"

    media_id: Mapped[str] = mapped_column(Text, primary_key=True)
    listing_reference_id: Mapped[str] = mapped_column(ForeignKey("canonical_listing.reference_id"), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str | None] = mapped_column(Text)
    caption: Mapped[str | None] = mapped_column(Text)
    ordering: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    storage_key: Mapped[str | None] = mapped_column(Text)
    mime_type: Mapped[str | None] = mapped_column(Text)
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    file_size: Mapped[int | None] = mapped_column(BigInteger)
    download_status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")


class SourcePublicationQAReviewModel(Base):
    __tablename__ = "source_publication_qa_review"
    __table_args__ = (UniqueConstraint("source_listing_id", "reviewer"),)

    review_id: Mapped[str] = mapped_column(Text, primary_key=True)
    source_listing_id: Mapped[str] = mapped_column(ForeignKey("source_listing.source_listing_id"), nullable=False)
    listing_reference_id: Mapped[str | None] = mapped_column(ForeignKey("canonical_listing.reference_id"))
    qa_state: Mapped[str] = mapped_column(Text, nullable=False)
    reviewer: Mapped[str] = mapped_column(Text, nullable=False, default="system")
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    import_eligible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    import_eligibility_reason: Mapped[str | None] = mapped_column(Text)
    blocked_import_reason: Mapped[str | None] = mapped_column(Text)
    source_publication_type: Mapped[str | None] = mapped_column(Text)
    scrape_acceptance_status: Mapped[str | None] = mapped_column(Text)
    evidence_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class StatusHistoryModel(Base):
    __tablename__ = "status_history"
    __table_args__ = (UniqueConstraint("subject_type", "subject_id", "to_status", "observed_at"),)

    status_event_id: Mapped[str] = mapped_column(Text, primary_key=True)
    subject_type: Mapped[str] = mapped_column(Text, nullable=False)
    subject_id: Mapped[str] = mapped_column(Text, nullable=False)
    from_status: Mapped[str | None] = mapped_column(Text)
    to_status: Mapped[str] = mapped_column(Text, nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    provenance_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class EntityResolutionCandidateModel(Base):
    __tablename__ = "entity_resolution_candidate"
    __table_args__ = (
        UniqueConstraint("primary_listing_reference_id", "candidate_listing_reference_id", "candidate_type"),
    )

    candidate_id: Mapped[str] = mapped_column(Text, primary_key=True)
    candidate_type: Mapped[str] = mapped_column(Text, nullable=False)
    primary_listing_reference_id: Mapped[str] = mapped_column(ForeignKey("canonical_listing.reference_id"), nullable=False)
    candidate_listing_reference_id: Mapped[str | None] = mapped_column(ForeignKey("canonical_listing.reference_id"))
    candidate_property_id: Mapped[str | None] = mapped_column(ForeignKey("property_entity.property_id"))
    review_status: Mapped[str] = mapped_column(Text, nullable=False, default="needs_review")
    confidence_score: Mapped[float | None] = mapped_column(Float)
    score_components_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    conflict_reasons_jsonb: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    accepted_only_filter_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    evidence_snapshot_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class EntityResolutionReviewEventModel(Base):
    __tablename__ = "entity_resolution_review_event"

    review_event_id: Mapped[str] = mapped_column(Text, primary_key=True)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("entity_resolution_candidate.candidate_id"), nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    actor_user_id: Mapped[str | None] = mapped_column(ForeignKey("app_user.user_id"))
    from_status: Mapped[str | None] = mapped_column(Text)
    to_status: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[str | None] = mapped_column(Text)
    evidence_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class MediaDescriptionModel(Base):
    __tablename__ = "media_description"

    media_description_id: Mapped[str] = mapped_column(Text, primary_key=True)
    media_id: Mapped[str | None] = mapped_column(ForeignKey("media_asset.media_id"))
    listing_media_id: Mapped[str | None] = mapped_column(ForeignKey("listing_media.media_id"))
    listing_reference_id: Mapped[str | None] = mapped_column(ForeignKey("canonical_listing.reference_id"))
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    model_name: Mapped[str] = mapped_column(Text, nullable=False)
    model_version: Mapped[str | None] = mapped_column(Text)
    coverage_state: Mapped[str] = mapped_column(Text, nullable=False, default="pending")
    scene_type: Mapped[str | None] = mapped_column(Text)
    description_text: Mapped[str | None] = mapped_column(Text)
    confidence_score: Mapped[float | None] = mapped_column(Float)
    uncertainty_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    evidence_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class AvailabilityCalendarModel(Base):
    __tablename__ = "availability_calendar"

    calendar_id: Mapped[str] = mapped_column(Text, primary_key=True)
    listing_reference_id: Mapped[str | None] = mapped_column(ForeignKey("canonical_listing.reference_id"))
    offer_id: Mapped[str | None] = mapped_column(ForeignKey("property_offer.offer_id"))
    calendar_type: Mapped[str] = mapped_column(Text, nullable=False)
    source_name: Mapped[str | None] = mapped_column(ForeignKey("source_registry.source_name"))
    source_url: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active")
    metadata_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AvailabilitySlotModel(Base):
    __tablename__ = "availability_slot"
    __table_args__ = (UniqueConstraint("calendar_id", "slot_start", "slot_end"),)

    slot_id: Mapped[str] = mapped_column(Text, primary_key=True)
    calendar_id: Mapped[str] = mapped_column(ForeignKey("availability_calendar.calendar_id"), nullable=False)
    slot_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    slot_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    slot_status: Mapped[str] = mapped_column(Text, nullable=False)
    price_amount: Mapped[float | None] = mapped_column(Numeric)
    currency: Mapped[str | None] = mapped_column(Text)
    metadata_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class AvailabilityObservationModel(Base):
    __tablename__ = "availability_observation"

    observation_id: Mapped[str] = mapped_column(Text, primary_key=True)
    listing_reference_id: Mapped[str | None] = mapped_column(ForeignKey("canonical_listing.reference_id"))
    offer_id: Mapped[str | None] = mapped_column(ForeignKey("property_offer.offer_id"))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    availability_status: Mapped[str] = mapped_column(Text, nullable=False)
    price_amount: Mapped[float | None] = mapped_column(Numeric)
    currency: Mapped[str | None] = mapped_column(Text)
    provenance_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class ViewingInquiryRequestModel(Base):
    __tablename__ = "viewing_inquiry_request"

    request_id: Mapped[str] = mapped_column(Text, primary_key=True)
    listing_reference_id: Mapped[str | None] = mapped_column(ForeignKey("canonical_listing.reference_id"))
    property_id: Mapped[str | None] = mapped_column(ForeignKey("property_entity.property_id"))
    offer_id: Mapped[str | None] = mapped_column(ForeignKey("property_offer.offer_id"))
    requester_user_id: Mapped[str | None] = mapped_column(ForeignKey("app_user.user_id"))
    contact_id: Mapped[str | None] = mapped_column(ForeignKey("person_contact.contact_id"))
    request_type: Mapped[str] = mapped_column(Text, nullable=False)
    request_status: Mapped[str] = mapped_column(Text, nullable=False, default="new")
    preferred_time_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    message_summary: Mapped[str | None] = mapped_column(Text)
    provenance_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ExternalChatRefModel(Base):
    __tablename__ = "external_chat_ref"

    chat_ref_id: Mapped[str] = mapped_column(Text, primary_key=True)
    thread_id: Mapped[str | None] = mapped_column(ForeignKey("lead_thread.thread_id"))
    request_id: Mapped[str | None] = mapped_column(ForeignKey("viewing_inquiry_request.request_id"))
    listing_reference_id: Mapped[str | None] = mapped_column(ForeignKey("canonical_listing.reference_id"))
    property_id: Mapped[str | None] = mapped_column(ForeignKey("property_entity.property_id"))
    offer_id: Mapped[str | None] = mapped_column(ForeignKey("property_offer.offer_id"))
    participant_contact_id: Mapped[str | None] = mapped_column(ForeignKey("person_contact.contact_id"))
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    external_thread_ref: Mapped[str | None] = mapped_column(Text)
    handoff_status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")
    metadata_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


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
    password_hash: Mapped[str | None] = mapped_column(Text)
    user_mode: Mapped[str] = mapped_column(Text, nullable=False, default="buyer")
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class SavedPropertyModel(Base):
    __tablename__ = "saved_property"
    __table_args__ = (UniqueConstraint("user_id", "property_id"),)

    saved_id: Mapped[str] = mapped_column(Text, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("app_user.user_id"), nullable=False)
    property_id: Mapped[str] = mapped_column(ForeignKey("property_entity.property_id"), nullable=False)
    listing_reference_id: Mapped[str | None] = mapped_column(ForeignKey("canonical_listing.reference_id"))
    status: Mapped[str] = mapped_column(Text, nullable=False, default="liked")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SavedPropertyStatusEventModel(Base):
    __tablename__ = "saved_property_status_event"

    event_id: Mapped[str] = mapped_column(Text, primary_key=True)
    saved_id: Mapped[str] = mapped_column(ForeignKey("saved_property.saved_id"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("app_user.user_id"), nullable=False)
    property_id: Mapped[str] = mapped_column(ForeignKey("property_entity.property_id"), nullable=False)
    actor_user_id: Mapped[str | None] = mapped_column(ForeignKey("app_user.user_id"))
    action: Mapped[str] = mapped_column(Text, nullable=False)
    from_status: Mapped[str | None] = mapped_column(Text)
    to_status: Mapped[str] = mapped_column(Text, nullable=False)
    details_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


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


class LeadThreadPropertyLinkModel(Base):
    __tablename__ = "lead_thread_property_link"

    link_id: Mapped[str] = mapped_column(Text, primary_key=True)
    thread_id: Mapped[str] = mapped_column(ForeignKey("lead_thread.thread_id"), nullable=False)
    property_id: Mapped[str | None] = mapped_column(ForeignKey("property_entity.property_id"))
    source_listing_id: Mapped[str | None] = mapped_column(ForeignKey("source_listing.source_listing_id"))
    offer_id: Mapped[str | None] = mapped_column(ForeignKey("property_offer.offer_id"))
    relationship_type: Mapped[str] = mapped_column(Text, nullable=False)


class UserPropertyChatModel(Base):
    __tablename__ = "user_property_chat"
    __table_args__ = (UniqueConstraint("user_id", "property_id"),)

    chat_id: Mapped[str] = mapped_column(Text, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("app_user.user_id"), nullable=False)
    property_id: Mapped[str] = mapped_column(ForeignKey("property_entity.property_id"), nullable=False)
    thread_id: Mapped[str] = mapped_column(ForeignKey("lead_thread.thread_id"), nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


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


# --- Stage 1 scrape control plane (Varna-only, region-first) ---


class ScrapeRegionModel(Base):
    __tablename__ = "scrape_region"

    region_key: Mapped[str] = mapped_column(Text, primary_key=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    country_code: Mapped[str] = mapped_column(Text, nullable=False, default="BG")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SourceSectionModel(Base):
    __tablename__ = "source_section"
    __table_args__ = (UniqueConstraint("source_name", "region_key", "segment_key", "vertical_key"),)

    section_id: Mapped[str] = mapped_column(Text, primary_key=True)
    source_name: Mapped[str] = mapped_column(ForeignKey("source_registry.source_name"), nullable=False)
    region_key: Mapped[str] = mapped_column(ForeignKey("scrape_region.region_key"), nullable=False)
    segment_key: Mapped[str] = mapped_column(Text, nullable=False)
    vertical_key: Mapped[str] = mapped_column(Text, nullable=False)
    section_label: Mapped[str] = mapped_column(Text, nullable=False)
    entry_urls: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    legal_notes: Mapped[str | None] = mapped_column(Text)
    varna_filter: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SourceSectionPatternModel(Base):
    __tablename__ = "source_section_pattern"
    __table_args__ = (UniqueConstraint("section_id", "pattern_layer", "schema_version"),)

    pattern_id: Mapped[str] = mapped_column(Text, primary_key=True)
    section_id: Mapped[str] = mapped_column(ForeignKey("source_section.section_id"), nullable=False)
    pattern_layer: Mapped[str] = mapped_column(Text, nullable=False)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    parser_profile: Mapped[str] = mapped_column(Text, nullable=False, default="generic_html_v1")
    spec_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CrawlRunModel(Base):
    __tablename__ = "crawl_run"

    run_id: Mapped[str] = mapped_column(Text, primary_key=True)
    region_key: Mapped[str] = mapped_column(ForeignKey("scrape_region.region_key"), nullable=False)
    mode: Mapped[str] = mapped_column(Text, nullable=False, default="planned")
    status: Mapped[str] = mapped_column(Text, nullable=False, default="created")
    initiated_by: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_jsonb: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)


class CrawlQueueTaskModel(Base):
    __tablename__ = "crawl_queue_task"

    task_id: Mapped[str] = mapped_column(Text, primary_key=True)
    run_id: Mapped[str | None] = mapped_column(ForeignKey("crawl_run.run_id"))
    section_id: Mapped[str] = mapped_column(ForeignKey("source_section.section_id"), nullable=False)
    task_type: Mapped[str] = mapped_column(Text, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    payload_jsonb: Mapped[dict[str, Any]] = mapped_column("payload", JSONB, nullable=False, default=dict)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    next_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    lease_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CrawlErrorModel(Base):
    __tablename__ = "crawl_error"

    error_id: Mapped[str] = mapped_column(Text, primary_key=True)
    task_id: Mapped[str | None] = mapped_column(ForeignKey("crawl_queue_task.task_id"))
    phase: Mapped[str] = mapped_column(Text, nullable=False)
    error_code: Mapped[str | None] = mapped_column(Text)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    detail_jsonb: Mapped[dict[str, Any]] = mapped_column("detail", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SegmentFulfillmentModel(Base):
    __tablename__ = "segment_fulfillment"

    fulfillment_id: Mapped[str] = mapped_column(Text, primary_key=True)
    section_id: Mapped[str] = mapped_column(ForeignKey("source_section.section_id"), nullable=False, unique=True)
    target_valid_listings: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    current_valid_listings: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_total_listings: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_counted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_status: Mapped[str] = mapped_column(Text, nullable=False, default="unknown")
    threshold_reached_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    incremental_ready: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[str | None] = mapped_column(Text)


class ScrapeRunnerStateModel(Base):
    __tablename__ = "scrape_runner_state"

    singleton_id: Mapped[str] = mapped_column(Text, primary_key=True)
    global_pause: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CanonicalListingVersionModel(Base):
    __tablename__ = "canonical_listing_version"

    version_id: Mapped[str] = mapped_column(Text, primary_key=True)
    reference_id: Mapped[str] = mapped_column(ForeignKey("canonical_listing.reference_id"), nullable=False)
    snapshot_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
