from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .models import SourceRegistryEntry


def build_source_matrix_markdown(entries: Iterable[SourceRegistryEntry]) -> str:
    lines = [
        "# Source Parser Matrix",
        "",
        "| Source | Tier | Family | Primary URL | Access | Legal Mode | MVP Phase | Freshness | Publish Capable | Best Method |",
        "|---|---:|---|---|---|---|---|---|---|---|",
    ]
    for entry in entries:
        lines.append(
            f"| {entry.source_name} | {entry.tier} | {entry.source_family.value} | {entry.primary_url} | {entry.access_mode.value} | "
            f"{entry.legal_mode} | {entry.mvp_phase} | {entry.freshness_target.value} | "
            f"{'yes' if entry.publish_capable else 'no'} | {entry.best_extraction_method} |"
        )
    return "\n".join(lines) + "\n"


def build_legal_risk_markdown(entries: Iterable[SourceRegistryEntry]) -> str:
    lines = [
        "# Legal Risk Matrix",
        "",
        "| Source | Risk | Legal Mode | Owner Group | Notes |",
        "|---|---|---|---|---|",
    ]
    for entry in entries:
        lines.append(f"| {entry.source_name} | {entry.risk_mode.value} | {entry.legal_mode} | {entry.owner_group} | {entry.notes} |")
    return "\n".join(lines) + "\n"


def export_matrices(entries: Iterable[SourceRegistryEntry], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    entries = list(entries)
    (out_dir / "source-matrix.md").write_text(build_source_matrix_markdown(entries), encoding="utf-8")
    (out_dir / "legal-risk-matrix.md").write_text(build_legal_risk_markdown(entries), encoding="utf-8")
