from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "codex_project_hooks.py"
SPEC = importlib.util.spec_from_file_location("codex_project_hooks", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
hooks = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = hooks
SPEC.loader.exec_module(hooks)


class CodexProjectHooksTests(unittest.TestCase):
    def test_live_scrape_command_requires_gate(self) -> None:
        errors = hooks.evaluate_command("make scrape-all-full")
        self.assertTrue(any("live_scrape_operator_gate" in err for err in errors))

    def test_dry_run_scrape_command_is_allowed(self) -> None:
        errors = hooks.evaluate_command("make scrape-bcpea-dry")
        self.assertFalse(errors)

    def test_literal_api_key_in_command_is_blocked(self) -> None:
        errors = hooks.evaluate_command(
            "curl -H 'Authorization: Bearer sk-abcdefghijklmnopqrstuvwxyz1234567890'"
        )
        self.assertTrue(any("literal_command_secret" in err for err in errors))

    def test_broad_git_add_is_blocked(self) -> None:
        errors = hooks.evaluate_command("git add -A")
        self.assertTrue(any("no_broad_git_add" in err for err in errors))

    def test_unsafe_import_flags_are_blocked(self) -> None:
        errors = hooks.evaluate_command("python3 scripts/import_scraped_listings.py --include-unreviewed")
        self.assertTrue(any("unsafe_import_flags" in err for err in errors))

    def test_hook_inventory_has_one_per_agent_plus_codex(self) -> None:
        owners = {hook.owner for hook in hooks.HOOKS}
        expected = {
            "planner",
            "backend_developer",
            "data_analyst",
            "scraper_1",
            "scraper_sm",
            "ux_ui_designer",
            "debugger",
            "ops_release_manager",
            "infra_db_operator",
            "market_intelligence_analyst",
            "user_analytics_agent",
            "vision_media_agent",
            "entity_resolution_agent",
            "knowledge_context_agent",
        }
        self.assertTrue(expected.issubset(owners))
        self.assertGreaterEqual(len(hooks.HOOKS), 10)


if __name__ == "__main__":
    unittest.main()
