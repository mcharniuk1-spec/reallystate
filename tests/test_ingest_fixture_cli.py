from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from bgrealestate.cli import main as cli_main


ROOT = Path(__file__).resolve().parents[1]


class TestIngestFixtureCli(unittest.TestCase):
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

    def test_ingest_fixture_dry_run_homes(self) -> None:
        fixture = ROOT / "tests" / "fixtures" / "homes_bg" / "basic_listing"
        rc, out = self._run_cli(["bgrealestate", "ingest-fixture", "Homes.bg", str(fixture), "--dry-run"])
        self.assertEqual(rc, 0)
        self.assertIn('"source_name": "Homes.bg"', out)
        self.assertIn('"external_id": "HB-12345"', out)

    def test_ingest_fixture_non_dry_run_calls_ingest(self) -> None:
        if sys.version_info < (3, 10):
            self.skipTest("non-dry-run import path requires Python 3.10+ typing support in SQLAlchemy models")
        import importlib
        try:
            importlib.import_module("bgrealestate.db.session")
        except Exception:
            self.skipTest("cannot import bgrealestate.db.session (missing sqlalchemy or typing incompatibility)")
        fixture = ROOT / "tests" / "fixtures" / "homes_bg" / "basic_listing"
        with patch("bgrealestate.db.session.create_db_engine", return_value=object()) as p_engine:
            with patch(
                "bgrealestate.connectors.ingest.ingest_listing_detail_html",
                return_value={
                    "raw_capture_id": "r1",
                    "source_listing_id": "s1",
                    "snapshot_id": "ss1",
                    "reference_id": "Homes.bg:HB-12345",
                    "property_id": None,
                },
            ) as p_ingest:
                rc, out = self._run_cli(["bgrealestate", "ingest-fixture", "Homes.bg", str(fixture)])
        self.assertEqual(rc, 0)
        self.assertTrue(p_engine.called)
        self.assertTrue(p_ingest.called)
        self.assertIn("ingested:", out)


if __name__ == "__main__":
    unittest.main()
