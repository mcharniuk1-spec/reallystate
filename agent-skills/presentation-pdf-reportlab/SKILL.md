---
name: presentation-pdf-reportlab
description: Generate polished PDF slide decks with reportlab and matplotlib, including chart-safe layout regions and visual QA checks. Use when creating investor or strategy PDFs.
---

# Presentation PDF (ReportLab)

## Use When

- Producing final PDF investor decks.
- Converting strategy docs into presentation format.

## Workflow

1. Define slide grid: title area, paragraph area, visual area, footer/source area.
2. Render charts separately (PNG) and place in fixed zones.
3. Keep paragraph copy concise and readable; avoid dense bullets.
4. Add source/footer lines for factual slides.
5. Re-render and inspect each page for clipping and overlaps.

## Layout Guardrails

- Never stack chart + table + long paragraph on same slide.
- Minimum text size: 14 for body on slides.
- Maintain consistent top/bottom margins.
- Keep color semantics stable (green done, amber current, blue next, red blocked).

## Output

```text
PDF path:
Slide count:
Layout QA status:
Sources cited:
Known limitations:
```
