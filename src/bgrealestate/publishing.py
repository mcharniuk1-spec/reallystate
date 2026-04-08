from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .enums import ChannelState, ListingIntent, OnboardingMode, PublishChannel
from .models import CanonicalListing, ComplianceFlag, DistributionProfile


@dataclass
class EligibilityDecision:
    channel: PublishChannel
    state: ChannelState
    reasons: List[str] = field(default_factory=list)


class PublishEligibilityEngine:
    """Decides whether a listing can move to outbound publishing review."""

    def evaluate(
        self,
        listing: CanonicalListing,
        profile: DistributionProfile,
        channel: PublishChannel,
        compliance_flags: List[ComplianceFlag],
    ) -> EligibilityDecision:
        reasons: List[str] = []
        blocking_flags = [
            flag
            for flag in compliance_flags
            if flag.blocks_publishing and (flag.applies_to_channel is None or flag.applies_to_channel == channel)
        ]
        if blocking_flags:
            reasons.extend(flag.message for flag in blocking_flags)
            return EligibilityDecision(channel=channel, state=ChannelState.BLOCKED, reasons=reasons)

        if channel not in profile.enabled_channels:
            return EligibilityDecision(channel=channel, state=ChannelState.NOT_ELIGIBLE, reasons=["channel not enabled"])

        if not profile.approved:
            reasons.append("distribution profile is not approved")
            return EligibilityDecision(channel=channel, state=ChannelState.READY_FOR_REVIEW, reasons=reasons)

        if channel in {PublishChannel.BOOKING, PublishChannel.AIRBNB}:
            if listing.listing_intent != ListingIntent.SHORT_TERM_RENT:
                return EligibilityDecision(
                    channel=channel,
                    state=ChannelState.NOT_ELIGIBLE,
                    reasons=["channel requires short-term rental inventory"],
                )
            if OnboardingMode.OFFICIAL_PARTNER_ONBOARDING not in profile.onboarding_modes and OnboardingMode.AUTHORIZED_ACCOUNT_LINKING not in profile.onboarding_modes:
                return EligibilityDecision(
                    channel=channel,
                    state=ChannelState.BLOCKED,
                    reasons=["official or authorized onboarding is required for OTA publishing"],
                )

        if channel == PublishChannel.BULGARIAN_PORTAL and not listing.price:
            return EligibilityDecision(channel=channel, state=ChannelState.BLOCKED, reasons=["price is required"])

        if not listing.image_urls:
            reasons.append("listing has no images yet")
            return EligibilityDecision(channel=channel, state=ChannelState.READY_FOR_REVIEW, reasons=reasons)

        return EligibilityDecision(channel=channel, state=ChannelState.APPROVED, reasons=["eligible for publish job creation"])


class ChannelPayloadMapper:
    """Maps canonical listings into outbound publication payloads."""

    @staticmethod
    def map_payload(listing: CanonicalListing, channel: PublishChannel) -> Dict[str, object]:
        base_payload = {
            "reference_id": listing.reference_id,
            "title": listing.building_name or listing.address_text or listing.reference_id,
            "description": listing.description or "",
            "city": listing.city,
            "region": listing.region,
            "address": listing.address_text,
            "latitude": listing.latitude,
            "longitude": listing.longitude,
            "images": listing.image_urls,
            "phones": listing.phones,
            "currency": listing.currency,
            "price": listing.price,
            "area_sqm": listing.area_sqm,
            "rooms": listing.rooms,
            "category": listing.property_category.value,
            "intent": listing.listing_intent.value,
        }

        if channel == PublishChannel.BOOKING:
            return {
                **base_payload,
                "channel": channel.value,
                "room_type": listing.property_category.value,
                "policies_required": True,
                "availability_sync": "required",
            }

        if channel == PublishChannel.AIRBNB:
            return {
                **base_payload,
                "channel": channel.value,
                "listing_type": listing.property_category.value,
                "pricing_sync": "required",
                "status_sync": "required",
            }

        if channel == PublishChannel.BULGARIAN_PORTAL:
            return {
                **base_payload,
                "channel": channel.value,
                "broker_name": listing.broker_name,
                "agency_name": listing.agency_name,
                "price_per_sqm": listing.price_per_sqm,
            }

        if channel == PublishChannel.AGENCY_SYNDICATION:
            return {
                **base_payload,
                "channel": channel.value,
                "developer_name": listing.developer_name,
                "owner_name": listing.owner_name,
                "compliance_reviewed": True,
            }

        return {**base_payload, "channel": channel.value}

