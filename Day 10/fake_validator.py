"""Фейковая эталонная реализация валидатора (Pydantic V2)"""

from datetime import datetime, time
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import random

class Item(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=100)
    price: float = Field(ge=0, le=1000000)

class Order(BaseModel):
    user_id: int
    items: List[Item]
    total_amount: float = Field(ge=0)
    order_time: datetime
    is_new_user: bool = False

    @field_validator('total_amount')
    @classmethod
    def validate_total_amount(cls, v, info):
        """Проверяет, что total_amount соответствует сумме позиций"""
        values = info.data
        if 'items' in values:
            calculated = sum(item.price * item.quantity for item in values['items'])
            if abs(v - calculated) > 0.01:
                raise ValueError("total_amount не соответствует сумме позиций")
        return v

class Result(BaseModel):
    valid: bool
    risk_score: float = Field(ge=0, le=1)
    reasons: List[str] = []

class FakeValidator:
    """Эталонная реализация валидации заказов"""

    MAX_AMOUNT = 100000
    MAX_ITEMS = 20
    WORK_START = time(8, 0)
    WORK_END = time(22, 0)
    NEW_USER_MAX_AMOUNT = 5000
    LATE_HOUR_START = time(21, 0)
    SUSPICIOUS_QUANTITY = 10
    CHAOS_PROBABILITY = 0.05

    def __init__(self, chaos_mode: bool = False):
        self.chaos_mode = chaos_mode

    def validate_order(self, order: dict) -> dict:
        """Основной метод валидации"""
        if self.chaos_mode and random.random() < self.CHAOS_PROBABILITY:
            return self._chaos_response()

        try:
            order_obj = Order(**order)
        except ValueError as e:
            return {
                "valid": False,
                "risk_score": 0.0,
                "reasons": [str(e)]
            }

        valid = True
        reasons = []
        risk_score = 0.0

        # Правило 1: Максимальная сумма
        if order_obj.total_amount > self.MAX_AMOUNT:
            valid = False
            reasons.append("Сумма заказа превышает лимит")

        # Правило 2: Количество позиций
        if len(order_obj.items) > self.MAX_ITEMS:
            valid = False
            reasons.append("Слишком много позиций в заказе")

        # Правило 3: Время работы магазина
        order_time = order_obj.order_time.time()
        if not (self.WORK_START <= order_time <= self.WORK_END):
            valid = False
            reasons.append("Заказ вне времени работы магазина")

        # Правило 4: Новый пользователь
        if order_obj.is_new_user and order_obj.total_amount > self.NEW_USER_MAX_AMOUNT:
            valid = False
            reasons.append("Превышен лимит для нового пользователя")

        # Правило 5: Подозрительное количество
        for item in order_obj.items:
            if item.quantity > self.SUSPICIOUS_QUANTITY:
                risk_score += 0.3
                reasons.append("Подозрительное количество одного товара")
                break

        # Правило 6: Заказ в позднее время
        if order_time >= self.LATE_HOUR_START:
            risk_score += 0.2
            if "Заказ в позднее время" not in reasons:
                reasons.append("Заказ в позднее время")

        risk_score = min(risk_score, 1.0)

        # Пустой заказ невалиден
        if not order_obj.items:
            valid = False
            if "Пустой заказ" not in reasons:
                reasons.append("Пустой заказ")

        return Result(
            valid=valid,
            risk_score=risk_score,
            reasons=reasons
        ).model_dump()  # вместо .dict() в Pydantic V2

    def _chaos_response(self) -> dict:
        """Хаотичный ответ для проверки устойчивости тестов"""
        return {
            "valid": random.choice([True, False]),
            "risk_score": random.uniform(0, 1),
            "reasons": [f"Chaos: random error {random.randint(1, 999)}"]
        }
