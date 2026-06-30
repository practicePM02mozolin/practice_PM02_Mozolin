"""
Тестирование глобального обработчика ошибок FastAPI (Вариант 11)
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.exceptions import EntityNotFoundException
from app.services import OrderService


# ============ ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ПЕРЕОПРЕДЕЛЕНИЯ ЗАВИСИМОСТЕЙ ============

def override_dependency(app_instance, dependency_func, mock_service):
    """
    Вспомогательная функция для переопределения зависимости в FastAPI
    """
    def override():
        return mock_service
    
    app_instance.dependency_overrides[dependency_func] = override
    return override


# ============ ТЕСТ 1: ОБРАБОТКА ОШИБКИ 404 ============

def test_global_handler_returns_404(mocker):
    """
    Тест проверяет, что глобальный обработчик возвращает статус 404
    и корректный JSON при возникновении EntityNotFoundException
    """
    # Arrange
    from app.main import get_order_service
    
    mock_service = mocker.Mock(spec=OrderService)
    mock_service.get_order.side_effect = EntityNotFoundException(
        "Order with id 999 not found"
    )
    
    # Переопределяем зависимость
    def override_get_order_service():
        return mock_service
    
    app.dependency_overrides[get_order_service] = override_get_order_service
    
    client = TestClient(app)
    
    # Act
    response = client.get("/api/orders/999")
    
    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "code": 404,
        "message": "Order with id 999 not found"
    }
    mock_service.get_order.assert_called_once_with(999)
    
    # Очищаем переопределения после теста
    app.dependency_overrides = {}


def test_global_handler_returns_404_with_custom_message(mocker):
    """
    Тест проверяет, что глобальный обработчик использует кастомное сообщение
    """
    # Arrange
    from app.main import get_order_service
    
    custom_message = "Заказ с ID 888 не найден в системе"
    mock_service = mocker.Mock(spec=OrderService)
    mock_service.get_order.side_effect = EntityNotFoundException(custom_message)
    
    def override_get_order_service():
        return mock_service
    
    app.dependency_overrides[get_order_service] = override_get_order_service
    
    client = TestClient(app)
    
    # Act
    response = client.get("/api/orders/888")
    
    # Assert
    assert response.status_code == 404
    assert response.json()["message"] == custom_message
    mock_service.get_order.assert_called_once_with(888)
    
    app.dependency_overrides = {}


# ============ ТЕСТ 2: УСПЕШНОЕ ПОЛУЧЕНИЕ ЗАКАЗА ============

def test_get_order_success(mocker):
    """
    Тест проверяет успешное получение заказа
    """
    # Arrange
    from app.main import get_order_service
    
    expected_order = {
        "id": 1,
        "total": 100.0,
        "status": "PAID"
    }
    
    mock_service = mocker.Mock(spec=OrderService)
    mock_service.get_order.return_value = expected_order
    
    def override_get_order_service():
        return mock_service
    
    app.dependency_overrides[get_order_service] = override_get_order_service
    
    client = TestClient(app)
    
    # Act
    response = client.get("/api/orders/1")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == expected_order
    mock_service.get_order.assert_called_once_with(1)
    
    app.dependency_overrides = {}


# ============ ТЕСТ 3: ПРОВЕРКА ДРУГИХ ЭНДПОИНТОВ ============

def test_health_check_endpoint():
    """
    Тест проверяет эндпоинт /health
    """
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_all_orders(mocker):
    """
    Тест проверяет эндпоинт получения всех заказов
    """
    # Arrange
    from app.main import get_order_service
    
    expected_orders = [
        {"id": 1, "total": 100.0, "status": "PAID"},
        {"id": 2, "total": 250.0, "status": "PENDING"}
    ]
    
    mock_service = mocker.Mock(spec=OrderService)
    mock_service.get_all_orders.return_value = expected_orders
    
    def override_get_order_service():
        return mock_service
    
    app.dependency_overrides[get_order_service] = override_get_order_service
    
    client = TestClient(app)
    
    # Act
    response = client.get("/api/orders")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == expected_orders
    mock_service.get_all_orders.assert_called_once()
    
    app.dependency_overrides = {}


# ============ ТЕСТ 4: ПРОВЕРКА СТРУКТУРЫ ОШИБКИ ============

def test_error_response_structure(mocker):
    """
    Тест проверяет структуру ответа при ошибке
    """
    # Arrange
    from app.main import get_order_service
    
    mock_service = mocker.Mock(spec=OrderService)
    mock_service.get_order.side_effect = EntityNotFoundException(
        "Test error message"
    )
    
    def override_get_order_service():
        return mock_service
    
    app.dependency_overrides[get_order_service] = override_get_order_service
    
    client = TestClient(app)
    
    # Act
    response = client.get("/api/orders/999")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "code" in data
    assert "message" in data
    assert isinstance(data["code"], int)
    assert isinstance(data["message"], str)
    assert data["code"] == 404
    
    app.dependency_overrides = {}


# ============ ПАРАМЕТРИЗОВАННЫЙ ТЕСТ ============

@pytest.mark.parametrize("order_id,should_succeed", [
    (1, True),
    (2, True),
    (3, True),
    (999, False),
    (-1, False),
    (0, False),
])
def test_get_order_with_different_ids(mocker, order_id, should_succeed):
    """
    Параметризованный тест для различных ID заказов
    """
    # Arrange
    from app.main import get_order_service
    
    mock_service = mocker.Mock(spec=OrderService)
    
    if should_succeed:
        mock_service.get_order.return_value = {
            "id": order_id,
            "total": 100.0,
            "status": "PAID"
        }
    else:
        mock_service.get_order.side_effect = EntityNotFoundException(
            f"Order with id {order_id} not found"
        )
    
    def override_get_order_service():
        return mock_service
    
    app.dependency_overrides[get_order_service] = override_get_order_service
    
    client = TestClient(app)
    
    # Act
    response = client.get(f"/api/orders/{order_id}")
    
    # Assert
    if should_succeed:
        assert response.status_code == 200
        assert response.json()["id"] == order_id
    else:
        assert response.status_code == 404
        assert "not found" in response.json()["message"].lower()
    
    app.dependency_overrides = {}