---
name: docs-export
description: Use when creating or exporting Markdown, Mermaid diagrams, DOCX, PDF, source matrices, and portable handoff documentation.
---

# docs-export

Use this skill when creating or exporting Markdown, DOCX, PDF, or diagrams.

## Read First
- `PLAN.md`
- `platform-mvp-plan.md`
- `docs/diagrams/platform-architecture.mmd`
- `data/source_registry.json`

## Workflow
1. Keep Markdown preview-safe and portable.
2. Keep the Mermaid diagram in source form and render it for DOCX/PDF when tools exist.
3. Include source coverage, database structure, app structure, agent setup, roadmap, gates, and test plan.
4. Use Pandoc and LibreOffice headless for exports when available.

## Acceptance
- Markdown previews cleanly.
- DOCX/PDF include numbered plan, tables, and rendered block diagram.
