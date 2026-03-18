from fastapi import APIRouter

from app.powertools import logger

router = APIRouter(tags=["health"])


@router.get("/health", summary="Health check")
def health_check():
    logger.debug("Health check called")
    return {"status": "ok"}
