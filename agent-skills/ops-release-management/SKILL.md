---
name: ops-release-management
description: Perform safe git staging, secret checks, commits, pushes, release notes, and rollback handoffs for the Bulgaria Real Estate MVP.
---

# Ops Release Management

## Purpose

Use this skill before staging, committing, pushing, releasing, or preparing deployment handoffs.

## Required Inputs

- `.gitignore`
- current `git status`
- `plan 13.05.md`
- relevant changed files
- release target branch

## Safe Staging Rules

Never stage:

- `.env`, `.env.local`, or secret-bearing config
- `.openclaw/` runtime state
- `.cursor/*.log`
- raw scrape HTML under `data/scraped/**/raw/`
- DB dumps, backups, SQLite files, zips, pid/lock/log files
- unreviewed large scraped corpus batches unless explicitly approved

Prefer staging:

- code
- migrations
- tests
- docs
- agent role docs and skills
- source registry and small reviewed config files

## Workflow

1. Clean the index without changing working files if unsafe entries are staged.
2. Stage only approved paths.
3. Review staged names.
4. Run a staged secret scan.
5. Run focused validation.
6. Commit with a concise message.
7. Push without force unless explicitly approved.
8. Report commit hash, branch, tests, and risks.

## Secret Scan Pattern

Search staged diff for:

```text
SECRET|PASSWORD|TOKEN|API_KEY|PRIVATE|DATABASE_URL|BEGIN .*PRIVATE KEY
```

Stop if real secrets are found.
