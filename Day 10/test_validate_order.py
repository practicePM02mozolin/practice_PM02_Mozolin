"""Тесты для функции validate_order"""
import pytest
from datetime import datetime
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st
from fake_validator import FakeValidator

@pytest.fixture
def validator():
    return FakeValidator(chaos_mode=False)


@pytest.fixture
def chaos_validator():
    return FakeValidator(chaos_mode=True)

@pytest.mark.parametrize("order,expected_valid,expected_risk_min,expected_risk_max,reasons_contain", [
    # TC-01: Валидный заказ
    (
        {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 2, "price": 100}],
            "total_amount": 200,
            "order_time": datetime(2026, 6, 16, 12, 0, 0),
            "is_new_user": False
        },
        True, 0.0, 0.0, []
    ),
    # TC-02: Сумма превышает лимит
    (
        {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 1, "price": 150000}],
            "total_amount": 150000,
            "order_time": datetime(2026, 6, 16, 12, 0, 0),
            "is_new_user": False
        },
        False, 0.0, 0.0, ["Сумма заказа превышает лимит"]
    ),
    # TC-03: Слишком много позиций
    (
        {
            "user_id": 1,
            "items": [{"product_id": i, "quantity": 1, "price": 100} for i in range(21)],
            "total_amount": 2100,
            "order_time": datetime(2026, 6, 16, 12, 0, 0),
            "is_new_user": False
        },
        False, 0.0, 0.0, ["Слишком много позиций в заказе"]
    ),
    # TC-04: Время до 8:00 (невалидный, риск 0.0)
    (
        {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 1, "price": 100}],
            "total_amount": 100,
            "order_time": datetime(2026, 6, 16, 7, 0, 0),
            "is_new_user": False
        },
        False, 0.0, 0.0, ["Заказ вне времени работы магазина"]
    ),
    # TC-05: Время после 22:00 (невалидный, но риск 0.2 из-за позднего времени)
    (
        {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 1, "price": 100}],
            "total_amount": 100,
            "order_time": datetime(2026, 6, 16, 23, 0, 0),
            "is_new_user": False
        },
        False, 0.2, 0.2, ["Заказ вне времени работы магазина", "Заказ в позднее время"]
    ),
    # TC-06: Новый пользователь, валидный
    (
        {
            "user_id": 2,
            "items": [{"product_id": 1, "quantity": 1, "price": 100}],
            "total_amount": 100,
            "order_time": datetime(2026, 6, 16, 12, 0, 0),
            "is_new_user": True
        },
        True, 0.0, 0.0, []
    ),
    # TC-07: Новый пользователь, превышен лимит
    (
        {
            "user_id": 2,
            "items": [{"product_id": 1, "quantity": 1, "price": 10000}],
            "total_amount": 10000,
            "order_time": datetime(2026, 6, 16, 12, 0, 0),
            "is_new_user": True
        },
        False, 0.0, 0.0, ["Превышен лимит для нового пользователя"]
    ),
    # TC-08: Подозрительное количество
    (
        {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 15, "price": 100}],
            "total_amount": 1500,
            "order_time": datetime(2026, 6, 16, 12, 0, 0),
            "is_new_user": False
        },
        True, 0.3, 0.3, ["Подозрительное количество одного товара"]
    ),
    # TC-09: Позднее время (валидный, риск 0.2)
    (
        {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 1, "price": 100}],
            "total_amount": 100,
            "order_time": datetime(2026, 6, 16, 21, 30, 0),
            "is_new_user": False
        },
        True, 0.2, 0.2, ["Заказ в позднее время"]
    ),
    # TC-10: quantity>10 + время>21:00
    (
        {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 15, "price": 100}],
            "total_amount": 1500,
            "order_time": datetime(2026, 6, 16, 21, 30, 0),
            "is_new_user": False
        },
        True, 0.5, 0.5, ["Подозрительное количество одного товара", "Заказ в позднее время"]
    ),
    # TC-11: Граница суммы (100000) — валидный
    (
        {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 1, "price": 100000}],
            "total_amount": 100000,
            "order_time": datetime(2026, 6, 16, 12, 0, 0),
            "is_new_user": False
        },
        True, 0.0, 0.0, []
    ),
    # TC-12: Граница суммы (100001) — невалидный
    (
        {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 1, "price": 100001}],
            "total_amount": 100001,
            "order_time": datetime(2026, 6, 16, 12, 0, 0),
            "is_new_user": False
        },
        False, 0.0, 0.0, ["Сумма заказа превышает лимит"]
    ),
    # TC-13: Граница позиций (20) — валидный
    (
        {
            "user_id": 1,
            "items": [{"product_id": i, "quantity": 1, "price": 100} for i in range(20)],
            "total_amount": 2000,
            "order_time": datetime(2026, 6, 16, 12, 0, 0),
            "is_new_user": False
        },
        True, 0.0, 0.0, []
    ),
    # TC-14: Граница позиций (21) — невалидный
    (
        {
            "user_id": 1,
            "items": [{"product_id": i, "quantity": 1, "price": 100} for i in range(21)],
            "total_amount": 2100,
            "order_time": datetime(2026, 6, 16, 12, 0, 0),
            "is_new_user": False
        },
        False, 0.0, 0.0, ["Слишком много позиций в заказе"]
    ),
    # TC-15: Пустой заказ
    (
        {
            "user_id": 1,
            "items": [],
            "total_amount": 0,
            "order_time": datetime(2026, 6, 16, 12, 0, 0),
            "is_new_user": False
        },
        False, 0.0, 0.0, ["Пустой заказ"]
    ),
])
def test_validate_order_decision_table(validator, order, expected_valid, expected_risk_min, expected_risk_max, reasons_contain):
    result = validator.validate_order(order)
    
    assert result["valid"] == expected_valid
    assert expected_risk_min <= result["risk_score"] <= expected_risk_max
    for reason in reasons_contain:
        assert reason in result["reasons"]


