# Linear Integration Guide

This document prepares the repository for Linear-based delivery management.

## Current State

- The repository now contains a prepared backlog structure for Linear.
- The current session does not expose live callable Linear tools, so this integration is repo-side and process-side first.
- Once the Linear app is connected in Cursor/Codex, this repo is ready to map implementation work to real issues and projects.

## Recommended Linear Structure

### Team

Use one team dedicated to the product, for example:

- `REA` or `RST`

### Project

Create one main project:

- `Bulgaria Real Estate MVP`

Optional subprojects:

- `Foundation and Infrastructure`
- `Ingestion and Connectors`
- `Map and Search MVP`
- `CRM and Publishing`

## Recommended Issue Groups

Use these as the top-level backlog slices:

1. Foundation and agent automation
2. Database and persistence
3. Runtime and compliance
4. Tier-1 connectors
5. Tier-2 and partner/vendor channels
6. Media and dedupe
7. Geospatial and building matching
8. Backend APIs
9. Frontend MVP
10. Reverse publishing
11. QA, monitoring, and launch

## Recommended Labels

- `foundation`
- `database`
- `connector`
- `geo`
- `map`
- `crm`
- `publishing`
- `frontend`
- `backend`
- `compliance`
- `qa`
- `blocked`
- `high-risk`
- `partner-only`

## Recommended Workflow States

- `Backlog`
- `Planned`
- `In Progress`
- `Blocked`
- `Review`
- `Done`

## Issue Naming Convention

Use concise action-first titles:

- `Set up Alembic migration runtime`
- `Add source registry repository roundtrip tests`
- `Implement Homes.bg discovery parser`
- `Add map viewport API`

## Branch And Commit Conventions

When an issue key exists:

- branch: `reallystate/<ISSUE-KEY>-short-slug`
- fallback branch for Codex work: `codex/<ISSUE-KEY>-short-slug`
- commit: `<ISSUE-KEY>: short summary`

Examples:

- `reallystate/REA-12-source-registry-repo-tests`
- `REA-12: add source registry repository tests`

## How To Use The Prepared Backlog CSV

The file [linear-import-roadmap.csv](/Users/getapple/Documents/Real%20Estate%20Bulg/docs/exports/linear-import-roadmap.csv) is prepared as an import-friendly backlog seed.

Suggested usage:

1. Import the CSV into Linear.
2. Map the imported rows to the `Bulgaria Real Estate MVP` project.
3. Add team-specific issue keys after import.
4. Keep the local roadmap and Linear issue status aligned.

## Local Fallback When Linear Tools Are Unavailable

If the current agent session cannot call Linear directly:

1. Treat `docs/project-status-roadmap.md` as the status source of truth.
2. Treat `docs/exports/linear-import-roadmap.csv` as the backlog seed.
3. Update `docs/reports/*.md` when a reconciliation or stage review is needed.

## Immediate Recommended Linear Epics

1. `Foundation and repo automation`
2. `Database and persistence`
3. `Tier-1 source ingestion`
4. `Property graph and dedupe`
5. `Map and search MVP`
6. `CRM inbox MVP`
7. `Publishing control plane`
8. `QA and launch readiness`
