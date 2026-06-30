"""Data Transfer Objects"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from enum import Enum


@dataclass
class BookingCreateDTO:
    """DTO для создания бронирования"""
    room_id: int
    guest_name: str
    guest_email: str
    check_in: date
    check_out: date
    total_price: float
    room_type: str = "standard"
    
    def __post_init__(self):
        if self.check_out <= self.check_in:
            raise ValueError("Дата выезда должна быть позже даты заезда")
        if self.total_price < 0:
            raise ValueError("Стоимость не может быть отрицательной")
        if not self.guest_name or not self.guest_name.strip():
            raise ValueError("Имя гостя обязательно")
        if "@" not in self.guest_email:
            raise ValueError("Неверный формат email")


@dataclass
class BookingUpdateDTO:
    """DTO для обновления бронирования"""
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
    check_in: Optional[date] = None
    check_out: Optional[date] = None
    total_price: Optional[float] = None
    room_type: Optional[str] = None


@dataclass
class AnalyticsReportDTO:
    """DTO для отчета аналитики"""
    total_bookings: int
    total_revenue: float
    average_price: float
    cancellation_rate: float
    occupancy_rate: float
    top_room_types: Dict[str, int]
    monthly_trends: Dict[str, int]
    peak_season: Dict[str, Any]
    generated_at: datetime = None
    
    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now()


@dataclass
class RevenueReportDTO:
    """DTO для отчета по выручке"""
    total_revenue: float
    average_booking_value: float
    revenue_by_room_type: Dict[str, float]
    revenue_by_month: Dict[str, float]
    top_rooms: Dict[int, float]
    period_start: date
    period_end: date
    generated_at: datetime = None
    
    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now()