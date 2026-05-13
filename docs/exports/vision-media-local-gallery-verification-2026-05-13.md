# Vision Media: Local Gallery Verification Before Image Descriptions

Date: 2026-05-13

## Result

- Status: file-backed verification contract prepared.
- No image descriptions were generated.
- No remote images were fetched.

## Current Gallery Evidence

From `docs/exports/source-item-photo-coverage.json`:

- Sources with coverage rows: 27
- Saved listings: 30,334
- Items with remote photos: 30,331
- Items with local media: 30,014
- Full-gallery items: 27,528
- Total remote photo references: 604,488
- Total local photos: 611,131
- Stored/importer-state accepted candidates in this media export: 1,612

## Key Source Readiness Notes

| Source | Saved | Accepted in media export | Full-gallery items | Local-media items | Local photos | Remote refs | Image-description status |
|---|---:|---:|---:|---:|---:|---:|---|
| imot.bg | 9,937 | 1,535 | 9,728 | 9,753 | 102,046 | 102,804 | not generated |
| Homes.bg | 144 | 60 | 86 | 104 | 740 | 1,077 | not generated |
| LUXIMMO | 2,512 | 11 | 2,508 | 2,512 | 28,601 | 17,947 | not generated |
| property.bg | 3,094 | 5 | 3,091 | 3,094 | 138,764 | 138,662 | not generated |
| SUPRIMMO | 4,948 | 1 | 4,943 | 4,948 | 229,556 | 229,204 | not generated |
| Address.bg | 6,473 | 0 | 6,276 | 6,379 | 50,748 | 47,367 | not generated |
| BulgarianProperties | 2,289 | 0 | 18 | 2,289 | 55,247 | 61,878 | not generated |

## Verification Rule

Before any image description or semantic room/condition/equipment statement:

1. The row must be an accepted single-unit source publication.
2. Local image files must exist and be readable.
3. Full-gallery or partial-gallery status must be explicit.
4. Duplicate/variant media must be identified or carried as uncertainty.
5. The image report must state missing rooms/scenes and uncertainty.
6. Semantic image output must not overwrite source facts.

## Blockers

- Operator has not issued `Action0 now`.
- DA-02/DA-04 denominator certification and BD-18/BD-19 DB fields are not fully verified.
- Some media counters are stored/importer-state counters, not accepted-only DB-backed counts.

## Next Owner Prompt

`vision_media_agent`: verify local gallery paths/readability for accepted rows first; write image-description reports only after `Action0 now`, using local files only, and preserve uncertainty for every semantic conclusion.
