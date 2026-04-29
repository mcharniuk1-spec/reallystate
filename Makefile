.PHONY: doctor install install-scrape-agents dev-up dev-down dev-ready dev-logs db-shell db-init migrate test test-docker golden-path lint typecheck validate docs-refresh run-api run-api-public run-worker run-scheduler run-frontend run-frontend-public run-frontend-build run-frontend-prod frontend-typecheck frontend-lint run-frontend-static export-docs source-report status-report linear-export architecture-doc dashboard-doc connector-fixtures list-sources list-skills ingest-fixture ingest-fixture-dry sync-registry sync-social-registry export-tier4-data seed-social-fixtures export-source-stats tier4-plan scraping-inventory tier12-metrics download-images import-scraped scrape-bcpea scrape-validate-manifest scrape-sync-sections scrape-sync-sections-dry scrape-threshold-summary scrape-queue-status scrape-control-worker-once scrape-runner-once scrape-runner-pause scrape-runner-unpause scrape-generate-varna-manifest scrape-varna-full scrape-all-full action1-matrix-snapshot

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

test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s tests -v

lint:
	$(PYTHON) -m ruff check .

typecheck:
	$(PYTHON) -m mypy src tests

validate:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/validate_project.py

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
	$(PYTHON) scripts/generate_progress_dashboard.py
	$(PYTHON) scripts/generate_website_inventory_analysis.py
	$(PYTHON) scripts/generate_source_item_photo_coverage.py
	$(PYTHON) scripts/generate_tier12_pattern_status.py
	$(PYTHON) scripts/generate_scrape_status_dashboard.py

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
