# User Event Taxonomy

## Scope

FACT: the current website surfaces browse/search, listing cards, a MapLibre map with DOM fallback pins, property detail pages, media galleries, chat, account/profile cabinet, and an admin dashboard.

INTERPRETATION: instrumentation should be first-party and local to the product so UX decisions can be made without installing external analytics or sending user data to third parties.

HYPOTHESIS: the first useful product questions are funnel and friction questions: search to detail, map to detail, detail to save/contact/chat, profile to repeat use, and admin review throughput.

GAP: final payload fields must be rechecked after `BD-13`, `BD-17`, `BD-19`, and `UX-15` stabilize.

## Privacy Rules

- No external analytics SDKs.
- No third-party analytics endpoints.
- No raw chat messages, raw search text, emails, phone numbers, names, private notes, auth tokens, IP addresses, user agents, source URLs, or contact details in analytics payloads.
- Typed search and chat text are represented only by safe derived fields such as `length_bucket`, `token_count_bucket`, `query_mode`, `has_filters`, and `result_count_bucket`.
- Authenticated users may be represented only by a server-side pseudonymous `actor_hash`.
- Anonymous users may be represented only by a first-party `session_hash` with rotation/expiry.
- Listing references should use the internal public listing identifier or a one-way hash. Do not store external listing URLs in analytics.
- Admin review events store queue/action/result enums only; no raw review comments or scraped raw content.
- Payloads are allowlisted by event name and schema version; unknown fields are rejected or dropped.

## Common Envelope

| Field | Type | Rule |
|---|---|---|
| `event_name` | string | Required, one of the allowlisted names below. |
| `schema_version` | string | Start with `v1`. |
| `occurred_at` | ISO timestamp | Client time accepted, server receive time also stored. |
| `surface` | enum | `home`, `listings`, `map`, `property_detail`, `chat`, `settings`, `admin`. |
| `session_hash` | string | First-party pseudonymous session id. |
| `actor_hash` | string/null | Server-side pseudonym only when authenticated. |
| `role` | enum/null | `anonymous`, `buyer`, `renter`, `seller`, `operator`, `admin`. |
| `device_class` | enum | `mobile`, `tablet`, `desktop`; no raw user agent. |
| `viewport_bucket` | enum | `xs`, `sm`, `md`, `lg`, `xl`; no exact screen size needed. |
| `route_pattern` | string | Pattern only, e.g. `/properties/[id]`. |
| `experiment_keys` | string[] | Optional first-party feature flags; no user attributes. |

## Event Groups

### Listing Search And Feed

| Event | Trigger | Payload | Privacy rule |
|---|---|---|---|
| `search_changed` | User changes search mode or typed search settles after debounce. | `query_mode`, `length_bucket`, `token_count_bucket`, `has_filters`, `deal_mode`, `space_mode`, `result_count_bucket` | No raw query text. |
| `search_submitted` | User explicitly submits or presses Enter. | `query_mode`, `length_bucket`, `token_count_bucket`, `deal_mode`, `space_mode`, `result_count_bucket`, `zero_results` | No raw query text. |
| `filter_changed` | Deal, space, aggregate-only, sort, or structured filter changes. | `filter_key`, `filter_value_bucket`, `deal_mode`, `space_mode`, `result_count_bucket` | Use buckets/enums only. |
| `listing_impression_batch` | A viewport batch of listing cards becomes visible. | `visible_count`, `position_start`, `position_end`, `result_count_bucket`, `source_mix_count`, `quality_state_mix` | No per-card event spam; no raw URLs. |
| `listing_card_selected` | User clicks a listing card or map selection pins it to the feed. | `listing_ref_hash`, `position`, `selection_source`, `source_count`, `scrape_acceptance_status`, `media_status`, `price_status` | Listing id may be hashed. |
| `source_link_opened` | User opens an original source link. | `listing_ref_hash`, `source_key`, `is_current`, `source_count`, `media_status` | Store source key only, not URL. |

### Map Use

| Event | Trigger | Payload | Privacy rule |
|---|---|---|---|
| `map_ready` | Map engine or fallback becomes ready. | `map_engine`, `fallback_visible`, `tile_issue`, `listing_count_bucket` | No network error URLs. |
| `map_marker_selected` | User selects a property or cluster marker. | `marker_kind`, `cluster_size_bucket`, `listing_ref_hash`, `result_count_bucket`, `zoom_bucket` | Cluster items count only unless opening a specific listing. |
| `map_view_changed` | Move/zoom settles after debounce. | `zoom_bucket`, `bbox_bucket`, `visible_marker_count`, `visible_listing_count_bucket`, `is_3d` | Do not store exact map bounds until geospatial privacy reviewed; use coarse buckets. |
| `map_mode_changed` | User switches 2D/3D. | `from_mode`, `to_mode`, `zoom_bucket`, `building_layer_visible` | No raw coordinates. |
| `map_preset_clicked` | User clicks Varna or reset map control. | `preset`, `is_3d`, `result_count_bucket` | Enum only. |

### Save, Like, Contact

| Event | Trigger | Payload | Privacy rule |
|---|---|---|---|
| `property_saved` | Authenticated user saves/likes a property. | `listing_ref_hash`, `surface`, `save_state`, `source_count`, `scrape_acceptance_status` | Actor pseudonym only. |
| `property_unsaved` | User removes saved/liked state. | `listing_ref_hash`, `surface`, `previous_save_state` | Actor pseudonym only. |
| `contact_intent_clicked` | User clicks call/message/contact CTA. | `listing_ref_hash`, `intent_type`, `surface`, `is_enabled`, `blocked_reason` | Do not store phone/email/message body. |
| `property_share_clicked` | User clicks share/copy link. | `listing_ref_hash`, `surface` | No destination or clipboard contents. |

