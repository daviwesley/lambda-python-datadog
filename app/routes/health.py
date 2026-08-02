from fastapi import APIRouter

from app.observability import logger

router = APIRouter(tags=["health"])


@router.get("/health", summary="Health check")
def health_check():
    logger.info("Health check called")
    return {"status": "ok"}
