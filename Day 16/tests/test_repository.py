"""
Интеграционные тесты для OrderRepository
"""

import pytest
import json
from datetime import datetime, timedelta
import httpx

from app.repositories import OrderRepository
from app.models import Order, OrderItem, OrderStatus
from app.exceptions import EntityNotFoundException, DeliveryCalculationException


# ============ ТЕСТ 1: СОЗДАНИЕ ЗАКАЗА ============

def test_create_order(db_session, sample_order_data):
    """
    Тест создания заказа с позициями
    """
    # Arrange
    repo = OrderRepository(db_session)
    
    # Act
    order = repo.create(sample_order_data)
    
    # Assert
    assert order.id is not None
    assert order.customer_name == "Иван Петров"
    assert order.delivery_address == "г. Москва, ул. Тверская, д. 1"
    assert order.status == OrderStatus.PENDING.value
    
    # Проверяем, что позиции сохранились
    assert len(order.items) == 2
    assert order.items[0].product_name == "Товар 1"
    assert order.items[0].quantity == 2
    assert order.items[0].price == 150.0
    
    # Проверяем, что total_amount пересчитался правильно
    expected_total = 2 * 150.0 + 1 * 300.0
    assert order.total_amount == expected_total


def test_create_order_with_empty_items(db_session):
    """
    Тест создания заказа без позиций
    """
    # Arrange
    repo = OrderRepository(db_session)
    order_data = {
        "customer_name": "Пустой заказ",
        "delivery_address": "Адрес",
        "total_amount": 0.0,
        "items": []
    }
    
    # Act
    order = repo.create(order_data)
    
    # Assert
    assert order.id is not None
    assert len(order.items) == 0
    assert order.total_amount == 0.0


# ============ ТЕСТ 2: ПОИСК ПО ID ============

def test_find_order_by_id(db_session, sample_order_data):
    """
    Тест поиска существующего заказа по ID
    """
    # Arrange
    repo = OrderRepository(db_session)
    created_order = repo.create(sample_order_data)
    
    # Act
    found_order = repo.find_by_id(created_order.id)
    
    # Assert
    assert found_order is not None
    assert found_order.id == created_order.id
    assert found_order.customer_name == created_order.customer_name


def test_find_order_by_id_not_found(db_session):
    """
    Тест поиска несуществующего заказа
    """
    # Arrange
    repo = OrderRepository(db_session)
    
    # Act
    found_order = repo.find_by_id(999)
    
    # Assert
    assert found_order is None


# ============ ТЕСТ 3: ПОИСК ПО СТАТУСУ (ПАРАМЕТРИЗОВАННЫЙ) ============

@pytest.mark.parametrize("status", [
    OrderStatus.PENDING.value,
    OrderStatus.PAID.value,
    OrderStatus.SHIPPED.value,
    OrderStatus.CANCELLED.value
])
def test_find_all_by_status(db_session, sample_order_data, status):
    """
    Параметризованный тест поиска заказов по статусу
    """
    # Arrange
    repo = OrderRepository(db_session)
    
    # Создаём несколько заказов с разными статусами
    order1 = repo.create(sample_order_data)
    order2 = repo.create(sample_order_data)
    order3 = repo.create(sample_order_data)
    
    # Обновляем статусы
    repo.update_status(order1.id, status)
    repo.update_status(order2.id, OrderStatus.PAID.value if status != OrderStatus.PAID.value else OrderStatus.PENDING.value)
    repo.update_status(order3.id, status)
    
    # Act
    orders = repo.find_all_by_status(status)
    
    # Assert
    assert len(orders) == 2
    for order in orders:
        assert order.status == status


def test_find_all_by_status_empty(db_session):
    """
    Тест поиска по статусу, когда заказов нет
    """
    # Arrange
    repo = OrderRepository(db_session)
    
    # Act
    orders = repo.find_all_by_status(OrderStatus.PENDING.value)
    
    # Assert
    assert orders == []


# ============ ТЕСТ 4: ОБНОВЛЕНИЕ СТАТУСА ============

def test_update_status(db_session, sample_order_data):
    """
    Тест обновления статуса заказа
    """
    # Arrange
    repo = OrderRepository(db_session)
    order = repo.create(sample_order_data)
    
    # Act
    updated_order = repo.update_status(order.id, OrderStatus.PAID.value)
    
    # Assert
    assert updated_order.status == OrderStatus.PAID.value
    assert updated_order.id == order.id


