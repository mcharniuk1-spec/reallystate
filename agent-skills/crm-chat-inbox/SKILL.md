---
name: crm-chat-inbox
description: Use for CRM chat inbox, lead threads, messages, reminders, assignments, templates, channel accounts, webhooks, and property-linked conversations.
---

# crm-chat-inbox

Use this skill for the chat folder, CRM inbox, leads, and messaging adapters.

## Read First
- `PLAN.md`
- `sql/schema.sql`
- `data/source_registry.json`

## Workflow
1. Treat `/chat` as a full CRM inbox, not a passive message folder.
2. Model threads, messages, reminders, assignments, saved replies, attachments, webhook events, and audit history.
3. Link every thread to contact and optionally listing/property/offer.
4. Support manual channel mode first.
5. Add WhatsApp Business, Messenger, Instagram, Viber, Telegram, and email only through authorized/consented routes.

## Acceptance
- Messages are append-only.
- Operators can assign, reply, follow up, and audit.
- Unsupported/private channels degrade to manual assist.
