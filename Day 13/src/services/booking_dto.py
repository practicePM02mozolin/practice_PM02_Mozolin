# src/dto/booking_dto.py
from pydantic import BaseModel, field_validator, ValidationInfo
from datetime import date, datetime
from typing import Optional

class BookingCreateDTO(BaseModel):
    room_id: int
    guest_name: str
    guest_email: str
    check_in: date
    check_out: date

    @field_validator('check_out')
    @classmethod
    def validate_dates(cls, v: date, info: ValidationInfo) -> date:
        if 'check_in' in info.data and v <= info.data['check_in']:
            raise ValueError('Дата выезда должна быть позже даты заезда')
        if 'check_in' in info.data and (v - info.data['check_in']).days > 30:
            raise ValueError('Бронирование не может превышать 30 дней')
        return v
class BookingResponseDTO(BaseModel):
    id: int
    room_id: int
    guest_name: str
    check_in: date
    check_out: date
    total_price: float
    status: str
    created_at: datetime
    cancellation_fee: float = 0.0

    model_config = {"from_attributes": True}
class BookingUpdateDTO(BaseModel):
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
class CancellationResultDTO(BaseModel):
    booking_id: int
    cancellation_fee: float
    refund_amount: float
    policy: str
    days_before_checkin: int