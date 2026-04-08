---
name: frontend-pages
description: Use when building the Next.js MVP pages for listings, property detail, 3D map, CRM chat, settings, and admin/operator workflows.
---

# frontend-pages

Use this skill for the Next.js MVP frontend.

## Read First
- `PLAN.md`
- API contracts in the backend implementation

## Workflow
1. Build pages in order: `/listings`, `/properties/[id]`, `/map`, `/chat`, `/settings`, `/admin`.
2. Use typed API clients and stable response models.
3. Add loading, empty, error, and permission states.
4. Keep source provenance, compliance flags, dedupe confidence, and geocode confidence visible where relevant.
5. Use MapLibre GL JS and deck.gl for map/3D.

## Acceptance
- Listing feed, detail, map, chat, settings, and admin flows are usable.
- Frontend tests cover core routes.
- Public UI remains gated by operator workflow readiness.
