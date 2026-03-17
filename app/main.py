import logging

from ddtrace.contrib.asgi import TraceMiddleware
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routes.health import router as health_router
from app.routes.items import router as items_router

# ---------------------------------------------------------------------------
# Structured logging — Lambda captures stdout as JSON when using Powertools or
# plain logging; ddtrace injects trace/span IDs automatically.
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] [dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    application = FastAPI(
        title="lambda-python-datadog",
        description="FastAPI application running on AWS Lambda with Datadog observability.",
        version="1.0.0",
    )

    # ------------------------------------------------------------------
    # Datadog APM — adds a trace for every incoming HTTP request.
    # The middleware picks up DD_SERVICE, DD_ENV, DD_VERSION automatically
    # from the environment variables configured in serverless.yml.
    # ------------------------------------------------------------------
    application.add_middleware(TraceMiddleware)

    # ------------------------------------------------------------------
    # Routers
    # ------------------------------------------------------------------
    application.include_router(health_router)
    application.include_router(items_router)

    # ------------------------------------------------------------------
    # Global exception handler — log unexpected errors so they show up in
    # Datadog Logs correlated with the active trace.
    # ------------------------------------------------------------------
    @application.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    return application


app = create_app()
