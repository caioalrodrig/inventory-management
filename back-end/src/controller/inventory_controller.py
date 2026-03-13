from fastapi import APIRouter, Body, Query, status

from src.schemas.inventory import (
    AddInventoryRequest,
    AddInventoryResponse,
    InventoryItem,
)

from src.utils.inventory_utils import InventoryUtils


router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
)


@router.post("/", response_model=AddInventoryResponse, status_code=status.HTTP_202_ACCEPTED)
def upsert_inventory_item(body: AddInventoryRequest):
    identifier = InventoryUtils.normalize_identifier(body.name)
    # to-do: implement upsert inventory service 
    return AddInventoryResponse(id=1, identifier=identifier)


@router.get("/", response_model=list[InventoryItem])
def list_inventory_items(
    order_by: str | None = Query(None, description="name | quantity | last_updated"),
    direction: str | None = Query(None, description="asc | desc"),
):
    # to-do: implement get inventory-list service 
    return [
        InventoryItem(
            id=1,
            identifier="apple",
            name="Apple",
            quantity=50,
            last_updated="2024-06-07T12:00:00"
        ),
        InventoryItem(
            id=2,
            identifier="banana",
            name="Banana",
            quantity=30,
            last_updated="2024-06-07T13:00:00"
        )
    ]


@router.get("/{item_id}/", response_model=InventoryItem)
def get_inventory_item(item_id: int):
    # mock: simulate retrieving an inventory item by id
    return InventoryItem(
        id=1,
        identifier="apple",
        name="Apple",
        quantity=50,
        last_updated="2024-06-07T12:00:00"
    )


@router.delete("/{item_id}/", status_code=status.HTTP_200_OK)
def remove_inventory_quantity(item_id: int, quantity: int = Body(embed=True)):
    pass
