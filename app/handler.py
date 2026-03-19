"""AWS Lambda entry-point.

Mangum translates API Gateway / ALB / Function URL events into ASGI-compatible
requests so that FastAPI can handle them without modification.

Powertools decorators applied (outermost first):
  @logger.inject_lambda_context — enriches every log record with Lambda context

Tracing is handled by Datadog APM via the ``datadog_lambda_wrapper`` decorator
and the ``ddtrace`` ``TraceMiddleware`` in ``app/main.py``.

The ``datadog_lambda_wrapper`` decorator adds:
  - Enhanced Lambda metrics (invocations, errors, duration)
  - Distributed tracing via Datadog APM
  - Custom metrics via ``datadog_lambda.metric``
"""
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.logging.formatters.datadog import (
    DatadogLogFormatter,
)
from datadog_lambda.wrapper import datadog_lambda_wrapper
from mangum import Mangum

from app.main import fastapi_app

# Mangum converts the Lambda event/context into an ASGI scope.
_asgi_handler = Mangum(fastapi_app, lifespan="off")

logger = Logger(logger_formatter=DatadogLogFormatter())


@logger.inject_lambda_context(
    correlation_id_path=correlation_paths.API_GATEWAY_HTTP,
    clear_state=True
)
@datadog_lambda_wrapper
def lambda_handler(event, context):
    logger.info(
        "Received HTTP event",
        extra={"http": event.get("requestContext", {}).get("http", {})},
    )
    return _asgi_handler(event, context)
