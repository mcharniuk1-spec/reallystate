from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .enums import (
    AccessMode,
    ChannelState,
    FreshnessTarget,
    LifecycleEventType,
    ListingIntent,
    OnboardingMode,
    PropertyCategory,
    PublishChannel,
    RiskMode,
    SourceFamily,
)


@dataclass(frozen=True)
class SourceRegistryEntry:
    source_name: str
    tier: int
    source_family: SourceFamily
    owner_group: str
    access_mode: AccessMode
    risk_mode: RiskMode
    freshness_target: FreshnessTarget
    publish_capable: bool
    dedupe_cluster_hint: str
    languages: List[str] = field(default_factory=list)
    listing_types: List[str] = field(default_factory=list)
    best_extraction_method: str = ""
    notes: str = ""
    legal_mode: str = "public_or_contract_review"
    mvp_phase: str = "source_first_ingestion"
    primary_url: str = ""
    related_urls: List[str] = field(default_factory=list)


@dataclass
class RawCapture:
    source_name: str
    url: str
    content_type: str
    body: str
    fetched_at: datetime
    parser_version: str = "v1"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedListing:
    source_name: str
    url: str
    external_id: str
    title: Optional[str] = None
    listing_intent: ListingIntent = ListingIntent.MIXED
    property_category: PropertyCategory = PropertyCategory.UNKNOWN
    city: Optional[str] = None
    district: Optional[str] = None
    resort: Optional[str] = None
    region: Optional[str] = None
    address_text: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    geocode_confidence: Optional[float] = None
    building_name: Optional[str] = None
    area_sqm: Optional[float] = None
    rooms: Optional[float] = None
    floor: Optional[int] = None
    total_floors: Optional[int] = None
    construction_type: Optional[str] = None
    construction_year: Optional[int] = None
    stage: Optional[str] = None
    act16_present: Optional[bool] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    fees: Optional[float] = None
    agency_name: Optional[str] = None
    owner_name: Optional[str] = None
    developer_name: Optional[str] = None
    broker_name: Optional[str] = None
    phones: List[str] = field(default_factory=list)
    messenger_handles: List[str] = field(default_factory=list)
    outbound_channel_hints: List[str] = field(default_factory=list)
    description: Optional[str] = None
    amenities: List[str] = field(default_factory=list)
    image_urls: List[str] = field(default_factory=list)
    raw_payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CanonicalListing:
    source_name: str
    owner_group: str
    listing_url: str
    external_id: str
    reference_id: str
    listing_intent: ListingIntent
    property_category: PropertyCategory
    city: Optional[str]
    district: Optional[str]
    resort: Optional[str]
    region: Optional[str]
    address_text: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    geocode_confidence: Optional[float]
    building_name: Optional[str]
    area_sqm: Optional[float]
    rooms: Optional[float]
    floor: Optional[int]
    total_floors: Optional[int]
    construction_type: Optional[str]
    construction_year: Optional[int]
    stage: Optional[str]
    act16_present: Optional[bool]
    price: Optional[float]
    currency: Optional[str]
    fees: Optional[float]
    price_per_sqm: Optional[float]
    broker_name: Optional[str]
    agency_name: Optional[str]
    owner_name: Optional[str]
    developer_name: Optional[str]
    phones: List[str]
    messenger_handles: List[str]
    outbound_channel_hints: List[str]
    description: Optional[str]
    amenities: List[str]
    image_urls: List[str]
    first_seen: datetime
    last_seen: datetime
    last_changed_at: datetime
    removed_at: Optional[datetime]
    parser_version: str
    crawl_provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PropertyEntity:
    property_id: str
    dedupe_key: str
    canonical_address: Optional[str]
    canonical_city: Optional[str]
    canonical_building_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]


@dataclass
class ContactEntity:
    contact_id: str
    display_name: str
    phones: List[str]
    organization: Optional[str] = None
    messenger_handles: List[str] = field(default_factory=list)


@dataclass
class BuildingEntity:
    building_id: str
    name: Optional[str]
    latitude: float
    longitude: float
    source: str
    confidence: float


@dataclass
class ListingMedia:
    media_id: str
    listing_reference_id: str
    url: str
    content_hash: Optional[str] = None
    caption: Optional[str] = None
    ordering: int = 0


@dataclass
class ListingEvent:
    event_id: str
    listing_reference_id: str
    event_type: LifecycleEventType
    emitted_at: datetime
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SourceAccount:
    account_id: str
    source_name: str
    onboarding_mode: OnboardingMode
    authorized: bool
    external_account_reference: Optional[str] = None


@dataclass
class DistributionProfile:
    profile_id: str
    property_reference_id: str
    listing_intent: ListingIntent
    enabled_channels: List[PublishChannel]
    owner_operator_mode: str
    onboarding_modes: List[OnboardingMode]
    approved: bool = False


@dataclass
class ChannelMapping:
    mapping_id: str
    property_reference_id: str
    channel: PublishChannel
    external_listing_id: Optional[str] = None
    state: ChannelState = ChannelState.NOT_ELIGIBLE
    last_synced_at: Optional[datetime] = None


@dataclass
class PublishJob:
    publish_job_id: str
    property_reference_id: str
    channel: PublishChannel
    requested_at: datetime
    payload: Dict[str, Any]


@dataclass
class PublishResult:
    publish_job_id: str
    channel: PublishChannel
    state: ChannelState
    processed_at: datetime
    external_listing_id: Optional[str] = None
    messages: List[str] = field(default_factory=list)


@dataclass
class ComplianceFlag:
    code: str
    severity: str
    message: str
    blocks_publishing: bool
    applies_to_channel: Optional[PublishChannel] = None
