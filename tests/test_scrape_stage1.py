"""Stage 1 scrape control plane: manifest validation (no database, no network)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from bgrealestate.scraping.control_worker import build_fetch_list_tasks
from bgrealestate.scraping.orchestrator import decide_section_action
from bgrealestate.scraping.section_catalog import SEGMENT_ORDER, build_varna_sections
from bgrealestate.scraping.manifest import default_manifest_path, validate_manifest
from bgrealestate.scraping.pattern_layers import PATTERN_LAYERS
from bgrealestate.source_registry import SourceRegistry


ROOT = Path(__file__).resolve().parents[1]


class TestManifestValidation(unittest.TestCase):
    def test_catalog_covers_all_tier1_tier2_sources_with_four_segments(self) -> None:
        registry = SourceRegistry.from_file(ROOT / "data" / "source_registry.json")
        sections = build_varna_sections(registry)
        source_names = {sec["source_name"] for sec in sections}
        expected = {
            entry.source_name
            for entry in registry.all()
            if entry.tier in {1, 2}
        }
        self.assertEqual(source_names, expected)
        counts: dict[str, int] = {}
        for sec in sections:
            counts[sec["source_name"]] = counts.get(sec["source_name"], 0) + 1
        for source_name in expected:
            self.assertEqual(counts[source_name], len(SEGMENT_ORDER))

    def test_default_manifest_path_under_repo_data(self) -> None:
        p = default_manifest_path(ROOT)
        self.assertTrue(str(p).endswith("data/scrape_patterns/regions/varna/sections.json"))
        self.assertEqual(p.parent.name, "varna")

    def test_validate_rejects_non_varna_region(self) -> None:
        bad = {
            "region_key": "sofia",
            "sections": [
                {
                    "section_id": "x",
                    "source_name": "Homes.bg",
                    "region_key": "sofia",
                    "segment_key": "buy_personal",
                    "vertical_key": "all",
                    "section_label": "t",
                    "entry_urls": [],
                    "active": False,
                    "patterns": {layer: {"layer": layer} for layer in PATTERN_LAYERS},
                }
            ],
        }
        with self.assertRaises(ValueError):
            validate_manifest(bad, path="inline")

    def test_committed_varna_manifest_validates(self) -> None:
        path = ROOT / "data" / "scrape_patterns" / "regions" / "varna" / "sections.json"
        if not path.exists():
            self.skipTest("sections.json not present")
        data = json.loads(path.read_text(encoding="utf-8"))
        validate_manifest(data, path=str(path))
        self.assertEqual(data["region_key"], "varna")
        self.assertGreaterEqual(len(data["sections"]), 1)


class TestScrapeCliDryCommands(unittest.TestCase):
    def test_scrape_validate_manifest_cli(self) -> None:
        from bgrealestate.cli import main as cli_main

        import sys

        path = ROOT / "data" / "scrape_patterns" / "regions" / "varna" / "sections.json"
        if not path.exists():
            self.skipTest("sections.json not present")
        saved = sys.argv
        sys.argv = ["bgrealestate", "scrape-validate-manifest", "--manifest", str(path)]
        try:
            rc = cli_main()
        finally:
            sys.argv = saved
        self.assertEqual(rc, 0)

    def test_scrape_varna_full_dry_run_cli(self) -> None:
        from bgrealestate.cli import main as cli_main

        import sys

        path = ROOT / "data" / "scrape_patterns" / "regions" / "varna" / "sections.json"
        if not path.exists():
            self.skipTest("sections.json not present")
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "summary.json"
            saved = sys.argv
            sys.argv = [
                "bgrealestate",
                "scrape-varna-full",
                "--manifest",
                str(path),
                "--dry-run",
                "--output",
                str(output),
            ]
            try:
                rc = cli_main()
            finally:
                sys.argv = saved
            self.assertEqual(rc, 0)
            self.assertTrue(output.exists())

    def test_scrape_all_full_dry_run_cli(self) -> None:
        from bgrealestate.cli import main as cli_main

        import sys

        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "summary.json"
            saved = sys.argv
            sys.argv = [
                "bgrealestate",
                "scrape-all-full",
                "--dry-run",
                "--sources",
                "olx_bg",
                "--output",
                str(output),
            ]
            try:
                rc = cli_main()
            finally:
                sys.argv = saved
            self.assertEqual(rc, 0)
            self.assertTrue(output.exists())


class TestSectionPlanning(unittest.TestCase):
    def test_decide_section_action_threshold_reached(self) -> None:
        action, reason = decide_section_action(
            active=True,
            support_status="supported",
            pattern_status="Patterned",
            global_pause=False,
            valid_count=100,
            target_valid_listings=100,
            skip_reason=None,
        )
        self.assertEqual(action, "threshold_reached")
        self.assertIn("incremental", reason.lower())

    def test_decide_section_action_pause_blocks_backfill(self) -> None:
        action, reason = decide_section_action(
            active=True,
            support_status="supported",
            pattern_status="Patterned",
            global_pause=True,
            valid_count=12,
            target_valid_listings=100,
            skip_reason=None,
        )
        self.assertEqual(action, "paused_pending_backfill")
        self.assertIn("pause", reason.lower())

    def test_scrape_sync_sections_dry_run_cli(self) -> None:
        from bgrealestate.cli import main as cli_main

        import sys

        path = ROOT / "data" / "scrape_patterns" / "regions" / "varna" / "sections.json"
        if not path.exists():
            self.skipTest("sections.json not present")
        saved = sys.argv
        sys.argv = ["bgrealestate", "scrape-sync-sections", "--manifest", str(path), "--dry-run"]
        try:
            rc = cli_main()
        finally:
            sys.argv = saved
        self.assertEqual(rc, 0)


class TestControlWorkerHelpers(unittest.TestCase):
    def test_build_fetch_list_tasks_from_entry_urls_and_templates(self) -> None:
        tasks = build_fetch_list_tasks(
            {
                "section_id": "homes_bg__varna__buy_personal__all",
                "source_name": "Homes.bg",
                "entry_urls": ["https://example.com/results"],
                "source_spec": {"source_key": "homes_bg"},
                "list_spec": {
                    "discovery_templates": {
                        "api_templates": ["https://api.example.com/page={page}"],
                        "list_templates": ["https://site.example.com/page/{page}"],
                    }
                },
            }
        )
        self.assertEqual(len(tasks), 3)
        self.assertEqual({task["task_type"] for task in tasks}, {"fetch_list"})
        kinds = {task["payload"]["list_target"]["kind"] for task in tasks}
        self.assertEqual(kinds, {"entry_url", "api_template", "list_template"})
        for task in tasks:
            self.assertEqual(task["payload"]["execution_hint"]["runtime_source_key"], "homes_bg")

    def test_build_fetch_list_tasks_empty_payload(self) -> None:
        tasks = build_fetch_list_tasks(
            {
                "section_id": "x",
                "source_name": "Demo",
                "entry_urls": [],
                "source_spec": {},
                "list_spec": {},
            }
        )
        self.assertEqual(tasks, [])
