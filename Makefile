.PHONY: install dev-up dev-down dev-logs db-init migrate test lint typecheck validate run-api run-worker run-scheduler run-frontend export-docs source-report status-report connector-fixtures list-sources

PYTHON ?= python3
PYTHONPATH ?= src
SOURCE ?= homes_bg

install:
	$(PYTHON) -m pip install -e . || true

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

run-api:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate.dev_api

run-worker:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate.dev_worker

run-scheduler:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate.dev_scheduler

run-frontend:
	$(PYTHON) -m http.server 3000 --directory web

export-docs: export-matrices source-report status-report
	@mkdir -p docs/exports
	@cp PLAN.md docs/exports/platform-mvp-plan.md
	@echo "Markdown exported to docs/exports/platform-mvp-plan.md. DOCX/PDF export requires Pandoc, Mermaid CLI, and LibreOffice in a later phase."

export-matrices:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate export-matrices --out-dir artifacts

source-report:
	$(PYTHON) scripts/generate_source_report.py

status-report:
	$(PYTHON) scripts/generate_status_doc.py

connector-fixtures:
	@mkdir -p tests/fixtures/$(SOURCE)
	@echo "Created tests/fixtures/$(SOURCE). Add offline HTML/JSON fixtures and expected outputs before implementing the connector."

list-sources:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bgrealestate list-sources
