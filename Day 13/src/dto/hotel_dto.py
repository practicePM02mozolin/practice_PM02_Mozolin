# dto/hotel_dto.py
from pydantic import BaseModel, field_validator
from typing import Optional
from src.domain.models import CancellationPolicy

class HotelCreateDTO(BaseModel):
    """DTO для создания отеля"""
    name: str
    address: str
    phone: str
    rating: float = 0.0

    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v: float) -> float:
        """Валидация рейтинга отеля"""
        if v < 0 or v > 5:
            raise ValueError('Рейтинг должен быть от 0 до 5')
        return v

class HotelResponseDTO(BaseModel):
    """DTO для ответа с данными отеля"""
    id: int
    name: str
    address: str
    phone: str
    rating: float
    cancellation_policy: str
    
    model_config = {"from_attributes": True}

class HotelUpdateDTO(BaseModel):
    """DTO для обновления отеля"""
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    rating: Optional[float] = None

    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v: Optional[float]) -> Optional[float]:
        """Валидация рейтинга отеля при обновлении"""
        if v is not None and (v < 0 or v > 5):
            raise ValueError('Рейтинг должен быть от 0 до 5')
        return v