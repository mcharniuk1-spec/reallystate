# Development Setup

This project targets Python 3.12+, PostgreSQL/PostGIS, Redis, MinIO, Temporal, and Next.js at the repo root.

For **Docker install**, service ports, **media on disk vs MinIO**, and **SQL helper scripts**, see [`docker-and-database.md`](docker-and-database.md).

## Current Stage

Core scaffold, Alembic migrations (initial schema from `sql/schema.sql`), Docker Compose stack, and a Next.js app shell are present; connectors and full API surface evolve per `PLAN.md`.

## Local Containers

Start infrastructure:

```bash
make dev-up
make dev-ready   # optional: block until Postgres accepts connections
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

```bash
make doctor     # which interpreter Make uses, 3.12+ check, ruff/mypy presence
make install    # editable install + dev tools; fails fast if Python is below 3.12
make test-docker # build Python 3.12 image and run the full unit test suite (needs Docker)
```

## Database

The local PostgreSQL URL is (psycopg3):

```text
postgresql+psycopg://bgrealestate:bgrealestate@localhost:5432/bgrealestate
```

Initialize the database via migrations (requires `DATABASE_URL` in the environment, e.g. from `.env`):

```bash
cp .env.example .env   # once
make dev-up && make dev-ready
make db-init
```

Schema evolution is via Alembic; `sql/schema.sql` is the source of truth loaded by the initial migration.

Interactive SQL:

```bash
make db-shell
```

## Frontend

Next.js lives at the repository root (`package.json`, `app/`). After `npm install`:

```bash
npm run dev
```

`make run-frontend` may still serve a static fallback if present; prefer `npm run dev` for the app shell.

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
