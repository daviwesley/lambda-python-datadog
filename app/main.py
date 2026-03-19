from ddtrace.contrib.asgi import TraceMiddleware
from fastapi import FastAPI

from app.routes.health import router as health_router
from app.routes.items import router as items_router
from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging.formatters.datadog import (
    DatadogLogFormatter,
)

logger = Logger(logger_formatter=DatadogLogFormatter())

fastapi_app = FastAPI(
    title="lambda-python-datadog",
    description=(
        "FastAPI application running on AWS Lambda with Datadog "
        "observability."
    ),
    version="1.0.0",
)

# ------------------------------------------------------------------
# Datadog APM — adds a trace for every incoming HTTP request.
# The middleware picks up DD_SERVICE, DD_ENV, DD_VERSION automatically
# from the environment variables configured in serverless.yml.
# ------------------------------------------------------------------
fastapi_app.add_middleware(TraceMiddleware)

# ------------------------------------------------------------------
# Powertools correlation ID — appends the API Gateway request ID to
# every log record emitted during the request lifecycle so that logs
# can be correlated across services.
# ------------------------------------------------------------------


# @fastapi_app.middleware("http")
# async def powertools_correlation_id(request: Request, call_next):
#     correlation_id = (
#         request.headers.get("x-amzn-requestid")
#         or request.headers.get("x-request-id")
#     )
#     if correlation_id:
#         logger.set_correlation_id(correlation_id)
#     response = await call_next(request)
#     logger.set_correlation_id(None)
#     return response

# ------------------------------------------------------------------
# Routers
# ------------------------------------------------------------------
fastapi_app.include_router(health_router)
fastapi_app.include_router(items_router)

# ------------------------------------------------------------------
# Global exception handler — log unexpected errors so they show up in
# Datadog Logs and Powertools structured logs correlated with the trace.
# ------------------------------------------------------------------


# @fastapi_app.exception_handler(Exception)
# async def unhandled_exception_handler(request: Request, exc: Exception):
#     logger.exception("Unhandled exception", exc_info=exc)
#     return JSONResponse(status_code=500, content={"detail": "Internal server error"}) # noqa: E501
