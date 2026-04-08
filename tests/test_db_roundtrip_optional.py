from __future__ import annotations

import os
import unittest


class TestDbRoundtripOptional(unittest.TestCase):
    def test_optional_db_roundtrip(self) -> None:
        """
        This is intentionally optional:
        - unit tests must not require a running database
        - local dev can run it by setting DATABASE_URL and installing deps
        """
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            self.skipTest("DATABASE_URL not set")
        try:
            import sqlalchemy  # noqa: F401
            from sqlalchemy import text

            from bgrealestate.db.session import create_db_engine, session_scope
        except Exception as exc:  # pragma: no cover
            self.skipTest(f"db deps not available: {exc}")

        engine = create_db_engine(database_url)
        with session_scope(engine) as session:
            # Basic smoke: verify the DB responds and core table exists.
            session.execute(text("select 1"))
            session.execute(text("select source_name from source_registry limit 1"))


if __name__ == "__main__":
    unittest.main()

