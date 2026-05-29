.PHONY: doctor install install-scrape-agents dev-up dev-down dev-ready dev-logs db-shell db-init migrate backup-db restore-db verify-db-counts bd18-db-smoke-import test test-docker golden-path lint typecheck validate codex-hooks codex-hooks-json docs-refresh run-api run-api-public run-worker run-scheduler run-frontend run-frontend-public run-frontend-build run-frontend-prod frontend-typecheck frontend-lint run-frontend-static export-docs source-report status-report linear-export architecture-doc dashboard-doc operational-dashboard-doc connector-fixtures list-sources list-skills ingest-fixture ingest-fixture-dry sync-registry sync-social-registry export-tier4-data seed-social-fixtures export-source-stats tier4-plan scraping-inventory tier12-metrics property-link-search property-link-search-fixture download-images import-scraped scrape-bcpea scrape-validate-manifest scrape-sync-sections scrape-sync-sections-dry scrape-threshold-summary scrape-queue-status scrape-control-worker-once scrape-runner-once scrape-runner-pause scrape-runner-unpause scrape-generate-varna-manifest scrape-varna-full scrape-all-full action1-matrix-snapshot action1-telegram-report action1-checkpoint-notify action1-running-report action1-openclaw-continue action1-openclaw-main-resume action1-scrape-full-uncapped action1-scrape-full-uncapped-detached action1-telegram-watch action1-telegram-watch-detached action1-telegram-ops-rehydrate action1-openclaw-report-monitor openclaw-preflight action1-reporter-status action1-reporter-on action1-reporter-off action1-reporter-stop

# Prefer 3.13/3.12 when unset so install/lint match pyproject.toml requires-python >=3.12
PYENV_PYTHON := $(shell ls "$$HOME"/.pyenv/versions/3.13*/bin/python3.13 "$$HOME"/.pyenv/versions/3.12*/bin/python3.12 2>/dev/null | sed -n '1p')
PYTHON ?= $(or $(PYENV_PYTHON),$(shell command -v python3.13 2>/dev/null || command -v python3.12 2>/dev/null || command -v python3))
PYTHONPATH ?= src
SOURCE ?= homes_bg

doctor:
	@echo "PYTHON selected by Make: $(PYTHON)"
	@$(PYTHON) -V
	@$(PYTHON) -c "import sys; v=sys.version_info; print('pyproject requires-python: OK (>=3.12)' if v >= (3, 12) else 'pyproject requires-python: NO — need 3.12+; try: brew install python@3.12 or pyenv (see .python-version), then make install PYTHON=python3.12')"
	@$(PYTHON) -c "import ruff" 2>/dev/null && echo "ruff: installed" || echo "ruff: missing — run make install (after Python 3.12+)"
	@$(PYTHON) -c "import mypy" 2>/dev/null && echo "mypy: installed" || echo "mypy: missing — run make install (after Python 3.12+)"
	@$(PYTHON) -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)" 2>/dev/null || echo "Tip: make test-docker — run the test suite in Python 3.12 via Docker (no host upgrade required)."

test-docker:
	@command -v docker >/dev/null 2>&1 || { echo >&2 "docker is required for make test-docker"; exit 1; }
	docker build -t bgrealestate:test .
	docker run --rm bgrealestate:test

install:
	@$(PYTHON) -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)" || \
		{ echo >&2 "bgrealestate requires Python 3.12+. Current: $$($(PYTHON) -V). Install python3.12+ (e.g. brew install python@3.12), set PYTHON=python3.12, or use: make test-docker"; exit 1; }
	$(PYTHON) -m pip install -e ".[dev]"

install-scrape-agents:
	@$(PYTHON) -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)" || \
		{ echo >&2 "bgrealestate requires Python 3.12+. Current: $$($(PYTHON) -V). Install python3.12+ (e.g. brew install python@3.12), set PYTHON=python3.12, or use: make test-docker"; exit 1; }
	$(PYTHON) -m pip install -e ".[dev,scrape-agents]"
	@echo "Installed scrape-agent extras. If browser automation is needed next, run: $(PYTHON) -m playwright install chromium"