def test_update_status_not_found(db_session):
    """
    Тест обновления статуса несуществующего заказа
    """
    # Arrange
    repo = OrderRepository(db_session)
    
    # Act & Assert
    with pytest.raises(EntityNotFoundException) as exc_info:
        repo.update_status(999, OrderStatus.PAID.value)
    
    assert "Order with id 999 not found" in str(exc_info.value)


# ============ ТЕСТ 5: УДАЛЕНИЕ ЗАКАЗА ============

def test_delete_order(db_session, sample_order_data):
    """
    Тест удаления заказа
    """
    # Arrange
    repo = OrderRepository(db_session)
    order = repo.create(sample_order_data)
    order_id = order.id
    
    # Проверяем, что заказ существует
    assert repo.find_by_id(order_id) is not None
    
    # Act
    repo.delete(order_id)
    
    # Assert
    assert repo.find_by_id(order_id) is None


def test_delete_nonexistent_order(db_session):
    """
    Тест удаления несуществующего заказа (не должно быть ошибки)
    """
    # Arrange
    repo = OrderRepository(db_session)
    
    # Act (не должно вызывать исключение)
    repo.delete(999)
    
    # Assert - ничего не произошло


# ============ ТЕСТ 6: ПОИСК ПО ДИАПАЗОНУ ДАТ ============

def test_find_by_date_range(db_session, sample_order_data):
    """
    Тест поиска заказов по диапазону дат
    """
    # Arrange
    repo = OrderRepository(db_session)
    
    now = datetime.now()
    
    # Создаём заказы с разными датами
    order1 = repo.create(sample_order_data)
    db_session.query(Order).filter(Order.id == order1.id).update({
        "created_at": now - timedelta(days=5)
    })
    
    order2 = repo.create(sample_order_data)
    db_session.query(Order).filter(Order.id == order2.id).update({
        "created_at": now - timedelta(days=10)
    })
    
    order3 = repo.create(sample_order_data)
    db_session.query(Order).filter(Order.id == order3.id).update({
        "created_at": now - timedelta(days=1)
    })
    
    db_session.commit()
    
    # Act
    start_date = now - timedelta(days=8)
    end_date = now - timedelta(days=2)
    orders = repo.find_by_date_range(start_date, end_date)
    
    # Assert
    assert len(orders) == 1
    assert orders[0].id == order1.id


def test_find_by_date_range_no_orders(db_session):
    """
    Тест поиска по диапазону дат без результатов
    """
    # Arrange
    repo = OrderRepository(db_session)
    now = datetime.now()
    
    # Act
    orders = repo.find_by_date_range(now - timedelta(days=10), now - timedelta(days=5))
    
    # Assert
    assert orders == []


# ============ ТЕСТ 7: ПОДСЧЁТ СУММЫ ЗАКАЗА ============

def test_get_total_amount_for_order(db_session, sample_order_data):
    """
    Тест подсчёта суммы заказа
    """
    # Arrange
    repo = OrderRepository(db_session)
    order = repo.create(sample_order_data)
    
    # Act
    total = repo.get_total_amount_for_order(order.id)
    
    # Assert
    expected_total = 2 * 150.0 + 1 * 300.0
    assert total == expected_total


def test_get_total_amount_for_nonexistent_order(db_session):
    """
    Тест подсчёта суммы для несуществующего заказа
    """
    # Arrange
    repo = OrderRepository(db_session)
    
    # Act
    total = repo.get_total_amount_for_order(999)
    
    # Assert
    assert total == 0.0


# ============ ТЕСТ 8: ТРАНЗАКЦИОННОСТЬ ============

def test_transaction_rollback_on_invalid_data(db_session, sample_order_data_with_negative_quantity):
    """
    Тест проверки транзакционности: при ошибке данные не сохраняются
    """
    # Arrange
    repo = OrderRepository(db_session)
    
    # Act & Assert
    with pytest.raises(Exception):
        repo.create(sample_order_data_with_negative_quantity)
    
    # Явно откатываем транзакцию
    db_session.rollback()
    
    # Проверяем, что в БД ничего не сохранилось
    orders = db_session.query(Order).all()
    items = db_session.query(OrderItem).all()
    
    assert len(orders) == 0
    assert len(items) == 0


