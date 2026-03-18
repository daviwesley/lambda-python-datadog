"""Shared AWS Lambda Powertools singletons.

Import Logger and Metrics from this module throughout the application to ensure
a single, consistently configured instance of each utility.

Tracing is handled exclusively by Datadog APM via ``ddtrace`` and the
``TraceMiddleware`` in ``app/main.py``.  Powertools Tracer / AWS X-Ray is not
used.

Environment variables (set in serverless.yml):
  POWERTOOLS_SERVICE_NAME      — service name tag on every log/metric
  POWERTOOLS_LOG_LEVEL         — log level (DEBUG / INFO / WARNING / ERROR)
  POWERTOOLS_METRICS_NAMESPACE — CloudWatch namespace for EMF metrics
"""

from aws_lambda_powertools import Logger, Metrics

# Structured JSON logger — injects Lambda context (request_id, cold_start,
# function_name, etc.) and optionally a correlation ID on every log record.
logger = Logger()

# CloudWatch EMF metrics — flushed to CloudWatch Logs as structured JSON;
# no Datadog Agent or custom forwarder required for this signal.
metrics = Metrics()
