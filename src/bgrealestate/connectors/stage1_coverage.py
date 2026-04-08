from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..source_registry import SourceRegistry


REQUIRED_PRODUCT_TYPES = ("sale", "long_term_rent", "short_term_rent", "land", "new_build")


@dataclass(frozen=True)
class FixtureCase:
    source_name: str
    tier: int
    fixture_path: str
    listing_intent: str | None
    property_category: str | None


def _iter_expected_files(fixtures_root: Path) -> list[Path]:
    return sorted(fixtures_root.glob("*/*/expected.json"))


def _is_marketplace_tier12(entry: Any) -> bool:
    fam = str(entry.source_family.value)
    return entry.tier in (1, 2) and fam not in {"social_public_channel", "private_messenger"}


def collect_stage1_fixture_cases(registry: SourceRegistry, fixtures_root: Path) -> list[FixtureCase]:
    by_name = {e.source_name: e for e in registry.all() if _is_marketplace_tier12(e)}
    out: list[FixtureCase] = []
    for path in _iter_expected_files(fixtures_root):
        try:
            import json

            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        src = payload.get("source_name")
        if not isinstance(src, str) or src not in by_name:
            continue
        entry = by_name[src]
        out.append(
            FixtureCase(
                source_name=src,
                tier=int(entry.tier),
                fixture_path=str(path.relative_to(fixtures_root.parent)),
                listing_intent=payload.get("listing_intent"),
                property_category=payload.get("property_category"),
            )
        )
    return out


def compute_stage1_product_type_coverage(cases: list[FixtureCase]) -> dict[str, list[str]]:
    coverage: dict[str, list[str]] = {k: [] for k in REQUIRED_PRODUCT_TYPES}
    for c in cases:
        handle = f"{c.source_name}::{c.fixture_path}"
        if c.listing_intent == "sale":
            coverage["sale"].append(handle)
        if c.listing_intent == "long_term_rent":
            coverage["long_term_rent"].append(handle)
        if c.listing_intent == "short_term_rent":
            coverage["short_term_rent"].append(handle)
        if c.property_category == "land":
            coverage["land"].append(handle)
        # "new_build" is represented by project/new-build fixtures.
        if c.property_category == "project":
            coverage["new_build"].append(handle)
    return coverage


def render_stage1_coverage_markdown(cases: list[FixtureCase], coverage: dict[str, list[str]]) -> str:
    lines = [
        "# Stage-1 Product Type Coverage (Tier 1-2)",
        "",
        "Generated from fixture `expected.json` files for tier-1/2 marketplace sources.",
        "",
        "## Required product types",
        "",
        "| Product type | Covered | Fixture count | Example fixtures |",
        "|---|---:|---:|---|",
    ]
    for key in REQUIRED_PRODUCT_TYPES:
        refs = coverage.get(key, [])
        shown = ", ".join(refs[:3]) if refs else "-"
        lines.append(f"| {key} | {'yes' if refs else 'no'} | {len(refs)} | {shown} |")

    lines.extend(
        [
            "",
            "## Fixture inventory used",
            "",
            "| Source | Tier | listing_intent | property_category | Fixture |",
            "|---|---:|---|---|---|",
        ]
    )
    for c in sorted(cases, key=lambda x: (x.tier, x.source_name, x.fixture_path)):
        lines.append(
            f"| {c.source_name} | {c.tier} | {c.listing_intent or ''} | {c.property_category or ''} | {c.fixture_path} |"
        )
    lines.append("")
    return "\n".join(lines)