dev-up:
	docker compose up -d postgres redis minio temporal temporal-ui

dev-ready:
	@command -v docker >/dev/null 2>&1 || { echo >&2 "docker is required"; exit 1; }
	@echo "Waiting for Postgres (bgrealestate)..."
	@until docker compose exec -T postgres pg_isready -U bgrealestate -d bgrealestate >/dev/null 2>&1; do sleep 1; done
	@echo "Postgres is ready."

dev-down:
	docker compose down

db-shell:
	docker compose exec postgres psql -U bgrealestate -d bgrealestate

dev-logs:
	docker compose logs -f --tail=100

db-init:
	@if [ -z "$$DATABASE_URL" ]; then \
		echo "DATABASE_URL is not set. Tip: cp .env.example .env and export DATABASE_URL, then run 'make dev-up'."; \
		exit 1; \
	fi
	@echo "Applying migrations to $$DATABASE_URL"
	$(PYTHON) -m alembic -c alembic.ini upgrade head

migrate:
	$(PYTHON) -m alembic -c alembic.ini upgrade head

backup-db:
	@if [ -z "$$DATABASE_URL" ]; then echo "DATABASE_URL is required"; exit 1; fi
	@mkdir -p /tmp/bgrealestate-backups
	pg_dump -Fc --no-owner --no-acl "$$DATABASE_URL" -f "$${DB_DUMP:-/tmp/bgrealestate-backups/bgrealestate_full_$$(date +%Y%m%d_%H%M%S).dump}"
	@shasum -a 256 "$${DB_DUMP:-$$(ls -t /tmp/bgrealestate-backups/bgrealestate_full_*.dump | sed -n '1p')}" > "$${DB_DUMP:-$$(ls -t /tmp/bgrealestate-backups/bgrealestate_full_*.dump | sed -n '1p')}.sha256"

restore-db:
	@if [ -z "$$REMOTE_DATABASE_URL" ]; then echo "REMOTE_DATABASE_URL is required"; exit 1; fi
	@if [ -z "$$DB_DUMP" ]; then echo "DB_DUMP=/path/to/file.dump is required"; exit 1; fi
	pg_restore --clean --if-exists --no-owner --no-acl -d "$$REMOTE_DATABASE_URL" "$$DB_DUMP"

verify-db-counts:
	@if [ -z "$$DATABASE_URL" ]; then echo "DATABASE_URL is required"; exit 1; fi
	@for table in source_registry source_endpoint crawl_run crawl_item canonical_listing source_publication_qa_review status_history entity_resolution_candidate entity_resolution_review_event property_entity property_offer media_asset listing_media media_description availability_calendar availability_slot availability_observation viewing_inquiry_request external_chat_ref app_user saved_property saved_search saved_area owner_property_claim owner_property_permission property_edit_revision lead_thread lead_message; do \
		printf "%-28s " "$$table"; \
		psql "$$DATABASE_URL" -Atc "select count(*) from $$table;" 2>/dev/null || echo "missing_or_unavailable"; \
	done

bd18-db-smoke-import:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/bd18_db_smoke_import.py

test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s tests -v

lint:
	$(PYTHON) -m ruff check .

typecheck:
	$(PYTHON) -m mypy src tests

validate:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/validate_project.py

codex-hooks:
	$(PYTHON) scripts/codex_project_hooks.py

codex-hooks-json:
	$(PYTHON) scripts/codex_project_hooks.py --json

golden-path:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/golden_path_check.py

docs-refresh: export-docs
	@echo "docs refreshed (exports regenerated)"

run-api:
	@$(PYTHON) -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)" || \
		{ echo >&2 "run-api requires Python 3.12+. Current: $$($(PYTHON) -V). Install python3.12+ (e.g. brew install python@3.12) and run: make run-api PYTHON=python3.12"; exit 1; }
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate.dev_api

run-api-public:
	@$(PYTHON) -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)" || \
		{ echo >&2 "run-api-public requires Python 3.12+."; exit 1; }
	PYTHONPATH=$(PYTHONPATH) API_HOST=0.0.0.0 $(PYTHON) -m bgrealestate.dev_api

