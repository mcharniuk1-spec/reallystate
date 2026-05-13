# MCP And Skills Setup

Date: 2026-05-13

## Current Repo State

The repo already has Cursor MCP config in `.cursor/mcp.json`:

- `context7`: current library documentation.
- `playwright`: browser automation for local UI and source inspection.
- `postgres-readonly`: read-only schema/query inspection through `READONLY_DATABASE_URL`.

Do not put secrets into `.cursor/mcp.json`. Use environment variables.

## Recommended MCP Servers

| Server | Use | Safety Rule |
| --- | --- | --- |
| Context7 | Current docs for Next.js, FastAPI, SQLAlchemy, Alembic, MapLibre, Playwright. | Use for docs only; validate generated code locally. |
| Playwright MCP | Browser QA and source exploration. | Prefer local UI; do not use to bypass private/login/CAPTCHA gates. |
| Filesystem MCP | Optional file access in MCP clients. | Restrict to repo root only. |
| Git MCP | Optional repository inspection. | Write operations still go through `ops_release_manager`. |
| Postgres MCP | Schema/count inspection. | Use read-only connection string only. |
| Time MCP | Scheduled/report timestamp consistency. | Safe. |

References:

- Context7: `https://github.com/upstash/context7`
- Playwright MCP: `https://github.com/microsoft/playwright-mcp`
- MCP reference servers: `https://github.com/modelcontextprotocol/servers`

## Codex Setup Sketch

Add to Codex MCP config only after the operator approves local tool installation:

```toml
[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp"]

[mcp_servers.playwright]
command = "npx"
args = ["@playwright/mcp@latest"]

[mcp_servers.postgres_readonly]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-postgres", "${READONLY_DATABASE_URL}"]
```

## Required Environment

```bash
export READONLY_DATABASE_URL='postgresql://readonly_user:...@host:5432/bgrealestate'
```

Do not use the write-capable production database URL for MCP.

## Skill Installation Policy

Project skills must be version-controlled under `agent-skills/<name>/SKILL.md`.

Use these skills by role:

- `planner`: `agent-architecture-governance`, `software-architecture`, `subagent-driven-development`, `context-engineering`, `prompt-engineering`.
- `ops_release_manager`: `ops-release-management`, `qa-review-release`, `security-audit`, `ci-cd-pipeline`.
- `infra_db_operator`: `infra-db-migration`, `postgres-ops-psql`, `postgres-postgis-schema`, `railway-deploy`.
- `backend_developer`: `backend-data-engineering`, `postgres-postgis-schema`, `workflow-runtime`, `fullstack-coding`.
- `scraper_1`: `scraper-connector-builder`, `browser-scrape-ops`, `hybrid-scrape-stack`, `parser-fixture-qa`, `runtime-compliance-evaluator`.
- `scraper_sm`: `publishing-compliance`, `runtime-compliance-evaluator`, `deep-research-workflow`, `scraper-connector-builder`.
- `data_analyst`: `postgres-analysis`, `dashboard-visual-ops`, `test-generator`.
- `market_intelligence_analyst`: `market-intelligence`, `deep-research-workflow`.
- `user_analytics_agent`: `user-analytics-instrumentation`, `dashboard-visual-ops`, `web-performance-accessibility`.
- `vision_media_agent`: `image-media-pipeline`, `managed-scrape-platforms`.
- `entity_resolution_agent`: `dedupe-entity-resolution`, `postgres-analysis`.
- `ux_ui_designer`: `web-frontend-nextjs`, `frontend-pages`, `geo-map-3d`, `visual-3d-map`, `web-performance-accessibility`.
- `debugger`: `debugger-golden-path`, `qa-review-release`, `security-audit`, `test-generator`.
- `knowledge_context_agent`: `context-engineering`, `docs-export`, `skill-discovery`.

## Not Installed In This Run

No home-level MCP or global package install was performed in this session. The repo is prepared with docs and local skill files; actual MCP installation needs operator approval because it writes outside the repository and may download packages.
