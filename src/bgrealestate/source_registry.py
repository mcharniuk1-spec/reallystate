from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Optional

from .enums import AccessMode, FreshnessTarget, RiskMode, SourceFamily
from .models import SourceRegistryEntry


def _coerce_source(entry: dict) -> SourceRegistryEntry:
    return SourceRegistryEntry(
        source_name=entry["source_name"],
        tier=int(entry["tier"]),
        source_family=SourceFamily(entry["source_family"]),
        owner_group=entry["owner_group"],
        access_mode=AccessMode(entry["access_mode"]),
        risk_mode=RiskMode(entry["risk_mode"]),
        freshness_target=FreshnessTarget(entry["freshness_target"]),
        publish_capable=bool(entry["publish_capable"]),
        dedupe_cluster_hint=entry["dedupe_cluster_hint"],
        languages=list(entry.get("languages", [])),
        listing_types=list(entry.get("listing_types", [])),
        best_extraction_method=entry.get("best_extraction_method", ""),
        notes=entry.get("notes", ""),
        legal_mode=entry.get("legal_mode", "public_or_contract_review"),
        mvp_phase=entry.get("mvp_phase", "source_first_ingestion"),
        primary_url=entry.get("primary_url", ""),
        related_urls=list(entry.get("related_urls", [])),
    )


class SourceRegistry:
    def __init__(self, entries: Iterable[SourceRegistryEntry]):
        self._entries = list(entries)

    @classmethod
    def from_file(cls, path: Path) -> "SourceRegistry":
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls(_coerce_source(entry) for entry in raw["sources"])

    def all(self) -> List[SourceRegistryEntry]:
        return list(self._entries)

    def by_name(self, source_name: str) -> Optional[SourceRegistryEntry]:
        return next((entry for entry in self._entries if entry.source_name == source_name), None)

    def by_tier(self, tier: int) -> List[SourceRegistryEntry]:
        return [entry for entry in self._entries if entry.tier == tier]

    def by_family(self, family: SourceFamily) -> List[SourceRegistryEntry]:
        return [entry for entry in self._entries if entry.source_family == family]

    def promotion_candidates(self) -> List[SourceRegistryEntry]:
        return [
            entry
            for entry in self._entries
            if entry.freshness_target in {FreshnessTarget.HOURLY, FreshnessTarget.TEN_MINUTES}
            and entry.tier == 1
        ]

    def legal_review_queue(self) -> List[SourceRegistryEntry]:
        return [
            entry
            for entry in self._entries
            if entry.risk_mode in {RiskMode.HIGH, RiskMode.PROHIBITED_WITHOUT_CONTRACT}
        ]

    def publishable_sources(self) -> List[SourceRegistryEntry]:
        return [entry for entry in self._entries if entry.publish_capable]
