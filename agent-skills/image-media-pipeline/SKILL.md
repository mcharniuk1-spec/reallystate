---
name: image-media-pipeline
description: Use when downloading, validating, analyzing, compressing, and storing listing media plus metadata for the Bulgaria real estate pipeline.
---

# image-media-pipeline

Use this skill when a scraper or backend slice touches listing photos, media quality, media storage, or DB metadata.

## Read First
- `src/bgrealestate/services/media.py`
- `sql/schema.sql`
- `docs/exports/scraper-1-tier12-status.md`
- `docs/exports/tier12-source-analysis.md`

## Workflow
1. Keep the original remote URL, local storage key, content hash, MIME type, size, and dimensions.
2. Validate media before trusting it:
   - non-empty body
   - supported image MIME type
   - sane file size
   - decodable image when possible
3. Distinguish three stages:
   - raw fetch and cache
   - quality/readability analysis
   - derivative compression/resize policy
4. Prefer filesystem or object storage for binaries and store metadata in PostgreSQL. Do not bloat hot relational tables with large image blobs unless there is a deliberate archival requirement.
5. Record analysis fields that help downstream ranking and QA:
   - width and height
   - aspect ratio
   - duplicate hash
   - blur or unreadable flag
   - watermark or banner suspicion
   - source ordering
6. Compression policy:
   - keep the original where storage allows
   - generate web derivatives for serving
   - avoid repeated lossy recompression of the same asset
7. If CV analysis is added, make it additive and auditable. Keep the original metadata path intact.

## Output Format

```text
Objective:
Raw storage plan:
Metadata to persist:
Compression/derivative policy:
Quality checks:
DB impact:
Operational risks:
```

## Acceptance
- Original media remains traceable.
- Metadata is rich enough for QA, dedupe, and UI delivery.
- Compression is policy-driven and does not silently destroy evidence quality.
