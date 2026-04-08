from enum import Enum


class SourceFamily(str, Enum):
    PORTAL = "portal"
    CLASSIFIEDS = "classifieds"
    AGENCY = "agency"
    DEVELOPER = "developer"
    OTA = "ota"
    ANALYTICS_VENDOR = "analytics_vendor"
    OFFICIAL_REGISTER = "official_register"
    SOCIAL_PUBLIC_CHANNEL = "social_public_channel"
    PRIVATE_MESSENGER = "private_messenger"


class AccessMode(str, Enum):
    HTML = "html"
    HEADLESS = "headless"
    HIDDEN_JSON = "hidden_json"
    OFFICIAL_API = "official_api"
    PARTNER_FEED = "partner_feed"
    LICENSED_DATA = "licensed_data"
    MANUAL_CONSENT_ONLY = "manual_consent_only"


class RiskMode(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PROHIBITED_WITHOUT_CONTRACT = "prohibited_without_contract"


class FreshnessTarget(str, Enum):
    TEN_MINUTES = "ten_minutes"
    HOURLY = "hourly"
    DAILY = "daily"
    VENDOR_SYNC = "vendor_sync"
    CONSENT_DRIVEN = "consent_driven"


class ListingIntent(str, Enum):
    SALE = "sale"
    LONG_TERM_RENT = "long_term_rent"
    SHORT_TERM_RENT = "short_term_rent"
    MIXED = "mixed"


class PropertyCategory(str, Enum):
    APARTMENT = "apartment"
    HOUSE = "house"
    BUILDING = "building"
    LAND = "land"
    PROJECT = "project"
    OFFICE = "office"
    VILLA = "villa"
    HOTEL = "hotel"
    UNKNOWN = "unknown"


class LifecycleEventType(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    PRICE_CHANGED = "price_changed"
    MEDIA_CHANGED = "media_changed"
    REMOVED = "removed"
    RELISTED = "relisted"


class OnboardingMode(str, Enum):
    OFFICIAL_PARTNER_ONBOARDING = "official_partner_onboarding"
    AUTHORIZED_ACCOUNT_LINKING = "authorized_account_linking"
    ASSISTED_MANUAL_ONBOARDING = "assisted_manual_onboarding"


class PublishChannel(str, Enum):
    BOOKING = "booking"
    AIRBNB = "airbnb"
    BULGARIAN_PORTAL = "bulgarian_portal"
    AGENCY_SYNDICATION = "agency_syndication"
    WHATSAPP_BUSINESS = "whatsapp_business"
    INSTAGRAM_MESSAGING = "instagram_messaging"
    MESSENGER = "messenger"
    VIBER_BOT = "viber_bot"


class ChannelState(str, Enum):
    NOT_ELIGIBLE = "not_eligible"
    READY_FOR_REVIEW = "ready_for_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    OUT_OF_SYNC = "out_of_sync"
    BLOCKED = "blocked"
    REMOVED = "removed"

