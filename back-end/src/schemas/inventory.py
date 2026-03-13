from pydantic import BaseModel


class AddInventoryRequest(BaseModel):
    """Body for POST /api/inventory/"""

    name: str
    quantity: int


class AddInventoryResponse(BaseModel):
    """Response for POST /api/inventory/ (202)."""

    id: int
    identifier: str


class InventoryItem(BaseModel):
    """Single inventory item (GET /api/inventory/<id>/)."""

    id: int
    identifier: str
    name: str | None = None
    quantity: int | None = None
    last_updated: str | None = None
