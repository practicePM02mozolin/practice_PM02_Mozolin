"""Фабрика тестовых данных"""

from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
import json
import random


class BookingDataFactory:
    """Фабрика для создания тестовых данных бронирований"""
    
    @staticmethod
    def create_booking(
        room_id: int = 101,
        guest_name: str = "John Doe",
        guest_email: str = "john@example.com",
        check_in: Optional[date] = None,
        check_out: Optional[date] = None,
        total_price: float = 1000.0,
        status: str = "confirmed",
        room_type: str = "standard",
        nights: int = 5,
        created_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Создание одного бронирования"""
        if check_in is None:
            check_in = date.today() + timedelta(days=30)
        if check_out is None:
            check_out = check_in + timedelta(days=nights)
        if created_at is None:
            created_at = datetime.now() - timedelta(days=random.randint(0, 30))
        
        return {
            'room_id': room_id,
            'guest_name': guest_name,
            'guest_email': guest_email,
            'check_in': check_in.isoformat(),
            'check_out': check_out.isoformat(),
            'total_price': total_price,
            'status': status,
            'room_type': room_type,
            'nights': nights,
            'created_at': created_at.isoformat()
        }
    
    @staticmethod
    def create_bookings(count: int = 10) -> List[Dict[str, Any]]:
        """Создание списка бронирований"""
        bookings = []
        statuses = ['confirmed', 'cancelled', 'pending', 'completed']
        room_types = ['standard', 'deluxe', 'suite', 'presidential']
        names = ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 'Charlie Wilson']
        domains = ['example.com', 'test.com', 'mail.com', 'gmail.com']
        
        for i in range(count):
            name = random.choice(names)
            domain = random.choice(domains)
            email = f"{name.lower().replace(' ', '.')}@{domain}"
            
            nights = random.randint(1, 14)
            price_per_night = random.randint(50, 500)
            
            booking = BookingDataFactory.create_booking(
                room_id=random.randint(100, 110),
                guest_name=name,
                guest_email=email,
                total_price=float(price_per_night * nights),
                status=random.choice(statuses),
                room_type=random.choice(room_types),
                nights=nights
            )
            bookings.append(booking)
        
        return bookings
    
    @staticmethod
    def create_data_with_none_values() -> List[Dict[str, Any]]:
        """Создание данных с None значениями"""
        return [
            {
                'room_id': 101,
                'guest_name': 'John Doe',
                'guest_email': 'john@example.com',
                'check_in': date.today().isoformat(),
                'check_out': (date.today() + timedelta(days=5)).isoformat(),
                'total_price': None,
                'status': 'confirmed',
                'room_type': 'standard',
                'nights': 5,
                'created_at': None
            },
            {
                'room_id': None,
                'guest_name': 'Jane Smith',
                'guest_email': 'jane@example.com',
                'check_in': None,
                'check_out': (date.today() + timedelta(days=3)).isoformat(),
                'total_price': 500.0,
                'status': 'cancelled',
                'room_type': None,
                'nights': 3,
                'created_at': datetime.now().isoformat()
            },
            {
                'room_id': 103,
                'guest_name': None,
                'guest_email': 'bob@example.com',
                'check_in': date.today().isoformat(),
                'check_out': None,
                'total_price': 750.0,
                'status': None,
                'room_type': 'deluxe',
                'nights': None,
                'created_at': datetime.now().isoformat()
            }
        ]
    
    @staticmethod
    def create_edge_case_data() -> List[Dict[str, Any]]:
        """Создание данных с граничными значениями"""
        today = date.today()
        
        return [
            # Минимальные значения
            {
                'room_id': 1,
                'guest_name': 'A',
                'guest_email': 'a@b.c',
                'check_in': today.isoformat(),
                'check_out': (today + timedelta(days=1)).isoformat(),
                'total_price': 0.0,
                'status': 'pending',
                'room_type': 'standard',
                'nights': 1,
                'created_at': datetime.now().isoformat()
            },
            # Максимальные значения
            {
                'room_id': 9999,
                'guest_name': 'X' * 100,
                'guest_email': 'x' * 50 + '@' + 'y' * 50 + '.com',
                'check_in': today.isoformat(),
                'check_out': (today + timedelta(days=365)).isoformat(),
                'total_price': 999999.99,
                'status': 'confirmed',
                'room_type': 'presidential',
                'nights': 365,
                'created_at': datetime.now().isoformat()
            },
            # Длинное бронирование
            {
                'room_id': 200,
                'guest_name': 'Long Stay Guest',
                'guest_email': 'long@stay.com',
                'check_in': today.isoformat(),
                'check_out': (today + timedelta(days=90)).isoformat(),
                'total_price': 9000.0,
                'status': 'confirmed',
                'room_type': 'suite',
                'nights': 90,
                'created_at': datetime.now().isoformat()
            }
        ]
    
    @staticmethod
    def save_to_json(bookings: List[Dict[str, Any]], filename: str = "test_data.json") -> None:
        """Сохранение данных в JSON файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(bookings, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_from_json(filename: str = "test_data.json") -> List[Dict[str, Any]]:
        """Загрузка данных из JSON файла"""
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)