from fastapi import Depends
from sqlalchemy.orm import Session

from src.database import get_db, get_db_tx
from src.inventory.repository import InventoryRepository
from src.inventory.service import InventoryService


def _get_inventory_repository(
    db: Session = Depends(get_db),
) -> InventoryRepository:
    """Repository with read-only session. Use for queries."""
    return InventoryRepository(db)


def _get_inventory_repository_tx(
    db: Session = Depends(get_db_tx),
) -> InventoryRepository:
    """Repository with transactional session. Use for mutations; commit at request end."""
    return InventoryRepository(db)


def get_inventory_service(
    repo: InventoryRepository = Depends(_get_inventory_repository),
) -> InventoryService:
    """Service for read operations (list, get). No transaction."""
    return InventoryService(repo)


def get_inventory_service_tx(
    repo: InventoryRepository = Depends(_get_inventory_repository_tx),
) -> InventoryService:
    """Service for mutations (upsert, remove_quantity). One transaction per request."""
    return InventoryService(repo)
