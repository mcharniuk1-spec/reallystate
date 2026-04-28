"""Layered pattern contract (persisted in ``source_section_pattern.pattern_layer``)."""

from __future__ import annotations

PATTERN_LAYERS: tuple[str, ...] = (
    "source",  # site-wide: robots, legal, global headers, base hosts
    "section",  # division: intent filters, navigation entry points
    "list_page",  # search results: card selectors, pagination, URL templates
    "detail_page",  # listing detail: full attribute + text extraction
    "media_gallery",  # ordered gallery URLs + metadata hooks
)

__all__ = ["PATTERN_LAYERS"]
