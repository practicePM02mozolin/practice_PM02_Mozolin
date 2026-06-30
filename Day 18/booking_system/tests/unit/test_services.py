# tests/unit/test_services.py
"""Тесты для сервиса аналитики"""

import pytest
from datetime import datetime, date, timedelta
import math
from src.application.services import AnalyticsService
from src.core.exceptions import AnalyticsError


class MockBookingRepository:
    """Мок репозитория для тестирования"""
    
    def __init__(self, bookings=None):
        self.bookings = bookings or []
    
    def get_all(self):
        return self.bookings
    
    def get_by_id(self, booking_id):
        for booking in self.bookings:
            if booking.get('id') == booking_id:
                return booking
        return None
    
    def save(self, booking):
        booking['id'] = len(self.bookings) + 1
        self.bookings.append(booking)
        return booking['id']


@pytest.fixture
def service():
    """Фикстура для сервиса аналитики"""
    repository = MockBookingRepository()
    return AnalyticsService(repository)


@pytest.fixture
def sample_bookings():
    """Фикстура с тестовыми бронированиями"""
    return [
        {
            'id': 1,
            'room_id': 101,
            'room_type': 'standard',
            'guest_name': 'John Doe',
            'guest_email': 'john@example.com',
            'total_price': 1000.0,
            'status': 'confirmed',
            'check_in': '2026-05-01',
            'check_out': '2026-05-06',
            'created_at': '2026-05-01T10:00:00',
            'nights': 6
        },
        {
            'id': 2,
            'room_id': 102,
            'room_type': 'deluxe',
            'guest_name': 'Jane Smith',
            'guest_email': 'jane@example.com',
            'total_price': 1500.0,
            'status': 'cancelled',
            'check_in': '2026-05-02',
            'check_out': '2026-05-07',
            'created_at': '2026-05-02T14:30:00',
            'nights': 6
        },
        {
            'id': 3,
            'room_id': 101,
            'room_type': 'standard',
            'guest_name': 'Bob Johnson',
            'guest_email': 'bob@example.com',
            'total_price': 1200.0,
            'status': 'confirmed',
            'check_in': '2026-06-01',
            'check_out': '2026-06-05',
            'created_at': '2026-06-01T09:00:00',
            'nights': 5
        },
        {
            'id': 4,
            'room_id': 103,
            'room_type': 'suite',
            'guest_name': 'Alice Brown',
            'guest_email': 'alice@example.com',
            'total_price': 2000.0,
            'status': 'confirmed',
            'check_in': '2026-06-10',
            'check_out': '2026-06-15',
            'created_at': '2026-06-10T16:00:00',
            'nights': 6
        }
    ]


# ============= ТЕСТЫ ДЛЯ GET_TOTAL_REVENUE =============

def test_get_total_revenue(sample_bookings, service):
    """Тест расчета общей выручки"""
    result = service.get_total_revenue(sample_bookings)
    assert result == 5700.0


def test_get_total_revenue_with_none_values(service):
    """Тест с None значениями в total_price"""
    bookings = [
        {'total_price': None},
        {'total_price': 1000.0},
        {'total_price': None},
        {'total_price': 500.0}
    ]
    result = service.get_total_revenue(bookings)
    assert result == 1500.0


def test_get_total_revenue_with_nan_values(service):
    """Тест с NaN значениями в total_price"""
    bookings = [
        {'total_price': float('nan')},
        {'total_price': 1000.0},
        {'total_price': float('nan')}
    ]
    result = service.get_total_revenue(bookings)
    assert result == 1000.0


def test_get_total_revenue_empty_list(service):
    """Тест с пустым списком"""
    result = service.get_total_revenue([])
    assert result == 0.0


def test_get_total_revenue_missing_key(service):
    """Тест с отсутствием ключа total_price"""
    bookings = [
        {'some_other_field': 100},
        {'total_price': 2000.0}
    ]
    result = service.get_total_revenue(bookings)
    assert result == 2000.0


