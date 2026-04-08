---
name: subagent-driven-development
description: Dispatches independent subagents for parallel task slices with explicit checkpoints, verifier handoffs, and merge-safe outputs. Use for multi-agent execution where tasks can run concurrently.
---

# Subagent-Driven Development

## Use When

- Running multiple specialist agents in parallel.
- Splitting a large feature into independent slices.
- Coordinating verifier checkpoints between agent outputs.

## Read First

- `docs/agents/TASKS.md`
- `docs/agents/README.md`
- `AGENTS.md`

## Workflow

1. Select one active slice per agent.
2. Verify dependency gates before dispatch.
3. Run independent slices in parallel.
4. Require each agent to append `JOURNEY.md`.
5. Route each completed slice to verifier.
6. Promote only `VERIFIED` slices to done.

## Dispatch Template

```text
Agent:
Slice ID:
Inputs:
Acceptance gate:
Expected outputs:
Verifier:
Depends on:
```

## Safety Rules

- Never bypass legal/risk/access gates for scraping.
- Never allow live-network dependency in fixture tests.
- Keep outputs merge-safe and incrementally reviewable.