run-worker:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate.dev_worker

run-scheduler:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate.dev_scheduler

run-frontend:
	@command -v npm >/dev/null 2>&1 || { echo "npm is required for the Next.js UI. Install Node.js or use: make run-frontend-static"; exit 1; }
	npm install && npm run dev

run-frontend-public:
	@command -v npm >/dev/null 2>&1 || { echo "npm is required for the Next.js UI."; exit 1; }
	npm install && npm run dev:public

run-frontend-build:
	@command -v npm >/dev/null 2>&1 || { echo "npm is required"; exit 1; }
	npm install && npm run build

run-frontend-prod:
	@command -v npm >/dev/null 2>&1 || { echo "npm is required"; exit 1; }
	npm run build && npm start

frontend-typecheck:
	npx tsc --noEmit

frontend-lint:
	npx next lint

run-frontend-static:
	$(PYTHON) -m http.server 3000 --directory web

export-docs: export-matrices source-report status-report architecture-doc dashboard-doc
	@mkdir -p docs/exports
	@cp PLAN.md docs/exports/platform-mvp-plan.md
	@echo "Markdown exported to docs/exports/platform-mvp-plan.md. DOCX/PDF export requires Pandoc, Mermaid CLI, and LibreOffice in a later phase."

export-matrices:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate export-matrices --out-dir artifacts

source-report:
	$(PYTHON) scripts/generate_source_report.py

status-report:
	$(PYTHON) scripts/generate_status_doc.py

linear-export:
	$(PYTHON) scripts/generate_linear_import.py

architecture-doc:
	$(PYTHON) scripts/generate_architecture_guide.py

dashboard-doc:
	$(PYTHON) scripts/generate_data_quality_deep_review.py
	$(PYTHON) scripts/generate_progress_dashboard.py
	$(PYTHON) scripts/generate_website_inventory_analysis.py
	$(PYTHON) scripts/generate_source_item_photo_coverage.py
	$(PYTHON) scripts/generate_tier12_pattern_status.py
	$(PYTHON) scripts/generate_scrape_status_dashboard.py
	$(PYTHON) scripts/generate_operational_dashboards.py

operational-dashboard-doc:
	$(PYTHON) scripts/generate_data_quality_deep_review.py
	$(PYTHON) scripts/generate_operational_dashboards.py

investor-deck:
	$(PYTHON) scripts/generate_investor_presentation.py

connector-fixtures:
	@mkdir -p tests/fixtures/$(SOURCE)
	@echo "Created tests/fixtures/$(SOURCE). Add offline HTML/JSON fixtures and expected outputs before implementing the connector."

list-sources:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate list-sources

list-skills:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate list-skills

ingest-fixture:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate ingest-fixture $(SOURCE_NAME) $(FIXTURE_DIR) $(EXTRA_ARGS)

ingest-fixture-dry:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate ingest-fixture $(SOURCE_NAME) $(FIXTURE_DIR) --dry-run

sync-registry:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate sync-database

sync-social-registry:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate sync-social-database

export-tier4-data:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate export-tier4 --out-dir docs/exports

seed-social-fixtures:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate seed-social-fixtures --account-id acct_tier4_seed

export-source-stats:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/export_source_stats_xlsx.py

tier4-plan:
	$(PYTHON) scripts/generate_tier4_plan.py

scrape-bcpea:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate scrape-bcpea --pages 5 --perpage 36 --fetch-details --out-dir output/bcpea

scrape-bcpea-dry:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate scrape-bcpea --pages 2 --perpage 12 --dry-run

scraping-inventory:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/generate_scraping_inventory.py

tier12-metrics:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/generate_tier12_metrics_deep_dive.py

download-images:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate download-images $(EXTRA_ARGS)

import-scraped:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/import_scraped_listings.py $(EXTRA_ARGS)

property-link-search:
	@if [ -z "$(URL)" ]; then echo "URL is required. Usage: make property-link-search URL='https://...'"; exit 1; fi
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/property_link_comparable_search.py --url "$(URL)" --fetch-live $(EXTRA_ARGS)

