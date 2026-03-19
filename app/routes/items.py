from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.logging.formatters.datadog import (
    DatadogLogFormatter,
)

logger = Logger(logger_formatter=DatadogLogFormatter())

router = APIRouter(prefix="/items", tags=["items"])

# In-memory store — replace with a real database in production
_items: dict[int, dict] = {}
_counter: int = 0


class ItemCreate(BaseModel):
    name: str
    description: str | None = None
    price: float


class ItemResponse(ItemCreate):
    id: int


@router.get("", response_model=list[ItemResponse], summary="List all items")
def list_items():
    logger.info("Listing items", extra={"item_count": len(_items)})
    return [ItemResponse(id=item_id, **item) for item_id, item in _items.items()]


@router.get("/{item_id}", response_model=ItemResponse, summary="Get a single item")
def get_item(item_id: int):
    if item_id not in _items:
        logger.warning("Item not found", extra={"item_id": item_id})
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info("Fetching item", extra={"item_id": item_id})
    return ItemResponse(id=item_id, **_items[item_id])


@router.post("", response_model=ItemResponse, status_code=201, summary="Create an item")
def create_item(payload: ItemCreate):
    global _counter
    _counter += 1
    _items[_counter] = payload.model_dump()
    logger.info("Created item", extra={"item_id": _counter, "item_name": payload.name})
    return ItemResponse(id=_counter, **_items[_counter])


@router.delete("/{item_id}", status_code=204, summary="Delete an item")
def delete_item(item_id: int):
    if item_id not in _items:
        logger.warning("Item not found for deletion", extra={"item_id": item_id})
        raise HTTPException(status_code=404, detail="Item not found")
    del _items[item_id]
    logger.info("Deleted item", extra={"item_id": item_id})
