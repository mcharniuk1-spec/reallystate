import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bgrealestate.enums import ListingIntent, OnboardingMode, PropertyCategory, PublishChannel
from bgrealestate.models import CanonicalListing, ComplianceFlag, DistributionProfile
from bgrealestate.publishing import ChannelPayloadMapper, PublishEligibilityEngine


class PublishingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = PublishEligibilityEngine()
        self.listing = CanonicalListing(
            source_name="Booking.com",
            owner_group="Booking Holdings",
            listing_url="https://example.com/apt-1",
            external_id="apt-1",
            reference_id="booking:apt-1",
            listing_intent=ListingIntent.SHORT_TERM_RENT,
            property_category=PropertyCategory.APARTMENT,
            city="Burgas",
            district="Center",
            resort=None,
            region="Burgas",
            address_text="1 Aleksandrovska",
            latitude=42.5048,
            longitude=27.4626,
            geocode_confidence=0.91,
            building_name="Burgas Residence",
            area_sqm=78.0,
            rooms=2.0,
            floor=3,
            total_floors=6,
            construction_type="brick",
            construction_year=2022,
            stage="completed",
            act16_present=True,
            price=135.0,
            currency="EUR",
            fees=None,
            price_per_sqm=1.73,
            broker_name="Agent",
            agency_name="Coast Agency",
            owner_name=None,
            developer_name=None,
            phones=["+359 888 000 111"],
            messenger_handles=[],
            outbound_channel_hints=[],
            description="Short-term rental near Burgas center.",
            amenities=["wifi", "parking"],
            image_urls=["https://example.com/photo.jpg"],
            first_seen=datetime(2026, 4, 6, 10, 0, 0),
            last_seen=datetime(2026, 4, 6, 10, 0, 0),
            last_changed_at=datetime(2026, 4, 6, 10, 0, 0),
            removed_at=None,
            parser_version="v1",
            crawl_provenance={},
        )
        self.profile = DistributionProfile(
            profile_id="profile-1",
            property_reference_id=self.listing.reference_id,
            listing_intent=ListingIntent.SHORT_TERM_RENT,
            enabled_channels=[PublishChannel.BOOKING, PublishChannel.AIRBNB],
            owner_operator_mode="client_owned_accounts",
            onboarding_modes=[OnboardingMode.OFFICIAL_PARTNER_ONBOARDING],
            approved=True,
        )

    def test_booking_listing_is_eligible(self) -> None:
        decision = self.engine.evaluate(self.listing, self.profile, PublishChannel.BOOKING, [])
        self.assertEqual(decision.state.value, "approved")

    def test_blocking_compliance_flag_stops_publish(self) -> None:
        flags = [
            ComplianceFlag(
                code="missing_license",
                severity="high",
                message="municipal short-stay license missing",
                blocks_publishing=True,
                applies_to_channel=PublishChannel.BOOKING,
            )
        ]
        decision = self.engine.evaluate(self.listing, self.profile, PublishChannel.BOOKING, flags)
        self.assertEqual(decision.state.value, "blocked")

    def test_airbnb_payload_contains_sync_flags(self) -> None:
        payload = ChannelPayloadMapper.map_payload(self.listing, PublishChannel.AIRBNB)
        self.assertEqual(payload["channel"], "airbnb")
        self.assertEqual(payload["pricing_sync"], "required")


if __name__ == "__main__":
    unittest.main()
