"""Property entity URL/source aggregation + richer dedupe support.

Revision ID: 20260430_0005
Revises: 20260429_0004
Create Date: 2026-04-30
"""

from __future__ import annotations

from alembic import op

revision = "20260430_0005"
down_revision = "20260429_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("alter table property_entity add column if not exists canonical_url text")
    op.execute("alter table property_entity add column if not exists source_links jsonb not null default '[]'::jsonb")
    op.execute("alter table property_entity add column if not exists merged_image_urls jsonb not null default '[]'::jsonb")
    op.execute("alter table property_entity add column if not exists description_summary text")
    op.execute("alter table canonical_listing add column if not exists title text")


def downgrade() -> None:
    raise NotImplementedError("Early MVP migrations are forward-only.")

