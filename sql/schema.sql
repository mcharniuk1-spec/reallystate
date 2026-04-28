-- Core schema for Bulgaria real estate ingestion and reverse publishing.
-- This file is a blueprint for the PostgreSQL/PostGIS MVP migrations.

create extension if not exists postgis;
create extension if not exists pg_trgm;

create table if not exists source_registry (
    source_name text primary key,
    tier integer not null,
    source_family text not null,
    owner_group text not null,
    access_mode text not null,
    risk_mode text not null,
    freshness_target text not null,
    publish_capable boolean not null,
    dedupe_cluster_hint text not null,
    legal_mode text not null default 'public_or_contract_review',
    mvp_phase text not null default 'source_first_ingestion',
    best_extraction_method text,
    notes text,
    primary_url text,
    related_urls jsonb not null default '[]'::jsonb,
    languages jsonb not null default '[]'::jsonb,
    listing_types jsonb not null default '[]'::jsonb
);

create table if not exists source_endpoint (
    endpoint_id text primary key,
    source_name text not null references source_registry(source_name),
    endpoint_kind text not null,
    base_url text not null,
    params_template jsonb not null default '{}'::jsonb,
    method text not null default 'GET',
    requires_headless boolean not null default false,
    requires_auth boolean not null default false,
    rate_limit_policy jsonb not null default '{}'::jsonb
);

create table if not exists source_legal_rule (
    rule_id text primary key,
    source_name text not null references source_registry(source_name),
    allowed_for_ingestion boolean not null,
    allowed_for_publishing boolean not null,
    requires_contract boolean not null default false,
    requires_consent boolean not null default false,
    blocks_live_scrape boolean not null default false,
    reason text not null
);

create table if not exists crawl_job (
    job_id text primary key,
    source_name text not null references source_registry(source_name),
    endpoint_id text references source_endpoint(endpoint_id),
    job_type text not null,
    status text not null,
    priority integer not null default 100,
    scheduled_for timestamptz not null,
    started_at timestamptz,
    finished_at timestamptz,
    attempt_count integer not null default 0,
    cursor_key text,
    idempotency_key text not null unique,
    metadata jsonb not null default '{}'::jsonb
);

create table if not exists crawl_cursor (
    cursor_id text primary key,
    source_name text not null references source_registry(source_name),
    endpoint_id text references source_endpoint(endpoint_id),
    cursor_key text not null,
    cursor_value jsonb not null default '{}'::jsonb,
    last_success_at timestamptz,
    last_seen_external_id text,
    metadata jsonb not null default '{}'::jsonb,
    unique(source_name, endpoint_id, cursor_key)
);

create table if not exists crawl_attempt (
    attempt_id text primary key,
    job_id text not null references crawl_job(job_id),
    status_code integer,
    error_code text,
    error_message text,
    proxy_id text,
    user_agent text,
    duration_ms integer,
    blocked_detected boolean not null default false,
    created_at timestamptz not null
);

create table if not exists raw_capture (
    raw_capture_id text primary key,
    source_name text not null references source_registry(source_name),
    url text not null,
    content_type text not null,
    body text not null,
    storage_key text,
    sha256 text,
    http_status integer,
    headers_json jsonb not null default '{}'::jsonb,
    fetched_at timestamptz not null,
    parser_version text not null,
    metadata jsonb not null default '{}'::jsonb
);

create table if not exists parser_fixture (
    fixture_id text primary key,
    source_name text not null references source_registry(source_name),
    page_type text not null,
    storage_key text not null,
    expected_output_jsonb jsonb not null default '{}'::jsonb,
    created_from_raw_capture_id text references raw_capture(raw_capture_id),
    case_label text not null,
    created_at timestamptz not null default now()
);

create table if not exists source_listing (
    source_listing_id text primary key,
    source_name text not null references source_registry(source_name),
    external_id text not null,
    canonical_url text not null,
    first_seen_at timestamptz not null,
    last_seen_at timestamptz not null,
    status text not null,
    current_snapshot_id text,
    source_reference text,
    source_payload_jsonb jsonb not null default '{}'::jsonb,
    unique(source_name, external_id)
);

