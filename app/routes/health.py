from fastapi import APIRouter

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.logging.formatters.datadog import (
    DatadogLogFormatter,
)

logger = Logger(logger_formatter=DatadogLogFormatter())

router = APIRouter(tags=["health"])


@router.get("/health", summary="Health check")
def health_check():
    logger.info("Health check called")
    return {"status": "ok"}
