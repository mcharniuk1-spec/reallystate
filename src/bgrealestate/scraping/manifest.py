"""Load and validate the Varna-only scrape pattern manifest (JSON on disk)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .pattern_layers import PATTERN_LAYERS
from .region import ONLY_REGION_KEY
from .segments import is_allowed_segment


@dataclass(frozen=True)
class SectionManifestEntry:
    section_id: str
    source_name: str
    region_key: str
    segment_key: str
    vertical_key: str
    section_label: str
    entry_urls: list[str]
    active: bool
    patterns: dict[str, Any]


def default_manifest_path(repo_root: Path | None = None) -> Path:
    # manifest.py -> scraping -> bgrealestate -> src -> repo root
    root = repo_root or Path(__file__).resolve().parents[3]
    return root / "data" / "scrape_patterns" / "regions" / ONLY_REGION_KEY / "sections.json"


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    validate_manifest(data, path=str(path))
    return data


def validate_manifest(data: dict[str, Any], *, path: str = "") -> None:
    rk = data.get("region_key")
    if rk != ONLY_REGION_KEY:
        raise ValueError(f"{path}: region_key must be {ONLY_REGION_KEY!r}, got {rk!r}")
    sections = data.get("sections")
    if not isinstance(sections, list) or not sections:
        raise ValueError(f"{path}: sections must be a non-empty list")
    seen: set[str] = set()
    for i, sec in enumerate(sections):
        if not isinstance(sec, dict):
            raise ValueError(f"{path}: sections[{i}] must be an object")
        sid = sec.get("section_id")
        if not isinstance(sid, str) or not sid:
            raise ValueError(f"{path}: sections[{i}].section_id required")
        if sid in seen:
            raise ValueError(f"{path}: duplicate section_id {sid!r}")
        seen.add(sid)
        if sec.get("source_name") is None:
            raise ValueError(f"{path}: {sid}: source_name required")
        if sec.get("region_key") != ONLY_REGION_KEY:
            raise ValueError(f"{path}: {sid}: region_key must be {ONLY_REGION_KEY!r}")
        seg = sec.get("segment_key")
        if not isinstance(seg, str) or not is_allowed_segment(seg):
            raise ValueError(f"{path}: {sid}: invalid segment_key {seg!r}")
        if not isinstance(sec.get("vertical_key"), str):
            raise ValueError(f"{path}: {sid}: vertical_key must be a string")
        pats = sec.get("patterns")
        if not isinstance(pats, dict):
            raise ValueError(f"{path}: {sid}: patterns must be an object")
        if int(pats.get("target_valid_listings") or 0) < 1:
            raise ValueError(f"{path}: {sid}: target_valid_listings must be >= 1")
        for layer in PATTERN_LAYERS:
            if layer not in pats:
                raise ValueError(f"{path}: {sid}: missing patterns[{layer!r}]")
        section_spec = pats.get("section") or {}
        if not isinstance(section_spec, dict):
            raise ValueError(f"{path}: {sid}: patterns['section'] must be an object")
        if "support_status" not in section_spec:
            raise ValueError(f"{path}: {sid}: patterns['section'].support_status required")


def iter_sections(data: dict[str, Any]) -> list[SectionManifestEntry]:
    out: list[SectionManifestEntry] = []
    for sec in data["sections"]:
        pats = sec["patterns"]
        out.append(
            SectionManifestEntry(
                section_id=str(sec["section_id"]),
                source_name=str(sec["source_name"]),
                region_key=str(sec["region_key"]),
                segment_key=str(sec["segment_key"]),
                vertical_key=str(sec["vertical_key"]),
                section_label=str(sec.get("section_label") or sec["section_id"]),
                entry_urls=list(sec.get("entry_urls") or []),
                active=bool(sec.get("active", False)),
                patterns=dict(pats),
            )
        )
    return out
