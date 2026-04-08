"""Database package for the PostgreSQL/PostGIS persistence layer.

The concrete SQLAlchemy modules intentionally live behind explicit imports so
the current stdlib-only tests can still run before local dependencies are
installed.
"""

