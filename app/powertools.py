"""Shared AWS Lambda Powertools singletons.

Import Logger, Tracer, and Metrics from this module throughout the application
to ensure a single, consistently configured instance of each utility.

Environment variables (set in serverless.yml):
  POWERTOOLS_SERVICE_NAME   — service name tag on every log/trace/metric
  POWERTOOLS_LOG_LEVEL      — log level (DEBUG / INFO / WARNING / ERROR)
  POWERTOOLS_METRICS_NAMESPACE — CloudWatch namespace for EMF metrics
"""

from aws_lambda_powertools import Logger, Metrics, Tracer

# Structured JSON logger — injects Lambda context (request_id, cold_start,
# function_name, etc.) and optionally a correlation ID on every log record.
logger = Logger()

# X-Ray tracer — patches supported AWS SDK clients automatically.
# Works side-by-side with Datadog APM (ddtrace).
tracer = Tracer()

# CloudWatch EMF metrics — flushed to CloudWatch Logs as structured JSON;
# no Datadog Agent or custom forwarder required for this signal.
metrics = Metrics()
