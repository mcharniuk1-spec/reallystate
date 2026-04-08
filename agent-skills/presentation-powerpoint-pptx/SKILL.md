---
name: presentation-powerpoint-pptx
description: Create Microsoft PowerPoint decks with python-pptx using stable, non-overlapping templates and investor-grade visual hierarchy. Use when users request .pptx outputs.
---

# PowerPoint Deck Generation (python-pptx)

## Use When

- User requests `.pptx` output.
- Deck must be editable in Microsoft PowerPoint.
- Deck should be import-ready for Google Slides.

## Build Pattern

1. Use 16:9 slide size.
2. Create reusable templates:
   - title + paragraph
   - paragraph + chart
   - 3-column metrics
   - roadmap/timeline
3. Place text and visuals in fixed bounding boxes.
4. Keep one paragraph block per slide as narrative context.
5. Export with deterministic filenames by date.

## Quality Rules

- Avoid text overflow and overlapping placeholders.
- Limit each slide to one primary chart.
- Use consistent fonts, spacing, and color tokens.
- Add source note lines for market numbers.

## Output

```text
PPTX path:
Slides generated:
Template types used:
Paragraph compliance (each slide):
```
