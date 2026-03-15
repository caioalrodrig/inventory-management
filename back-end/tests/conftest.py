from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src.inventory.dependencies import get_inventory_service, get_inventory_service_tx
from src.inventory.service import InventoryService
from src.main import app


@pytest.fixture
def mock_service():
    return MagicMock()


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def service(mock_repo):
    return InventoryService(mock_repo)


@pytest.fixture
def client(mock_service):
    app.dependency_overrides[get_inventory_service] = lambda: mock_service
    app.dependency_overrides[get_inventory_service_tx] = lambda: mock_service
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
