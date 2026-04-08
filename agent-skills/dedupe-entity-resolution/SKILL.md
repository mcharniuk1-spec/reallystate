---
name: dedupe-entity-resolution
description: Use when implementing property, contact, media, address, and geospatial duplicate scoring, merge candidates, and reviewable entity resolution.
---

# dedupe-entity-resolution

Use this skill when building property/contact/media duplicate matching.

## Read First
- `src/bgrealestate/pipeline.py`
- `sql/schema.sql`
- `data/source_registry.json`

## Workflow
1. Score exact source ID matches first.
2. Add address, city, area, price, contact, photo hash, building/project name, and geospatial similarity.
3. Create reviewable duplicate candidates for ambiguous matches.
4. Never silently merge low-confidence records.
5. Track price/media/status lifecycle events separately from identity merges.

## Acceptance
- Duplicate precision is measured on a labeled Bulgarian sample.
- Same property across portal/agency/group sources can be clustered.
- Ambiguous merges are operator-reviewable.
