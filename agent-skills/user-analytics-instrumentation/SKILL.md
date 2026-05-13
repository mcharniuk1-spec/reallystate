---
name: user-analytics-instrumentation
description: Design privacy-safe event tracking, funnels, UX telemetry, and dashboards for the Bulgaria Real Estate website.
---

# User Analytics Instrumentation

## Purpose

Use this skill when defining website analytics events, funnels, UX health metrics, and product telemetry dashboards.

## Required Inputs

- frontend routes under `app/`
- components under `components/`
- product UX docs
- user/auth/profile requirements
- privacy and compliance guardrails

## Core Event Groups

- search/filter changed
- listing card viewed
- listing card opened
- source link clicked
- map pin selected
- 2D/3D mode switched
- property saved/unsaved
- chat opened from property
- contact intent clicked
- account mode changed
- admin review action

## Workflow

1. Define event name, trigger, payload, and privacy rule.
2. Keep payloads minimal and non-secret.
3. Avoid raw message text, phone numbers, emails, and private notes in analytics events.
4. Map events to funnels:
   - browse to detail
   - detail to save/contact/chat
   - map interaction to detail
   - account setup to repeat use
5. Define dashboard views for product decisions.
6. Hand implementation tasks to frontend/backend.

## Acceptance Gate

- Event taxonomy is documented.
- No sensitive PII in payloads.
- Debugger can inspect and test events.
