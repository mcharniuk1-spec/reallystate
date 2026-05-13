"""User-property state ledger and property chat links.

Revision ID: 20260429_0004
Revises: 20260423_0003
Create Date: 2026-04-29
"""

from __future__ import annotations

from alembic import op


revision = "20260429_0004"
down_revision = "20260423_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("alter table saved_property add column if not exists status text not null default 'liked'")
    op.execute("alter table saved_property add column if not exists updated_at timestamptz not null default now()")

    op.execute(
        """
        create table if not exists saved_property_status_event (
            event_id text primary key,
            saved_id text not null references saved_property(saved_id) on delete cascade,
            user_id text not null references app_user(user_id) on delete cascade,
            property_id text not null references property_entity(property_id) on delete cascade,
            actor_user_id text references app_user(user_id) on delete set null,
            action text not null,
            from_status text,
            to_status text not null,
            details_jsonb jsonb not null default '{}'::jsonb,
            created_at timestamptz not null default now()
        )
        """
    )
    op.execute(
        "create index if not exists idx_saved_property_user_status "
        "on saved_property(user_id, status, created_at desc)"
    )
    op.execute(
        "create index if not exists idx_saved_property_status_event_saved "
        "on saved_property_status_event(saved_id, created_at desc)"
    )

    op.execute(
        """
        create table if not exists user_property_chat (
            chat_id text primary key,
            user_id text not null references app_user(user_id) on delete cascade,
            property_id text not null references property_entity(property_id) on delete cascade,
            thread_id text not null references lead_thread(thread_id) on delete cascade,
            status text not null default 'open',
            created_at timestamptz not null default now(),
            updated_at timestamptz not null default now(),
            last_message_at timestamptz,
            metadata_jsonb jsonb not null default '{}'::jsonb,
            unique(user_id, property_id)
        )
        """
    )
    op.execute(
        "create index if not exists idx_user_property_chat_user_status "
        "on user_property_chat(user_id, status, updated_at desc)"
    )


def downgrade() -> None:
    raise NotImplementedError("Early MVP migrations are forward-only.")
