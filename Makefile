.PHONY: install lint test run export-requirements deploy deploy-prod remove

STAGE  ?= dev
REGION ?= us-east-1

# ---------------------------------------------------------------------------
# Setup — create venv and install all deps (runtime + dev)
# ---------------------------------------------------------------------------
install:
	uv sync

# ---------------------------------------------------------------------------
# Quality
# ---------------------------------------------------------------------------
lint:
	uv run ruff check app tests

test:
	uv run pytest tests/ -v

# ---------------------------------------------------------------------------
# Local development
# ---------------------------------------------------------------------------
run:
	DD_TRACE_ENABLED=false uv run uvicorn app.main:app --reload --port 8000

# ---------------------------------------------------------------------------
# Lambda packaging — regenerate requirements.txt consumed by
# serverless-python-requirements during deployment.
# Run this whenever pyproject.toml dependencies change.
# ---------------------------------------------------------------------------
export-requirements:
	uv export --no-dev --no-hashes --no-editable --output-file requirements.txt

# ---------------------------------------------------------------------------
# Deploy (Serverless Framework)
# ---------------------------------------------------------------------------
deploy: export-requirements
	npx serverless deploy --stage $(STAGE) --region $(REGION)

deploy-prod: export-requirements
	npx serverless deploy --stage prod --region $(REGION)

remove:
	npx serverless remove --stage $(STAGE) --region $(REGION)
