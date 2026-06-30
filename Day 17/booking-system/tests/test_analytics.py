# tests/test_analytics.py
import pytest
from datetime import datetime, timedelta
import math
from src.analytics import (
    calculate_average_booking_value,
    calculate_occupancy_rate,
    calculate_revenue_trend,
    calculate_cancellation_rate,
    calculate_average_stay_duration,
    detect_anomalies,
    fill_missing_values
)

# ============================================================
# Тесты для calculate_average_booking_value
# ============================================================

def test_average_booking_value_basic():
    """Базовая проверка средней стоимости"""
    bookings = [
        {'total_price': 100},
        {'total_price': 200},
        {'total_price': 300}
    ]
    result = calculate_average_booking_value(bookings)
    assert result == 200.0

def test_average_booking_value_empty():
    """Пустой список бронирований"""
    result = calculate_average_booking_value([])
    assert result == 0.0

def test_average_booking_value_single():
    """Одно бронирование"""
    bookings = [{'total_price': 150}]
    result = calculate_average_booking_value(bookings)
    assert result == 150.0

# ============================================================
# Тесты для calculate_occupancy_rate
# ============================================================

def test_occupancy_rate_basic():
    """Базовая проверка загруженности"""
    bookings = [
        {'check_in': '2026-06-10', 'check_out': '2026-06-15'},
        {'check_in': '2026-06-12', 'check_out': '2026-06-18'}
    ]
    result = calculate_occupancy_rate(bookings, 10, '2026-06-10', '2026-06-20')
    # Ожидаем: 5 дней * 1 номер + 6 дней * 1 номер = 11 / (10 * 11) * 100 = 10%
    assert result == 10.0

def test_occupancy_rate_zero_rooms():
    """Нулевое количество номеров"""
    bookings = [{'check_in': '2026-06-10', 'check_out': '2026-06-15'}]
    result = calculate_occupancy_rate(bookings, 0, '2026-06-10', '2026-06-20')
    assert result == 0.0

def test_occupancy_rate_empty_bookings():
    """Нет бронирований"""
    result = calculate_occupancy_rate([], 10, '2026-06-10', '2026-06-20')
    assert result == 0.0

# ============================================================
# Тесты для calculate_revenue_trend
# ============================================================

def test_revenue_trend_basic():
    """Базовая проверка тренда выручки"""
    bookings = [
        {'check_in': '2026-06-10', 'total_price': 100},
        {'check_in': '2026-06-15', 'total_price': 200},
        {'check_in': '2026-07-01', 'total_price': 300}
    ]
    result = calculate_revenue_trend(bookings)
    assert result == {'2026-06': 300, '2026-07': 300}

# ============================================================
# Тесты для calculate_cancellation_rate
# ============================================================

def test_cancellation_rate_basic():
    """Базовая проверка процента отмен"""
    bookings = [
        {'status': 'confirmed'},
        {'status': 'cancelled'},
        {'status': 'confirmed'},
        {'status': 'cancelled'}
    ]
    result = calculate_cancellation_rate(bookings)
    assert result == 50.0

def test_cancellation_rate_no_cancellations():
    """Нет отмен"""
    bookings = [
        {'status': 'confirmed'},
        {'status': 'confirmed'}
    ]
    result = calculate_cancellation_rate(bookings)
    assert result == 0.0

def test_cancellation_rate_empty():
    """Пустой список"""
    result = calculate_cancellation_rate([])
    assert result == 0.0

# ============================================================
# Тесты для calculate_average_stay_duration
# ============================================================

def test_average_stay_duration_basic():
    """Базовая проверка средней продолжительности"""
    bookings = [
        {'check_in': '2026-06-10', 'check_out': '2026-06-15'},
        {'check_in': '2026-06-12', 'check_out': '2026-06-14'}
    ]
    result = calculate_average_stay_duration(bookings)
    assert result == 3.5  # (5 + 2) / 2 = 3.5

def test_average_stay_duration_empty():
    """Пустой список"""
    result = calculate_average_stay_duration([])
    assert result == 0.0

# ============================================================
# Тесты для detect_anomalies
# ============================================================

def test_detect_anomalies_none():
    """Нет аномалий"""
    bookings = [
        {'total_price': 100, 'check_in': '2026-06-10', 'check_out': '2026-06-15', 'status': 'confirmed'}
    ]
    result = detect_anomalies(bookings)
    assert result == []

def test_detect_anomalies_missing_price():
    """Отсутствует цена"""
    bookings = [
        {'total_price': None, 'check_in': '2026-06-10', 'check_out': '2026-06-15', 'status': 'confirmed'}
    ]
    result = detect_anomalies(bookings)
    assert len(result) == 1
    assert 'missing_price' in result[0]['issues']

def test_detect_anomalies_nan_price():
    """Цена NaN"""
    bookings = [
        {'total_price': float('nan'), 'check_in': '2026-06-10', 'check_out': '2026-06-15', 'status': 'confirmed'}
    ]
    result = detect_anomalies(bookings)
    assert len(result) == 1
    assert 'nan_price' in result[0]['issues']

# ============================================================
# Тесты для fill_missing_values
# ============================================================

def test_fill_missing_values_basic():
    """Заполнение пропусков"""
    bookings = [
        {'total_price': None, 'status': None, 'check_in': None, 'check_out': None}
    ]
    result = fill_missing_values(bookings)
    assert result[0]['total_price'] == 0.0
    assert result[0]['status'] == 'unknown'
    assert result[0]['check_in'] is not None
    assert result[0]['check_out'] is not None