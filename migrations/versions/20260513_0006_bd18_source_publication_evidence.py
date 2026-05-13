"""BD-18 source-publication evidence and review tables.

Revision ID: 20260513_0006
Revises: 20260430_0005
Create Date: 2026-05-13
"""

from __future__ import annotations

from alembic import op

revision = "20260513_0006"
down_revision = "20260430_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        create table if not exists source_publication_qa_review (
            review_id text primary key,
            source_listing_id text not null references source_listing(source_listing_id) on delete cascade,
            listing_reference_id text references canonical_listing(reference_id) on delete set null,
            qa_state text not null,
            reviewer text not null default 'system',
            reviewed_at timestamptz not null default now(),
            import_eligible boolean not null default false,
            import_eligibility_reason text,
            blocked_import_reason text,
            source_publication_type text,
            scrape_acceptance_status text,
            evidence_jsonb jsonb not null default '{}'::jsonb,
            unique(source_listing_id, reviewer)
        )
        """
    )
    op.execute(
        "create index if not exists idx_source_publication_qa_review_state "
        "on source_publication_qa_review(qa_state, import_eligible, reviewed_at desc)"
    )
    op.execute(
        "create index if not exists idx_source_publication_qa_review_listing "
        "on source_publication_qa_review(listing_reference_id)"
    )

    op.execute(
        """
        create table if not exists status_history (
            status_event_id text primary key,
            subject_type text not null,
            subject_id text not null,
            from_status text,
            to_status text not null,
            observed_at timestamptz not null,
            source_observed_at timestamptz,
            provenance_jsonb jsonb not null default '{}'::jsonb,
            unique(subject_type, subject_id, to_status, observed_at)
        )
        """
    )
    op.execute(
        "create index if not exists idx_status_history_subject "
        "on status_history(subject_type, subject_id, observed_at desc)"
    )

    op.execute(
        """
        create table if not exists entity_resolution_candidate (
            candidate_id text primary key,
            candidate_type text not null,
            primary_listing_reference_id text not null references canonical_listing(reference_id) on delete cascade,
            candidate_listing_reference_id text references canonical_listing(reference_id) on delete cascade,
            candidate_property_id text references property_entity(property_id) on delete set null,
            review_status text not null default 'needs_review',
            confidence_score double precision,
            score_components_jsonb jsonb not null default '{}'::jsonb,
            conflict_reasons_jsonb jsonb not null default '[]'::jsonb,
            accepted_only_filter_jsonb jsonb not null default '{}'::jsonb,
            evidence_snapshot_jsonb jsonb not null default '{}'::jsonb,
            created_at timestamptz not null default now(),
            updated_at timestamptz not null default now(),
            unique(primary_listing_reference_id, candidate_listing_reference_id, candidate_type)
        )
        """
    )
    op.execute(
        "create index if not exists idx_entity_resolution_candidate_review "
        "on entity_resolution_candidate(review_status, candidate_type, confidence_score desc nulls last)"
    )
    op.execute(
        """
        create table if not exists entity_resolution_review_event (
            review_event_id text primary key,
            candidate_id text not null references entity_resolution_candidate(candidate_id) on delete cascade,
            action text not null,
            actor_user_id text references app_user(user_id) on delete set null,
            from_status text,
            to_status text not null,
            rationale text,
            evidence_jsonb jsonb not null default '{}'::jsonb,
            created_at timestamptz not null default now()
        )
        """
    )

    op.execute(
        """
        create table if not exists media_description (
            media_description_id text primary key,
            media_id text references media_asset(media_id) on delete cascade,
            listing_media_id text references listing_media(media_id) on delete cascade,
            listing_reference_id text references canonical_listing(reference_id) on delete cascade,
            generated_at timestamptz not null default now(),
            model_name text not null,
            model_version text,
            coverage_state text not null default 'pending',
            scene_type text,
            description_text text,
            confidence_score double precision,
            uncertainty_jsonb jsonb not null default '{}'::jsonb,
            evidence_jsonb jsonb not null default '{}'::jsonb
        )
        """
    )
    op.execute(
        "create index if not exists idx_media_description_listing "
        "on media_description(listing_reference_id, coverage_state, generated_at desc)"
    )

    op.execute(
        """
        create table if not exists availability_calendar (
            calendar_id text primary key,
            listing_reference_id text references canonical_listing(reference_id) on delete cascade,
            offer_id text references property_offer(offer_id) on delete cascade,
            calendar_type text not null,
            source_name text references source_registry(source_name) on delete set null,
            source_url text,
            status text not null default 'active',
            metadata_jsonb jsonb not null default '{}'::jsonb,
            created_at timestamptz not null default now(),
            updated_at timestamptz not null default now()
        )
        """
    )
    op.execute(
        """
        create table if not exists availability_slot (
            slot_id text primary key,
            calendar_id text not null references availability_calendar(calendar_id) on delete cascade,
            slot_start timestamptz not null,
            slot_end timestamptz not null,
            slot_status text not null,
            price_amount numeric,
            currency text,
            metadata_jsonb jsonb not null default '{}'::jsonb,
            unique(calendar_id, slot_start, slot_end)
        )
        """
    )
    op.execute(
        """
        create table if not exists availability_observation (
            observation_id text primary key,
            listing_reference_id text references canonical_listing(reference_id) on delete cascade,
            offer_id text references property_offer(offer_id) on delete cascade,
            observed_at timestamptz not null,
            source_observed_at timestamptz,
            availability_status text not null,
            price_amount numeric,
            currency text,
            provenance_jsonb jsonb not null default '{}'::jsonb
        )
        """
    )

    op.execute(
        """
        create table if not exists viewing_inquiry_request (
            request_id text primary key,
            listing_reference_id text references canonical_listing(reference_id) on delete set null,
            property_id text references property_entity(property_id) on delete set null,
            offer_id text references property_offer(offer_id) on delete set null,
            requester_user_id text references app_user(user_id) on delete set null,
            contact_id text references person_contact(contact_id) on delete set null,
            request_type text not null,
            request_status text not null default 'new',
            preferred_time_jsonb jsonb not null default '{}'::jsonb,
            message_summary text,
            provenance_jsonb jsonb not null default '{}'::jsonb,
            created_at timestamptz not null default now(),
            updated_at timestamptz not null default now()
        )
        """
    )
    op.execute(
        """
        create table if not exists external_chat_ref (
            chat_ref_id text primary key,
            thread_id text references lead_thread(thread_id) on delete set null,
            request_id text references viewing_inquiry_request(request_id) on delete set null,
            listing_reference_id text references canonical_listing(reference_id) on delete set null,
            property_id text references property_entity(property_id) on delete set null,
            offer_id text references property_offer(offer_id) on delete set null,
            participant_contact_id text references person_contact(contact_id) on delete set null,
            provider text not null,
            external_thread_ref text,
            handoff_status text not null default 'pending',
            metadata_jsonb jsonb not null default '{}'::jsonb,
            created_at timestamptz not null default now(),
            updated_at timestamptz not null default now()
        )
        """
    )


def downgrade() -> None:
    raise NotImplementedError("Early MVP migrations are forward-only.")