### Chat

| Event | Trigger | Payload | Privacy rule |
|---|---|---|---|
| `chat_opened` | Global chat expands or chat page/thread opens. | `chat_surface`, `thread_kind`, `property_context_present`, `listing_ref_hash` | No messages. |
| `chat_tab_changed` | User switches search/property chat tabs. | `from_tab`, `to_tab`, `property_context_present` | Enum only. |
| `chat_message_sent` | User sends a message. | `chat_surface`, `thread_kind`, `length_bucket`, `token_count_bucket`, `property_context_present`, `active_filter_count` | No message text. |
| `chat_response_received` | Backend/fallback returns a response. | `provider_class`, `latency_bucket_ms`, `response_length_bucket`, `thread_kind`, `property_context_present` | No response text. |
| `chat_failed` | Chat request fails. | `provider_class`, `error_class`, `http_status_bucket`, `thread_kind` | No raw exception text if it may include URLs/secrets. |

### Profile And Account

| Event | Trigger | Payload | Privacy rule |
|---|---|---|---|
| `profile_opened` | User opens `/settings`. | `role`, `liked_count_bucket`, `chat_count_bucket`, `saved_search_count_bucket` | No email/name/phone. |
| `account_mode_changed` | Buyer/renter/seller mode changes. | `from_mode`, `to_mode` | Enum only. |
| `saved_search_created` | User creates a saved search. | `deal_mode`, `space_mode`, `filter_count`, `location_scope`, `result_count_bucket` | No raw query text/address. |
| `saved_search_alert_toggled` | Alert switch changes. | `enabled`, `location_scope`, `deal_mode`, `space_mode` | Enum only. |
| `profile_field_edited` | User edits profile field. | `field_key`, `action` | Field key only; never field value. |

### Admin Review

| Event | Trigger | Payload | Privacy rule |
|---|---|---|---|
| `admin_dashboard_opened` | Operator opens `/admin`. | `queue_count_bucket`, `source_status_mix` | No operator PII. |
| `admin_queue_opened` | Operator opens a review queue. | `queue_key`, `count_bucket`, `severity` | Enum/count only. |
| `admin_review_action` | Operator accepts, rejects, marks grouped, marks lost, requests rescrape, merges, or defers. | `queue_key`, `action`, `entity_kind`, `reason_code`, `previous_status`, `next_status` | No review notes/raw scraped text. |
| `admin_source_status_filter_changed` | Operator filters source health table. | `status_filter`, `source_key`, `count_bucket` | Source key only. |
| `admin_export_clicked` | Operator exports dashboard/report. | `export_type`, `scope`, `row_count_bucket` | No exported content in event. |

### Media Interactions

| Event | Trigger | Payload | Privacy rule |
|---|---|---|---|
| `media_gallery_viewed` | Listing card/detail gallery enters viewport. | `listing_ref_hash`, `surface`, `remote_photo_count_bucket`, `local_photo_count_bucket`, `full_gallery_downloaded`, `image_report_status` | No image URLs. |
| `media_gallery_navigated` | User clicks next/previous thumbnail/photo. | `listing_ref_hash`, `surface`, `direction`, `photo_index_bucket`, `photo_count_bucket` | No image URLs. |
| `media_lightbox_opened` | Detail gallery lightbox opens. | `listing_ref_hash`, `photo_count_bucket`, `image_report_status` | No image URLs. |
| `media_load_failed` | Proxied image fails to render. | `listing_ref_hash`, `surface`, `source_key`, `photo_index_bucket`, `failure_class` | No raw image URL or HTTP body. |

## Funnel Metrics

| Funnel | Stages | Product decision supported |
|---|---|---|
| Browse to detail | `listing_impression_batch` -> `listing_card_selected` -> property detail route | Card density, ranking, and whether evidence badges help selection. |
| Search to result | `search_changed`/`search_submitted` -> result count -> `listing_card_selected` | Whether search modes and filters find usable inventory. |
| Map to detail | `map_ready` -> `map_marker_selected` -> `listing_card_selected`/detail route | Whether map pins and clusters drive exploration. |
| Detail to intent | detail view -> `property_saved`/`contact_intent_clicked`/`chat_opened` | Which evidence drives user intent. |
| Chat success | `chat_opened` -> `chat_message_sent` -> `chat_response_received`/`chat_failed` -> property action | Whether chat produces useful property actions without logging content. |
| Profile retention | `profile_opened` -> `account_mode_changed`/saved search/alert toggle -> repeat save/chat | Whether account features create repeat value. |
| Admin throughput | `admin_queue_opened` -> `admin_review_action` -> next status | Whether review queues clear accepted/LOST/grouped evidence safely. |
| Media confidence | `media_gallery_viewed` -> `media_gallery_navigated`/`media_lightbox_opened` -> save/contact/chat | Whether full galleries and image reports improve trust. |

## Implementation Contract

1. Add no external analytics dependency.
2. Implement a small first-party client wrapper only after event intake exists or a local debug sink is approved.
3. Backend owns allowlisting, schema validation, payload redaction, persistence, retention, and dashboard query APIs.
4. UX owns firing events from stable interactions with safe derived payloads.
5. Debugger verifies that payloads cannot include raw text, URLs, contacts, tokens, or private notes.
6. Keep high-frequency events debounced and batched: search changes, map moves, and impressions should not write per-keystroke/per-pixel/per-card events.

## Next Slices

- `UA-02`: freeze instrumentation implementation plan after UI/backend contracts stabilize.
- `BD-20`: add first-party analytics event intake/storage with strict allowlists.
- `UX-20`: add frontend instrumentation hooks without external analytics.
- `UA-03`: define product analytics dashboard queries and acceptance thresholds.
- `DBG-19`: verify privacy, payload schemas, and no external analytics.
