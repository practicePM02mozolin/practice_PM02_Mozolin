# src/analytics.py
"""
Модуль аналитики по бронированиям для системы управления отелями
"""
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import math
import json


def calculate_average_booking_value(bookings: List[Dict[str, Any]]) -> float:
    """
    Рассчитать среднюю стоимость бронирования.
    
    Args:
        bookings: Список бронирований с полем 'total_price'
    
    Returns:
        Средняя стоимость бронирования
    """
    if not bookings:
        return 0.0
    
    # ОШИБКА 1: Не обрабатывает None значения в total_price
    # ОШИБКА 2: Не обрабатывает NaN значения
    total = sum(booking['total_price'] for booking in bookings)
    return total / len(bookings)


def calculate_occupancy_rate(bookings: List[Dict[str, Any]], 
                            total_rooms: int,
                            start_date: str,
                            end_date: str) -> float:
    """
    Рассчитать загруженность отеля за период.
    
    Args:
        bookings: Список бронирований с check_in и check_out
        total_rooms: Общее количество номеров
        start_date: Начальная дата периода (строка)
        end_date: Конечная дата периода (строка)
    
    Returns:
        Процент загруженности (0-100)
    """
    if total_rooms <= 0:
        return 0.0
    
    # ОШИБКА 3: Не обрабатывает None/null значения в датах
    # ОШИБКА 4: Деление на ноль при total_rooms == 0 уже обработано,
    #           но есть другие проблемы
    
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    total_days = (end - start).days + 1
    
    if total_days <= 0:
        return 0.0
    
    occupied_room_days = 0
    for booking in bookings:
        # ОШИБКА 5: Не проверяет наличие ключей 'check_in', 'check_out'
        check_in = datetime.fromisoformat(booking['check_in'])
        check_out = datetime.fromisoformat(booking['check_out'])
        
        # Пересечение с периодом
        if check_out > start and check_in < end:
            overlap_start = max(check_in, start)
            overlap_end = min(check_out, end)
            days = (overlap_end - overlap_start).days
            if days > 0:
                occupied_room_days += days
    
    return (occupied_room_days / (total_rooms * total_days)) * 100


def calculate_revenue_trend(bookings: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Рассчитать тренд выручки по месяцам.
    
    Returns:
        Словарь {месяц: выручка}
    """
    # ОШИБКА 6: Не обрабатывает пустой список
    # ОШИБКА 7: Не обрабатывает None в датах
    # ОШИБКА 8: Не обрабатывает NaN в total_price
    
    trend = {}
    for booking in bookings:
        if 'check_in' not in booking or 'total_price' not in booking:
            continue
        
        # ОШИБКА 9: Нет проверки на None в booking['check_in']
        date = datetime.fromisoformat(booking['check_in'])
        month_key = date.strftime("%Y-%m")
        
        # ОШИБКА 10: Не обрабатывает None в booking['total_price']
        trend[month_key] = trend.get(month_key, 0) + booking['total_price']
    
    return trend


def calculate_cancellation_rate(bookings: List[Dict[str, Any]]) -> float:
    """
    Рассчитать процент отмененных бронирований.
    
    Returns:
        Процент отмен (0-100)
    """
    if not bookings:
        return 0.0
    
    # ОШИБКА 11: Не обрабатывает None в статусе
    # ОШИБКА 12: Не обрабатывает отсутствие ключа 'status'
    cancelled = sum(1 for b in bookings if b['status'] == 'cancelled')
    return (cancelled / len(bookings)) * 100


def calculate_average_stay_duration(bookings: List[Dict[str, Any]]) -> float:
    """
    Рассчитать среднюю продолжительность пребывания в днях.
    
    Returns:
        Среднее количество дней
    """
    if not bookings:
        return 0.0
    
    # ОШИБКА 13: Не обрабатывает None в датах
    # ОШИБКА 14: Не обрабатывает отсутствие ключей
    
    total_days = 0
    valid_bookings = 0
    
    for booking in bookings:
        try:
            check_in = datetime.fromisoformat(booking['check_in'])
            check_out = datetime.fromisoformat(booking['check_out'])
            days = (check_out - check_in).days
            if days > 0:
                total_days += days
                valid_bookings += 1
        except (KeyError, ValueError, TypeError):
            continue
    
    if valid_bookings == 0:
        return 0.0
    
    return total_days / valid_bookings


def detect_anomalies(bookings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Обнаружить аномалии в данных бронирований.
    
    Returns:
        Список аномальных бронирований с описанием проблемы
    """
    anomalies = []
    
    for booking in bookings:
        issues = []
        
        # Проверка на None/NaN
        if booking.get('total_price') is None:
            issues.append("missing_price")
        elif isinstance(booking['total_price'], float) and math.isnan(booking['total_price']):
            issues.append("nan_price")
        
        # Проверка дат
        check_in = booking.get('check_in')
        check_out = booking.get('check_out')
        
        if check_in is None:
            issues.append("missing_check_in")
        if check_out is None:
            issues.append("missing_check_out")
        
        # Проверка статуса
        if booking.get('status') is None:
            issues.append("missing_status")
        
        if issues:
            booking_copy = booking.copy()
            booking_copy['issues'] = issues
            anomalies.append(booking_copy)
    
    return anomalies


def fill_missing_values(bookings: List[Dict[str, Any]], 
                        default_price: float = 0.0,
                        default_status: str = "unknown") -> List[Dict[str, Any]]:
    """
    Заполнить пропущенные значения в данных бронирований.
    
    Returns:
        Список бронирований с заполненными значениями
    """
    # ОШИБКА 15: Не обрабатывает None в bookings
    # ОШИБКА 16: Не создает копию, изменяет исходные данные
    
    for booking in bookings:
        if booking.get('total_price') is None:
            booking['total_price'] = default_price
        
        if booking.get('status') is None:
            booking['status'] = default_status
        
        if booking.get('check_in') is None:
            booking['check_in'] = datetime.now().isoformat()
        
        if booking.get('check_out') is None:
            booking['check_out'] = (datetime.now() + timedelta(days=1)).isoformat()
    
    return bookings