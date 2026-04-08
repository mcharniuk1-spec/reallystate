from __future__ import annotations

from typing import TYPE_CHECKING

from ..enums import SourceFamily
from .homes_bg import HomesBgConnector
from .olx_bg import OlxBgConnector
from .protocol import Connector
from .scaffold import HtmlPortalConnector
from .tier3 import BcpeaAuctionConnector, PartnerFeedStubConnector
from .tier2_stubs import BazarBgConnector, DomazaConnector, Home2UConnector, YavlenaConnector

if TYPE_CHECKING:
    from ..models import SourceRegistryEntry
    from ..source_registry import SourceRegistry


TIER1_HTML_SOURCES = frozenset({
    "alo.bg",
    "imot.bg",
    "BulgarianProperties",
    "Address.bg",
    "SUPRIMMO",
    "LUXIMMO",
    "property.bg",
    "imoti.net",
})


def is_marketplace_source(entry: SourceRegistryEntry) -> bool:
    """True for portals, classifieds, agencies, OTAs, registers, analytics — not social/messenger."""
    return entry.source_family not in (SourceFamily.SOCIAL_PUBLIC_CHANNEL, SourceFamily.PRIVATE_MESSENGER)


def marketplace_sources(registry: SourceRegistry) -> list[SourceRegistryEntry]:
    return [e for e in registry.all() if is_marketplace_source(e)]


def build_connector(source_name: str, registry: SourceRegistry, *, client: object | None = None) -> Connector:
    """Return the connector implementation for a source."""
    if source_name == "Homes.bg":
        return HomesBgConnector(registry, client=client)
    if source_name == "OLX.bg":
        return OlxBgConnector(registry, client=client)
    if source_name == "Bazar.bg":
        return BazarBgConnector(registry, client=client)
    if source_name == "Domaza":
        return DomazaConnector(registry, client=client)
    if source_name == "Yavlena":
        return YavlenaConnector(registry, client=client)
    if source_name == "Home2U":
        return Home2UConnector(registry, client=client)
    if source_name == "BCPEA property auctions":
        return BcpeaAuctionConnector(registry, client=client)
    if source_name in {"Airbnb", "Booking.com", "Vrbo"}:
        return PartnerFeedStubConnector(source_name, registry, client=client)
    return HtmlPortalConnector(source_name, registry, client=client)
