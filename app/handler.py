"""AWS Lambda entry-point.

Mangum translates API Gateway / ALB / Function URL events into ASGI-compatible
requests so that FastAPI can handle them without modification.

The ``datadog_lambda_wrapper`` decorator adds:
- Enhanced Lambda metrics (invocations, errors, duration)
- Distributed tracing correlation between X-Ray and Datadog APM
- Custom metrics via ``datadog_lambda.metric``
"""

import logging

from datadog_lambda.wrapper import datadog_lambda_wrapper
from mangum import Mangum

from app.main import app

logger = logging.getLogger(__name__)

# Mangum converts the Lambda event/context into an ASGI scope.
_asgi_handler = Mangum(app, lifespan="off")


@datadog_lambda_wrapper
def lambda_handler(event, context):
    logger.info("Received event: %s", event.get("requestContext", {}).get("http", {}))
    return _asgi_handler(event, context)
