---
name: agent-architecture-governance
description: Maintain multi-agent task ownership, handoffs, dependencies, verification loops, and prompt-to-slice conversion for the Bulgaria Real Estate MVP.
---

# Agent Architecture Governance

## Purpose

Use this skill when updating `docs/agents/TASKS.md`, agent role docs, handoff rules, execution cadence, or self-development architecture.

## Required Inputs

- `AGENTS.md`
- `docs/agents/SELF_DEVELOPMENT_ARCHITECTURE.md`
- `docs/agents/TASKS.md`
- relevant `docs/agents/*/JOURNEY.md`
- latest operator prompt
- project wiki memory/insights when available

## Workflow

1. Separate FACT, INTERPRETATION, HYPOTHESIS, and GAP.
2. Identify whether the latest prompt supersedes the current task.
3. Keep one clear owner and verifier per slice.
4. Preserve source-tier boundaries:
   - `scraper_1`: tier-1/2 websites
   - `scraper_sm`: tier-3 partner/vendor/official plus tier-4 consent/public overlays
   - `debugger`: acceptance gate
5. Keep the next 1-3 planned slices visible.
6. Add blockers as tasks, not chat notes.
7. Update role docs only when responsibility changes.

## Output

- Updated `TASKS.md` or role docs.
- Journey entry.
- Debugger handoff.

## Safety

Do not assign live scraping, DB writes, or private/social automation without legal/access gates and explicit operator scope.
