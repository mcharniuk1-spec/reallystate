"""Photo classification stub for real estate listing images.

Classifies images by room type, exterior/interior, floorplan detection,
and quality scoring. The current implementation uses filename/URL heuristics
only; swap in a real model (e.g. CLIP, ResNet fine-tuned) when ready.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any


ROOM_PATTERNS: list[tuple[str, str]] = [
    (r"kitchen|кухня|kuhnya", "kitchen"),
    (r"bathroom|баня|banya|toalet|тоалетна", "bathroom"),
    (r"bedroom|спалня|spalnya", "bedroom"),
    (r"living|хол|hol|дневна|dnevna", "living_room"),
    (r"balcon|тераса|terasa|балкон", "balcony"),
    (r"entrance|вход|коридор|koridor", "entrance"),
    (r"garage|гараж|garazh", "garage"),
    (r"garden|двор|градина", "garden"),
    (r"pool|басейн", "pool"),
]

EXTERIOR_PATTERNS = re.compile(
    r"exterior|фасад|facade|outside|изглед|view|building|сграда|street|улица|aerial|drone",
    re.IGNORECASE,
)

FLOORPLAN_PATTERNS = re.compile(
    r"floor[\s_]*plan|план|schema|layout|razpol|разпол|разпред|blueprint|чертеж",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class PhotoClassification:
    room_type: str | None
    quality_score: float
    is_exterior: bool
    is_floorplan: bool
    confidence: float
    method: str


def classify_image(
    path_or_url: str,
    *,
    metadata: dict[str, Any] | None = None,
) -> PhotoClassification:
    """Classify a real estate photo using heuristics on the filename/URL.

    Args:
        path_or_url: Local path or remote URL of the image.
        metadata: Optional dict with keys like 'caption', 'alt_text', 'sort_order'.

    Returns:
        PhotoClassification with room_type, quality_score, is_exterior, is_floorplan.
    """
    metadata = metadata or {}
    text_blob = " ".join([
        os.path.basename(path_or_url),
        metadata.get("caption", ""),
        metadata.get("alt_text", ""),
    ]).lower()

    room_type = _detect_room_type(text_blob)
    is_exterior = bool(EXTERIOR_PATTERNS.search(text_blob))
    is_floorplan = bool(FLOORPLAN_PATTERNS.search(text_blob))
    quality_score = _estimate_quality(path_or_url, metadata)

    confidence = 0.3 if room_type or is_exterior or is_floorplan else 0.1

    return PhotoClassification(
        room_type=room_type,
        quality_score=quality_score,
        is_exterior=is_exterior,
        is_floorplan=is_floorplan,
        confidence=confidence,
        method="heuristic_v1",
    )


def _detect_room_type(text: str) -> str | None:
    for pattern, label in ROOM_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return label
    return None


def _estimate_quality(path_or_url: str, metadata: dict[str, Any]) -> float:
    """Rough quality estimate based on available metadata.

    Returns a score in [0.0, 1.0]. This stub uses image dimensions if provided.
    """
    width = metadata.get("width", 0) or 0
    height = metadata.get("height", 0) or 0

    if width == 0 or height == 0:
        return 0.5

    pixels = width * height
    if pixels >= 2_000_000:
        return 0.9
    if pixels >= 1_000_000:
        return 0.7
    if pixels >= 500_000:
        return 0.5
    return 0.3


def classify_batch(
    items: list[tuple[str, dict[str, Any] | None]],
) -> list[PhotoClassification]:
    """Classify a batch of images."""
    return [classify_image(path, metadata=meta) for path, meta in items]
