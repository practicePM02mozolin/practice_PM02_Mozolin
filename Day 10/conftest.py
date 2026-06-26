"""Фикстуры для тестирования валидатора"""

import pytest
from datetime import datetime, timedelta
from fake_validator import FakeValidator


@pytest.fixture
def validator():
    """Базовый валидатор без хаос-режима"""
    return FakeValidator(chaos_mode=False)

@pytest.fixture
def chaos_validator():
    """Валидатор с хаос-режимом"""
    return FakeValidator(chaos_mode=True)

@pytest.fixture
def valid_order():
    """Валидный заказ"""
    return {
        "user_id": 1,
        "items": [
            {"product_id": 1, "quantity": 2, "price": 100}
        ],
        "total_amount": 200,
        "order_time": datetime(2026, 6, 16, 12, 0, 0),
        "is_new_user": False
    }

@pytest.fixture
def base_order():
    """Базовый заказ для модификации"""
    return {
        "user_id": 1,
        "items": [{"product_id": 1, "quantity": 1, "price": 100}],
        "total_amount": 100,
        "order_time": datetime(2026, 6, 16, 12, 0, 0),
        "is_new_user": False
    }
