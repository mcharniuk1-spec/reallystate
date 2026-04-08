---
name: prompt-engineering
description: Systematic prompt design techniques including Anthropic best practices, chain-of-thought, few-shot, and constraint-based prompting. Use when crafting agent instructions or improving output quality.
---

# Prompt Engineering

## Use When

- Writing or refining system prompts for agents.
- Improving output quality or reducing hallucination.
- Designing few-shot examples or chain-of-thought patterns.

## Core Techniques

1. **Be specific**: state the exact output format, constraints, and success criteria.
2. **Chain-of-thought**: ask the model to reason step by step before answering.
3. **Few-shot examples**: provide 2-3 concrete input/output pairs.
4. **Constraint framing**: state what NOT to do alongside what to do.
5. **Role assignment**: give the model a specific expert persona.
6. **Structured output**: request JSON, markdown tables, or templated formats.

## Anthropic Best Practices

- Use XML tags to separate instructions from content.
- Put examples inside `<example>` blocks.
- Use `<thinking>` for internal reasoning that should not appear in output.
- Prefer direct instructions over indirect hints.

## Quality Checks

- Does the prompt specify success criteria?
- Is the output format unambiguous?
- Are edge cases addressed?
- Can the prompt be shortened without losing intent?
