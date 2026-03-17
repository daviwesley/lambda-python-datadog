"""Shared AWS Lambda Powertools singletons.

Import Logger, Tracer, and Metrics from this module throughout the application
to ensure a single, consistently configured instance of each utility.

Environment variables (set in serverless.yml):
  POWERTOOLS_SERVICE_NAME        — service name tag on every log/trace/metric
  POWERTOOLS_LOG_LEVEL           — log level (DEBUG / INFO / WARNING / ERROR)
  POWERTOOLS_METRICS_NAMESPACE   — CloudWatch namespace for EMF metrics
  POWERTOOLS_TRACER_CAPTURE_RESPONSE — set false to skip response capture in X-Ray
  POWERTOOLS_TRACE_DISABLED      — set true to disable X-Ray tracing (local dev / tests)

Dual-tracer architecture
------------------------
This application uses TWO independent tracers that send to different backends:

  ddtrace TraceMiddleware  →  Datadog APM  (HTTP spans visible in Datadog APM UI)
  Powertools Tracer        →  AWS X-Ray    (Lambda + method subsegments in X-Ray console)

They coexist without conflict because they target different sinks.  To prevent
*double-patching* of AWS SDK / HTTP libraries (both ddtrace and aws-xray-sdk
would otherwise monkey-patch boto3, requests, httpx, etc.), the Powertools
Tracer is initialised with ``patch_modules=[]``.  Library-level instrumentation
is left entirely to ddtrace; Powertools Tracer only creates structural X-Ray
segments via ``@tracer.capture_lambda_handler`` and ``@tracer.capture_method``.
"""

from aws_lambda_powertools import Logger, Metrics, Tracer

# Structured JSON logger — injects Lambda context (request_id, cold_start,
# function_name, etc.) and optionally a correlation ID on every log record.
logger = Logger()

# X-Ray tracer — structural segments only; library auto-patching is disabled
# (patch_modules=[]) to avoid double-instrumentation with ddtrace, which already
# patches boto3, requests, httpx, etc. for Datadog APM.
tracer = Tracer(patch_modules=[])

# CloudWatch EMF metrics — flushed to CloudWatch Logs as structured JSON;
# no Datadog Agent or custom forwarder required for this signal.
metrics = Metrics()
