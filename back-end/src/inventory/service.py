import uuid
from typing import Optional

from src.inventory.entity import InventoryItemEntity
from src.inventory.repository import InventoryRepository
from src.inventory.schema import (
    AddInventoryResponse,
    InventoryItem,
)


def _entity_to_item(entity: InventoryItemEntity) -> InventoryItem:
    return InventoryItem.model_validate(entity)


class InventoryService:
    def __init__(self, repo: InventoryRepository):
        self._repo = repo

    def upsert_item(
        self,
        *,
        identifier: str,
        quantity: int,
        name: Optional[str] = None,
    ) -> AddInventoryResponse:
        entity = self._repo.find_by_identifier(identifier)
        if entity is None:
            entity = self._repo.create(
                identifier=identifier,
                name=name,
                quantity=quantity,
            )
        else:
            entity.quantity += quantity
            # name can differ for a same identifier so we keep it updated
            if name is not None:
                entity.name = name
            self._repo.save(entity)
        return AddInventoryResponse(id=entity.id, identifier=entity.identifier)

    def list_items(
        self,
        *,
        order_by: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> list[InventoryItem]:
        entities = self._repo.list_all(
            order_by=order_by,
            direction=direction,
        )
        return [_entity_to_item(e) for e in entities]

    def get_item(self, item_id: uuid.UUID) -> Optional[InventoryItem]:
        entity = self._repo.find_by_id(item_id)
        return None if entity is None else _entity_to_item(entity)

    def remove_quantity(
        self,
        item_id: uuid.UUID,
        quantity: int,
    ) -> InventoryItem:
        entity = self._repo.find_by_id(item_id)
        if entity is None:
            raise ValueError("Item not found")
        if quantity > entity.quantity:
            raise ValueError("Insufficient quantity")
        entity.quantity -= quantity
        self._repo.save(entity)
        return _entity_to_item(entity)
