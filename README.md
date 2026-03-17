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
| Traces  | `ddtrace` + Datadog Lambda Layer |
| Metrics | Enhanced Lambda Metrics via `datadog-lambda` |
| Logs    | Structured logs correlated to traces via `DD_LOGS_INJECTION=true` |

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.12 |
| Node.js | ≥ 18 |
| Serverless Framework | 3.x |
| AWS CLI | configured with deploy permissions |

---

## Quick start

### 1. Clone and install dependencies

```bash
git clone https://github.com/daviwesley/lambda-python-datadog.git
cd lambda-python-datadog

# Python (runtime + dev tools)
pip install -r requirements-dev.txt

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

## Deployment

### Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DD_API_KEY_SECRET_ARN` | ✅ | ARN of the AWS Secrets Manager secret that holds your Datadog API key |
| `DD_SITE` | ✅ | Datadog site, e.g. `datadoghq.com` or `datadoghq.eu` |
| `APP_VERSION` | optional | Semantic version tag injected as `DD_VERSION` (default: `1.0.0`) |

Store your Datadog API key in AWS Secrets Manager:

```bash
aws secretsmanager create-secret \
  --name /datadog/api-key \
  --secret-string "YOUR_DD_API_KEY"
```

Then export the ARN:

```bash
export DD_API_KEY_SECRET_ARN="arn:aws:secretsmanager:us-east-1:123456789012:secret:/datadog/api-key"
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
├── app/
│   ├── __init__.py
│   ├── handler.py          # Lambda entry-point
│   ├── main.py             # FastAPI app factory
│   └── routes/
│       ├── __init__.py
│       ├── health.py
│       └── items.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── serverless.yml          # Serverless Framework IaC
├── package.json            # Serverless plugins
├── requirements.txt        # Runtime dependencies
├── requirements-dev.txt    # Dev/test dependencies
├── Makefile
└── README.md
```

---

## Datadog configuration details

The `serverless-plugin-datadog` plugin automatically:

1. Attaches the **Datadog Lambda Layer** (contains the Datadog Forwarder & ddtrace).
2. Sets all required environment variables (`DD_API_KEY_SECRET_ARN`, `DD_SITE`, etc.).
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
