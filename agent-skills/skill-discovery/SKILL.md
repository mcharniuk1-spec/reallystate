---
name: skill-discovery
description: Use when an agent needs to discover, select, or create project skills before implementation.
---

# skill-discovery

Use this skill at the start of work to find existing skills and avoid duplicating instructions.

## Read First
- `docs/agent-skills-index.md`
- `agent-skills/*/SKILL.md`
- `AGENTS.md`

## Workflow
1. Run `python -m bgrealestate list-skills` (or `make list-skills`) to see available skills.
2. Pick the minimum set needed for the slice.
3. If a recurring workflow is missing, create `agent-skills/<new-skill>/SKILL.md`.
4. Update `docs/agent-skills-index.md` in the same change.

## Acceptance
- The chosen skill list is explicit in the agent closeout.
- New skills are committed with the code/docs they support.

