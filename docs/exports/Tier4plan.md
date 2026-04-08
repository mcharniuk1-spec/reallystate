# Tier-4 Social Collection Plan

Date: 2026-04-08

## Goal
Build a legal-safe tier-4 social intelligence layer that stores social links in the registry database, stores each message/post as a separate CRM message row, and keeps all fixture tests fully offline.

## What to do with links
Every known tier-4 social URL should be inserted into `source_endpoint` using endpoint kind `social_channel`, while preserving source-level legal policy in `source_legal_rule`. Links are divided into primary and related URLs so operators can prioritize official endpoints first.

## What may be needed
Per-platform credentials for official APIs, operator approval workflows for consent-restricted sources, and moderation/redaction checks before any message is saved. For Facebook/Instagram/Threads, ingestion should remain manual/consent-driven until explicit authorization paths are in place.

## Options by platform
Telegram and X can run via official API ingestion with strong rate limits and audit metadata. Facebook/Instagram/Threads should run in assisted-manual mode unless official API scopes and app review are approved. Viber and WhatsApp should run only under explicit opt-in or official business/vendor channels.

## Database output model
Use `source_endpoint` for links, and `lead_thread` + `lead_message` for one row per post/message. Raw payload snapshots should be retained in `raw_capture` with redaction metadata and parser version for traceability.

## Execution order
First sync tier-4 links to DB, then seed/ingest social messages (fixture-first), then validate extraction quality and move to operator-reviewed live ingestion for explicitly allowed channels only.
