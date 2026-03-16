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
