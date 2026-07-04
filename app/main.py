from ddtrace.contrib.asgi import TraceMiddleware
from fastapi import FastAPI

from app.routes.health import router as health_router
from app.routes.items import router as items_router

fastapi_app = FastAPI(
    title="lambda-python-datadog",
    description=(
        "FastAPI application running on AWS Lambda with Datadog observability."
    ),
    version="1.0.0",
)

fastapi_app.add_middleware(TraceMiddleware)

fastapi_app.include_router(health_router)
fastapi_app.include_router(items_router)

app = fastapi_app
