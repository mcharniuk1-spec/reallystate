from __future__ import annotations

import unittest
from pathlib import Path

from bgrealestate.connectors.stage1_coverage import (
    REQUIRED_PRODUCT_TYPES,
    collect_stage1_fixture_cases,
    compute_stage1_product_type_coverage,
)
from bgrealestate.source_registry import SourceRegistry


class TestStage1ProductTypeCoverage(unittest.TestCase):
    def test_required_product_types_are_covered(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        registry = SourceRegistry.from_file(repo / "data" / "source_registry.json")
        cases = collect_stage1_fixture_cases(registry, repo / "tests" / "fixtures")
        coverage = compute_stage1_product_type_coverage(cases)

        self.assertTrue(cases, "expected at least one tier-1/2 fixture case")
        tiers = {c.tier for c in cases}
        self.assertIn(1, tiers, "tier-1 fixture coverage missing")
        self.assertIn(2, tiers, "tier-2 fixture coverage missing")

        missing = [k for k in REQUIRED_PRODUCT_TYPES if not coverage.get(k)]
        self.assertEqual([], missing, f"missing required product types: {missing}")


if __name__ == "__main__":
    unittest.main()
