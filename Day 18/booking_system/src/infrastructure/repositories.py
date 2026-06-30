"""Реализация репозиториев"""

from typing import List, Optional, Dict, Any
from datetime import date
from src.application.interfaces import IBookingRepository


class InMemoryBookingRepository(IBookingRepository):
    """In-memory репозиторий бронирований"""
    
    def __init__(self):
        self._bookings: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Получить все бронирования"""
        return list(self._bookings.values())
    
    def get_by_id(self, booking_id: int) -> Optional[Dict[str, Any]]:
        """Получить бронирование по ID"""
        return self._bookings.get(booking_id)
    
    def get_by_room_id(self, room_id: int) -> List[Dict[str, Any]]:
        """Получить бронирования по ID номера"""
        return [
            booking for booking in self._bookings.values()
            if booking.get('room_id') == room_id
        ]
    
    def get_by_guest_email(self, email: str) -> List[Dict[str, Any]]:
        """Получить бронирования по email гостя"""
        return [
            booking for booking in self._bookings.values()
            if booking.get('guest_email', '').lower() == email.lower()
        ]
    
    def get_by_date_range(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Получить бронирования по диапазону дат"""
        result = []
        for booking in self._bookings.values():
            check_in = booking.get('check_in')
            check_out = booking.get('check_out')
            
            if check_in and check_out:
                if isinstance(check_in, str):
                    check_in_date = date.fromisoformat(check_in)
                elif isinstance(check_in, date):
                    check_in_date = check_in
                else:
                    continue
                
                if isinstance(check_out, str):
                    check_out_date = date.fromisoformat(check_out)
                elif isinstance(check_out, date):
                    check_out_date = check_out
                else:
                    continue
                
                if not (check_out_date <= start_date or check_in_date >= end_date):
                    result.append(booking)
        
        return result
    
    def save(self, booking: Dict[str, Any]) -> int:
        """Сохранить бронирование"""
        booking_id = self._next_id
        self._next_id += 1
        booking_with_id = dict(booking)
        booking_with_id['id'] = booking_id
        self._bookings[booking_id] = booking_with_id
        return booking_id
    
    def update(self, booking_id: int, data: Dict[str, Any]) -> None:
        """Обновить бронирование"""
        if booking_id not in self._bookings:
            raise ValueError(f"Бронирование с ID {booking_id} не найдено")
        
        for key, value in data.items():
            self._bookings[booking_id][key] = value
    
    def delete(self, booking_id: int) -> None:
        """Удалить бронирование"""
        if booking_id in self._bookings:
            del self._bookings[booking_id]