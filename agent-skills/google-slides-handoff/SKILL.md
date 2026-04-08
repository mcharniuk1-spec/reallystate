---
name: google-slides-handoff
description: Prepare presentation artifacts for Google Slides import and collaboration, including PPTX compatibility checks, source notes, and speaker-note structure. Use when users ask for Google Slides readiness.
---

# Google Slides Handoff

## Use When

- User requests Google Slides output or compatibility.
- Deck is generated in PPTX/PDF and needs collaborative handoff.

## Workflow

1. Generate canonical `.pptx` first (import source for Slides).
2. Ensure all fonts are standard and cross-platform safe.
3. Keep charts as embedded images to preserve layout on import.
4. Add concise speaker notes (or a companion markdown notes file).
5. Provide import steps:
   - Upload PPTX to Drive
   - Open with Google Slides
   - Verify layout and notes

## Compatibility Checks

- No custom non-standard fonts.
- No absolute-positioned text that can spill after import.
- No overlapping objects at 100% zoom.

## Output

```text
Google Slides import source:
Import checklist:
Speaker notes location:
Post-import QA points:
```
