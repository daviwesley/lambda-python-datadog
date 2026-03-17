from fastapi import APIRouter

from app.powertools import logger, tracer

router = APIRouter(tags=["health"])


@router.get("/health", summary="Health check")
@tracer.capture_method
def health_check():
    logger.debug("Health check called")
    return {"status": "ok"}
