# lambda-python-datadog

> FastAPI web application running on **AWS Lambda**, deployed with the [Serverless Framework](https://www.serverless.com/), and fully instrumented with **Datadog** for observability (APM traces, metrics, and logs).

---

## Architecture

```
API Gateway HTTP API
       │
       ▼
AWS Lambda  (Python 3.12)
  ├── app/handler.py       ← Lambda entry-point (Mangum + datadog_lambda_wrapper)
  ├── app/main.py          ← FastAPI application factory + Datadog TraceMiddleware
  └── app/routes/
        ├── health.py      ← GET /health
        └── items.py       ← CRUD /items
```

**Observability stack**

| Signal  | Tool |
|---------|------|
| Traces (APM) | `ddtrace` + Datadog Lambda Layer |
| Metrics (Datadog) | Enhanced Lambda Metrics via `datadog-lambda` |
| Metrics (CloudWatch) | Powertools `Metrics` via EMF (Embedded Metrics Format) |
| Logs | Powertools `Logger` (structured JSON) correlated to traces via `DD_LOGS_INJECTION=true` |

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.12 | `brew install python@3.12` on macOS |
| [uv](https://docs.astral.sh/uv/) | ≥ 0.4 | `brew install uv` on macOS |
| Node.js | ≥ 18 | `brew install node` on macOS |
| Serverless Framework | 3.x | installed via `npm install` |
| AWS CLI | any | only needed for deployment |
| Docker Desktop | any | only needed for deployment from macOS |

---

## Quick start

### 1. Clone and install dependencies

```bash
git clone https://github.com/daviwesley/lambda-python-datadog.git
cd lambda-python-datadog

# Creates .venv and installs runtime + dev dependencies via uv
make install

# Serverless Framework plugins
npm install
```

### 2. Run locally

```bash
make run
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)
```

`DD_TRACE_ENABLED` is set to `false` for local runs so ddtrace doesn't try to reach a Datadog Agent.

### 3. Run tests

```bash
make test
```

---

## Local development on macOS

Yes — the application runs fully on macOS without any AWS account or Datadog Agent.

### Prerequisites

Install the required tools with [Homebrew](https://brew.sh):

```bash
# Python 3.12
brew install python@3.12

# uv (fast Python package manager)
brew install uv
# alternatively, the official installer also works on macOS:
# curl -LsSf https://astral.sh/uv/install.sh | sh

# Node.js (for Serverless Framework and plugins)
brew install node
```

> **Docker Desktop** is only needed when you want to deploy from macOS.
> `serverless-python-requirements` uses `dockerizePip: non-linux` to build Linux-compatible
> native packages (e.g. `ddtrace`) inside a Docker container that matches the Lambda runtime.
> For `make run` and `make test` Docker is **not** required.

### Run the server locally

```bash
make install   # creates .venv and installs all dependencies
make run       # → http://localhost:8000
               # → http://localhost:8000/docs  (Swagger UI)
```

`DD_TRACE_ENABLED=false` is set automatically so ddtrace never tries to connect to a Datadog Agent. The API works identically to production — only the observability signals (traces, metrics) are suppressed.

### Run the tests

```bash
make test
```

All tests run in-process with no external services required.

### Deploy from macOS

Docker Desktop must be running before you deploy:

```bash
# Start Docker Desktop, then:
make deploy
```

`serverless-python-requirements` will spin up a `lambci/lambda:build-python3.12`
container automatically to produce Linux-compatible wheels.

---

### Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DD_API_KEY` | ✅ | Raw Datadog API key (set as a GitHub Actions Variable — see CI/CD section) |
| `DD_SITE` | ✅ | Datadog site, e.g. `datadoghq.com` or `datadoghq.eu` |
| `APP_VERSION` | optional | Semantic version tag injected as `DD_VERSION` (default: `1.0.0`) |

Export the variables for a manual deploy:

```bash
export DD_API_KEY="YOUR_DD_API_KEY"
export DD_SITE="datadoghq.com"
```

### Deploy to `dev`

```bash
make deploy
# or
npx serverless deploy --stage dev
```

### Deploy to `prod`

```bash
make deploy-prod
# or
npx serverless deploy --stage prod
```

### Remove a stack

```bash
make remove STAGE=dev
```

---

## CI/CD (GitHub Actions)

Two workflows are included in `.github/workflows/`:

| Workflow | File | Trigger |
|----------|------|---------|
| **CI** | `ci.yml` | Every push and pull request |
| **Deploy** | `deploy.yml` | Push to `main` → `dev`; tag `v*` → `prod` |

### Required GitHub Secrets

Navigate to **Settings → Secrets and variables → Actions → Secrets** in your repository and add:

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS IAM access key with Lambda / CloudFormation deploy permissions |
| `AWS_SECRET_ACCESS_KEY` | Corresponding AWS IAM secret key |

### Required GitHub Variables

Navigate to **Settings → Secrets and variables → Actions → Variables** and add:

| Variable | Description | Default |
|----------|-------------|---------|
| `DD_API_KEY` | Raw Datadog API key used at deploy time | _(none — must be set)_ |
| `DD_SITE` | Datadog ingest site (e.g. `datadoghq.com`) | _(none — must be set)_ |
| `AWS_REGION` | AWS region to deploy to | `us-east-1` |

### Deployment flow

```
push to main  ─────────────────► deploy to dev  (APP_VERSION = git SHA)
push tag v1.2.3  ──────────────► deploy to prod (APP_VERSION = v1.2.3)
```

The `dev` and `prod` jobs use GitHub [Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment), so you can add deployment protection rules (e.g. require a manual approval before prod).

### Minimum IAM permissions

The IAM user referenced by the AWS secrets needs the following permissions to deploy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "s3:*",
        "lambda:*",
        "apigateway:*",
        "iam:GetRole",
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:PutRolePolicy",
        "iam:DeleteRolePolicy",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "iam:PassRole",
        "logs:DescribeLogGroups",
        "logs:CreateLogGroup",
        "logs:DeleteLogGroup",
        "logs:PutRetentionPolicy"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## API reference

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/items` | List all items |
| `POST` | `/items` | Create an item |
| `GET` | `/items/{id}` | Get an item by ID |
| `DELETE` | `/items/{id}` | Delete an item |

Interactive docs are available at `/docs` (Swagger UI) and `/redoc`.

---

## Project structure

```
.
├── .github/
│   └── workflows/
│       ├── ci.yml              # Lint + test on every push/PR
│       └── deploy.yml          # Deploy to dev (main) / prod (v* tags)
├── app/
│   ├── __init__.py
│   ├── handler.py          # Lambda entry-point
│   ├── main.py             # FastAPI app factory
│   ├── powertools.py       # Shared Logger and Metrics singletons
│   └── routes/
│       ├── __init__.py
│       ├── health.py
│       └── items.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_main.py
├── .python-version         # Pins Python 3.12 for uv
├── pyproject.toml          # Single source of truth for all dependencies
├── uv.lock                 # Full dependency lock file (committed)
├── requirements.txt        # Auto-generated by `make export-requirements` for Lambda packaging
├── serverless.yml          # Serverless Framework IaC
├── package.json            # Serverless plugins
├── pytest.ini              # Test configuration
├── Makefile
└── README.md
```

> **`requirements.txt` is auto-generated** by `uv export` and should not be edited by hand.  
> Run `make export-requirements` after changing dependencies in `pyproject.toml`.

---

## AWS Lambda Powertools

[AWS Lambda Powertools for Python](https://docs.powertools.aws.dev/lambda/python/latest/) is integrated via `app/powertools.py`, which exposes two shared singletons imported throughout the application.

Tracing is handled exclusively by **Datadog APM** (`ddtrace` + `TraceMiddleware`). Powertools Tracer / AWS X-Ray is not used.

### Logger

Powertools `Logger` replaces stdlib logging and outputs structured JSON on every invocation:

```json
{
  "level": "INFO",
  "location": "list_items:app/routes/items.py:23",
  "message": "Listing items",
  "item_count": 3,
  "service": "lambda-python-datadog",
  "cold_start": true,
  "function_name": "lambda-python-datadog-dev-api",
  "correlation_id": "abc-123"
}
```

The `@logger.inject_lambda_context` decorator on the handler automatically appends `cold_start`, `function_name`, `function_arn`, and `request_id` to every log line.  
The FastAPI correlation-ID middleware in `app/main.py` forwards the API Gateway `x-amzn-requestid` header so all logs within a request share the same `correlation_id`.

### Environment variables (set in `serverless.yml`)

| Variable | Value | Purpose |
|----------|-------|---------|
| `POWERTOOLS_SERVICE_NAME` | `lambda-python-datadog` | Tags every log/metric |
| `POWERTOOLS_LOG_LEVEL` | `INFO` | Minimum log level |
| `POWERTOOLS_METRICS_NAMESPACE` | `LambdaPythonDatadog` | CloudWatch namespace |

---

## Datadog configuration details

The `serverless-plugin-datadog` plugin automatically:

1. Attaches the **Datadog Lambda Layer** (contains the Datadog Forwarder & ddtrace).
2. Sets all required environment variables (`DD_API_KEY`, `DD_SITE`, etc.).
3. Enables **Enhanced Lambda Metrics** (billed invocations, errors, cold starts, etc.).
4. Enables **Log correlation** — every log line is tagged with the active `trace_id` / `span_id`.

The `TraceMiddleware` in `app/main.py` creates a Datadog APM span for every HTTP request, visible in **APM > Services** in the Datadog UI.

### Unified Service Tagging

The following tags are set automatically from `serverless.yml`:

| Tag | Value |
|-----|-------|
| `service` | `lambda-python-datadog` |
| `env` | Serverless stage (`dev`, `prod`, …) |
| `version` | `APP_VERSION` env var |

---

## License

[MIT](LICENSE)
