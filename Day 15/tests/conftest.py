"""
Конфигурация pytest с фикстурами
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """
    Фикстура для создания тестового клиента FastAPI
    """
    return TestClient(app)


@pytest.fixture
def sample_order():
    """
    Фикстура с тестовыми данными заказа
    """
    return {
        "id": 1,
        "total": 100.0,
        "status": "PAID"
    }


@pytest.fixture
def sample_order_404():
    """
    Фикстура с тестовыми данными несуществующего заказа
    """
    return {
        "id": 999,
        "message": "Order with id 999 not found"
    }