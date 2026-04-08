---
name: geo-map-3d
description: Use for geocoding, PostGIS building matching, map APIs, vector payloads, 2D fallback, and 3D MapLibre/deck.gl map behavior.
---

# geo-map-3d

Use this skill for geocoding, building matching, map APIs, and 3D map UI.

## Read First
- `sql/schema.sql`
- `PLAN.md`
- `docs/diagrams/platform-architecture.mmd`

## Workflow
1. Normalize raw address into `address`.
2. Use PostGIS geometry for viewport and building queries.
3. Match buildings with confidence based on coordinate quality, address text, distance, and footprint containment.
4. Provide 2D fallback when geometry or confidence is weak.
5. Prioritize Sofia, Varna, Burgas, Sunny Beach/Nessebar, and Bansko.

## Acceptance
- `/map/viewport` and building summary APIs return map-ready payloads.
- 3D rendering works where footprints/heights exist.
- Confidence is visible to operators.
