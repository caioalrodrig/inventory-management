import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from src.inventory.schema import AddInventoryResponse, InventoryItem


def _fake_entity(
    *, id=None, identifier="item", name="Item", quantity=10, last_updated=None
):
    o = MagicMock()
    o.id = id or uuid.uuid4()
    o.identifier = identifier
    o.name = name
    o.quantity = quantity
    o.last_updated = last_updated or datetime.now(timezone.utc)
    return o


# ----- upsert_item -----


def test_upsert_item_when_identifier_not_found_creates_and_returns_response(
    service, mock_repo
):
    mock_repo.find_by_identifier.return_value = None
    created = _fake_entity(
        id=uuid.uuid4(), identifier="newitem", name="New Item", quantity=5
    )
    mock_repo.create.return_value = created

    result = service.upsert_item(identifier="newitem", quantity=5, name="New Item")

    assert result == AddInventoryResponse(id=created.id, identifier="newitem")
    mock_repo.find_by_identifier.assert_called_once_with("newitem")
    mock_repo.create.assert_called_once_with(
        identifier="newitem", name="New Item", quantity=5
    )
    mock_repo.save.assert_not_called()


def test_upsert_item_when_identifier_found_sums_quantity_and_saves(
    service, mock_repo
):
    existing = _fake_entity(identifier="item", name="Item", quantity=10)
    mock_repo.find_by_identifier.return_value = existing

    result = service.upsert_item(identifier="item", quantity=3)

    assert result.id == existing.id
    assert result.identifier == "item"
    assert existing.quantity == 13
    mock_repo.save.assert_called_once_with(existing)
    mock_repo.create.assert_not_called()


def test_upsert_item_when_identifier_found_and_name_given_updates_name(
    service, mock_repo
):
    existing = _fake_entity(identifier="cafe", name="Café", quantity=5)
    mock_repo.find_by_identifier.return_value = existing

    service.upsert_item(identifier="cafe", quantity=0, name="Café com leite")

    assert existing.name == "Café com leite"
    assert existing.quantity == 5
    mock_repo.save.assert_called_once_with(existing)


def test_upsert_item_when_identifier_found_and_name_none_keeps_existing_name(
    service, mock_repo
):
    existing = _fake_entity(identifier="item", name="Old Name", quantity=2)
    mock_repo.find_by_identifier.return_value = existing

    service.upsert_item(identifier="item", quantity=1)

    assert existing.name == "Old Name"
    assert existing.quantity == 3
    mock_repo.save.assert_called_once_with(existing)


# ----- remove_quantity -----


def test_remove_quantity_when_item_found_and_quantity_ok_decrements_and_returns_item(
    service, mock_repo
):
    item_id = uuid.uuid4()
    existing = _fake_entity(id=item_id, identifier="x", quantity=10)
    mock_repo.find_by_id.return_value = existing

    result = service.remove_quantity(item_id=item_id, quantity=4)

    assert existing.quantity == 6
    mock_repo.save.assert_called_once_with(existing)
    assert isinstance(result, InventoryItem)
    assert result.quantity == 6


def test_remove_quantity_when_item_not_found_raises_value_error(service, mock_repo):
    mock_repo.find_by_id.return_value = None

    with pytest.raises(ValueError, match="Item not found"):
        service.remove_quantity(item_id=uuid.uuid4(), quantity=1)

    mock_repo.save.assert_not_called()


def test_remove_quantity_when_quantity_exceeds_stock_raises_value_error(
    service, mock_repo
):
    existing = _fake_entity(quantity=3)
    mock_repo.find_by_id.return_value = existing

    with pytest.raises(ValueError, match="Insufficient quantity"):
        service.remove_quantity(item_id=existing.id, quantity=5)

    assert existing.quantity == 3
    mock_repo.save.assert_not_called()


def test_remove_quantity_when_quantity_equals_stock_goes_to_zero(service, mock_repo):
    item_id = uuid.uuid4()
    existing = _fake_entity(id=item_id, quantity=2)
    mock_repo.find_by_id.return_value = existing

    result = service.remove_quantity(item_id=item_id, quantity=2)

    assert existing.quantity == 0
    mock_repo.save.assert_called_once_with(existing)
    assert result.quantity == 0


# ----- get_item -----


def test_get_item_when_found_returns_item(service, mock_repo):
    item_id = uuid.uuid4()
    existing = _fake_entity(id=item_id, identifier="x", name="X", quantity=1)
    mock_repo.find_by_id.return_value = existing

    result = service.get_item(item_id)

    assert result is not None
    assert result.id == item_id
    assert result.identifier == "x"
    assert result.quantity == 1
    mock_repo.find_by_id.assert_called_once_with(item_id)


def test_get_item_when_not_found_returns_none(service, mock_repo):
    mock_repo.find_by_id.return_value = None

    result = service.get_item(uuid.uuid4())

    assert result is None


# ----- list_items  -----


def test_list_items_delegates_to_repo_and_maps_to_items(service, mock_repo):
    item_id = uuid.uuid4()
    entity = _fake_entity(id=item_id, identifier="a", name="A", quantity=1)
    mock_repo.list_all.return_value = [entity]

    result = service.list_items(order_by="name", direction="asc")

    mock_repo.list_all.assert_called_once_with(order_by="name", direction="asc")
    assert len(result) == 1
    assert result[0].identifier == "a"
    assert result[0].quantity == 1