create table if not exists source_listing_snapshot (
    snapshot_id text primary key,
    source_listing_id text not null references source_listing(source_listing_id),
    raw_capture_id text references raw_capture(raw_capture_id),
    title text,
    description text,
    price_amount numeric,
    currency text,
    area_sqm double precision,
    rooms double precision,
    floor integer,
    total_floors integer,
    city text,
    district text,
    address_text text,
    latitude double precision,
    longitude double precision,
    parsed_jsonb jsonb not null default '{}'::jsonb,
    created_at timestamptz not null
);

create table if not exists parsed_listing (
    parsed_listing_id text primary key,
    source_name text not null references source_registry(source_name),
    url text not null,
    external_id text not null,
    payload jsonb not null default '{}'::jsonb,
    parsed_at timestamptz not null
);

create table if not exists canonical_listing (
    reference_id text primary key,
    source_name text not null references source_registry(source_name),
    owner_group text not null,
    listing_url text not null,
    external_id text not null,
    listing_intent text not null,
    property_category text not null,
    city text,
    district text,
    resort text,
    region text,
    address_text text,
    latitude double precision,
    longitude double precision,
    geocode_confidence double precision,
    building_name text,
    area_sqm double precision,
    rooms double precision,
    floor integer,
    total_floors integer,
    construction_type text,
    construction_year integer,
    stage text,
    act16_present boolean,
    price numeric,
    currency text,
    fees numeric,
    price_per_sqm numeric,
    broker_name text,
    agency_name text,
    owner_name text,
    developer_name text,
    phones jsonb not null default '[]'::jsonb,
    messenger_handles jsonb not null default '[]'::jsonb,
    outbound_channel_hints jsonb not null default '[]'::jsonb,
    description text,
    amenities jsonb not null default '[]'::jsonb,
    image_urls jsonb not null default '[]'::jsonb,
    first_seen timestamptz not null,
    last_seen timestamptz not null,
    last_changed_at timestamptz not null,
    removed_at timestamptz,
    parser_version text not null,
    crawl_provenance jsonb not null default '{}'::jsonb
);

create table if not exists property_entity (
    property_id text primary key,
    dedupe_key text not null unique,
    entity_type text not null default 'unknown',
    canonical_title text,
    canonical_description text,
    canonical_address_id text,
    building_id text,
    project_id text,
    canonical_address text,
    canonical_city text,
    canonical_building_name text,
    latitude double precision,
    longitude double precision,
    geom geometry(Point, 4326),
    confidence_score double precision,
    review_status text not null default 'needs_review'
);

create table if not exists property_offer (
    offer_id text primary key,
    property_id text not null references property_entity(property_id),
    source_listing_id text references source_listing(source_listing_id),
    listing_reference_id text references canonical_listing(reference_id),
    intent text not null,
    offer_status text not null,
    price_amount numeric,
    currency text,
    price_per_sqm numeric,
    fees_amount numeric,
    available_from date,
    min_stay_days integer,
    last_changed_at timestamptz not null
);

create table if not exists property_attribute (
    attribute_id text primary key,
    property_id text not null references property_entity(property_id),
    key text not null,
    value_text text,
    value_num double precision,
    value_bool boolean,
    source_listing_id text references source_listing(source_listing_id),
    confidence double precision not null default 1.0
);

create table if not exists property_description (
    description_id text primary key,
    property_id text not null references property_entity(property_id),
    language text not null,
    title text,
    summary text,
    full_text text,
    source_listing_id text references source_listing(source_listing_id),
    is_canonical boolean not null default false
);

create table if not exists price_history (
    price_event_id text primary key,
    offer_id text not null references property_offer(offer_id),
    old_price numeric,
    new_price numeric,
    currency text,
    event_type text not null,
    detected_at timestamptz not null,
    source_listing_snapshot_id text references source_listing_snapshot(snapshot_id)
);

create table if not exists contact_entity (
    contact_id text primary key,
    display_name text not null,
    organization text,
    phones jsonb not null default '[]'::jsonb,
    messenger_handles jsonb not null default '[]'::jsonb
);

create table if not exists organization (
    organization_id text primary key,
    name text not null,
    org_type text not null,
    website text,
    source_owner_group text,
    normalized_name text,
    country text,
    city text,
    metadata jsonb not null default '{}'::jsonb
);

