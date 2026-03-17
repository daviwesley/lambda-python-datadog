"""AWS Lambda entry-point.

Mangum translates API Gateway / ALB / Function URL events into ASGI-compatible
requests so that FastAPI can handle them without modification.

Powertools decorators applied (outermost first):
  @metrics.log_metrics     — flushes CloudWatch EMF metrics after every invocation
  @tracer.capture_lambda_handler — creates an X-Ray subsegment for the handler
  @logger.inject_lambda_context  — enriches every log record with Lambda context

The ``datadog_lambda_wrapper`` decorator adds:
  - Enhanced Lambda metrics (invocations, errors, duration)
  - Distributed tracing correlation between X-Ray and Datadog APM
  - Custom metrics via ``datadog_lambda.metric``
"""

from datadog_lambda.wrapper import datadog_lambda_wrapper
from mangum import Mangum

from app.main import app
from app.powertools import logger, metrics, tracer

# Mangum converts the Lambda event/context into an ASGI scope.
_asgi_handler = Mangum(app, lifespan="off")


@metrics.log_metrics
@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=False)
@datadog_lambda_wrapper
def lambda_handler(event, context):
    logger.info(
        "Received HTTP event",
        extra={"http": event.get("requestContext", {}).get("http", {})},
    )
    return _asgi_handler(event, context)
