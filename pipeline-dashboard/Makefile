# Makefile for SDLC Pipeline Dashboard
.PHONY: install install-dev test test-unit test-integration test-e2e lint security-scan run clean

PYTHON ?= python3
PIP ?= pip
APP_MODULE ?= app.main:app
HOST ?= 127.0.0.1
PORT ?= 8000

install:
	$(PIP) install -r requirements.txt

install-dev: install
	$(PIP) install -r requirements-dev.txt

test: test-unit test-integration

# Run unit tests (DAO, guardrails, providers, agents, orchestrator)
test-unit:
	$(PYTHON) -m pytest tests/unit -v --tb=short

# Run integration tests (API endpoints, SSE, full pipeline)
test-integration:
	$(PYTHON) -m pytest tests/integration -v --tb=short

# Run E2E tests with Playwright (requires dev server)
test-e2e:
	$(PYTHON) -m pytest tests/e2e -v --tb=short

# Run all tests
test-all: test-unit test-integration test-e2e

# Lint with ruff (if installed)
lint:
	-$(PYTHON) -m ruff check app/ tests/
	-$(PYTHON) -m ruff format --check app/ tests/

# Run security scans
security-scan:
	bash scripts/security-scan.sh

# Start development server with auto-reload
run:
	$(PYTHON) -m uvicorn $(APP_MODULE) --reload --host $(HOST) --port $(PORT)

# Start production server (no reload)
run-prod:
	$(PYTHON) -m uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT) --workers 1

# Clean generated artifacts
clean:
	rm -rf __pycache__ .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