# ============= ТЕСТЫ ДЛЯ GET_AVERAGE_BOOKING_VALUE =============

def test_get_average_booking_value(sample_bookings, service):
    """Тест расчета средней стоимости бронирования"""
    result = service.get_average_booking_value(sample_bookings)
    assert result == 1425.0


def test_get_average_booking_value_empty_list(service):
    """Тест с пустым списком бронирований"""
    result = service.get_average_booking_value([])
    assert result == 0.0


def test_get_average_booking_value_single_booking(service):
    """Тест с одним бронированием"""
    bookings = [{'total_price': 1000.0}]
    result = service.get_average_booking_value(bookings)
    assert result == 1000.0


# ============= ТЕСТЫ ДЛЯ GET_OCCUPANCY_RATE =============

def test_get_occupancy_rate(service):
    """Тест расчета загрузки отеля"""
    result = service.get_occupancy_rate(100, 75)
    assert result == 75.0


def test_get_occupancy_rate_zero_rooms(service):
    """Тест с нулевым количеством номеров"""
    result = service.get_occupancy_rate(0, 0)
    assert result == 0.0


def test_get_occupancy_rate_negative_rooms(service):
    """Тест с отрицательным количеством номеров"""
    result = service.get_occupancy_rate(-10, 5)
    assert result == 0.0


def test_get_occupancy_rate_negative_booked(service):
    """Тест с отрицательным количеством забронированных номеров"""
    result = service.get_occupancy_rate(100, -10)
    assert result == 0.0


def test_get_occupancy_rate_booked_more_than_total(service):
    """Тест когда забронировано больше чем есть номеров"""
    result = service.get_occupancy_rate(50, 75)
    assert result == 100.0


# ============= ТЕСТЫ ДЛЯ GET_CANCELLATION_RATE =============

def test_get_cancellation_rate(sample_bookings, service):
    """Тест расчета процента отмен"""
    result = service.get_cancellation_rate(sample_bookings)
    assert result == 25.0


def test_get_cancellation_rate_empty_list(service):
    """Тест с пустым списком"""
    result = service.get_cancellation_rate([])
    assert result == 0.0


def test_get_cancellation_rate_no_cancellations(service):
    """Тест без отмен"""
    bookings = [
        {'status': 'confirmed'},
        {'status': 'confirmed'},
        {'status': 'confirmed'}
    ]
    result = service.get_cancellation_rate(bookings)
    assert result == 0.0


def test_get_cancellation_rate_all_cancellations(service):
    """Тест все отменены"""
    bookings = [
        {'status': 'cancelled'},
        {'status': 'cancelled'},
        {'status': 'cancelled'}
    ]
    result = service.get_cancellation_rate(bookings)
    assert result == 100.0


def test_get_cancellation_rate_with_none_status(service):
    """Тест с None в статусе"""
    bookings = [
        {'status': None},
        {'status': 'cancelled'},
        {'status': 'confirmed'}
    ]
    result = service.get_cancellation_rate(bookings)
    assert result == 50.0


# ============= ТЕСТЫ ДЛЯ GET_BOOKING_TRENDS =============

def test_get_booking_trends(sample_bookings, service):
    """Тест анализа трендов бронирований"""
    result = service.get_booking_trends(sample_bookings)
    expected = {'2026-05': 2, '2026-06': 2}
    assert result == expected


def test_get_booking_trends_empty_list(service):
    """Тест с пустым списком"""
    result = service.get_booking_trends([])
    assert result == {}


def test_get_booking_trends_with_none_dates(service):
    """Тест с None значениями в датах"""
    bookings = [
        {'created_at': None},
        {'created_at': '2026-06-01T10:00:00'},
        {'created_at': None}
    ]
    result = service.get_booking_trends(bookings)
    expected = {'2026-06': 1}
    assert result == expected


