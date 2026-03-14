"""
Inventory domain entity (ORM model).
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from src.database import Base


class InventoryItemEntity(Base):
    """Inventory item table."""

    __tablename__ = "inventory_items"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    identifier: Mapped[str] = mapped_column(String(255), unique=True, nullable=False) # normalized name
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True) # defined by the user
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_updated: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.now(),
        onupdate=func.now(),
    )
