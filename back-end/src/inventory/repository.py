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
        self._db.commit()
        self._db.refresh(entity)
        return entity

    def save(self, entity: InventoryItemEntity) -> None:
        """Commit and refresh entity (after in-memory changes)."""
        self._db.commit()
        self._db.refresh(entity)

    def list_all(
        self,
        *,
        order_by: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> list[InventoryItemEntity]:
        """Return all entities with optional ordering."""
        stmt = select(InventoryItemEntity)
        if (
            order_by
            and direction
            and order_by in ("name", "quantity", "last_updated")
        ):
            col = getattr(InventoryItemEntity, order_by)
            stmt = stmt.order_by(
                col.desc() if direction.lower() == "desc" else col.asc()
            )
        else:
            critical_first = case((InventoryItemEntity.quantity < 5, 0), else_=1)
            stmt = stmt.order_by(
                critical_first,
                InventoryItemEntity.last_updated.desc().nulls_last(),
                InventoryItemEntity.name.asc().nulls_last(),
            )
        return list(self._db.execute(stmt).scalars().all())