# =====================================================
# Property-Based тесты (Hypothesis) с исправлением HealthCheck
# =====================================================

@given(
    user_id=st.integers(min_value=1, max_value=1000),
    items=st.lists(
        st.builds(
            dict,
            product_id=st.integers(min_value=1, max_value=100),
            quantity=st.integers(min_value=1, max_value=5),
            price=st.floats(min_value=1, max_value=1000)
        ),
        min_size=1, max_size=10
    ),
    is_new_user=st.booleans()
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_hypothesis_valid_orders_always_valid(validator, user_id, items, is_new_user):
    """Генерируем валидные заказы и проверяем, что они всегда проходят"""
    total_amount = sum(item["quantity"] * item["price"] for item in items)
    if is_new_user and total_amount > 5000:
        return
    
    order = {
        "user_id": user_id,
        "items": items,
        "total_amount": total_amount,
        "order_time": datetime(2026, 6, 16, 12, 0, 0),
        "is_new_user": is_new_user
    }
    
    result = validator.validate_order(order)
    assert result["valid"] is True


def test_hypothesis_risk_monotonicity(validator):
    """Проверка монотонности риск-скора при увеличении суммы"""
    results = []
    for i in range(1, 10):
        order = {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 1, "price": i * 1000}],
            "total_amount": i * 1000,
            "order_time": datetime(2026, 6, 16, 12, 0, 0),
            "is_new_user": False
        }
        result = validator.validate_order(order)
        results.append(result["risk_score"])
    
    for i in range(1, len(results)):
        assert results[i] >= results[i-1]


def test_hypothesis_invariant(validator):
    """Инвариант: если заказ невалиден, есть причина"""
    order = {
        "user_id": 1,
        "items": [{"product_id": 1, "quantity": 1, "price": 150000}],
        "total_amount": 150000,
        "order_time": datetime(2026, 6, 16, 12, 0, 0),
        "is_new_user": False
    }
    
    result = validator.validate_order(order)
    
    if result["valid"] is False:
        assert len(result["reasons"]) > 0
