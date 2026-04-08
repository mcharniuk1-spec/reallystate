from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from ..models import RawCapture


@dataclass(frozen=True)
class DiscoveryResult:
    urls: list[str]
    next_cursor: dict[str, Any] | None
    discovered_at: datetime


class Connector(Protocol):
    source_name: str

    def discover_listing_urls(self, *, cursor: dict[str, Any] | None = None) -> DiscoveryResult: ...

    def fetch_listing_detail(self, *, url: str, fetched_at: datetime) -> RawCapture: ...

