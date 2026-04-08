"""Control-plane tests for the Backend_developer "DB sync + control plane bootstrap" slice.

Tests here must work WITHOUT a running database (no live-network dependency).
"""
from __future__ import annotations

import ast
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestDbSyncImport(unittest.TestCase):
    """db_sync module + CLI sync-database should be importable and syntax-valid."""

    def test_db_sync_is_syntax_valid(self) -> None:
        src = ROOT / "src" / "bgrealestate" / "db_sync.py"
        ast.parse(src.read_text(encoding="utf-8"))

    def test_cli_sync_database_dry_run(self) -> None:
        from bgrealestate.cli import main as cli_main

        import sys
        saved = sys.argv
        sys.argv = ["bgrealestate", "sync-database", "--dry-run"]
        try:
            rc = cli_main()
        finally:
            sys.argv = saved
        self.assertEqual(rc, 0)

    def test_marketplace_sources_excludes_social(self) -> None:
        from bgrealestate.connectors.factory import marketplace_sources
        from bgrealestate.source_registry import SourceRegistry

        registry = SourceRegistry.from_file(ROOT / "data" / "source_registry.json")
        sources = marketplace_sources(registry)
        names = {s.source_name for s in sources}
        self.assertIn("Homes.bg", names)
        self.assertIn("OLX.bg", names)
        for s in sources:
            self.assertNotIn("social", s.source_family.value.lower())
            self.assertNotIn("messenger", s.source_family.value.lower())


class TestExportScriptSyntax(unittest.TestCase):
    def test_export_source_stats_xlsx_is_syntax_valid(self) -> None:
        src = ROOT / "scripts" / "export_source_stats_xlsx.py"
        ast.parse(src.read_text(encoding="utf-8"))


class TestSourceStatsModel(unittest.TestCase):
    def test_source_stat_row_has_registry_fields(self) -> None:
        from bgrealestate.stats.source_stats import SourceStatRow

        r = SourceStatRow(
            source_name="test",
            tier=1,
            legal_mode="public_crawl_with_review",
            canonical_listings=0,
            raw_captures=0,
            with_description=0,
            with_photos=0,
            photo_coverage_pct=0.0,
            intent_sale=0,
            intent_rent=0,
            intent_str=0,
            intent_auction=0,
            category_apartment=0,
            category_house=0,
            category_land=0,
            category_commercial=0,
            has_legal_rule=True,
            has_endpoint=True,
        )
        self.assertEqual(r.tier, 1)
        self.assertTrue(r.has_legal_rule)


try:
    from fastapi.testclient import TestClient
except ImportError:
    TestClient = None  # type: ignore[assignment,misc]


class TestReadinessEndpoint(unittest.TestCase):
    """GET /api/v1/ready with no DATABASE_URL / REDIS_URL returns 200 + ok."""

    def setUp(self) -> None:
        if TestClient is None or sys.version_info < (3, 10):
            self.skipTest("fastapi runtime checks require fastapi installed on Python 3.10+")
        from bgrealestate.api import deps as deps_mod
        from bgrealestate.api.main import create_app

        self._saved = {
            "DATABASE_URL": os.environ.pop("DATABASE_URL", None),
            "REDIS_URL": os.environ.pop("REDIS_URL", None),
            "API_KEYS_JSON": os.environ.pop("API_KEYS_JSON", None),
        }
        os.environ["API_KEYS_JSON"] = '{"admin-key":["admin:read"]}'
        deps_mod._engine = None
        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        from bgrealestate.api import deps as deps_mod

        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        deps_mod._engine = None

    def test_ready_ok_without_deps(self) -> None:
        r = self.client.get("/api/v1/ready")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["status"], "ok")
        pg = [c for c in body["checks"] if c["name"] == "postgres"][0]
        self.assertIsNone(pg["ok"])

    def test_admin_source_stats_returns_503_without_db(self) -> None:
        r = self.client.get("/admin/source-stats", headers={"X-API-Key": "admin-key"})
        self.assertEqual(r.status_code, 503)
