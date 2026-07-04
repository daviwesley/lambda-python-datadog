from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.logging.formatters.datadog import (
    DatadogLogFormatter,
)
from datadog_lambda.wrapper import datadog_lambda_wrapper
from mangum import Mangum

from app.main import fastapi_app

_asgi_handler = Mangum(fastapi_app, lifespan="off")

logger = Logger(logger_formatter=DatadogLogFormatter())


@logger.inject_lambda_context(
    correlation_id_path=correlation_paths.API_GATEWAY_HTTP, clear_state=True
)
@datadog_lambda_wrapper
def lambda_handler(event, context):
    logger.info(
        "Received HTTP event",
        extra={"http": event.get("requestContext", {}).get("http", {})},
    )
    return _asgi_handler(event, context)
