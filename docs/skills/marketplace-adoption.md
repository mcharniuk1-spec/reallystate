# Claude Skills Marketplace Adoption (Project Policy)

Source reference: [Claude Skills Hub](https://claudeskills.info/)

## Goal

Adopt relevant marketplace skills for this project in a reproducible, repo-first way.

## Adoption rule

1. Discover candidate skills from marketplace collections.
2. Evaluate relevance to current roadmap and guardrails.
3. Mirror each accepted skill into `agent-skills/<skill-name>/SKILL.md`.
4. Register it in `docs/agent-skills-index.md`.
5. Use in agent runs and report under `Skills used`.

## Selected capability groups

- Architecture and planning:
  - software-architecture
  - subagent-driven-development
  - claude-opus-planner
- Research and data:
  - deep-research-workflow
  - postgres-analysis
- Web and dashboard:
  - wordpress-development
  - web-frontend-nextjs
  - dashboard-visual-ops
  - web-performance-accessibility

## Notes

- This policy keeps skill behavior deterministic and version-controlled across devices.
- Marketplace links are discovery sources; repository-local skills are execution sources.

## 2026-04-14 adoption update

- Installed successfully into local Codex skill storage:
  - `web-scraping`
- Evaluated as relevant from the public skills ecosystem:
  - `https://skills.sh/mindrally/skills/web-scraping`
  - `https://skills.sh/timelessco/recollect/postgresql-psql`
- Installer issues encountered:
  - `postgresql-psql` upstream path did not match installer assumptions.
  - image-compression installation attempts ran into local disk-space exhaustion before extraction completed.
- Project-local mirrors added instead:
  - `agent-skills/browser-scrape-ops/SKILL.md`
  - `agent-skills/postgres-ops-psql/SKILL.md`
  - `agent-skills/image-media-pipeline/SKILL.md`

This keeps the repo executable even when third-party marketplace packaging is inconsistent.

## 2026-04-20 scraping-market update

- Reviewed current official product and documentation signals for:
  - Playwright
  - Crawlee
  - Browserbase and Stagehand
  - Firecrawl
  - Zyte API
  - `curl_cffi`
- Decision:
  - keep the repo local-first and deterministic for bulk tier-1/2 work
  - treat managed platforms as escalation layers, not the default execution path
- Project-local skills added from this market scan:
  - `agent-skills/hybrid-scrape-stack/SKILL.md`
  - `agent-skills/managed-scrape-platforms/SKILL.md`
  - `agent-skills/universal-agent-scrape-setup/SKILL.md`
- Shared setup artifacts added:
  - `docs/exports/scraping-tools-market-radar-2026-04-20.md`
  - `docs/exports/universal-agent-scrape-setup-2026-04-20.md`

This keeps both Codex and Claude-agent execution aligned with the same current tool market and the same repo-controlled operating model.
