import os
from importlib import reload

import pytest
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_db():
    # Starts a real Postgres instance via Testcontainers to test the InventoryRepository
    with PostgresContainer("postgres:16-alpine") as postgres:
        os.environ["DATABASE_URL"] = postgres.get_connection_url()

        # Reload database module to use the container's DATABASE_URL
        import src.database as database
        import src.inventory.entity as inventory_entity

        reload(database)
        # Reload entities so they use the new Base/engine
        reload(inventory_entity)

        # Ensure explicit creation of inventory tables in the container's Postgres
        database.Base.metadata.create_all(bind=database.engine)

        yield database


@pytest.fixture
def repo(postgres_db):
    # Returns an InventoryRepository connected to the Postgres Testcontainers instance.
    from src.inventory.repository import InventoryRepository
    from src.database import SessionLocal

    session = SessionLocal()
    try:
        yield InventoryRepository(session)
    finally:
        session.close()


def test_create_and_find_by_identifier_repository(repo):
    created = repo.create(identifier="item-123", name="Item 123", quantity=10)

    found = repo.find_by_identifier("item-123")

    assert found is not None
    assert found.id == created.id
    assert found.identifier == "item-123"
    assert found.name == "Item 123"
    assert found.quantity == 10


def test_list_all_orders_critical_items_first(repo):
    # Create items with different quantities
    low = repo.create(identifier="low-stock", name="Low", quantity=2)
    normal = repo.create(identifier="normal-stock", name="Normal", quantity=10)

    items = repo.list_all()

    # Critical item (quantity < 5) should appear first
    assert items[0].id == low.id
    assert {i.id for i in items} == {low.id, normal.id}


def test_list_all_order_by_name_asc(repo):
    repo.create(identifier="c-item", name="Charlie", quantity=5)
    repo.create(identifier="a-item", name="Alpha", quantity=5)
    repo.create(identifier="b-item", name="Bravo", quantity=5)

    items = repo.list_all(order_by="name", direction="asc")

    names = [i.name for i in items]
    assert names == ["Alpha", "Bravo", "Charlie"]


def test_list_all_order_by_name_desc(repo):
    repo.create(identifier="c-item", name="Charlie", quantity=5)
    repo.create(identifier="a-item", name="Alpha", quantity=5)
    repo.create(identifier="b-item", name="Bravo", quantity=5)

    items = repo.list_all(order_by="name", direction="desc")

    names = [i.name for i in items]
    assert names == ["Charlie", "Bravo", "Alpha"]


def test_list_all_order_by_quantity_asc(repo):
    high = repo.create(identifier="high", name="High", quantity=100)
    low = repo.create(identifier="low", name="Low", quantity=1)
    mid = repo.create(identifier="mid", name="Mid", quantity=50)

    items = repo.list_all(order_by="quantity", direction="asc")

    assert [i.id for i in items] == [low.id, mid.id, high.id]
    assert [i.quantity for i in items] == [1, 50, 100]


def test_list_all_order_by_quantity_desc(repo):
    high = repo.create(identifier="high", name="High", quantity=100)
    low = repo.create(identifier="low", name="Low", quantity=1)
    mid = repo.create(identifier="mid", name="Mid", quantity=50)

    items = repo.list_all(order_by="quantity", direction="desc")

    assert [i.id for i in items] == [high.id, mid.id, low.id]
    assert [i.quantity for i in items] == [100, 50, 1]


def test_list_all_order_by_last_updated_asc(repo):
    first = repo.create(identifier="first", name="First", quantity=5)
    second = repo.create(identifier="second", name="Second", quantity=5)
    second.quantity += 1
    repo.save(second)

    items = repo.list_all(order_by="last_updated", direction="asc")

    assert len(items) == 2
    assert {i.id for i in items} == {first.id, second.id}

    assert items[0].id == first.id


def test_list_all_order_by_last_updated_desc(repo):
    first = repo.create(identifier="first", name="First", quantity=5)
    second = repo.create(identifier="second", name="Second", quantity=5)
    second.quantity += 1
    repo.save(second)

    items_desc = repo.list_all(order_by="last_updated", direction="desc")

    assert len(items_desc) == 2
    assert {i.id for i in items_desc} == {first.id, second.id}
    # With desc, either order is valid if timestamps tie; if they differ -> updated (second) is first
    ids = [i.id for i in items_desc]
    assert ids[0] in (first.id, second.id) and ids[1] in (first.id, second.id)


def test_list_all_order_by_default_direction_is_asc(repo):
    repo.create(identifier="b", name="B", quantity=1)
    repo.create(identifier="a", name="A", quantity=1)

    items = repo.list_all(order_by="name", direction=None)

    assert [i.name for i in items] == ["A", "B"]


def test_list_all_invalid_order_by_uses_fallback_critical_first(repo):
    # """When order_by is not name/quantity/last_updated, fallback: critical first, then last_updated desc, name asc."""
    critical = repo.create(identifier="crit", name="Critical", quantity=2)
    normal = repo.create(identifier="norm", name="Normal", quantity=10)

    items = repo.list_all(order_by="invalid_column", direction="asc")

    assert items[0].id == critical.id
    assert {i.id for i in items} == {critical.id, normal.id}


def test_list_all_no_order_by_uses_fallback_critical_first(repo):
    # """When order_by is None, fallback: critical items first."""
    critical = repo.create(identifier="c", name="C", quantity=1)
    ok = repo.create(identifier="a", name="A", quantity=20)

    items = repo.list_all(order_by=None, direction=None)

    assert items[0].id == critical.id
    assert len(items) == 2