property-link-search-fixture:
	@if [ -z "$(URL)" ] || [ -z "$(HTML_FILE)" ]; then echo "URL and HTML_FILE are required. Usage: make property-link-search-fixture URL='https://...' HTML_FILE=path/to/raw.html SOURCE='Address.bg'"; exit 1; fi
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/property_link_comparable_search.py --url "$(URL)" --html-file "$(HTML_FILE)" $(if $(SOURCE),--source "$(SOURCE)",) $(EXTRA_ARGS)

scrape-generate-varna-manifest:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate scrape-generate-varna-manifest

scrape-validate-manifest:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate scrape-validate-manifest

scrape-sync-sections-dry:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate scrape-sync-sections --dry-run

scrape-sync-sections:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate scrape-sync-sections

scrape-threshold-summary:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate scrape-threshold-summary

scrape-queue-status:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate scrape-queue-status

scrape-control-worker-once:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate scrape-control-worker-once

scrape-runner-once:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate scrape-runner-once

scrape-runner-pause:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate scrape-set-runner-pause --paused true --note "Paused by operator"

scrape-runner-unpause:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate scrape-set-runner-pause --paused false --note "Unpaused by operator"

scrape-varna-full:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate scrape-varna-full $(EXTRA_ARGS)

scrape-all-full:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate scrape-all-full $(EXTRA_ARGS)

action1-matrix-snapshot:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/action1_scrape_matrix_snapshot.py

action1-telegram-report:
	$(PYTHON) scripts/action1_full_telegram_report.py --compact

action1-checkpoint-notify:
	$(PYTHON) scripts/action1_checkpoint_notify.py $(EXTRA_ARGS)

action1-running-report:
	$(PYTHON) scripts/action1_full_telegram_report.py --running-line

action1-openclaw-continue:
	./scripts/action1_openclaw_continue.sh

action1-openclaw-main-resume:
	./scripts/action1_openclaw_main_resume.sh

# Action1: seven sources, no per-source full-gallery cap (0 = until stall). Requires network; log under data/runs/.
action1-scrape-full-uncapped:
	./scripts/action1_scrape_full_uncapped.sh

# Detached runner to avoid interactive SIGTERM; writes pid + nohup log under data/runs/.
action1-scrape-full-uncapped-detached:
	./scripts/action1_scrape_full_uncapped_detached.sh

# Loop (300s): OpenClaw Telegram running-line report while Action1 scrape runs. Override ACTION1_TG_INTERVAL_SEC.
action1-telegram-watch:
	./scripts/action1_telegram_watch.sh

# Detached runner to keep Telegram loop alive; writes pid + nohup log under data/runs/.
action1-telegram-watch-detached:
	./scripts/action1_telegram_watch_detached.sh

# Reliable Telegram context reset: message send + verbatim RUNNING line (avoids long agent --deliver hangs).
action1-telegram-ops-rehydrate:
	bash ./scripts/action1_telegram_ops_rehydrate.sh

# Explicit TASKS/JOURNEY/run-log snapshot for OpenClaw (append full run to data/runs/openclaw_preflight.log).
# Optional: FOCUS=telegram PROBE=1 make openclaw-preflight
openclaw-preflight:
	bash ./scripts/openclaw_context_preflight.sh

# OpenClaw send + JSON parse + timeout; exits after STOP_AFTER_SUCCESS_STREAK consecutive OK sends (default 5). Logs data/runs/action1_report_monitor.log
action1-openclaw-report-monitor:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/action1_openclaw_report_monitor.py

# Reporter control (prevents “texts even when off” via enabled-file gating + pid kills).
action1-reporter-status:
	bash ./scripts/action1_reporter_control.sh status

action1-reporter-on:
	bash ./scripts/action1_reporter_control.sh start

action1-reporter-off:
	bash ./scripts/action1_reporter_control.sh disable

action1-reporter-stop:
	bash ./scripts/action1_reporter_control.sh stop
