import uuid

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from src.inventory.dependencies import (
    get_inventory_service,
    get_inventory_service_tx,
)
from src.inventory.schema import (
    AddInventoryRequest,
    AddInventoryResponse,
    InventoryItem,
)
from src.inventory.service import InventoryService
from src.inventory.utils import InventoryUtils
from src.inventory.tasks import run_inventory_event


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
    service: InventoryService = Depends(get_inventory_service_tx),
):
    identifier = InventoryUtils.normalize_identifier(body.name)
    result = service.upsert_item(
        identifier=identifier,
        quantity=body.quantity,
        name=body.name,
    )
    run_inventory_event.delay(
        event_type="ADD_OR_UPDATE",
        item_id=str(result.id),
        quantity=body.quantity,
    )

    return result


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
    service: InventoryService = Depends(get_inventory_service_tx),
):
    try:
        item = service.remove_quantity(item_id=item_id, quantity=quantity)
        run_inventory_event.delay(
            event_type="REMOVE",
            item_id=str(item_id),
            quantity=quantity,
        )

        return item
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
