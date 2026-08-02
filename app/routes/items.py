from dataclasses import dataclass, field

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.observability import logger

router = APIRouter(prefix="/items", tags=["items"])


@dataclass
class ItemStore:
    items: dict[int, dict[str, object]] = field(default_factory=dict)
    counter: int = 0

    def get_item(self, item_id: int) -> dict[str, object] | None:
        return self.items.get(item_id)

    def create_item(self, payload: "ItemCreate") -> int:
        self.counter += 1
        self.items[self.counter] = payload.model_dump()
        return self.counter

    def delete_item(self, item_id: int) -> None:
        del self.items[item_id]

    def reset(self) -> None:
        self.items.clear()
        self.counter = 0


store = ItemStore()


class ItemCreate(BaseModel):
    name: str
    description: str | None = None
    price: float


class ItemResponse(ItemCreate):
    id: int


@router.get("", response_model=list[ItemResponse], summary="List all items")
def list_items():
    items = store.items
    logger.info("Listing items", extra={"item_count": len(items)})
    return [
        ItemResponse(id=item_id, **item) for item_id, item in items.items()
    ]


@router.get(
    "/{item_id}", response_model=ItemResponse, summary="Get a single item"
)
def get_item(item_id: int):
    item = store.get_item(item_id)
    if item is None:
        logger.warning("Item not found", extra={"item_id": item_id})
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info("Fetching item", extra={"item_id": item_id})
    return ItemResponse(id=item_id, **item)


@router.post(
    "", response_model=ItemResponse, status_code=201, summary="Create an item"
)
def create_item(payload: ItemCreate):
    item_id = store.create_item(payload)
    logger.info(
        "Created item", extra={"item_id": item_id, "item_name": payload.name}
    )
    return ItemResponse(id=item_id, **store.items[item_id])


@router.delete("/{item_id}", status_code=204, summary="Delete an item")
def delete_item(item_id: int):
    if store.get_item(item_id) is None:
        logger.warning(
            "Item not found for deletion", extra={"item_id": item_id}
        )
        raise HTTPException(status_code=404, detail="Item not found")
    store.delete_item(item_id)
    logger.info("Deleted item", extra={"item_id": item_id})
