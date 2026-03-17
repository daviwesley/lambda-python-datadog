.PHONY: install install-dev lint test run deploy deploy-prod remove

PYTHON   ?= python3
PIP      ?= pip
STAGE    ?= dev
REGION   ?= us-east-1

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
install:
	$(PIP) install -r requirements.txt

install-dev:
	$(PIP) install -r requirements-dev.txt
	npm install --save-dev serverless-python-requirements serverless-plugin-datadog

# ---------------------------------------------------------------------------
# Quality
# ---------------------------------------------------------------------------
lint:
	$(PYTHON) -m ruff check app tests

test:
	$(PYTHON) -m pytest tests/ -v

# ---------------------------------------------------------------------------
# Local development
# ---------------------------------------------------------------------------
run:
	DD_TRACE_ENABLED=false $(PYTHON) -m uvicorn app.main:app --reload --port 8000

# ---------------------------------------------------------------------------
# Deploy (Serverless Framework)
# ---------------------------------------------------------------------------
deploy:
	npx serverless deploy --stage $(STAGE) --region $(REGION)

deploy-prod:
	npx serverless deploy --stage prod --region $(REGION)

remove:
	npx serverless remove --stage $(STAGE) --region $(REGION)
