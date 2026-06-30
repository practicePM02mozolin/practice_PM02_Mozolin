"""Core модуль - доменные сущности и исключения"""

from src.core.domain import Booking, Room, Guest, BookingStatus
from src.core.exceptions import (
    BookingNotFoundError,
    RoomUnavailableError,
    InvalidBookingDataError,
    AnalyticsError
)
from src.core.events import (
    BookingCreatedEvent,
    BookingCancelledEvent,
    BookingConfirmedEvent
)

__all__ = [
    "Booking",
    "Room",
    "Guest",
    "BookingStatus",
    "BookingNotFoundError",
    "RoomUnavailableError",
    "InvalidBookingDataError",
    "AnalyticsError",
    "BookingCreatedEvent",
    "BookingCancelledEvent",
    "BookingConfirmedEvent",
]