def test_transaction_rollback_on_invalid_price(db_session):
    """
    Тест проверки транзакционности при отрицательной цене
    """
    # Arrange
    repo = OrderRepository(db_session)
    invalid_data = {
        "customer_name": "Тест",
        "delivery_address": "Адрес",
        "total_amount": 0.0,
        "items": [
            {"product_name": "Товар", "quantity": 1, "price": -100.0}
        ]
    }
    
    # Act & Assert
    with pytest.raises(Exception):
        repo.create(invalid_data)
    
    # Явно откатываем транзакцию
    db_session.rollback()
    
    orders = db_session.query(Order).all()
    items = db_session.query(OrderItem).all()
    
    assert len(orders) == 0
    assert len(items) == 0


# ============ ТЕСТ 9: КОНТРАКТНЫЙ ТЕСТ ДЛЯ ВНЕШНЕГО API ============

def test_calculate_delivery_cost_success(db_session, sample_order_data, httpx_mock):
    """
    Контрактный тест: успешный расчёт доставки через внешний API
    """
    # Arrange
    repo = OrderRepository(db_session)
    order = repo.create(sample_order_data)
    
    # Мокаем внешний API
    httpx_mock.add_response(
        method="POST",
        url="https://api.delivery.com/calculate",
        json={"cost": 150.0},
        status_code=200
    )
    
    # Act
    cost = repo.calculate_delivery_cost(order.id)
    
    # Assert
    assert cost == 150.0


def test_calculate_delivery_cost_api_error(db_session, sample_order_data, httpx_mock):
    """
    Контрактный тест: ошибка внешнего API (500)
    """
    # Arrange
    repo = OrderRepository(db_session)
    order = repo.create(sample_order_data)
    
    # Мокаем ошибку API
    httpx_mock.add_response(
        method="POST",
        url="https://api.delivery.com/calculate",
        status_code=500,
        text="Internal Server Error"
    )
    
    # Act & Assert
    with pytest.raises(DeliveryCalculationException) as exc_info:
        repo.calculate_delivery_cost(order.id)
    
    assert "Delivery API error: 500" in str(exc_info.value)


def test_calculate_delivery_cost_invalid_response(db_session, sample_order_data, httpx_mock):
    """
    Контрактный тест: некорректный ответ от API (отсутствует поле cost)
    """
    # Arrange
    repo = OrderRepository(db_session)
    order = repo.create(sample_order_data)
    
    # Мокаем некорректный ответ без поля cost
    httpx_mock.add_response(
        method="POST",
        url="https://api.delivery.com/calculate",
        json={"invalid": "response"},
        status_code=200
    )
    
    # Act & Assert
    with pytest.raises(DeliveryCalculationException) as exc_info:
        repo.calculate_delivery_cost(order.id)
    
    assert "missing 'cost' field" in str(exc_info.value)


def test_calculate_delivery_cost_order_not_found(db_session):
    """
    Тест расчёта доставки для несуществующего заказа
    """
    # Arrange
    repo = OrderRepository(db_session)
    
    # Act & Assert
    with pytest.raises(EntityNotFoundException) as exc_info:
        repo.calculate_delivery_cost(999)
    
    assert "Order with id 999 not found" in str(exc_info.value)


def test_calculate_delivery_cost_checks_request_payload(db_session, sample_order_data, httpx_mock):
    """
    Тест проверки правильности формирования запроса к API
    """
    # Arrange
    repo = OrderRepository(db_session)
    order = repo.create(sample_order_data)
    
    # Используем callback для проверки запроса
    def check_request(request):
        # В pytest-httpx используем request.read() для получения тела
        body = request.read()
        payload = json.loads(body)
        
        assert payload["address"] == order.delivery_address
        # Вес: 2 * 0.5 + 1 * 0.5 = 1.5
        assert payload["weight"] == 1.5
        return httpx.Response(200, json={"cost": 200.0})
    
    httpx_mock.add_callback(check_request)
    
    # Act
    cost = repo.calculate_delivery_cost(order.id)
    
    # Assert
    assert cost == 200.0