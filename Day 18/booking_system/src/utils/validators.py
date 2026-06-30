"""Валидаторы"""

from datetime import date, datetime
import re
from typing import Optional, Tuple


def validate_email(email: str) -> bool:
    """
    Проверка корректности email адреса.
    
    Args:
        email: Email адрес для проверки
        
    Returns:
        True если email корректный, иначе False
    """
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_phone(phone: str) -> bool:
    """
    Проверка корректности номера телефона.
    
    Args:
        phone: Номер телефона для проверки
        
    Returns:
        True если номер корректный, иначе False
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Убираем все нецифровые символы
    digits = re.sub(r'\D', '', phone)
    
    # Проверяем длину (от 10 до 15 цифр)
    return 10 <= len(digits) <= 15


def validate_date_range(check_in: date, check_out: date) -> Tuple[bool, Optional[str]]:
    """
    Проверка корректности диапазона дат.
    
    Args:
        check_in: Дата заезда
        check_out: Дата выезда
        
    Returns:
        (is_valid, error_message)
    """
    if check_in is None or check_out is None:
        return False, "Даты не могут быть пустыми"
    
    if not isinstance(check_in, date) or not isinstance(check_out, date):
        return False, "Неверный формат даты"
    
    if check_out <= check_in:
        return False, "Дата выезда должна быть позже даты заезда"
    
    if check_in < date.today():
        return False, "Дата заезда не может быть в прошлом"
    
    return True, None


def validate_price(price: float) -> bool:
    """
    Проверка корректности цены.
    
    Args:
        price: Цена для проверки
        
    Returns:
        True если цена корректная, иначе False
    """
    if price is None:
        return False
    
    if not isinstance(price, (int, float)):
        return False
    
    if price < 0:
        return False
    
    if isinstance(price, float) and (price != price):  # NaN check
        return False
    
    return True


def validate_booking_data(data: dict) -> Tuple[bool, Optional[str]]:
    """
    Проверка данных бронирования.
    
    Args:
        data: Данные для проверки
        
    Returns:
        (is_valid, error_message)
    """
    required_fields = ['room_id', 'guest_name', 'guest_email', 'check_in', 'check_out', 'total_price']
    
    for field in required_fields:
        if field not in data or data[field] is None:
            return False, f"Отсутствует обязательное поле: {field}"
    
    if not isinstance(data['room_id'], int) or data['room_id'] <= 0:
        return False, "Некорректный ID номера"
    
    if not data['guest_name'] or not data['guest_name'].strip():
        return False, "Имя гостя не может быть пустым"
    
    if not validate_email(data['guest_email']):
        return False, "Некорректный email адрес"
    
    if not isinstance(data['total_price'], (int, float)) or data['total_price'] < 0:
        return False, "Некорректная цена"
    
    # Проверка дат
    if isinstance(data['check_in'], str):
        try:
            check_in = date.fromisoformat(data['check_in'])
        except ValueError:
            return False, "Неверный формат даты заезда"
    else:
        check_in = data['check_in']
    
    if isinstance(data['check_out'], str):
        try:
            check_out = date.fromisoformat(data['check_out'])
        except ValueError:
            return False, "Неверный формат даты выезда"
    else:
        check_out = data['check_out']
    
    is_valid, error = validate_date_range(check_in, check_out)
    if not is_valid:
        return False, error
    
    return True, None