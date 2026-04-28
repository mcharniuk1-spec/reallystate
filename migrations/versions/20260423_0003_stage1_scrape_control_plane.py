"""Stage 1 scrape control plane: region-first Varna-only sections, patterns, queue, fulfillment, versions.

Revision ID: 20260423_0003
Revises: 20260408_0002
Create Date: 2026-04-23
"""

from __future__ import annotations

from alembic import op


revision = "20260423_0003"
down_revision = "20260408_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Region (Varna-only; enforced by CHECK) ---
    op.execute(
        """
        create table if not exists scrape_region (
            region_key text primary key,
            display_name text not null,
            country_code text not null default 'BG',
            notes text,
            created_at timestamptz not null default now(),
            constraint scrape_region_only_varna check (region_key = 'varna')
        )
        """
    )
    op.execute(
        """
        insert into scrape_region (region_key, display_name, notes)
        values (
            'varna',
            'Varna (region-first MVP)',
            'Stage 1: only this region_key may exist. Expand to other regions only after explicit schema + policy change.'
        )
        on conflict (region_key) do nothing
        """
    )

    # --- Source website divisions (sections / verticals) ---
    op.execute(
        """
        create table if not exists source_section (
            section_id text primary key,
            source_name text not null references source_registry(source_name) on delete cascade,
            region_key text not null references scrape_region(region_key) on delete restrict,
            segment_key text not null,
            vertical_key text not null,
            section_label text not null,
            entry_urls jsonb not null default '[]'::jsonb,
            active boolean not null default false,
            legal_notes text,
            varna_filter jsonb not null default '{}'::jsonb,
            created_at timestamptz not null default now(),
            updated_at timestamptz not null default now(),
            constraint source_section_region_varna_only check (region_key = 'varna'),
            constraint source_section_segment_key check (
                segment_key in ('buy_personal','buy_commercial','rent_personal','rent_commercial')
            ),
            unique (source_name, region_key, segment_key, vertical_key)
        )
        """
    )
    op.execute("create index if not exists ix_source_section_source on source_section (source_name)")
    op.execute("create index if not exists ix_source_section_active on source_section (active) where active = true")

    # --- Layered crawl / parse patterns (JSON spec per layer) ---
    op.execute(
        """
        create table if not exists source_section_pattern (
            pattern_id text primary key,
            section_id text not null references source_section(section_id) on delete cascade,
            pattern_layer text not null,
            schema_version integer not null default 1,
            parser_profile text not null default 'generic_html_v1',
            spec_jsonb jsonb not null default '{}'::jsonb,
            created_at timestamptz not null default now(),
            constraint source_section_pattern_layer check (
                pattern_layer in ('source','section','list_page','detail_page','media_gallery')
            ),
            unique (section_id, pattern_layer, schema_version)
        )
        """
    )
    op.execute("create index if not exists ix_source_section_pattern_section on source_section_pattern (section_id)")

    # --- Orchestration: run + fine-grained queue tasks ---
    op.execute(
        """
        create table if not exists crawl_run (
            run_id text primary key,
            region_key text not null references scrape_region(region_key),
            mode text not null default 'planned',
            status text not null default 'created',
            initiated_by text,
            created_at timestamptz not null default now(),
            closed_at timestamptz,
            metadata jsonb not null default '{}'::jsonb,
            constraint crawl_run_region_varna_only check (region_key = 'varna')
        )
        """
    )

    op.execute(
        """
        create table if not exists crawl_queue_task (
            task_id text primary key,
            run_id text references crawl_run(run_id) on delete set null,
            section_id text not null references source_section(section_id) on delete cascade,
            task_type text not null,
            idempotency_key text not null unique,
            status text not null default 'pending',
            priority integer not null default 100,
            payload jsonb not null default '{}'::jsonb,
            attempt_count integer not null default 0,
            max_attempts integer not null default 5,
            next_attempt_at timestamptz,
            lease_until timestamptz,
            created_at timestamptz not null default now(),
            updated_at timestamptz not null default now(),
            constraint crawl_queue_task_type check (
                task_type in ('discover','fetch_list','fetch_detail','fetch_media','validate_listing','threshold_check')
            )
        )
        """
    )
    op.execute(
        "create index if not exists ix_crawl_queue_task_section_status on crawl_queue_task (section_id, status, next_attempt_at)"
    )

    op.execute(
        """
        create table if not exists crawl_error (
            error_id text primary key,
            task_id text references crawl_queue_task(task_id) on delete cascade,
            phase text not null,
            error_code text,
            message text not null,
            detail jsonb not null default '{}'::jsonb,
            created_at timestamptz not null default now()
        )
        """
    )
    op.execute("create index if not exists ix_crawl_error_task on crawl_error (task_id)")

    # --- Segment fulfillment (100 valid listings per bucket, later) ---
    op.execute(
        """
        create table if not exists segment_fulfillment (
            fulfillment_id text primary key,
            section_id text not null unique references source_section(section_id) on delete cascade,
            target_valid_listings integer not null default 100,
            current_valid_listings integer not null default 0,
            current_total_listings integer not null default 0,
            last_counted_at timestamptz,
            last_status text not null default 'unknown',
            threshold_reached_at timestamptz,
            incremental_ready boolean not null default false,
            notes text
        )
        """
    )

    # --- Global pause switch (default ON until operator approval) ---
    op.execute(
        """
        create table if not exists scrape_runner_state (
            singleton_id text primary key,
            global_pause boolean not null default true,
            notes text,
            updated_at timestamptz not null default now(),
            constraint scrape_runner_singleton check (singleton_id = 'global')
        )
        """
    )
    op.execute(
        """
        insert into scrape_runner_state (singleton_id, global_pause, notes)
        values (
            'global',
            true,
            'Stage 1 default: background scraping must not start until operator sets global_pause=false.'
        )
        on conflict (singleton_id) do nothing
        """
    )

    # --- Canonical listing versioning (append-only snapshots) ---
    op.execute(
        """
        create table if not exists canonical_listing_version (
            version_id text primary key,
            reference_id text not null references canonical_listing(reference_id) on delete cascade,
            snapshot_jsonb jsonb not null,
            reason text,
            created_at timestamptz not null default now()
        )
        """
    )
    op.execute(
        "create index if not exists ix_canonical_listing_version_ref on canonical_listing_version (reference_id, created_at desc)"
    )

    # --- Extend canonical_listing for region-first + full-detail pipeline ---
    op.execute("alter table canonical_listing add column if not exists region_key text")
    op.execute(
        "alter table canonical_listing add constraint canonical_listing_region_varna_only "
        "check (region_key is null or region_key = 'varna')"
    )
    op.execute("alter table canonical_listing add column if not exists segment_key text")
    op.execute("alter table canonical_listing add column if not exists vertical_key text")
    op.execute("alter table canonical_listing add column if not exists source_section_id text")
    op.execute(
        "alter table canonical_listing add constraint fk_canonical_listing_source_section "
        "foreign key (source_section_id) references source_section(section_id) on delete set null"
    )
    op.execute("alter table canonical_listing add column if not exists list_page_url text")
    op.execute("alter table canonical_listing add column if not exists detail_url_canonical text")
    op.execute("alter table canonical_listing add column if not exists combined_text text")
    op.execute("alter table canonical_listing add column if not exists normalized_text text")
    op.execute("alter table canonical_listing add column if not exists structured_extra jsonb not null default '{}'::jsonb")
    op.execute("alter table canonical_listing add column if not exists raw_text_fallback text")
    op.execute("alter table canonical_listing add column if not exists raw_detail_storage_key text")
    op.execute("create index if not exists ix_canonical_listing_region on canonical_listing (region_key)")
    op.execute("create index if not exists ix_canonical_listing_section on canonical_listing (source_section_id)")


def downgrade() -> None:
    # Best-effort teardown for local dev only.
    op.execute("alter table canonical_listing drop constraint if exists fk_canonical_listing_source_section")
    op.execute("alter table canonical_listing drop constraint if exists canonical_listing_region_varna_only")
    for col in (
        "region_key",
        "segment_key",
        "vertical_key",
        "source_section_id",
        "list_page_url",
        "detail_url_canonical",
        "combined_text",
        "normalized_text",
        "structured_extra",
        "raw_text_fallback",
        "raw_detail_storage_key",
    ):
        op.execute(f"alter table canonical_listing drop column if exists {col}")
    op.execute("drop table if exists canonical_listing_version cascade")
    op.execute("drop table if exists scrape_runner_state cascade")
    op.execute("drop table if exists segment_fulfillment cascade")
    op.execute("drop table if exists crawl_error cascade")
    op.execute("drop table if exists crawl_queue_task cascade")
    op.execute("drop table if exists crawl_run cascade")
    op.execute("drop table if exists source_section_pattern cascade")
    op.execute("drop table if exists source_section cascade")
    op.execute("drop table if exists scrape_region cascade")
