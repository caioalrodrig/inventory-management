from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def mock_service():
    return MagicMock()


@pytest.fixture
def client():
    return TestClient(app)
