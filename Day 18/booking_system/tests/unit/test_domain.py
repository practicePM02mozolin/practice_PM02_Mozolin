"""Тесты для доменных сущностей"""

import pytest
from datetime import date, datetime
from src.core.domain import Booking, Guest, Room, BookingStatus


class TestGuest:
    """Тесты для сущности Guest"""
    
    def test_create_valid_guest(self):
        """Создание корректного гостя"""
        guest = Guest(
            id=1,
            name="John Doe",
            email="john@example.com",
            phone="+1234567890",
            is_vip=True
        )
        assert guest.id == 1
        assert guest.name == "John Doe"
        assert guest.email == "john@example.com"
        assert guest.phone == "+1234567890"
        assert guest.is_vip is True
    
    def test_create_guest_invalid_email(self):
        """Создание гостя с неверным email"""
        with pytest.raises(ValueError, match="Неверный формат email"):
            Guest(name="John Doe", email="invalid-email")
    
    def test_create_guest_empty_name(self):
        """Создание гостя с пустым именем"""
        with pytest.raises(ValueError, match="Имя гостя не может быть пустым"):
            Guest(name="", email="john@example.com")
    
    def test_create_guest_whitespace_name(self):
        """Создание гостя с именем из пробелов"""
        with pytest.raises(ValueError, match="Имя гостя не может быть пустым"):
            Guest(name="   ", email="john@example.com")


class TestRoom:
    """Тесты для сущности Room"""
    
    def test_create_valid_room(self):
        """Создание корректного номера"""
        room = Room(
            id=101,
            room_number="101A",
            room_type="standard",
            price_per_night=100.0,
            capacity=2,
            is_available=True
        )
        assert room.id == 101
        assert room.room_number == "101A"
        assert room.room_type == "standard"
        assert room.price_per_night == 100.0
        assert room.capacity == 2
        assert room.is_available is True
    
    def test_create_room_negative_price(self):
        """Создание номера с отрицательной ценой"""
        with pytest.raises(ValueError, match="Цена не может быть отрицательной"):
            Room(room_number="101A", price_per_night=-100.0)
    
    def test_create_room_zero_capacity(self):
        """Создание номера с нулевой вместимостью"""
        with pytest.raises(ValueError, match="Вместимость должна быть не менее 1"):
            Room(room_number="101A", capacity=0)
    
    def test_create_room_empty_number(self):
        """Создание номера с пустым номером"""
        with pytest.raises(ValueError, match="Номер комнаты не может быть пустым"):
            Room(room_number="", price_per_night=100.0)


class TestBooking:
    """Тесты для агрегата Booking"""
    
    def test_create_valid_booking(self):
        """Создание корректного бронирования"""
        check_in = date(2026, 6, 15)
        check_out = date(2026, 6, 20)
        
        booking = Booking(
            id=1,
            room_id=101,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=check_in,
            check_out=check_out,
            total_price=500.0,
            status=BookingStatus.PENDING,
            room_type="standard"
        )
        
        assert booking.id == 1
        assert booking.room_id == 101
        assert booking.guest_name == "John Doe"
        assert booking.guest_email == "john@example.com"
        assert booking.check_in == check_in
        assert booking.check_out == check_out
        assert booking.total_price == 500.0
        assert booking.status == BookingStatus.PENDING
        assert booking.nights == 5
    
    def test_create_booking_invalid_dates(self):
        """Создание бронирования с неверными датами"""
        check_in = date(2026, 6, 20)
        check_out = date(2026, 6, 15)  # Выезд раньше заезда
        
        with pytest.raises(ValueError, match="Дата выезда должна быть позже даты заезда"):
            Booking(
                room_id=101,
                guest_name="John Doe",
                guest_email="john@example.com",
                check_in=check_in,
                check_out=check_out,
                total_price=500.0
            )
    
    def test_create_booking_negative_price(self):
        """Создание бронирования с отрицательной ценой"""
        check_in = date(2026, 6, 15)
        check_out = date(2026, 6, 20)
        
        with pytest.raises(ValueError, match="Стоимость не может быть отрицательной"):
            Booking(
                room_id=101,
                guest_name="John Doe",
                guest_email="john@example.com",
                check_in=check_in,
                check_out=check_out,
                total_price=-500.0
            )
    
    def test_booking_cancel(self):
        """Отмена бронирования"""
        check_in = date(2026, 6, 15)
        check_out = date(2026, 6, 20)
        
        booking = Booking(
            room_id=101,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=check_in,
            check_out=check_out,
            total_price=500.0
        )
        
        booking.cancel("Не подходят даты")
        assert booking.status == BookingStatus.CANCELLED
        assert booking.cancellation_reason == "Не подходят даты"
    
    def test_booking_cancel_already_cancelled(self):
        """Отмена уже отмененного бронирования"""
        check_in = date(2026, 6, 15)
        check_out = date(2026, 6, 20)
        
        booking = Booking(
            room_id=101,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=check_in,
            check_out=check_out,
            total_price=500.0
        )
        booking.cancel()
        
        with pytest.raises(ValueError, match="Бронирование уже отменено"):
            booking.cancel()
    
    def test_booking_cancel_completed(self):
        """Отмена завершенного бронирования"""
        check_in = date(2026, 6, 15)
        check_out = date(2026, 6, 20)
        
        booking = Booking(
            room_id=101,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=check_in,
            check_out=check_out,
            total_price=500.0
        )
        booking.complete()
        
        with pytest.raises(ValueError, match="Нельзя отменить завершенное бронирование"):
            booking.cancel()
    
    def test_booking_confirm(self):
        """Подтверждение бронирования"""
        check_in = date(2026, 6, 15)
        check_out = date(2026, 6, 20)
        
        booking = Booking(
            room_id=101,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=check_in,
            check_out=check_out,
            total_price=500.0,
            status=BookingStatus.PENDING
        )
        
        booking.confirm()
        assert booking.status == BookingStatus.CONFIRMED
    
    def test_booking_confirm_cancelled(self):
        """Подтверждение отмененного бронирования"""
        check_in = date(2026, 6, 15)
        check_out = date(2026, 6, 20)
        
        booking = Booking(
            room_id=101,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=check_in,
            check_out=check_out,
            total_price=500.0
        )
        booking.cancel()
        
        with pytest.raises(ValueError, match="Нельзя подтвердить отмененное бронирование"):
            booking.confirm()
    
    def test_booking_complete(self):
        """Завершение бронирования"""
        check_in = date(2026, 6, 15)
        check_out = date(2026, 6, 20)
        
        booking = Booking(
            room_id=101,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=check_in,
            check_out=check_out,
            total_price=500.0,
            status=BookingStatus.CONFIRMED
        )
        
        booking.complete()
        assert booking.status == BookingStatus.COMPLETED
    
    def test_booking_complete_cancelled(self):
        """Завершение отмененного бронирования"""
        check_in = date(2026, 6, 15)
        check_out = date(2026, 6, 20)
        
        booking = Booking(
            room_id=101,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=check_in,
            check_out=check_out,
            total_price=500.0
        )
        booking.cancel()
        
        with pytest.raises(ValueError, match="Нельзя завершить отмененное бронирование"):
            booking.complete()