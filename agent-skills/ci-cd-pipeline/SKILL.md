---
name: ci-cd-pipeline
description: Design and maintain CI/CD pipelines for multi-agent projects with lint, typecheck, test, and deployment stages. Use when setting up or fixing CI workflows.
---

# CI/CD Pipeline

## Use When

- Setting up GitHub Actions or GitLab CI for the project.
- Adding new stages (lint, typecheck, test, deploy).
- Debugging CI failures.

## Standard Pipeline Stages

1. **Lint**: `make lint` (ruff check).
2. **Typecheck**: `make typecheck` (mypy).
3. **Test**: `make test` (unittest discover, no DB).
4. **Validate**: `make validate` (project structure checks).
5. **Golden path**: `make golden-path` (with DB service container).
6. **Deploy**: conditional on branch and all gates passing.

## Service Containers

- PostgreSQL + PostGIS for golden-path tests.
- Redis for queue-dependent tests.

## Rules

- Never skip lint or typecheck in CI.
- Tests must pass without external network access.
- Deploy only from main/production branches.
- Keep CI runtime under 5 minutes for fast feedback.
