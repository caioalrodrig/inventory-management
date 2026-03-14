import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AddInventoryRequest(BaseModel):
    """Body for POST /api/inventory/"""

    name: str
    quantity: int


class AddInventoryResponse(BaseModel):
    """Response for POST /api/inventory/ (202)."""

    id: uuid.UUID
    identifier: str


class InventoryItem(BaseModel):
    """Single inventory item (GET /api/inventory/<id>/)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    identifier: str
    name: str | None = None
    quantity: int | None = None
    last_updated: datetime | None = None
