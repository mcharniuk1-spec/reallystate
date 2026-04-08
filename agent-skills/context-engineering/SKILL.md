---
name: context-engineering
description: Structure prompts and manage context windows effectively for AI agent interactions. Use when optimizing agent instructions, reducing token waste, or designing progressive disclosure patterns.
---

# Context Engineering

## Use When

- Designing agent instructions or system prompts.
- Managing large context windows efficiently.
- Structuring progressive disclosure for multi-step tasks.

## Principles

1. **Budget awareness**: every token competes for attention. Prioritize high-signal context.
2. **Progressive disclosure**: put essentials first, details in linked files.
3. **Attention mechanics**: recent and early context gets higher weight; bury low-priority items in the middle.
4. **Deduplication**: never repeat the same fact in multiple places; reference once.
5. **Structured output**: use headings, tables, and checklists to reduce ambiguity.

## Workflow

1. Identify the decision the agent must make.
2. List the minimum context required for that decision.
3. Order context by relevance (most critical first).
4. Move reference material to separate files with one-level links.
5. Validate: can the agent complete the task without re-reading unlinked files?

## Anti-Patterns

- Dumping entire files into prompts.
- Repeating instructions across multiple rules/skills.
- Using vague qualifiers ("try to", "maybe") instead of concrete constraints.
