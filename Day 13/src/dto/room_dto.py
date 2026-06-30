# dto/room_dto.py
from pydantic import BaseModel, field_validator
from typing import Optional

class RoomCreateDTO(BaseModel):
    """DTO для создания номера"""
    hotel_id: int
    number: str
    capacity: int
    price_per_night: float
    room_type: str = "standard"

    @field_validator('capacity')
    @classmethod
    def validate_capacity(cls, v: int) -> int:
        """Валидация вместимости номера"""
        if v < 1:
            raise ValueError('Вместимость должна быть не менее 1')
        return v

    @field_validator('price_per_night')
    @classmethod
    def validate_price(cls, v: float) -> float:
        """Валидация цены за ночь"""
        if v <= 0:
            raise ValueError('Цена должна быть больше 0')
        return v

class RoomResponseDTO(BaseModel):
    """DTO для ответа с данными номера"""
    id: int
    hotel_id: int
    number: str
    capacity: int
    price_per_night: float
    is_active: bool
    room_type: str
    
    model_config = {"from_attributes": True}

class RoomUpdateDTO(BaseModel):
    """DTO для обновления номера"""
    number: Optional[str] = None
    capacity: Optional[int] = None
    price_per_night: Optional[float] = None
    is_active: Optional[bool] = None
    room_type: Optional[str] = None

    @field_validator('capacity')
    @classmethod
    def validate_capacity(cls, v: Optional[int]) -> Optional[int]:
        """Валидация вместимости номера при обновлении"""
        if v is not None and v < 1:
            raise ValueError('Вместимость должна быть не менее 1')
        return v

    @field_validator('price_per_night')
    @classmethod
    def validate_price(cls, v: Optional[float]) -> Optional[float]:
        """Валидация цены за ночь при обновлении"""
        if v is not None and v <= 0:
            raise ValueError('Цена должна быть больше 0')
        return v