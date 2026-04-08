from __future__ import annotations

from pathlib import Path

from bgrealestate.connectors.stage1_coverage import (
    collect_stage1_fixture_cases,
    compute_stage1_product_type_coverage,
    render_stage1_coverage_markdown,
)
from bgrealestate.source_registry import SourceRegistry


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    registry = SourceRegistry.from_file(repo / "data" / "source_registry.json")
    fixtures_root = repo / "tests" / "fixtures"
    out_path = repo / "docs" / "exports" / "stage1-product-type-coverage.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cases = collect_stage1_fixture_cases(registry, fixtures_root)
    coverage = compute_stage1_product_type_coverage(cases)
    md = render_stage1_coverage_markdown(cases, coverage)
    out_path.write_text(md, encoding="utf-8")
    print(f"wrote {out_path} ({len(cases)} fixture cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
