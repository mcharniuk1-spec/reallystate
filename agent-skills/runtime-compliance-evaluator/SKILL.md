---
name: runtime-compliance-evaluator
description: Use when implementing or updating runtime enforcement for legal_mode/risk_mode/access_mode gates across connectors and publishing.
---

# runtime-compliance-evaluator

Use this skill when adding any code path that can fetch, parse, store, or publish data so that it is blocked/allowed according to `data/source_registry.json` and derived `source_legal_rule`.

## Read First

- `AGENTS.md`
- `data/source_registry.json`
- `src/bgrealestate/connectors/legal.py`
- `sql/schema.sql`
- `PLAN.md` (guardrails + phase gates)

## Workflow

1. **Fail closed**:
   - unknown `legal_mode` => block
   - social/messenger families => block marketplace crawling
2. **Centralize checks**:
   - use a single helper (e.g. `assert_live_http_allowed(entry)`) for all connector live fetches
   - ensure publishing checks use channel capability + compliance flags
3. **Persist explainability**:
   - store “why blocked” as `reason` in `source_legal_rule` and surface it in logs/errors
4. **Test gates offline**:
   - unit tests must not call network
   - include at least one “blocked” fixture case using seeded `external_id` + HTML

## Acceptance

- A connector cannot perform a live fetch if `blocks_live_scrape` is true (directly or via derived rule).
- Social/private-messaging sources are never treated as crawl targets.
- Tests demonstrate both allowed and blocked behavior without network.