create table if not exists person_contact (
    contact_id text primary key,
    display_name text not null,
    normalized_name text,
    organization_id text references organization(organization_id),
    role text,
    language_codes jsonb not null default '[]'::jsonb,
    metadata jsonb not null default '{}'::jsonb
);

create table if not exists contact_method (
    contact_method_id text primary key,
    contact_id text references person_contact(contact_id),
    legacy_contact_id text references contact_entity(contact_id),
    method_type text not null,
    value text not null,
    normalized_value text,
    verified_status text not null default 'unverified',
    source_listing_id text references source_listing(source_listing_id)
);

create table if not exists property_contact_link (
    link_id text primary key,
    property_id text not null references property_entity(property_id),
    contact_id text references person_contact(contact_id),
    legacy_contact_id text references contact_entity(contact_id),
    relationship_type text not null,
    source_listing_id text references source_listing(source_listing_id),
    confidence double precision not null default 1.0
);

create table if not exists media_asset (
    media_id text primary key,
    source_url text,
    storage_key_original text,
    storage_key_web text,
    sha256 text,
    perceptual_hash text,
    mime_type text,
    width integer,
    height integer,
    bytes bigint,
    download_status text not null default 'pending',
    created_at timestamptz not null default now(),
    room_type text,
    quality_score double precision,
    is_exterior boolean,
    is_floorplan boolean
);

create table if not exists property_media (
    property_media_id text primary key,
    property_id text not null references property_entity(property_id),
    media_id text not null references media_asset(media_id),
    source_listing_id text references source_listing(source_listing_id),
    listing_reference_id text references canonical_listing(reference_id),
    sort_order integer not null default 0,
    caption text,
    room_label text,
    is_primary boolean not null default false,
    confidence double precision not null default 1.0
);

create table if not exists raw_file (
    file_id text primary key,
    raw_capture_id text references raw_capture(raw_capture_id),
    storage_key text not null,
    file_type text not null,
    sha256 text,
    metadata jsonb not null default '{}'::jsonb
);

create table if not exists media_processing_job (
    job_id text primary key,
    media_id text not null references media_asset(media_id),
    job_type text not null,
    status text not null,
    error_message text,
    created_at timestamptz not null,
    finished_at timestamptz
);

create table if not exists address (
    address_id text primary key,
    country text not null default 'Bulgaria',
    region text,
    municipality text,
    city text,
    district text,
    street text,
    number text,
    postal_code text,
    raw_address text,
    geom geometry(Point, 4326),
    geocode_confidence double precision
);

create table if not exists building_entity (
    building_id text primary key,
    name text,
    latitude double precision not null,
    longitude double precision not null,
    footprint geometry(MultiPolygon, 4326),
    centroid geometry(Point, 4326),
    height_m double precision,
    levels integer,
    construction_year integer,
    source text not null,
    confidence double precision not null,
    metadata jsonb not null default '{}'::jsonb
);

create table if not exists building_match (
    match_id text primary key,
    property_id text not null references property_entity(property_id),
    building_id text not null references building_entity(building_id),
    method text not null,
    confidence double precision not null,
    distance_m double precision,
    review_status text not null default 'needs_review',
    created_at timestamptz not null default now()
);

create table if not exists city_area (
    area_id text primary key,
    name text not null,
    area_type text not null,
    parent_area_id text references city_area(area_id),
    geom geometry(MultiPolygon, 4326),
    metadata jsonb not null default '{}'::jsonb
);

create table if not exists map_tile_cache (
    tile_id text primary key,
    z integer not null,
    x integer not null,
    y integer not null,
    layer text not null,
    storage_key text not null,
    etag text,
    generated_at timestamptz not null,
    unique(z, x, y, layer)
);

create table if not exists listing_media (
    media_id text primary key,
    listing_reference_id text not null references canonical_listing(reference_id),
    url text not null,
    content_hash text,
    caption text,
    ordering integer not null default 0,
    storage_key text,
    mime_type text,
    width integer,
    height integer,
    file_size bigint,
    download_status text not null default 'pending'
);

create table if not exists listing_event (
    event_id text primary key,
    listing_reference_id text not null references canonical_listing(reference_id),
    event_type text not null,
    emitted_at timestamptz not null,
    details jsonb not null default '{}'::jsonb
);

