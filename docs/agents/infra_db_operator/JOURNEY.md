# Infra DB Operator Journey

## 2026-05-13 — INFRA-01 server and DB migration readiness

- **Action**: Prepared the next server/DB migration step with a dedicated runbook and Make targets for logical backup, restore, and key table count verification.
- **Changed files**: `docs/runbooks/server-db-migration.md`, `agent-skills/infra-db-migration/SKILL.md`, `docs/agents/roles/infra_db_operator.md`, `Makefile`, `docs/agents/TASKS.md`
- **Commands run**: documentation and Makefile inspection.
- **Tests run**: pending `make -n backup-db restore-db verify-db-counts`.
- **Status**: DONE_AWAITING_VERIFY
- **Review comments**: Migration cannot execute until server SSH, local `DATABASE_URL`, and remote `REMOTE_DATABASE_URL` are provided.

## 2026-05-13 — INFRA-02 migration input readiness handoff

- **Action**: Prepared the execution inputs for the next migration gate without touching production DB, scrape DB, or scraped corpus data.
- **FACT**: `Makefile` has `backup-db`, `restore-db`, and `verify-db-counts`; `make -n backup-db restore-db verify-db-counts` confirms the shell sequence is logical dump -> checksum -> restore -> table counts.
- **FACT**: `backup-db` and `verify-db-counts` require libpq-compatible `DATABASE_URL`; `restore-db` requires `REMOTE_DATABASE_URL` and `DB_DUMP`.
- **FACT**: DB-backed Action1 verification is still blocked by missing DB URLs and `BD-18` canonical import/schema alignment.
- **INTERPRETATION**: INFRA-02 is not executable yet; it is an input-gated verification slice, not a migration slice.
- **HYPOTHESIS**: Using `postgresql://...` URLs, not SQLAlchemy `postgresql+psycopg://...` URLs, will avoid `pg_dump`/`psql` incompatibility during backup and count checks.
- **GAP**: Missing server provider/OS confirmation, SSH host/user/key, remote directory, remote clone/deploy access, local DB URL, remote DB URL, dump filename/path, media/object-storage decision, remote app env values, and latest DA/BD verification artifacts.
- **Confirmed command sequence**: local `DATABASE_URL` export -> `make backup-db` -> transfer dump/checksum/media by `ssh`/`rsync` -> remote `docker compose up -d postgres redis minio temporal temporal-ui` -> export `REMOTE_DATABASE_URL` + `DB_DUMP` -> `make restore-db` -> run `make verify-db-counts` locally and remotely via `DATABASE_URL` -> `diff -u` count files -> debugger/backend/data_analyst signoff before live scraping resumes.
- **Planner handoff**: keep `INFRA-02` blocked until `INFRA-01` is verified, `BD-18` proves DB-backed import/schema alignment, and operator provides all credentials/URLs.
- **Debugger handoff**: verify this was dry-run only; later verify no DB dump, credential, runtime log, or scraped raw corpus file is committed.
- **Changed files**: `docs/agents/infra_db_operator/JOURNEY.md`, `docs/agents/TASKS.md`
- **Commands run**: `sed`/`rg` inspections, `make -n backup-db restore-db verify-db-counts`
- **Tests run**: dry-run Make inspection only; no DB commands executed.
- **Status**: BLOCKED pending credentials, `BD-18`, and verifier signoff.
- **Review comments**: Do not run backup/restore/count verification until the operator explicitly provides DB URLs and server SSH details.

## 2026-05-13 — INFRA-02 BD-18 DB gate attempt

- **Action**: Checked whether DB verification can run after BD-18 table/smoke-script implementation.
- **FACT**: `DATABASE_URL` is not set in this environment.
- **Commands run**:
  - `if [ -n "$DATABASE_URL" ]; then echo DATABASE_URL_set; else echo DATABASE_URL_missing; fi`
  - `make verify-db-counts`
  - `make bd18-db-smoke-import`
- **Result**: both Make targets block immediately with `DATABASE_URL is required`.
- **Status**: BLOCKED.
- **Next step**: operator provides a libpq-compatible `DATABASE_URL`; infra then runs `make migrate`, `make bd18-db-smoke-import`, and `make verify-db-counts`.
