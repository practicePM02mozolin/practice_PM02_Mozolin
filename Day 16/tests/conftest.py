"""
Конфигурация pytest с фикстурами для тестов
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.models import Base


@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Фикстура для создания тестовой БД SQLite in-memory
    
    Создаёт все таблицы перед тестом и откатывает транзакцию после
    """
    # Создаём движок для in-memory SQLite
    engine = create_engine("sqlite:///:memory:", echo=False)
    
    # Создаём все таблицы
    Base.metadata.create_all(engine)
    
    # Создаём сессию
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()
    
    # Отключаем autocommit для управления транзакциями
    session.begin()
    
    try:
        yield session
    finally:
        # Откатываем транзакцию
        session.rollback()
        session.close()
        # Удаляем все таблицы
        Base.metadata.drop_all(engine)


@pytest.fixture
def sample_order_data():
    """
    Фикстура с тестовыми данными для создания заказа
    """
    return {
        "customer_name": "Иван Петров",
        "delivery_address": "г. Москва, ул. Тверская, д. 1",
        "total_amount": 0.0,  # Будет пересчитано автоматически
        "items": [
            {"product_name": "Товар 1", "quantity": 2, "price": 150.0},
            {"product_name": "Товар 2", "quantity": 1, "price": 300.0},
        ]
    }


@pytest.fixture
def sample_order_data_with_negative_quantity():
    """
    Фикстура с некорректными данными (отрицательное количество)
    """
    return {
        "customer_name": "Тест Тестов",
        "delivery_address": "г. Москва, ул. Ленина, д. 10",
        "total_amount": 0.0,
        "items": [
            {"product_name": "Товар 1", "quantity": -1, "price": 100.0},
        ]
    }