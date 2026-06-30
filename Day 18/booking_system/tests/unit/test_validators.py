# tests/unit/test_validators.py
"""Тесты для валидаторов"""

import pytest
from datetime import date, datetime, timedelta
from src.utils.validators import (
    validate_email,
    validate_phone,
    validate_date_range,
    validate_price,
    validate_booking_data
)


class TestValidateEmail:
    """Тесты для валидации email"""
    
    def test_valid_emails(self):
        """Проверка корректных email адресов"""
        valid_emails = [
            "user@example.com",
            "john.doe@company.co.uk",
            "user_name@domain.com",
            "user+tag@domain.com",
            "user@sub.domain.com"
        ]
        for email in valid_emails:
            assert validate_email(email) is True
    
    def test_invalid_emails(self):
        """Проверка некорректных email адресов"""
        invalid_emails = [
            "",
            "user",
            "user@",
            "@domain.com",
            "user@domain",
            "user@domain.",
            "user@.com",
            "user name@domain.com"
        ]
        for email in invalid_emails:
            assert validate_email(email) is False
    
    def test_email_none(self):
        """Проверка None как email"""
        assert validate_email(None) is False
    
    def test_email_with_spaces(self):
        """Проверка email с пробелами"""
        assert validate_email(" user@domain.com ") is True


class TestValidatePhone:
    """Тесты для валидации телефона"""
    
    def test_valid_phones(self):
        """Проверка корректных номеров телефонов"""
        valid_phones = [
            "+1234567890",
            "1234567890",
            "+7 (123) 456-78-90",
            "8-123-456-7890",
            "+1-234-567-8900",
        ]
        for phone in valid_phones:
            assert validate_phone(phone) is True
    
    def test_invalid_phones(self):
        """Проверка некорректных номеров телефонов"""
        invalid_phones = [
            "",
            "123",
            "123456789",
            "1234567890123456",
            "abc123",
        ]
        for phone in invalid_phones:
            assert validate_phone(phone) is False
    
    def test_phone_none(self):
        """Проверка None как телефон"""
        assert validate_phone(None) is False


class TestValidateDateRange:
    """Тесты для валидации диапазона дат"""
    
    def test_valid_date_range(self):
        """Проверка корректного диапазона дат"""
        today = date.today()
        future = today + timedelta(days=5)
        is_valid, error = validate_date_range(today, future)
        assert is_valid is True
        assert error is None
    
    def test_invalid_date_range_check_out_before_check_in(self):
        """Проверка когда выезд раньше заезда"""
        check_in = date(2026, 6, 20)
        check_out = date(2026, 6, 15)
        is_valid, error = validate_date_range(check_in, check_out)
        assert is_valid is False
        assert error == "Дата выезда должна быть позже даты заезда"
    
    def test_invalid_date_range_same_day(self):
        """Проверка когда заезд и выезд в один день"""
        check_in = date(2026, 6, 15)
        check_out = date(2026, 6, 15)
        is_valid, error = validate_date_range(check_in, check_out)
        assert is_valid is False
        assert error == "Дата выезда должна быть позже даты заезда"
    
    def test_invalid_date_range_past(self):
        """Проверка когда заезд в прошлом"""
        past = date(2020, 1, 1)
        future = date(2020, 1, 5)
        is_valid, error = validate_date_range(past, future)
        assert is_valid is False
        assert error == "Дата заезда не может быть в прошлом"
    
    def test_date_range_with_none(self):
        """Проверка с None в датах"""
        is_valid, error = validate_date_range(None, date.today())
        assert is_valid is False
        assert error == "Даты не могут быть пустыми"


class TestValidatePrice:
    """Тесты для валидации цены"""
    
    def test_valid_prices(self):
        """Проверка корректных цен"""
        valid_prices = [0.0, 100.0, 1000.5, 999.99]
        for price in valid_prices:
            assert validate_price(price) is True
    
    def test_invalid_prices(self):
        """Проверка некорректных цен"""
        assert validate_price(-10.0) is False
        assert validate_price(None) is False
        assert validate_price("100") is False
        assert validate_price(float('nan')) is False


class TestValidateBookingData:
    """Тесты для валидации данных бронирования"""
    
    def test_valid_booking_data(self):
        """Проверка корректных данных бронирования"""
        # ИСПРАВЛЕНО: используем даты в будущем
        future_date = date.today() + timedelta(days=30)
        data = {
            'room_id': 101,
            'guest_name': 'John Doe',
            'guest_email': 'john@example.com',
            'check_in': future_date,
            'check_out': future_date + timedelta(days=5),
            'total_price': 500.0
        }
        is_valid, error = validate_booking_data(data)
        assert is_valid is True
        assert error is None
    
    def test_missing_required_field(self):
        """Проверка с отсутствием обязательного поля"""
        future_date = date.today() + timedelta(days=30)
        data = {
            'room_id': 101,
            'guest_name': 'John Doe',
            'guest_email': 'john@example.com',
            'check_in': future_date,
            'check_out': future_date + timedelta(days=5)
            # total_price отсутствует
        }
        is_valid, error = validate_booking_data(data)
        assert is_valid is False
        assert "Отсутствует обязательное поле" in error
    
    def test_invalid_room_id(self):
        """Проверка с неверным ID номера"""
        future_date = date.today() + timedelta(days=30)
        data = {
            'room_id': -1,
            'guest_name': 'John Doe',
            'guest_email': 'john@example.com',
            'check_in': future_date,
            'check_out': future_date + timedelta(days=5),
            'total_price': 500.0
        }
        is_valid, error = validate_booking_data(data)
        assert is_valid is False
        assert error == "Некорректный ID номера"
    
    def test_empty_guest_name(self):
        """Проверка с пустым именем гостя"""
        future_date = date.today() + timedelta(days=30)
        data = {
            'room_id': 101,
            'guest_name': '',
            'guest_email': 'john@example.com',
            'check_in': future_date,
            'check_out': future_date + timedelta(days=5),
            'total_price': 500.0
        }
        is_valid, error = validate_booking_data(data)
        assert is_valid is False
        assert error == "Имя гостя не может быть пустым"
    
    def test_invalid_email(self):
        """Проверка с неверным email"""
        future_date = date.today() + timedelta(days=30)
        data = {
            'room_id': 101,
            'guest_name': 'John Doe',
            'guest_email': 'invalid-email',
            'check_in': future_date,
            'check_out': future_date + timedelta(days=5),
            'total_price': 500.0
        }
        is_valid, error = validate_booking_data(data)
        assert is_valid is False
        assert error == "Некорректный email адрес"
    
    def test_negative_price(self):
        """Проверка с отрицательной ценой"""
        future_date = date.today() + timedelta(days=30)
        data = {
            'room_id': 101,
            'guest_name': 'John Doe',
            'guest_email': 'john@example.com',
            'check_in': future_date,
            'check_out': future_date + timedelta(days=5),
            'total_price': -500.0
        }
        is_valid, error = validate_booking_data(data)
        assert is_valid is False
        assert error == "Некорректная цена"