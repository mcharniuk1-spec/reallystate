# Database Migrations

Alembic owns the PostgreSQL/PostGIS schema from Stage 2 onward.

The first revision deliberately applies `sql/schema.sql` as the MVP schema blueprint so the hand-written schema and the migration entrypoint stay aligned during the early build. Later revisions should be smaller incremental migrations generated or written from SQLAlchemy models.

Run with:

```bash
DATABASE_URL=postgresql+psycopg://bgrealestate:bgrealestate@localhost:5432/bgrealestate make migrate
```

Notes:

- PostgreSQL must have PostGIS available.
- Local Python must include the project dependencies from `pyproject.toml`.
- In this workspace shell, Alembic/SQLAlchemy are not installed yet, so migration execution is expected to run from Docker, pyenv, uv, or a properly prepared Cursor environment.
