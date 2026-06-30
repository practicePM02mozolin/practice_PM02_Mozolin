# src/domain/models.py
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional

class BookingStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"

class CancellationPolicy(Enum):
    """Политика отмены бронирования"""
    FREE = "free"              #Бесплатная отмена
    PARTIAL = "partial"        #Частичная компенсация (50%)
    FULL = "full"              #Полная оплата (100% штраф)

@dataclass
class Hotel:
    id: Optional[int]
    name: str
    address: str
    phone: str
    rating: float = 0.0
    cancellation_policy: CancellationPolicy = CancellationPolicy.FREE
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Room:
    id: Optional[int]
    hotel_id: int
    number: str
    capacity: int
    price_per_night: float
    is_active: bool = True
    room_type: str = "standard"

@dataclass
class Booking:
    id: Optional[int]
    room_id: int
    guest_name: str
    guest_email: str
    check_in: date
    check_out: date
    total_price: float
    status: BookingStatus = BookingStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    cancelled_at: Optional[datetime] = None
    cancellation_fee: float = 0.0