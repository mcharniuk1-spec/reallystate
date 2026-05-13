# Strategic Code Manager Review — 2026-04-29

## Scope

Operator requested a deeper source-pattern and product architecture pass while OpenClaw Action1 is running.

## Action1 Boundary

FACT — `S1-22B` is `IN_PROGRESS` and owns the seven-source all-Bulgaria scrape/backfill path.

FACT — Current worktree includes large `data/scraped/**` churn from the Action1 run.

INTERPRETATION — This pass must not edit live scrape output, Action1 scripts, section catalog, or tier-1/2 parser patterns.

GAP — Action1 debugger QA is still pending, so remaining tier-1/2 expansion must stay queued behind `Action2 now`.

## Current Product/Backend State

FACT — User auth, mode switching, and saved-property endpoints already existed in `BD-13`, but saved state was not auditable as a status/action ledger.

FACT — `lead_thread`, `lead_message`, and `lead_thread_property_link` already model CRM conversation state, but there was no explicit authenticated `user -> property -> chat` table.

FACT — `/api/v1/chat` existed but defaulted to stub/OpenAI; frontend chat surfaces were mostly demo/local.

INTERPRETATION — The lowest-risk implementation is to add an operational state layer around existing tables:

- keep `saved_property` as the user-property like connection
- add `saved_property_status_event` for status-change history
- add `user_property_chat` for the explicit property chat join
- use existing `lead_thread` / `lead_message` for persisted chat messages
- add Ollama as the local model adapter behind the backend proxy

## Source Pattern Strategy

FACT — `S1-22C` already defines remaining legal tier-1/2 expansion after Action1 QA.

INTERPRETATION — Do not create a competing tier-1/2 live pattern path during Action1. Add only queue notes and non-executing source strategy.

FACT — Tier-3 has contract/licensed/official-register routes. Live Airbnb/Booking/Vrbo scraping remains blocked without contracts.

FACT — Tier-4 registry already contains Telegram public channels, X public accounts, Facebook/Instagram manual-consent routes, Viber opt-in communities, and WhatsApp opt-in groups.

INTERPRETATION — Messenger data must enter as source publications or CRM lead evidence first. Promotion to `property_entity` is allowed only after the single-unit evidence gate is met.

## Messenger Source Position

FACT — Telegram Bot API supports bot updates and webhook/long-polling flows for allowed bot-visible updates: https://core.telegram.org/bots/api

FACT — Viber REST Bot API requires an active commercial bot, auth token, and webhook setup: https://developers.viber.com/docs/api/rest-bot-api/

FACT — Meta WhatsApp Cloud API is the official server-side WhatsApp Business route and uses Graph API/webhook setup: https://developers.facebook.com/docs/whatsapp/cloud-api/get-started

INTERPRETATION — Telegram public channels can be the first automated messenger source if the channel is public and bot/API access is authorized. Viber/WhatsApp should be webhook or manual-consent ingestion, not group scraping.

HYPOTHESIS — The highest-value messenger path is not raw channel volume; it is lead-to-property candidate extraction with strict redaction, review status, and provenance.

GAP — Current code does not yet persist messenger publication candidates into `source_listing` / `parsed_listing` / `canonical_listing` with a review gate.

## Implemented In This Pass

FACT — Added DB schema/migration for liked-property status history and user-property chat joins.

FACT — Added authenticated API routes for liked properties and property chats.

FACT — Added Ollama local chat provider (`gemma4:26b` default) with stub fallback.

FACT — Updated global chat bar and `/chat` page to call the backend chat API through the masked Next proxy.

FACT — Rebuilt `/settings` as an account cabinet with mode switch, liked properties, saved searches, and chat entry points.

## Next Management Actions

1. Debugger verifies the new backend/frontend contract with fixture-only tests and a local UI smoke.
2. After Action1 QA, run `S1-22C` for remaining legal tier-1/2 sources.
3. Start `SM-08` as a fixture-first messenger publication candidate mapper.
4. Start `BD-19` only after `SM-08` defines the candidate schema and review statuses.