create table if not exists source_account (
    account_id text primary key,
    source_name text not null references source_registry(source_name),
    onboarding_mode text not null,
    authorized boolean not null,
    external_account_reference text
);

create table if not exists distribution_profile (
    profile_id text primary key,
    property_reference_id text not null references canonical_listing(reference_id),
    listing_intent text not null,
    enabled_channels jsonb not null default '[]'::jsonb,
    owner_operator_mode text not null,
    onboarding_modes jsonb not null default '[]'::jsonb,
    approved boolean not null default false
);

create table if not exists channel_mapping (
    mapping_id text primary key,
    property_reference_id text not null references canonical_listing(reference_id),
    channel text not null,
    external_listing_id text,
    state text not null,
    last_synced_at timestamptz
);

create table if not exists publish_job (
    publish_job_id text primary key,
    property_reference_id text not null references canonical_listing(reference_id),
    channel text not null,
    requested_at timestamptz not null,
    payload jsonb not null
);

create table if not exists publish_result (
    publish_job_id text primary key references publish_job(publish_job_id),
    channel text not null,
    state text not null,
    processed_at timestamptz not null,
    external_listing_id text,
    messages jsonb not null default '[]'::jsonb
);

create table if not exists compliance_flag (
    compliance_flag_id text primary key,
    property_reference_id text not null references canonical_listing(reference_id),
    code text not null,
    severity text not null,
    message text not null,
    blocks_publishing boolean not null,
    applies_to_channel text
);

create table if not exists app_user (
    user_id text primary key,
    external_auth_subject text unique,
    email text not null unique,
    display_name text not null,
    avatar_url text,
    password_hash text,
    user_mode text not null default 'buyer',
    status text not null default 'active',
    created_at timestamptz not null default now(),
    last_login_at timestamptz
);

create table if not exists saved_property (
    saved_id text primary key,
    user_id text not null references app_user(user_id),
    property_id text not null references property_entity(property_id),
    listing_reference_id text references canonical_listing(reference_id),
    notes text,
    created_at timestamptz not null default now(),
    unique(user_id, property_id)
);

create table if not exists organization_account (
    account_id text primary key,
    name text not null,
    account_type text not null default 'operator',
    billing_status text not null default 'trial',
    default_locale text not null default 'en',
    timezone text not null default 'Europe/Sofia',
    created_at timestamptz not null default now()
);

create table if not exists team_membership (
    membership_id text primary key,
    account_id text not null references organization_account(account_id),
    user_id text not null references app_user(user_id),
    role text not null,
    status text not null default 'active',
    created_at timestamptz not null default now(),
    unique(account_id, user_id)
);

create table if not exists permission_grant (
    grant_id text primary key,
    account_id text not null references organization_account(account_id),
    user_id text references app_user(user_id),
    permission text not null,
    resource_type text,
    resource_id text
);

create table if not exists service_account (
    service_account_id text primary key,
    account_id text not null references organization_account(account_id),
    name text not null,
    scopes_jsonb jsonb not null default '[]'::jsonb,
    status text not null default 'active',
    created_at timestamptz not null default now()
);

create table if not exists api_key (
    api_key_id text primary key,
    service_account_id text not null references service_account(service_account_id),
    key_hash text not null unique,
    prefix text not null,
    scopes_jsonb jsonb not null default '[]'::jsonb,
    expires_at timestamptz,
    last_used_at timestamptz
);