def test_get_booking_trends_with_datetime_objects(service):
    """Тест с datetime объектами"""
    bookings = [
        {'created_at': datetime(2026, 6, 1, 10, 0, 0)},
        {'created_at': datetime(2026, 6, 2, 14, 30, 0)},
        {'created_at': datetime(2026, 7, 1, 9, 0, 0)}
    ]
    result = service.get_booking_trends(bookings)
    expected = {'2026-06': 2, '2026-07': 1}
    assert result == expected


def test_get_booking_trends_missing_key(service):
    """Тест с отсутствием ключа created_at"""
    bookings = [
        {'other_field': 'value'},
        {'created_at': '2026-06-01T10:00:00'}
    ]
    result = service.get_booking_trends(bookings)
    expected = {'2026-06': 1}
    assert result == expected


# ============= ТЕСТЫ ДЛЯ GET_REVENUE_BY_ROOM_TYPE =============

def test_get_revenue_by_room_type(sample_bookings, service):
    """Тест анализа выручки по типам номеров"""
    result = service.get_revenue_by_room_type(sample_bookings)
    expected = {
        'standard': 2200.0,
        'deluxe': 1500.0,
        'suite': 2000.0
    }
    assert result == expected


def test_get_revenue_by_room_type_missing_key(service):
    """Тест с отсутствием ключа room_type"""
    bookings = [
        {'total_price': 1000.0},
        {'room_type': 'standard', 'total_price': 2000.0}
    ]
    result = service.get_revenue_by_room_type(bookings)
    expected = {'unknown': 1000.0, 'standard': 2000.0}
    assert result == expected


def test_get_revenue_by_room_type_empty_list(service):
    """Тест с пустым списком"""
    result = service.get_revenue_by_room_type([])
    assert result == {}


def test_get_revenue_by_room_type_with_none_values(service):
    """Тест с None значениями"""
    bookings = [
        {'room_type': None, 'total_price': 1000.0},
        {'room_type': 'standard', 'total_price': None},
        {'room_type': 'deluxe', 'total_price': 2000.0}
    ]
    result = service.get_revenue_by_room_type(bookings)
    expected = {'unknown': 1000.0, 'deluxe': 2000.0}
    assert result == expected


# ============= ТЕСТЫ ДЛЯ GET_PEAK_SEASON_ANALYSIS =============

def test_get_peak_season_analysis(sample_bookings, service):
    """Тест анализа пиковых сезонов"""
    result = service.get_peak_season_analysis(sample_bookings)
    expected = {
        'peak_month': 6,
        'peak_count': 2,
        'low_month': 5,
        'low_count': 2
    }
    assert result == expected


def test_get_peak_season_analysis_empty_list(service):
    """Тест с пустым списком"""
    result = service.get_peak_season_analysis([])
    assert result == {}


def test_get_peak_season_analysis_with_none_dates(service):
    """Тест с None в датах"""
    bookings = [
        {'check_in': None},
        {'check_in': '2026-06-15'},
        {'check_in': '2026-07-10'}
    ]
    result = service.get_peak_season_analysis(bookings)
    # Оба месяца имеют по 1 бронированию, порядок не важен
    assert result['peak_count'] == 1
    assert result['low_count'] == 1
    # Так как оба месяца имеют одинаковое количество, берется первый (6)
    # Просто проверяем что это валидный месяц
    assert result['peak_month'] in [6, 7]
    assert result['low_month'] in [6, 7]


def test_get_peak_season_analysis_with_date_objects(service):
    """Тест с date объектами"""
    bookings = [
        {'check_in': date(2026, 6, 1)},
        {'check_in': date(2026, 6, 15)},
        {'check_in': date(2026, 7, 1)}
    ]
    result = service.get_peak_season_analysis(bookings)
    expected = {
        'peak_month': 6,
        'peak_count': 2,
        'low_month': 7,
        'low_count': 1
    }
    assert result == expected


# ============= ТЕСТЫ ДЛЯ GET_GUEST_RETENTION_RATE =============

