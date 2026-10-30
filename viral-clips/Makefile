# AI Viral Clip Generator — developer entry points
PY ?= python3
VENV ?= ../../.venv
API_DIR := apps/api
WEB_DIR := apps/web
API_URL ?= http://127.0.0.1:8000

.PHONY: help setup api worker web test e2e sample long-sample fixture seed reset-db lint build clean

help:
	@grep -E '^[a-z-]+:.*?##' Makefile | sed 's/:.*##/\t—/'

setup: ## Create the venv, install API + web dependencies
	$(PY) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r $(API_DIR)/requirements.txt
	cd $(WEB_DIR) && npm install

api: ## Run the FastAPI service (http://127.0.0.1:8000, docs at /api/docs)
	cd $(API_DIR) && ../../$(VENV)/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

worker: ## Run a separate RQ worker (QUEUE_BACKEND=rq)
	cd $(API_DIR) && ../../$(VENV)/bin/rq worker -u $${REDIS_URL:-redis://127.0.0.1:6379/0} viral-clips

web: ## Run the Next.js app (http://127.0.0.1:3000)
	cd $(WEB_DIR) && npm run dev

test: ## Run the API test suite
	cd $(API_DIR) && ../../$(VENV)/bin/python -m pytest tests/ -q

e2e: ## Run Playwright end-to-end tests (needs `make api` + `make web` running)
	cd $(WEB_DIR) && npx playwright test

sample: ## Generate a 75s sample video
	$(VENV)/bin/python scripts/make_sample.py data/sample.mp4 75

long-sample: ## Generate a 4-minute sample video
	$(VENV)/bin/python scripts/make_sample.py data/sample-long.mp4 240

fixture: ## Build a synthetic transcript fixture (demo/test only)
	$(VENV)/bin/python scripts/make_fixture.py 240 data/fixtures/transcript.json

seed: ## Seed/reuse the demo account with a processed project
	$(VENV)/bin/python scripts/seed_demo.py $(API_URL)

reset-db: ## Delete the local SQLite database and generated media
	rm -rf data/viralclips.db data/viralclips.db-wal data/viralclips.db-shm data/media data/work

lint: ## Ruff + TypeScript check
	$(VENV)/bin/python -m ruff check $(API_DIR)/app $(API_DIR)/tests || true
	cd $(WEB_DIR) && npx tsc --noEmit

build: ## Production build of the web app
	cd $(WEB_DIR) && npm run build

clean: ## Remove build artefacts
	rm -rf $(WEB_DIR)/.next $(API_DIR)/.pytest_cache
