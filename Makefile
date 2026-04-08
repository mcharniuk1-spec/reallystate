.PHONY: doctor install dev-up dev-down dev-logs db-init migrate test test-docker golden-path lint typecheck validate docs-refresh run-api run-worker run-scheduler run-frontend export-docs source-report status-report linear-export architecture-doc dashboard-doc connector-fixtures list-sources list-skills ingest-fixture ingest-fixture-dry sync-registry export-source-stats

# Prefer 3.13/3.12 when unset so install/lint match pyproject.toml requires-python >=3.12
PYTHON ?= $(shell command -v python3.13 2>/dev/null || command -v python3.12 2>/dev/null || command -v python3)
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

dev-up:
	docker compose up -d postgres redis minio temporal temporal-ui

dev-down:
	docker compose down

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
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate.dev_api

run-worker:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate.dev_worker

run-scheduler:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate.dev_scheduler

run-frontend:
	@command -v npm >/dev/null 2>&1 || { echo "npm is required for the Next.js UI. Install Node.js or use: make run-frontend-static"; exit 1; }
	npm install && npm run dev

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

export-source-stats:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/export_source_stats_xlsx.py