def test_get_guest_retention_rate(sample_bookings, service):
    """Тест расчета повторных гостей"""
    result = service.get_guest_retention_rate(sample_bookings)
    assert result == 0.0


def test_get_guest_retention_rate_empty_list(service):
    """Тест с пустым списком"""
    result = service.get_guest_retention_rate([])
    assert result == 0.0


def test_get_guest_retention_rate_with_repeat_guests(service):
    """Тест с повторяющимися гостями"""
    bookings = [
        {'guest_email': 'john@example.com'},
        {'guest_email': 'john@example.com'},
        {'guest_email': 'jane@example.com'},
        {'guest_email': 'bob@example.com'},
        {'guest_email': 'bob@example.com'},
        {'guest_email': 'bob@example.com'}
    ]
    result = service.get_guest_retention_rate(bookings)
    assert result == pytest.approx(66.66666666666667)


def test_get_guest_retention_rate_with_none_emails(service):
    """Тест с None в email"""
    bookings = [
        {'guest_email': None},
        {'guest_email': 'john@example.com'},
        {'guest_email': 'john@example.com'}
    ]
    result = service.get_guest_retention_rate(bookings)
    assert result == 100.0


# ============= ТЕСТЫ ДЛЯ CALCULATE_REVENUE_PER_ROOM =============

def test_calculate_revenue_per_room(sample_bookings, service):
    """Тест расчета выручки на номер"""
    result = service.calculate_revenue_per_room(sample_bookings)
    expected = {
        101: 2200.0,
        102: 1500.0,
        103: 2000.0
    }
    assert result == expected


def test_calculate_revenue_per_room_empty_list(service):
    """Тест с пустым списком"""
    result = service.calculate_revenue_per_room([])
    assert result == {}


def test_calculate_revenue_per_room_with_none_values(service):
    """Тест с None значениями"""
    bookings = [
        {'room_id': 101, 'total_price': None},
        {'room_id': 101, 'total_price': 1000.0},
        {'room_id': None, 'total_price': 500.0}
    ]
    result = service.calculate_revenue_per_room(bookings)
    expected = {101: 1000.0}
    assert result == expected


# ============= ТЕСТЫ ДЛЯ GET_BOOKING_DURATION_STATS =============

def test_get_booking_duration_stats(sample_bookings, service):
    """Тест статистики длительности бронирований"""
    result = service.get_booking_duration_stats(sample_bookings)
    expected = {
        'mean': 5.75,
        'median': 6.0,
        'min': 5,
        'max': 6
    }
    assert result == expected


def test_get_booking_duration_stats_empty_list(service):
    """Тест с пустым списком"""
    result = service.get_booking_duration_stats([])
    assert result == {}


def test_get_booking_duration_stats_with_none_dates(service):
    """Тест с None в датах"""
    bookings = [
        {'check_in': None, 'check_out': '2026-06-20'},
        {'check_in': '2026-06-15', 'check_out': '2026-06-20'},
        {'check_in': '2026-07-01', 'check_out': None}
    ]
    result = service.get_booking_duration_stats(bookings)
    expected = {
        'mean': 6.0,
        'median': 6,
        'min': 6,
        'max': 6
    }
    assert result == expected


def test_get_booking_duration_stats_with_date_objects(service):
    """Тест с date объектами"""
    bookings = [
        {'check_in': date(2026, 6, 1), 'check_out': date(2026, 6, 5)},
        {'check_in': date(2026, 6, 10), 'check_out': date(2026, 6, 15)}
    ]
    result = service.get_booking_duration_stats(bookings)
    # 2026-06-01 до 2026-06-05 = 4 дня = 5 ночей
    # 2026-06-10 до 2026-06-15 = 5 дней = 6 ночей
    expected = {
        'mean': 5.5,
        'median': 5.5,
        'min': 5,
        'max': 6
    }
    assert result == expected


# ============= ТЕСТЫ ДЛЯ DETECT_ANOMALIES =============

