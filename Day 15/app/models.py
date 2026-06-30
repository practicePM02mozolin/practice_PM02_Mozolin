"""
Модуль с Pydantic моделями для валидации
"""

from pydantic import BaseModel
from typing import Optional


class OrderResponse(BaseModel):
    """Модель ответа для заказа"""
    id: int
    total: float
    status: str


class ErrorResponse(BaseModel):
    """Модель ответа для ошибок"""
    code: int
    message: str