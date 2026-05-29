---
project: real-estate-bulgaria
type: knowledge-entity
status: active
date: 2026-05-29
owner: lead_agent
---

# Strategic Planning Knowledge Entity

## Role

This note is the Real Estate Bulgaria vault-level planning entity. It should hold durable sequencing logic, cross-agent dependencies, and strategic interpretation that would otherwise be repeated in chat, TASKS, or temporary handoff docs.

## Boundaries

FACT:
- `docs/agents/TASKS.md` remains the execution queue.
- Agent `JOURNEY.md` files remain append-only execution logs.
- WikiLLM project files remain the cross-run memory layer.
- This entity is for planning meaning, not raw scraped listings, raw page copy, credentials, or generated Graphify dumps.

INTERPRETATION:
- Keeping strategy as a separate entity improves agent workflow because each agent can read a compact planning anchor before changing task status or implementing a slice.
- The entity should link out to source-specific notes, decisions, and run logs rather than duplicate them.

GAP:
- Nexus live note operations were not used in this run. Filesystem sync is the fallback until live vault readiness is confirmed.

## Update Rules

- Add only durable planning knowledge: sequencing decisions, blocked assumptions, accepted definitions, and cross-agent dependencies.
- Keep implementation details in repo docs or run logs.
- Mask private values before copying any command output or external source detail.
- Link decisions and strategy notes, for example [[Property Link Comparable Search Strategy]].

## Current Strategic Focus

1. Preserve compliance-first source publication identity.
2. Finish accepted-only persistence and active-link proof before public/dashboard claims.
3. Add property-link comparable search as the operator investigation layer between one-page scraping and entity-resolution review.
4. Keep tier-3 and social evidence route-gated. No private-channel scraping, no unauthorized partner access, and no automatic canonical merges.
