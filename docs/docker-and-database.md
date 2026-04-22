# Docker stack and database (local + media)

This document ties together **Docker Compose**, **PostgreSQL/PostGIS**, **MinIO (S3-compatible)**, **Redis**, **Temporal**, and how **listing images** are stored as **files** with **metadata in Postgres** — matching the architecture described for operators and API consumers.

## 1. Install Docker (host machine)

Docker is **not** bundled inside the Git repo. Install one of:

- [Docker Desktop](https://docs.docker.com/desktop/) (macOS / Windows) — includes Compose V2  
- [Docker Engine + Compose plugin](https://docs.docker.com/engine/install/) (Linux)

Verify:

```bash
docker --version
docker compose version
```

## 2. Start the project stack

From the repository root:

```bash
make dev-up      # postgres, redis, minio, temporal, temporal-ui
make dev-ready   # optional: wait until Postgres accepts connections
```

Services (see `docker-compose.yml`):

| Service       | Port(s)      | Role |
|---------------|-------------|------|
| `postgres`    | 5432        | PostGIS database `bgrealestate` |
| `redis`       | 6379        | Rate limits, locks, queues |
| `minio`       | 9000, 9001  | S3-compatible object storage (console on 9001) |
| `temporal`    | 7233        | Workflow engine (uses same Postgres DB) |
| `temporal-ui` | 8080        | Temporal Web UI |

Stop:

```bash
make dev-down
```

## 3. Configure environment and apply schema

1. Copy env template and set at least `DATABASE_URL` (values below match `docker-compose.yml` defaults):

   ```bash
   cp .env.example .env
   ```

2. Typical local URLs (already in `.env.example`):

   - `DATABASE_URL=postgresql+psycopg://bgrealestate:bgrealestate@localhost:5432/bgrealestate`
   - `REDIS_URL=redis://localhost:6379/0`
   - `S3_ENDPOINT_URL=http://localhost:9000` (+ bucket and MinIO root keys)

3. **Create tables** (Alembic runs the full `sql/schema.sql` on first migration):

   ```bash
   make db-init
   # or: make migrate
   ```

4. **Python API** (serves `/media/...`, listings, etc. when implemented):

   ```bash
   make run-api
   ```

5. **Next.js** uses `API_BASE_URL` / `lib/config.ts` to call the Python backend — keep media and listing JSON behind the **backend**, not duplicated in Next.

## 4. Where images live (files vs database)

| Layer | What is stored |
|-------|----------------|
| **Postgres** | Rows in `listing_media` (and optionally `media_asset` / `property_media` for the property graph): `url`, `storage_key`, `mime_type`, dimensions, `download_status`, link to `canonical_listing.reference_id`. |
| **Disk (default dev)** | Files under `MEDIA_STORAGE_PATH` (default `data/media/<reference_id>/...`) — see `src/bgrealestate/services/media.py`. |
| **MinIO / S3 (prod path)** | Same metadata in Postgres; **bytes** in a bucket (`S3_BUCKET`); `storage_key` points at the object key. |

Rule: **do not store large binaries in Postgres**; store **metadata + `storage_key`** and serve via **`GET /media/{media_id}`** or signed URLs from the backend.

## 5. SQL helpers

Reusable queries live under `sql/helpers/` (list all public tables, example joins for `listing_media`). Run with:

```bash
docker compose exec -T postgres psql -U bgrealestate -d bgrealestate < sql/helpers/01_list_public_tables.sql
```

Or from host if `psql` is installed:

```bash
psql "postgresql://bgrealestate:bgrealestate@localhost:5432/bgrealestate" -f sql/helpers/01_list_public_tables.sql
```

## 6. API / proxy architecture (unchanged contract)

- **Backend (FastAPI)** is the source of truth for **auth**, **listing JSON**, and **media** (`/media/proxy`, `/media/{id}`).  
- **Next.js** should call `API_BASE_URL` (see `lib/config.ts`); optional `/api/*` routes only forward to the backend.  
- **MinIO** holds raw captures and processed images when you wire S3 client code to completion; local `data/media` is fine for early ingest tests.

## 7. Optional: Postgres MCP / read-only user

`.env.example` includes `READONLY_DATABASE_URL` for IDE/MCP inspection. Creating `bgrealestate_readonly` is optional and not automated here — use your DBA flow if required.
