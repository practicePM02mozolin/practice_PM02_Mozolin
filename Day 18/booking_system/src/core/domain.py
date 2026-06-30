# src/core/domain.py
"""Domain модуль - DDD: Агрегаты, сущности, Value Objects"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List
import uuid


class BookingStatus(Enum):
    """Статусы бронирования"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


@dataclass
class Guest:
    """Сущность гостя"""
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    phone: str = ""
    is_vip: bool = False
    
    def __post_init__(self):
        # ИСПРАВЛЕНО: проверяем что name не None и не пустая строка
        if self.name is None or not self.name.strip():
            raise ValueError("Имя гостя не может быть пустым")
        if self.email and "@" not in self.email:
            raise ValueError("Неверный формат email")


@dataclass
class Room:
    """Сущность номера"""
    id: Optional[int] = None
    room_number: str = ""
    room_type: str = "standard"
    price_per_night: float = 0.0
    capacity: int = 2
    is_available: bool = True
    
    def __post_init__(self):
        if self.price_per_night < 0:
            raise ValueError("Цена не может быть отрицательной")
        if self.capacity < 1:
            raise ValueError("Вместимость должна быть не менее 1")
        # ИСПРАВЛЕНО: проверяем что room_number не None и не пустая строка
        if self.room_number is None or not self.room_number.strip():
            raise ValueError("Номер комнаты не может быть пустым")


@dataclass
class Booking:
    """Агрегат бронирования"""
    id: Optional[int] = None
    room_id: int = 0
    guest_name: str = ""
    guest_email: str = ""
    check_in: Optional[date] = None
    check_out: Optional[date] = None
    total_price: float = 0.0
    status: BookingStatus = BookingStatus.PENDING
    created_at: Optional[datetime] = field(default_factory=datetime.now)
    nights: int = 1
    room_type: str = "standard"
    cancellation_reason: Optional[str] = None
    
    def __post_init__(self):
        if self.check_in and self.check_out:
            if self.check_out <= self.check_in:
                raise ValueError("Дата выезда должна быть позже даты заезда")
            if self.total_price < 0:
                raise ValueError("Стоимость не может быть отрицательной")
            self.nights = (self.check_out - self.check_in).days
    
    def cancel(self, reason: Optional[str] = None) -> None:
        """Отмена бронирования"""
        if self.status == BookingStatus.CANCELLED:
            raise ValueError("Бронирование уже отменено")
        if self.status == BookingStatus.COMPLETED:
            raise ValueError("Нельзя отменить завершенное бронирование")
        
        self.status = BookingStatus.CANCELLED
        self.cancellation_reason = reason
    
    def confirm(self) -> None:
        """Подтверждение бронирования"""
        if self.status == BookingStatus.CANCELLED:
            raise ValueError("Нельзя подтвердить отмененное бронирование")
        self.status = BookingStatus.CONFIRMED
    
    def complete(self) -> None:
        """Завершение бронирования"""
        if self.status == BookingStatus.CANCELLED:
            raise ValueError("Нельзя завершить отмененное бронирование")
        self.status = BookingStatus.COMPLETED