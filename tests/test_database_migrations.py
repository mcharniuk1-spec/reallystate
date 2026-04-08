import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DatabaseMigrationTests(unittest.TestCase):
    def test_alembic_scaffold_exists(self) -> None:
        self.assertTrue((ROOT / "alembic.ini").exists())
        self.assertTrue((ROOT / "migrations" / "env.py").exists())
        self.assertTrue((ROOT / "migrations" / "script.py.mako").exists())
        self.assertTrue((ROOT / "migrations" / "versions" / "20260407_0001_initial_schema.py").exists())
        self.assertTrue((ROOT / "migrations" / "versions" / "20260408_0002_source_registry_planning_fields.py").exists())

    def test_initial_migration_is_syntax_valid_without_alembic_installed(self) -> None:
        migration = ROOT / "migrations" / "versions" / "20260407_0001_initial_schema.py"
        ast.parse(migration.read_text(encoding="utf-8"))

    def test_initial_migration_reuses_schema_blueprint(self) -> None:
        migration_text = (ROOT / "migrations" / "versions" / "20260407_0001_initial_schema.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('"sql" / "schema.sql"', migration_text)
        self.assertIn("def upgrade()", migration_text)

    def test_schema_blueprint_contains_core_mvp_tables(self) -> None:
        schema = (ROOT / "sql" / "schema.sql").read_text(encoding="utf-8")
        for table_name in [
            "source_registry",
            "crawl_job",
            "raw_capture",
            "canonical_listing",
            "property_entity",
            "media_asset",
            "building_entity",
            "app_user",
            "lead_thread",
            "lead_message",
            "publish_job",
            "publish_attempt",
        ]:
            self.assertIn(f"create table if not exists {table_name}", schema)

    def test_source_registry_includes_planning_columns(self) -> None:
        schema = (ROOT / "sql" / "schema.sql").read_text(encoding="utf-8")
        self.assertIn("primary_url text", schema)
        self.assertIn("related_urls jsonb", schema)
        self.assertIn("listing_types jsonb", schema)

    def test_make_migrate_points_to_alembic(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        self.assertIn("-m alembic -c alembic.ini upgrade head", makefile)


if __name__ == "__main__":
    unittest.main()