def test_detect_anomalies(sample_bookings, service):
    """Тест обнаружения аномалий"""
    result = service.detect_anomalies(sample_bookings)
    assert len(result) == 0


def test_detect_anomalies_empty_list(service):
    """Тест с пустым списком"""
    result = service.detect_anomalies([])
    assert result == []


def test_detect_anomalies_high_price(service):
    """Тест с высокой ценой"""
    bookings = [
        {
            'id': 1,
            'total_price': 5000.0,
            'nights': 3,
            'room_type': 'suite'
        }
    ]
    result = service.detect_anomalies(bookings)
    assert len(result) == 1
    assert result[0]['type'] == 'high_price'
    assert result[0]['price_per_night'] == 1666.6666666666667


def test_detect_anomalies_long_stay(service):
    """Тест с длительным проживанием"""
    bookings = [
        {
            'id': 1,
            'total_price': 1000.0,
            'nights': 35,
            'room_type': 'standard'
        }
    ]
    result = service.detect_anomalies(bookings)
    assert len(result) == 1
    assert result[0]['type'] == 'long_stay'
    assert result[0]['nights'] == 35


def test_detect_anomalies_with_none_values(service):
    """Тест с None значениями"""
    bookings = [
        {
            'id': 1,
            'total_price': None,
            'nights': 5,
            'room_type': 'standard'
        },
        {
            'id': 2,
            'total_price': 1000.0,
            'nights': None,
            'room_type': 'deluxe'
        }
    ]
    result = service.detect_anomalies(bookings)
    assert len(result) == 0


# ============= ТЕСТЫ ДЛЯ GENERATE_MONTHLY_REPORT =============

def test_generate_monthly_report(sample_bookings, service):
    """Тест генерации месячного отчета"""
    result = service.generate_monthly_report(sample_bookings)
    expected = {
        'total_revenue': 5700.0,
        'total_bookings': 4,
        'cancelled_count': 1,
        'cancellation_rate': 25.0,
        'average_price': 1425.0
    }
    assert result == expected


def test_generate_monthly_report_empty_list(service):
    """Тест с пустым списком"""
    result = service.generate_monthly_report([])
    assert result == {}


def test_generate_monthly_report_with_none_status(service):
    """Тест с None в статусе"""
    bookings = [
        {'total_price': 1000.0, 'status': None},
        {'total_price': 2000.0, 'status': 'cancelled'},
        {'total_price': 1500.0, 'status': 'confirmed'}
    ]
    result = service.generate_monthly_report(bookings)
    expected = {
        'total_revenue': 4500.0,
        'total_bookings': 3,
        'cancelled_count': 1,
        'cancellation_rate': 33.33333333333333,
        'average_price': 1500.0
    }
    assert result == expected


# ============= ТЕСТЫ ДЛЯ GET_FULL_ANALYTICS_REPORT =============

def test_get_full_analytics_report(sample_bookings, service):
    """Тест полного аналитического отчета"""
    result = service.get_full_analytics_report(sample_bookings)
    
    assert result['total_revenue'] == 5700.0
    assert result['average_booking_value'] == 1425.0
    assert result['cancellation_rate'] == 25.0
    assert result['total_bookings'] == 4
    assert 'monthly_trends' in result
    assert 'revenue_by_room_type' in result
    assert 'peak_season' in result
    assert 'guest_retention_rate' in result
    assert 'duration_stats' in result
    assert 'anomalies' in result


def test_get_full_analytics_report_empty(service):
    """Тест с пустыми данными"""
    result = service.get_full_analytics_report([])
    
    assert result['total_revenue'] == 0.0
    assert result['average_booking_value'] == 0.0
    assert result['cancellation_rate'] == 0.0
    assert result['total_bookings'] == 0
    assert result['monthly_trends'] == {}
    assert result['revenue_by_room_type'] == {}
    assert result['peak_season'] == {}
    assert result['guest_retention_rate'] == 0.0
    assert result['duration_stats'] == {}
    assert result['anomalies'] == []