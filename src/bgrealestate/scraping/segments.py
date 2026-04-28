"""Supported marketplace segment keys (Stage 1 contract).

Each ``source_section`` row binds a website division to one of these keys.
Verticals (apartments, houses, …) are orthogonal and stored as ``vertical_key``.
"""

from __future__ import annotations

SEGMENT_KEYS: tuple[str, ...] = (
    "buy_personal",
    "buy_commercial",
    "rent_personal",
    "rent_commercial",
)


def is_allowed_segment(value: str) -> bool:
    return value in SEGMENT_KEYS


__all__ = ["SEGMENT_KEYS", "is_allowed_segment"]
