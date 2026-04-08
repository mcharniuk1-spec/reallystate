---
name: multi-agent-patterns
description: Reference guide for multi-agent architecture patterns including supervisor/orchestrator, peer-to-peer, and hierarchical designs with context isolation. Use when designing or evolving agent coordination.
---

# Multi-Agent Architecture Patterns

## Use When

- Designing agent coordination for parallel execution.
- Choosing between orchestrator, peer, and hierarchical patterns.
- Implementing context isolation between specialist agents.

## Patterns

### Supervisor/Orchestrator
- One lead agent dispatches tasks and collects results.
- Specialists have no direct communication.
- Best for: clear task decomposition, audit trails.

### Peer-to-Peer / Swarm
- Agents communicate directly via shared state.
- No central coordinator.
- Best for: emergent collaboration, homogeneous tasks.

### Hierarchical
- Multiple layers: lead → team leads → specialists.
- Each layer has bounded context.
- Best for: large-scale projects with domain boundaries.

## Context Isolation Rules

1. Each agent reads only its assigned files and shared state.
2. Cross-agent communication goes through the task queue (TASKS.md).
3. No agent modifies another agent's journey log.
4. Verification is always by a different agent than the implementer.

## This Project's Pattern

- **Hierarchical with verification**: lead agent → 6 specialists → debugger verifier.
- Task queue: `docs/agents/TASKS.md`.
- Journey logs: `docs/agents/<agent>/JOURNEY.md`.
- Skills: `agent-skills/<name>/SKILL.md`.
