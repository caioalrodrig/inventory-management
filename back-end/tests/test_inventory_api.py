import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from src.inventory.schema import AddInventoryResponse, InventoryItem


# ----- POST /api/inventory/ -----


def test_given_valid_body_when_post_inventory_then_returns_202_with_id_and_identifier(
    client: TestClient, mock_service
):
    item_id = uuid.uuid4()
    mock_service.upsert_item.return_value = AddInventoryResponse(
        id=item_id, identifier="test-item"
    )
    response = client.post(
        "/api/inventory/",
        json={"name": "Test Item", "quantity": 10},
    )
    assert response.status_code == 202
    data = response.json()
    assert data["id"] == str(item_id)
    assert data["identifier"] == "test-item"
    mock_service.upsert_item.assert_called_once()
    call_kw = mock_service.upsert_item.call_args[1]
    assert call_kw["identifier"] == "test item"
    assert call_kw["quantity"] == 10
    assert call_kw["name"] == "Test Item"


def test_given_name_with_accents_when_post_inventory_then_creates_normalized_identifier(
    client: TestClient, mock_service
):
    item_id = uuid.uuid4()
    mock_service.upsert_item.return_value = AddInventoryResponse(
        id=item_id, identifier="cafe"
    )
    response = client.post(
        "/api/inventory/",
        json={"name": "Café", "quantity": 1},
    )
    assert response.status_code == 202
    mock_service.upsert_item.assert_called_once()
    call_kw = mock_service.upsert_item.call_args[1]
    assert call_kw["identifier"] == "cafe"
    assert call_kw["name"] == "Café"


def test_given_missing_required_fields_when_post_inventory_then_returns_422(
    client: TestClient, mock_service
):
    response = client.post(
        "/api/inventory/",
        json={"name": "Only Name"},
    )
    assert response.status_code == 422
    mock_service.upsert_item.assert_not_called()


def test_given_invalid_types_when_post_inventory_then_returns_422(
    client: TestClient, mock_service
):
    response = client.post(
        "/api/inventory/",
        json={"name": 123, "quantity": "not-a-number"},
    )
    assert response.status_code == 422
    mock_service.upsert_item.assert_not_called()


# ----- GET /api/inventory/ (list) -----


def test_given_items_in_inventory_when_get_list_then_returns_all_items(
    client: TestClient, mock_service
):
    item_id = uuid.uuid4()
    mock_service.list_items.return_value = [
        InventoryItem(
            id=item_id,
            identifier="item1",
            name="Item 1",
            quantity=5,
            last_updated=datetime.now(timezone.utc),
        ),
    ]
    response = client.get("/api/inventory/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["identifier"] == "item1"
    assert data[0]["quantity"] == 5
    mock_service.list_items.assert_called_once_with(order_by=None, direction=None)


# ----- GET /api/inventory/<id>/ -----


def test_given_existing_id_when_get_item_then_returns_item(
    client: TestClient, mock_service
):
    item_id = uuid.uuid4()
    mock_service.get_item.return_value = InventoryItem(
        id=item_id,
        identifier="existing",
        name="Existing",
        quantity=3,
        last_updated=datetime.now(timezone.utc),
    )
    response = client.get(f"/api/inventory/{item_id}/")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(item_id)
    assert data["identifier"] == "existing"
    assert data["quantity"] == 3
    mock_service.get_item.assert_called_once_with(item_id)


def test_given_non_existing_id_when_get_item_then_returns_404(
    client: TestClient, mock_service
):
    mock_service.get_item.return_value = None
    item_id = uuid.uuid4()
    response = client.get(f"/api/inventory/{item_id}/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Not found"
    mock_service.get_item.assert_called_once_with(item_id)


# ----- DELETE /api/inventory/<id>/ -----


def test_given_non_existing_id_when_delete_quantity_then_returns_404(
    client: TestClient, mock_service
):
    mock_service.remove_quantity.side_effect = ValueError("Item not found")
    item_id = uuid.uuid4()
    response = client.request(
        "DELETE",
        f"/api/inventory/{item_id}/",
        json={"quantity": 1},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Not found"
    mock_service.remove_quantity.assert_called_once_with(item_id=item_id, quantity=1)


def test_given_valid_quantity_when_delete_quantity_then_returns_200(
    client: TestClient, mock_service
):
    item_id = uuid.uuid4()
    mock_service.remove_quantity.return_value = InventoryItem(
        id=item_id,
        identifier="item",
        name="Item",
        quantity=5,
        last_updated=datetime.now(timezone.utc),
    )
    response = client.request(
        "DELETE",
        f"/api/inventory/{item_id}/",
        json={"quantity": 2},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 5
    mock_service.remove_quantity.assert_called_once_with(item_id=item_id, quantity=2)


def test_given_quantity_not_embedded_when_delete_quantity_then_returns_422(
    client: TestClient, mock_service
):
    item_id = uuid.uuid4()
    response = client.request(
        "DELETE",
        f"/api/inventory/{item_id}/",
        json=5,
    )
    assert response.status_code == 422
    mock_service.remove_quantity.assert_not_called()
