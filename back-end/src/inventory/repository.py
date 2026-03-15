import uuid
from typing import Optional

from sqlalchemy import case, select
from sqlalchemy.orm import Session

from src.inventory.entity import InventoryItemEntity


class InventoryRepository:
    def __init__(self, db: Session):
        self._db = db

    def find_by_identifier(self, identifier: str) -> Optional[InventoryItemEntity]:
        stmt = select(InventoryItemEntity).where(
            InventoryItemEntity.identifier == identifier
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def find_by_id(self, item_id: uuid.UUID) -> Optional[InventoryItemEntity]:
        stmt = select(InventoryItemEntity).where(InventoryItemEntity.id == item_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def create(
        self,
        *,
        identifier: str,
        name: Optional[str] = None,
        quantity: int = 0,
    ) -> InventoryItemEntity:
        """Create and persist a new entity. Returns refreshed entity."""
        entity = InventoryItemEntity(
            identifier=identifier,
            name=name,
            quantity=quantity,
        )
        self._db.add(entity)
        self._db.flush()
        self._db.refresh(entity)
        return entity

    def save(self, entity: InventoryItemEntity) -> None:
        """Flush and refresh entity."""
        self._db.flush()
        self._db.refresh(entity)

    def list_all(
        self,
        *,
        order_by: Optional[str] = None,
        direction: Optional[str] = "asc",
    ) -> list[InventoryItemEntity]:
        stmt = select(InventoryItemEntity)

        safe_direction = (direction or "asc").lower()

        if order_by and order_by in ("name", "quantity", "last_updated"):
            col = getattr(InventoryItemEntity, order_by)
            stmt = stmt.order_by(
                col.desc() if safe_direction == "desc" else col.asc()
            )
        else:
            # Fallback logic for critical items (quantity < 5)
            critical_first = case((InventoryItemEntity.quantity < 5, 0), else_=1)
            stmt = stmt.order_by(
                critical_first.asc(),
                InventoryItemEntity.last_updated.desc().nulls_last(),
                InventoryItemEntity.name.asc().nulls_last(),
            )

        result = self._db.execute(stmt)
        return list(result.scalars().all())
