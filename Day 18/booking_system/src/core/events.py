"""Domain Events модуль"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class BookingCreatedEvent:
    """Событие создания бронирования"""
    booking_id: int
    guest_name: str
    guest_email: str
    room_id: int
    check_in: str
    check_out: str
    total_price: float
    occurred_at: datetime = None
    
    def __post_init__(self):
        if self.occurred_at is None:
            self.occurred_at = datetime.now()


@dataclass
class BookingCancelledEvent:
    """Событие отмены бронирования"""
    booking_id: int
    guest_name: str
    guest_email: str
    room_id: int
    reason: Optional[str] = None
    occurred_at: datetime = None
    
    def __post_init__(self):
        if self.occurred_at is None:
            self.occurred_at = datetime.now()


@dataclass
class BookingConfirmedEvent:
    """Событие подтверждения бронирования"""
    booking_id: int
    guest_name: str
    guest_email: str
    room_id: int
    occurred_at: datetime = None
    
    def __post_init__(self):
        if self.occurred_at is None:
            self.occurred_at = datetime.now()