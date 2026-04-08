# Development Setup

This project targets Python 3.12+, PostgreSQL/PostGIS, Redis, MinIO, Temporal, and a future Next.js frontend.

## Current Stage

The environment scaffold exists, but the API server, worker, scheduler, and frontend app are not implemented yet.

## Local Containers

Start infrastructure:

```bash
make dev-up
```

Stop infrastructure:

```bash
make dev-down
```

Tail logs:

```bash
make dev-logs
```

## Python

The project is pinned to Python 3.12 in `.python-version` and the Dockerfile.

Current local machine check during setup showed `python3 --version` as `3.9.6`, so use Docker, pyenv, or uv to avoid version drift when adding FastAPI, SQLAlchemy, Temporal, and parser dependencies.

## Database

The local PostgreSQL URL is (psycopg3):

```text
postgresql+psycopg://bgrealestate:bgrealestate@localhost:5432/bgrealestate
```

Initialize the database via migrations:

```bash
DATABASE_URL=postgresql+psycopg://bgrealestate:bgrealestate@localhost:5432/bgrealestate make db-init
```

Alembic migrations are the next required implementation step; do not rely on raw SQL execution for long-term schema evolution.

## Frontend

`package.json` declares the intended frontend stack, but the `web/` app has not been generated yet.

Do not run `npm install` or create a lockfile until the frontend implementation phase begins.

For Stage 1 only, `make run-frontend` serves a static development shell from `web/index.html`. Replace it with `npm run dev` after the Next.js app is created.

## Development Entrypoints

These commands are intentionally lightweight until FastAPI, Temporal, and Next.js are implemented:

```bash
make run-api        # stdlib status API on http://127.0.0.1:8000
make run-worker     # placeholder worker heartbeat
make run-scheduler  # placeholder scheduler summary
make run-frontend   # static frontend shell on http://127.0.0.1:3000
make validate       # JSON, Office package, and unit-test validation
```

The placeholder API exposes:

```text
GET /health
GET /sources
GET /status
```

Do not treat these as production APIs; they only make the development environment runnable while the real backend stages are built.
