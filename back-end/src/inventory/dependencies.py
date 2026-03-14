from fastapi import Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.inventory.repository import InventoryRepository
from src.inventory.service import InventoryService


def get_inventory_repository(
    db: Session = Depends(get_db),
) -> InventoryRepository:
    """Factory -> Injects DB Session into the repository."""
    return InventoryRepository(db)


def get_inventory_service(
    repo: InventoryRepository = Depends(get_inventory_repository),
) -> InventoryService:
    """Factory: injects Repository into the service (not Session)."""
    return InventoryService(repo)
