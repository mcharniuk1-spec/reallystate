"""Initial PostgreSQL/PostGIS MVP schema.

Revision ID: 20260407_0001
Revises:
Create Date: 2026-04-07
"""

from __future__ import annotations

from pathlib import Path

from alembic import op


revision = "20260407_0001"
down_revision = None
branch_labels = None
depends_on = None


def _schema_sql() -> str:
    return (Path(__file__).resolve().parents[2] / "sql" / "schema.sql").read_text(encoding="utf-8")


def _statements(sql: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    for line in sql.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        current.append(line)
        if stripped.endswith(";"):
            statements.append("\n".join(current).rstrip().rstrip(";"))
            current = []
    if current:
        statements.append("\n".join(current).rstrip())
    return statements


def upgrade() -> None:
    for statement in _statements(_schema_sql()):
        op.execute(statement)


def downgrade() -> None:
    # The MVP migration is intentionally non-destructive by default. If a local
    # reset is needed during early development, recreate the dev database.
    raise NotImplementedError("Initial MVP schema downgrade is intentionally disabled.")