create table if not exists audit_log (
    audit_id text primary key,
    actor_type text not null,
    actor_id text,
    action text not null,
    resource_type text not null,
    resource_id text,
    ip_address text,
    user_agent text,
    details_jsonb jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists conversation_channel_account (
    channel_account_id text primary key,
    account_id text not null references organization_account(account_id),
    channel text not null,
    display_name text not null,
    external_account_id text,
    auth_status text not null default 'manual',
    capabilities_jsonb jsonb not null default '{}'::jsonb,
    last_sync_at timestamptz
);

create table if not exists lead_contact (
    lead_contact_id text primary key,
    account_id text not null references organization_account(account_id),
    person_contact_id text references person_contact(contact_id),
    display_name text not null,
    primary_phone text,
    primary_email text,
    preferred_channel text,
    tags_jsonb jsonb not null default '[]'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists lead_thread (
    thread_id text primary key,
    account_id text not null references organization_account(account_id),
    channel_account_id text references conversation_channel_account(channel_account_id),
    external_thread_id text,
    lead_contact_id text references lead_contact(lead_contact_id),
    status text not null default 'new',
    stage text not null default 'new',
    assignee_user_id text references app_user(user_id),
    priority text not null default 'normal',
    unread_count integer not null default 0,
    last_message_at timestamptz,
    follow_up_due_at timestamptz,
    created_at timestamptz not null default now()
);

create table if not exists lead_thread_property_link (
    link_id text primary key,
    thread_id text not null references lead_thread(thread_id),
    property_id text references property_entity(property_id),
    source_listing_id text references source_listing(source_listing_id),
    offer_id text references property_offer(offer_id),
    relationship_type text not null
);

create table if not exists lead_message (
    message_id text primary key,
    thread_id text not null references lead_thread(thread_id),
    direction text not null,
    sender_type text not null,
    sender_id text,
    external_message_id text,
    body_text text,
    body_html text,
    language text,
    sent_at timestamptz,
    received_at timestamptz,
    delivery_status text not null default 'stored',
    metadata_jsonb jsonb not null default '{}'::jsonb
);

create table if not exists message_attachment (
    attachment_id text primary key,
    message_id text not null references lead_message(message_id),
    media_id text references media_asset(media_id),
    external_url text,
    storage_key text,
    mime_type text,
    filename text,
    bytes bigint
);

create table if not exists thread_assignment_event (
    event_id text primary key,
    thread_id text not null references lead_thread(thread_id),
    old_assignee_id text references app_user(user_id),
    new_assignee_id text references app_user(user_id),
    changed_by_user_id text references app_user(user_id),
    created_at timestamptz not null default now()
);

create table if not exists task_reminder (
    task_id text primary key,
    thread_id text references lead_thread(thread_id),
    property_id text references property_entity(property_id),
    assigned_to_user_id text references app_user(user_id),
    due_at timestamptz not null,
    status text not null default 'open',
    title text not null,
    notes text,
    created_at timestamptz not null default now()
);

create table if not exists saved_reply_template (
    template_id text primary key,
    account_id text not null references organization_account(account_id),
    name text not null,
    language text not null default 'en',
    channel text,
    body_text text not null,
    variables_jsonb jsonb not null default '[]'::jsonb,
    enabled boolean not null default true
);

create table if not exists webhook_event (
    webhook_event_id text primary key,
    channel text not null,
    external_event_id text,
    payload_jsonb jsonb not null default '{}'::jsonb,
    received_at timestamptz not null default now(),
    processed_at timestamptz,
    status text not null default 'pending',
    error_message text
);

create table if not exists channel_capability (
    capability_id text primary key,
    channel text not null unique,
    supports_create boolean not null default false,
    supports_update boolean not null default false,
    supports_photos boolean not null default false,
    supports_rates boolean not null default false,
    supports_availability boolean not null default false,
    requires_partner boolean not null default false,
    requires_manual_review boolean not null default true,
    metadata jsonb not null default '{}'::jsonb
);

create table if not exists publish_attempt (
    attempt_id text primary key,
    publish_job_id text not null references publish_job(publish_job_id),
    status text not null,
    request_jsonb jsonb not null default '{}'::jsonb,
    response_jsonb jsonb not null default '{}'::jsonb,
    error_code text,
    error_message text,
    duration_ms integer,
    created_at timestamptz not null default now()
);

create table if not exists onboarding_session (
    session_id text primary key,
    account_id text not null references organization_account(account_id),
    channel text not null,
    mode text not null,
    status text not null,
    external_reference text,
    checklist_jsonb jsonb not null default '[]'::jsonb,
    created_at timestamptz not null default now(),
    completed_at timestamptz
);

create index if not exists idx_crawl_job_status_schedule on crawl_job(status, scheduled_for);
create index if not exists idx_raw_capture_source_fetched on raw_capture(source_name, fetched_at desc);
create index if not exists idx_source_listing_source_external on source_listing(source_name, external_id);
create index if not exists idx_source_listing_snapshot_listing_time on source_listing_snapshot(source_listing_id, created_at desc);
create index if not exists idx_canonical_listing_city_status on canonical_listing(city, last_seen desc);
create index if not exists idx_property_entity_geom on property_entity using gist(geom);
create index if not exists idx_building_entity_footprint on building_entity using gist(footprint);
create index if not exists idx_address_geom on address using gist(geom);
create index if not exists idx_city_area_geom on city_area using gist(geom);
create index if not exists idx_lead_thread_account_status on lead_thread(account_id, status, last_message_at desc);
create index if not exists idx_lead_message_thread_time on lead_message(thread_id, received_at desc);
create index if not exists idx_publish_job_channel on publish_job(channel, requested_at desc);
create index if not exists idx_contact_method_normalized_trgm on contact_method using gin(normalized_value gin_trgm_ops);

-- ---------------------------------------------------------------------------
-- Stage 1 scrape control plane (Varna-only, region-first). Mirrors Alembic
-- revision 20260423_0003. Prefer `alembic upgrade head` on real databases.
-- ---------------------------------------------------------------------------

create table if not exists scrape_region (
    region_key text primary key,
    display_name text not null,
    country_code text not null default 'BG',
    notes text,
    created_at timestamptz not null default now(),
    constraint scrape_region_only_varna check (region_key = 'varna')
);

insert into scrape_region (region_key, display_name, notes)
values (
    'varna',
    'Varna (region-first MVP)',
    'Stage 1: only this region_key may exist until explicit schema + policy change.'
)
on conflict (region_key) do nothing;

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
);

create index if not exists ix_source_section_source on source_section (source_name);
create index if not exists ix_source_section_active on source_section (active) where active = true;

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
);

