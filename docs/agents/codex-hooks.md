# Codex Hook Pack

This repo uses a local hook runner for Codex/Cursor agents:

```bash
make codex-hooks
python3 scripts/codex_project_hooks.py --list
python3 scripts/codex_project_hooks.py --command "make scrape-all-full"
```

The hooks are version-controlled under `scripts/codex_project_hooks.py` and `codex-hooks/bgrealestate-hooks.json`. They do not edit `~/.codex/config.toml`.

## Hook Matrix

| Hook | Agent | Blocks |
|---|---|---|
| `planner.dependency_integrity` | `planner` | dependency-summary drift, Action0/Action1/Action2 order drift |
| `backend.accepted_only_import` | `backend_developer` | bad saving, unsafe canonical import, pending/LOST/grouped promotion |
| `data.denominator_truth` | `data_analyst` | bad denominator claims and dashboard count ambiguity |
| `scraper_1.scope_identity` | `scraper_1` | bad scraping, unsafe source expansion, lost source-publication identity |
| `scraper_sm.consent_routes` | `scraper_sm` | private social scraping and messenger consent violations |
| `ux.accepted_only_public_export` | `ux_ui_designer` | public display of pending QA, `LOST`, inactive, or grouped/development rows |
| `debugger.verifier_queue` | `debugger` | unverified handoff completion |
| `ops.release_hygiene` | `ops_release_manager` | secrets, raw dumps, runtime logs, broad staging |
| `infra.db_safety` | `infra_db_operator` | committed DB dumps and unverified DB migration/count claims |
| `market.claim_gate` | `market_intelligence_analyst` | unsupported market or 95% coverage claims |
| `analytics.privacy` | `user_analytics_agent` | raw text, PII, URLs, IPs, tokens, or third-party analytics payloads |
| `vision.action0_gate` | `vision_media_agent` | ungated Action0 image reports or remote image fetches during semantic reporting |
| `entity.no_auto_merge` | `entity_resolution_agent` | auto-merge of grouped/development/uncertain rows |
| `knowledge.wiki_closeout` | `knowledge_context_agent` | chat-only conclusions and missing wiki run/log closeout |
| `codex.inventory` | `knowledge_context_agent` | missing hook manifest/docs |

## Pre-Command Guard

Use the command guard before high-risk shell commands:

```bash
python3 scripts/codex_project_hooks.py --command "<command>"
```

It blocks:

- live scrape commands unless `CODEX_ALLOW_LIVE_SCRAPE=1`
- media backfill unless `CODEX_ALLOW_MEDIA_BACKFILL=1`
- Action0 execution unless `CODEX_ALLOW_ACTION0=1`
- Action2 expansion unless `CODEX_ALLOW_ACTION2=1`
- unsafe import include flags unless `CODEX_ALLOW_UNSAFE_IMPORT=1`
- broad `git add -A`, `git add .`, or sensitive staging unless explicitly overridden
- literal API keys, tokens, passwords, Bearer tokens, and DB URLs in commands

## Operator Rule

Override env vars are not normal workflow. Use them only after the operator or verifier explicitly approves the relevant gate.
