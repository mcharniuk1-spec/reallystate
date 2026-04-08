---
name: real-estate-source-registry
description: Use when adding, reviewing, or enforcing Bulgaria real estate source inventory, source tiers, access modes, legal modes, MVP phase, and source matrix exports.
---

# real-estate-source-registry

Use this skill when adding, reviewing, or enforcing real estate market sources.

## Read First
- `data/source_registry.json`
- `deep-research-report.md`
- `artifacts/source-matrix.md`
- `artifacts/legal-risk-matrix.md`

## Workflow
1. Confirm the source already exists in `data/source_registry.json`; if not, add it with tier, family, owner group, access mode, risk mode, legal mode, MVP phase, publish capability, and dedupe cluster.
2. Preserve the tiering strategy: tier 1 first, tier 2 after parser gates, tier 3 partner/vendor/official routes, tier 4 lead overlays only.
3. Use `legal_mode` to block unsafe workflows before any connector or publishing adapter is implemented.
4. Regenerate matrices after registry changes.

## Acceptance
- Every source named in the research docs appears in the registry.
- High-risk/private/partner-only sources cannot be treated as normal public crawls.
- Tests loading the registry pass.
