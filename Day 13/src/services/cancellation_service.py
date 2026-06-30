# src/services/cancellation_service.py
from abc import ABC, abstractmethod
from datetime import date
from src.domain.models import Booking, CancellationPolicy
from src.domain.exceptions import CancellationNotAllowedError

class CancellationContext:
    """Контекст для политики отмены"""
    
    def __init__(self, booking: Booking, hotel_policy: CancellationPolicy):
        self.booking = booking
        self.hotel_policy = hotel_policy
        self.days_before_checkin = (booking.check_in - date.today()).days  
    def get_policy(self) -> 'CancellationPolicyState':
        """Получить подходящую политику отмены"""
        if self.days_before_checkin >= 7:
            return FreeCancellationState()
        elif self.days_before_checkin >= 3:
            return PartialCancellationState()
        elif self.days_before_checkin >= 1:
            return FullCancellationState()
        else:
            return NoCancellationState()
class CancellationPolicyState(ABC):
    """Базовый класс для политик отмены"""
    
    @abstractmethod
    def calculate_fee(self, context: CancellationContext) -> float:
        pass
    @abstractmethod
    def get_policy_name(self) -> str:
        pass
class FreeCancellationState(CancellationPolicyState):
    """Бесплатная отмена (за 7+ дней до заезда)"""
    
    def calculate_fee(self, context: CancellationContext) -> float:
        return 0.0
    
    def get_policy_name(self) -> str:
        return "Бесплатная отмена"
class PartialCancellationState(CancellationPolicyState):
    """Частичная компенсация (50% штраф за 3-6 дней до заезда)"""
    
    def calculate_fee(self, context: CancellationContext) -> float:
        return context.booking.total_price * 0.5
    
    def get_policy_name(self) -> str:
        return "Частичная компенсация (50%)"
class FullCancellationState(CancellationPolicyState):
    """Полная оплата (100% штраф за 1-2 дня до заезда)"""
    
    def calculate_fee(self, context: CancellationContext) -> float:
        return context.booking.total_price
    def get_policy_name(self) -> str:
        return "Полная оплата (100%)"

class NoCancellationState(CancellationPolicyState):
    """Отмена в день заезда или позже (отмена запрещена)"""
    
    def calculate_fee(self, context: CancellationContext) -> float:
        raise CancellationNotAllowedError(
            f"Отмена бронирования невозможна в день заезда или позже. "
            f"Заезд: {context.booking.check_in}"
        )
    
    def get_policy_name(self) -> str:
        return "Отмена запрещена"