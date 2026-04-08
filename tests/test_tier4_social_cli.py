from __future__ import annotations

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from bgrealestate.cli import main as cli_main
from bgrealestate.source_registry import SourceRegistry


ROOT = Path(__file__).resolve().parents[1]


class TestTier4SocialCli(unittest.TestCase):
    def _run_cli(self, argv: list[str]) -> tuple[int, str]:
        saved = sys.argv
        buf = io.StringIO()
        sys.argv = argv
        try:
            with redirect_stdout(buf):
                rc = cli_main()
        finally:
            sys.argv = saved
        return rc, buf.getvalue()

    def test_sync_social_database_dry_run(self) -> None:
        rc, out = self._run_cli(["bgrealestate", "sync-social-database", "--dry-run"])
        self.assertEqual(rc, 0)
        self.assertIn("would upsert", out)
        self.assertIn("tier-4 social sources", out)

    def test_export_tier4_writes_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rc, out = self._run_cli(["bgrealestate", "export-tier4", "--out-dir", tmp])
            self.assertEqual(rc, 0)
            self.assertIn("exported tier-4 dataset", out)
            self.assertTrue((Path(tmp) / "tier4-social-links.json").exists())
            self.assertTrue((Path(tmp) / "tier4-social-links.csv").exists())
            self.assertTrue((Path(tmp) / "tier4-social-posts.json").exists())
            self.assertTrue((Path(tmp) / "tier4-social-posts.csv").exists())

    def test_registry_has_expected_tier4_sources(self) -> None:
        registry = SourceRegistry.from_file(ROOT / "data" / "source_registry.json")
        tier4 = [entry.source_name for entry in registry.all() if entry.tier == 4]
        self.assertEqual(len(tier4), 7)
        self.assertIn("Telegram public channels", tier4)
        self.assertIn("X public search/accounts", tier4)


if __name__ == "__main__":
    unittest.main()