create index if not exists ix_source_section_pattern_section on source_section_pattern (section_id);

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
);

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
);

create index if not exists ix_crawl_queue_task_section_status on crawl_queue_task (section_id, status, next_attempt_at);

create table if not exists crawl_error (
    error_id text primary key,
    task_id text references crawl_queue_task(task_id) on delete cascade,
    phase text not null,
    error_code text,
    message text not null,
    detail jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists ix_crawl_error_task on crawl_error (task_id);

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
);

create table if not exists scrape_runner_state (
    singleton_id text primary key,
    global_pause boolean not null default true,
    notes text,
    updated_at timestamptz not null default now(),
    constraint scrape_runner_singleton check (singleton_id = 'global')
);

insert into scrape_runner_state (singleton_id, global_pause, notes)
values (
    'global',
    true,
    'Stage 1 default: background scraping must not start until operator sets global_pause=false.'
)
on conflict (singleton_id) do nothing;

create table if not exists canonical_listing_version (
    version_id text primary key,
    reference_id text not null references canonical_listing(reference_id) on delete cascade,
    snapshot_jsonb jsonb not null,
    reason text,
    created_at timestamptz not null default now()
);

create index if not exists ix_canonical_listing_version_ref on canonical_listing_version (reference_id, created_at desc);

alter table canonical_listing add column if not exists region_key text;
alter table canonical_listing add column if not exists segment_key text;
alter table canonical_listing add column if not exists vertical_key text;
alter table canonical_listing add column if not exists source_section_id text;
alter table canonical_listing add column if not exists list_page_url text;
alter table canonical_listing add column if not exists detail_url_canonical text;
alter table canonical_listing add column if not exists combined_text text;
alter table canonical_listing add column if not exists normalized_text text;
alter table canonical_listing add column if not exists structured_extra jsonb not null default '{}'::jsonb;
alter table canonical_listing add column if not exists raw_text_fallback text;
alter table canonical_listing add column if not exists raw_detail_storage_key text;

do $$
begin
    if not exists (
        select 1 from pg_constraint where conname = 'canonical_listing_region_varna_only'
    ) then
        alter table canonical_listing
            add constraint canonical_listing_region_varna_only
            check (region_key is null or region_key = 'varna');
    end if;
end $$;

do $$
begin
    if not exists (
        select 1 from pg_constraint where conname = 'fk_canonical_listing_source_section'
    ) then
        alter table canonical_listing
            add constraint fk_canonical_listing_source_section
            foreign key (source_section_id) references source_section(section_id) on delete set null;
    end if;
end $$;

create index if not exists ix_canonical_listing_region on canonical_listing (region_key);
create index if not exists ix_canonical_listing_section on canonical_listing (source_section_id);
