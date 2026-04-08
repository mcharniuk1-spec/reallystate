---
name: claude-opus-planner
description: Planning policy for Claude usage: prefer Opus for architecture and execution planning, then hand off implementation slices to faster models/agents. Use when defining roadmap, dependencies, and high-risk design choices.
---

# Claude Opus Planner

## Use When

- Creating or revising architecture plans.
- Defining multi-agent execution strategy.
- Making high-impact design decisions.

## Policy

1. Prefer Opus-level reasoning for planning and architecture reviews when Claude is the model path.
2. Convert the plan into concrete task slices for specialist agents.
3. Delegate implementation and repetitive coding to faster models/agents.
4. Re-escalate to Opus-level reasoning when blockers affect architecture or legal/compliance flow.

## Planning Output

```text
Goal:
Assumptions:
Parallel lanes:
Dependencies:
Acceptance gates:
Risk controls:
Next execution wave:
```

## Notes

- This is a policy skill; actual model availability depends on runtime tooling.
