# Ops Release Manager Journey

## 2026-05-13 — OPS-01 safe git push gate started

- **Action**: Added release hygiene rules to `.gitignore`, created `ops-release-management` skill, and prepared safe staging policy for Plan 13.05. Existing unsafe staged entries were unstaged without changing working files.
- **Changed files**: `.gitignore`, `agent-skills/ops-release-management/SKILL.md`, `docs/agents/roles/ops_release_manager.md`, `docs/agents/TASKS.md`
- **Commands run**: `git restore --staged :/`
- **Tests run**: pending staged secret scan and push gate.
- **Status**: IN_PROGRESS
- **Review comments**: Commit/push must exclude `.env`, `.env.local`, `.openclaw/`, raw captures, data run logs, DB dumps, archives, and unreviewed large scraped corpus.

## 2026-05-13 — OPS-01 staged safe release set

- **Action**: Staged safe project files for Plan 13.05: code, docs, agent roles, skills, runbooks, OpenClaw handoffs, tests, scripts, migrations, and UI/backend files. Confirmed staged paths exclude `.env`, `.openclaw`, `data/scraped`, `data/runs`, DB dumps, zips, logs, and build info.
- **Changed files**: staged release set from `git diff --cached --name-only`.
- **Commands run**:
  - `git add ...`
  - `git diff --cached --name-only`
  - `git diff --cached -- . ':!data/scraped/**/raw/**' | rg -n 'SECRET|PASSWORD|TOKEN|API_KEY|PRIVATE|DATABASE_URL|BEGIN .*PRIVATE KEY' || true`
  - `git diff --cached --name-only | rg '(^\\.env|^\\.openclaw|^data/scraped|^data/runs|\\.dump$|\\.backup$|\\.sqlite3?$|\\.zip$|tsconfig\\.tsbuildinfo|data/scraper\\.log|\\.cursor/.*\\.log)' || true`
- **Tests run**: unsafe path scan passed with no matches; secret scan matched only placeholder/env-var references, not literal credentials.
- **Status**: DONE_AWAITING_VERIFY before commit/push.
- **Review comments**: `make dashboard-doc` and `make validate` were partial because `generate_source_item_photo_coverage.py` stalled; DA-03 is queued.
