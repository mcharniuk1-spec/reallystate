from __future__ import annotations

from typing import TYPE_CHECKING

from ..enums import SourceFamily
from .homes_bg import HomesBgConnector
from .protocol import Connector
from .scaffold import HtmlPortalConnector

if TYPE_CHECKING:
    from ..models import SourceRegistryEntry
    from ..source_registry import SourceRegistry


def is_marketplace_source(entry: SourceRegistryEntry) -> bool:
    """True for portals, classifieds, agencies, OTAs, registers, analytics — not social/messenger."""
    return entry.source_family not in (SourceFamily.SOCIAL_PUBLIC_CHANNEL, SourceFamily.PRIVATE_MESSENGER)


def marketplace_sources(registry: SourceRegistry) -> list[SourceRegistryEntry]:
    return [e for e in registry.all() if is_marketplace_source(e)]


def build_connector(source_name: str, registry: SourceRegistry, *, client: object | None = None) -> Connector:
    """Return the connector implementation for a source (Homes.bg specialized; others use HTML scaffold)."""
    if source_name == "Homes.bg":
        return HomesBgConnector(registry, client=client)
    return HtmlPortalConnector(source_name, registry, client=client)
