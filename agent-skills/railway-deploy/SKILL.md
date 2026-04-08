---
name: railway-deploy
description: Deploy Python backend services to Railway with PostgreSQL, Redis, and worker processes. Use when setting up or managing Railway deployments for the backend stack.
---

# Railway Deployment

## Use When

- Deploying Python/FastAPI backend to Railway.
- Setting up PostgreSQL + PostGIS on Railway.
- Configuring worker processes and cron jobs.

## Setup

1. Install Railway CLI: `npm i -g @railway/cli`.
2. Login: `railway login`.
3. Create project: `railway init`.
4. Add PostgreSQL: `railway add --plugin postgresql`.
5. Deploy: `railway up`.

## Service Architecture

- **API service**: FastAPI with Gunicorn/Uvicorn.
- **Worker service**: Temporal worker or background job runner.
- **Database**: PostgreSQL with PostGIS extension.
- **Redis**: Session cache and job queue.

## Environment Variables

- `DATABASE_URL`: auto-provided by Railway PostgreSQL plugin.
- `REDIS_URL`: auto-provided by Railway Redis plugin.
- `PORT`: auto-provided; bind to `0.0.0.0:$PORT`.

## Health Checks

- Configure `/api/v1/ready` as the health check endpoint.
- Set restart policy for failed health checks.
