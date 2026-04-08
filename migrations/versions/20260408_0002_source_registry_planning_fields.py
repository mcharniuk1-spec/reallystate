"""Add planning fields on source_registry for URLs and taxonomy JSON.

Revision ID: 20260408_0002
Revises: 20260407_0001
Create Date: 2026-04-08
"""

from __future__ import annotations

from alembic import op


revision = "20260408_0002"
down_revision = "20260407_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("alter table source_registry add column if not exists primary_url text")
    op.execute(
        "alter table source_registry add column if not exists related_urls jsonb not null default '[]'::jsonb"
    )
    op.execute(
        "alter table source_registry add column if not exists languages jsonb not null default '[]'::jsonb"
    )
    op.execute(
        "alter table source_registry add column if not exists listing_types jsonb not null default '[]'::jsonb"
    )


def downgrade() -> None:
    op.execute("alter table source_registry drop column if exists primary_url")
    op.execute("alter table source_registry drop column if exists related_urls")
    op.execute("alter table source_registry drop column if exists languages")
    op.execute("alter table source_registry drop column if exists listing_types")
