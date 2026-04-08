---
name: visual-3d-map
description: Use when implementing 2D/3D map visualization, building overlays, and map-centric UX behavior.
---

# visual-3d-map

Use this skill for map rendering and visual experience work.

## Read First
- `PLAN.md` (map sections)
- `agent-skills/geo-map-3d/SKILL.md`
- `docs/project-architecture-execution-guide.md`

## Workflow
1. Keep geometry confidence explicit in UI.
2. Provide 3D where footprints/buildings are strong; fallback to 2D otherwise.
3. Keep map and list interactions synchronized (hover/select/filter).
4. Add fixtures/mocks for map data to avoid live dependencies in tests.

## Acceptance
- Map UX is understandable in both 2D and 3D modes.
- Weak-geometry areas degrade gracefully.

