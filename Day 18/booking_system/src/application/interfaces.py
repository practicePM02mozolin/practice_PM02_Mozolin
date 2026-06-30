"""Абстракции (порт-адаптер)"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date


class IBookingRepository(ABC):
    """Интерфейс репозитория бронирований"""
    
    @abstractmethod
    def get_all(self) -> List[Dict[str, Any]]:
        """Получить все бронирования"""
        pass
    
    @abstractmethod
    def get_by_id(self, booking_id: int) -> Optional[Dict[str, Any]]:
        """Получить бронирование по ID"""
        pass
    
    @abstractmethod
    def get_by_room_id(self, room_id: int) -> List[Dict[str, Any]]:
        """Получить бронирования по ID номера"""
        pass
    
    @abstractmethod
    def get_by_guest_email(self, email: str) -> List[Dict[str, Any]]:
        """Получить бронирования по email гостя"""
        pass
    
    @abstractmethod
    def get_by_date_range(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Получить бронирования по диапазону дат"""
        pass
    
    @abstractmethod
    def save(self, booking: Dict[str, Any]) -> int:
        """Сохранить бронирование"""
        pass
    
    @abstractmethod
    def update(self, booking_id: int, data: Dict[str, Any]) -> None:
        """Обновить бронирование"""
        pass
    
    @abstractmethod
    def delete(self, booking_id: int) -> None:
        """Удалить бронирование"""
        pass


class IAnalyticsService(ABC):
    """Интерфейс сервиса аналитики"""
    
    @abstractmethod
    def get_total_revenue(self, bookings: List[Dict]) -> float:
        """Рассчитать общую выручку"""
        pass
    
    @abstractmethod
    def get_average_booking_value(self, bookings: List[Dict]) -> float:
        """Рассчитать среднюю стоимость бронирования"""
        pass
    
    @abstractmethod
    def get_occupancy_rate(self, total_rooms: int, booked_rooms: int) -> float:
        """Рассчитать процент загрузки"""
        pass
    
    @abstractmethod
    def get_cancellation_rate(self, bookings: List[Dict]) -> float:
        """Рассчитать процент отмен"""
        pass
    
    @abstractmethod
    def get_booking_trends(self, bookings: List[Dict]) -> Dict[str, int]:
        """Анализ трендов по месяцам"""
        pass
    
    @abstractmethod
    def detect_anomalies(self, bookings: List[Dict]) -> List[Dict]:
        """Обнаружение аномалий"""
        pass


class IUnitOfWork(ABC):
    """Интерфейс Unit of Work"""
    
    @abstractmethod
    def begin(self) -> None:
        """Начать транзакцию"""
        pass
    
    @abstractmethod
    def commit(self) -> None:
        """Подтвердить транзакцию"""
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        """Откатить транзакцию"""
        pass
    
    @abstractmethod
    def get_repository(self, repo_type: str) -> IBookingRepository:
        """Получить репозиторий"""
        pass