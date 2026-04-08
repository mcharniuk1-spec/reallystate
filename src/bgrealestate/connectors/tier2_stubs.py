from __future__ import annotations

from ..source_registry import SourceRegistry
from .scaffold import HtmlPortalConnector


class BazarBgConnector(HtmlPortalConnector):
    source_name = "Bazar.bg"

    def __init__(self, registry: SourceRegistry, *, client: object | None = None) -> None:
        super().__init__(self.source_name, registry, client=client)


class DomazaConnector(HtmlPortalConnector):
    source_name = "Domaza"

    def __init__(self, registry: SourceRegistry, *, client: object | None = None) -> None:
        super().__init__(self.source_name, registry, client=client)


class YavlenaConnector(HtmlPortalConnector):
    source_name = "Yavlena"

    def __init__(self, registry: SourceRegistry, *, client: object | None = None) -> None:
        super().__init__(self.source_name, registry, client=client)


class Home2UConnector(HtmlPortalConnector):
    source_name = "Home2U"

    def __init__(self, registry: SourceRegistry, *, client: object | None = None) -> None:
        super().__init__(self.source_name, registry, client=client)

