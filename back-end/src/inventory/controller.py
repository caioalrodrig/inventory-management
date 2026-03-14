import uuid

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from src.inventory.dependencies import get_inventory_service
from src.inventory.schema import (
    AddInventoryRequest,
    AddInventoryResponse,
    InventoryItem,
)
from src.inventory.service import InventoryService
from src.inventory.utils import InventoryUtils


router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
)


@router.post(
    "/",
    response_model=AddInventoryResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def upsert_inventory_item(
    body: AddInventoryRequest,
    service: InventoryService = Depends(get_inventory_service),
):
    identifier = InventoryUtils.normalize_identifier(body.name)
    return service.upsert_item(
        identifier=identifier,
        quantity=body.quantity,
        name=body.name,
    )


@router.get("/", response_model=list[InventoryItem])
def list_inventory_items(
    service: InventoryService = Depends(get_inventory_service),
    order_by: str | None = Query(None, description="name | quantity | last_updated"),
    direction: str | None = Query(None, description="asc | desc"),
):
    return service.list_items(order_by=order_by, direction=direction)


@router.get("/{item_id}/", response_model=InventoryItem)
def get_inventory_item(
    item_id: uuid.UUID,
    service: InventoryService = Depends(get_inventory_service),
):
    item = service.get_item(item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found",
        )
    return item


@router.delete(
    "/{item_id}/", response_model=InventoryItem, status_code=status.HTTP_200_OK
)
def remove_inventory_quantity(
    item_id: uuid.UUID,
    quantity: int = Body(embed=True),
    service: InventoryService = Depends(get_inventory_service),
):
    try:
        return service.remove_quantity(item_id=item_id, quantity=quantity)
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient quantity",
        )
