# src/application/services.py
"""
Сервис аналитики для системы бронирования
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, date
import math
from src.core.exceptions import AnalyticsError
from src.application.interfaces import IBookingRepository, IAnalyticsService


class AnalyticsService(IAnalyticsService):
    """Сервис для анализа данных по бронированиям"""
    
    def __init__(self, booking_repository: IBookingRepository):
        self.booking_repository = booking_repository
    
    def get_total_revenue(self, bookings: List[Dict]) -> float:
        """Рассчитать общую выручку от бронирований."""
        try:
            total = 0.0
            for booking in bookings:
                price = booking.get('total_price')
                if price is not None and isinstance(price, (int, float)):
                    if not (isinstance(price, float) and math.isnan(price)):
                        total += price
            return total
        except Exception as e:
            raise AnalyticsError(f"Ошибка при расчете общей выручки: {str(e)}")
    
    def get_average_booking_value(self, bookings: List[Dict]) -> float:
        """Рассчитать среднюю стоимость бронирования."""
        try:
            if not bookings:
                return 0.0
            total = self.get_total_revenue(bookings)
            return total / len(bookings)
        except Exception as e:
            raise AnalyticsError(f"Ошибка при расчете средней стоимости: {str(e)}")
    
    def get_occupancy_rate(self, total_rooms: int, booked_rooms: int) -> float:
        """Рассчитать процент загрузки отеля."""
        try:
            if total_rooms <= 0:
                return 0.0
            if booked_rooms < 0:
                booked_rooms = 0
            if booked_rooms > total_rooms:
                booked_rooms = total_rooms
            return (booked_rooms / total_rooms) * 100
        except Exception as e:
            raise AnalyticsError(f"Ошибка при расчете загрузки: {str(e)}")
    
    def get_booking_trends(self, bookings: List[Dict]) -> Dict[str, int]:
        """Анализ трендов бронирований по месяцам."""
        try:
            trends = {}
            for booking in bookings:
                created_at = booking.get('created_at')
                if created_at is None:
                    continue
                try:
                    if isinstance(created_at, str):
                        try:
                            date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        except ValueError:
                            date_obj = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    elif isinstance(created_at, datetime):
                        date_obj = created_at
                    else:
                        continue
                    month = date_obj.strftime('%Y-%m')
                    trends[month] = trends.get(month, 0) + 1
                except (ValueError, TypeError):
                    continue
            return trends
        except Exception as e:
            raise AnalyticsError(f"Ошибка при анализе трендов: {str(e)}")
    
    def get_cancellation_rate(self, bookings: List[Dict]) -> float:
        """Рассчитать процент отмененных бронирований."""
        try:
            if not bookings:
                return 0.0
            cancelled = 0
            total_valid = 0
            for booking in bookings:
                status = booking.get('status')
                if status is None:
                    continue
                total_valid += 1
                if isinstance(status, str) and status.lower() == 'cancelled':
                    cancelled += 1
                elif hasattr(status, 'value') and status.value == 'cancelled':
                    cancelled += 1
            if total_valid == 0:
                return 0.0
            return (cancelled / total_valid) * 100
        except Exception as e:
            raise AnalyticsError(f"Ошибка при расчете процента отмен: {str(e)}")
    
    def get_revenue_by_room_type(self, bookings: List[Dict]) -> Dict[str, float]:
        """Анализ выручки по типам номеров."""
        try:
            revenue_by_type = {}
            for booking in bookings:
                room_type = booking.get('room_type', 'unknown')
                if room_type is None:
                    room_type = 'unknown'
                price = booking.get('total_price')
                if price is not None and isinstance(price, (int, float)):
                    if not (isinstance(price, float) and math.isnan(price)):
                        revenue_by_type[room_type] = revenue_by_type.get(room_type, 0) + price
            return revenue_by_type
        except Exception as e:
            raise AnalyticsError(f"Ошибка при анализе выручки по типам номеров: {str(e)}")
    
    def get_peak_season_analysis(self, bookings: List[Dict]) -> Dict[str, Any]:
        """Анализ пиковых сезонов."""
        try:
            if not bookings:
                return {}
            
            month_counts = {}
            for booking in bookings:
                check_in = booking.get('check_in')
                if check_in is None:
                    continue
                
                try:
                    if isinstance(check_in, str):
                        try:
                            date_obj = datetime.fromisoformat(check_in.replace('Z', '+00:00'))
                        except ValueError:
                            try:
                                date_obj = datetime.strptime(check_in, '%Y-%m-%d')
                            except ValueError:
                                date_obj = datetime.strptime(check_in, '%Y-%m-%d %H:%M:%S')
                    elif isinstance(check_in, datetime):
                        date_obj = check_in
                    elif isinstance(check_in, date):
                        date_obj = datetime.combine(check_in, datetime.min.time())
                    else:
                        continue
                    
                    month = date_obj.month
                    month_counts[month] = month_counts.get(month, 0) + 1
                except (ValueError, TypeError):
                    continue
            
            if not month_counts:
                return {}
            
            # ИСПРАВЛЕНО: находим месяц с максимальным количеством
            # Если несколько месяцев с одинаковым количеством, берем первый попавшийся
            peak_month, peak_count = max(month_counts.items(), key=lambda x: (x[1], x[0]))
            low_month, low_count = min(month_counts.items(), key=lambda x: (x[1], x[0]))
            
            return {
                'peak_month': peak_month,
                'peak_count': peak_count,
                'low_month': low_month,
                'low_count': low_count
            }
        except Exception as e:
            raise AnalyticsError(f"Ошибка при анализе пиковых сезонов: {str(e)}")
    
    def get_guest_retention_rate(self, bookings: List[Dict]) -> float:
        """Рассчитать процент повторных гостей."""
        try:
            if not bookings:
                return 0.0
            unique_guests = set()
            repeat_guests = set()
            guest_bookings = {}
            for booking in bookings:
                email = booking.get('guest_email')
                if email is None or not isinstance(email, str):
                    continue
                email = email.strip().lower()
                if not email:
                    continue
                if email not in guest_bookings:
                    guest_bookings[email] = []
                guest_bookings[email].append(booking)
                unique_guests.add(email)
            for email, bookings_list in guest_bookings.items():
                if len(bookings_list) > 1:
                    repeat_guests.add(email)
            if len(unique_guests) == 0:
                return 0.0
            return (len(repeat_guests) / len(unique_guests)) * 100
        except Exception as e:
            raise AnalyticsError(f"Ошибка при расчете повторных гостей: {str(e)}")
    
    def calculate_revenue_per_room(self, bookings: List[Dict]) -> Dict[int, float]:
        """Рассчитать выручку на номер."""
        try:
            revenue_per_room = {}
            for booking in bookings:
                room_id = booking.get('room_id')
                if room_id is None:
                    continue
                price = booking.get('total_price')
                if price is not None and isinstance(price, (int, float)):
                    if not (isinstance(price, float) and math.isnan(price)):
                        revenue_per_room[room_id] = revenue_per_room.get(room_id, 0) + price
            return revenue_per_room
        except Exception as e:
            raise AnalyticsError(f"Ошибка при расчете выручки на номер: {str(e)}")
    
    def get_booking_duration_stats(self, bookings: List[Dict]) -> Dict[str, float]:
        """Статистика по длительности бронирований."""
        try:
            if not bookings:
                return {}
            
            durations = []
            for booking in bookings:
                check_in = booking.get('check_in')
                check_out = booking.get('check_out')
                
                if check_in is None or check_out is None:
                    continue
                
                try:
                    # Преобразуем check_in в date
                    if isinstance(check_in, str):
                        try:
                            check_in_date = datetime.fromisoformat(check_in.replace('Z', '+00:00')).date()
                        except ValueError:
                            try:
                                check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
                            except ValueError:
                                check_in_date = datetime.strptime(check_in, '%Y-%m-%d %H:%M:%S').date()
                    elif isinstance(check_in, datetime):
                        check_in_date = check_in.date()
                    elif isinstance(check_in, date):
                        check_in_date = check_in
                    else:
                        continue
                    
                    # Преобразуем check_out в date
                    if isinstance(check_out, str):
                        try:
                            check_out_date = datetime.fromisoformat(check_out.replace('Z', '+00:00')).date()
                        except ValueError:
                            try:
                                check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
                            except ValueError:
                                check_out_date = datetime.strptime(check_out, '%Y-%m-%d %H:%M:%S').date()
                    elif isinstance(check_out, datetime):
                        check_out_date = check_out.date()
                    elif isinstance(check_out, date):
                        check_out_date = check_out
                    else:
                        continue
                    
                    duration = (check_out_date - check_in_date).days
                    if duration > 0:
                        durations.append(duration + 1)
                except (ValueError, TypeError):
                    continue
            
            if not durations:
                return {}
            
            sorted_durations = sorted(durations)
            n = len(sorted_durations)
            
            return {
                'mean': sum(durations) / n,
                'median': sorted_durations[n // 2] if n % 2 == 1 else (sorted_durations[n // 2 - 1] + sorted_durations[n // 2]) / 2,
                'min': min(durations),
                'max': max(durations)
            }
        except Exception as e:
            raise AnalyticsError(f"Ошибка при расчете статистики длительности: {str(e)}")
    
    def detect_anomalies(self, bookings: List[Dict]) -> List[Dict]:
        """Обнаружение аномалий в бронированиях."""
        try:
            if not bookings:
                return []
            anomalies = []
            for booking in bookings:
                booking_id = booking.get('id', 'unknown')
                price = booking.get('total_price')
                nights = booking.get('nights', 1)
                room_type = booking.get('room_type', 'unknown')
                if room_type is None:
                    room_type = 'unknown'
                if price is not None and isinstance(price, (int, float)):
                    if not (isinstance(price, float) and math.isnan(price)):
                        if nights is not None and isinstance(nights, (int, float)):
                            if nights > 0:
                                price_per_night = price / nights
                                if price_per_night > 1000:
                                    anomalies.append({
                                        'booking_id': booking_id,
                                        'type': 'high_price',
                                        'price_per_night': price_per_night,
                                        'room_type': room_type,
                                        'total_price': price,
                                        'nights': nights
                                    })
                if nights is not None and isinstance(nights, (int, float)):
                    if nights > 30:
                        anomalies.append({
                            'booking_id': booking_id,
                            'type': 'long_stay',
                            'nights': nights,
                            'room_type': room_type
                        })
            return anomalies
        except Exception as e:
            raise AnalyticsError(f"Ошибка при обнаружении аномалий: {str(e)}")
    
    def generate_monthly_report(self, bookings: List[Dict]) -> Dict[str, Any]:
        """Генерация месячного отчета."""
        try:
            if not bookings:
                return {}
            total_revenue = self.get_total_revenue(bookings)
            total_bookings = len(bookings)
            if total_bookings == 0:
                return {}
            cancelled_count = 0
            for booking in bookings:
                status = booking.get('status')
                if status is not None:
                    if isinstance(status, str) and status.lower() == 'cancelled':
                        cancelled_count += 1
                    elif hasattr(status, 'value') and status.value == 'cancelled':
                        cancelled_count += 1
            return {
                'total_revenue': total_revenue,
                'total_bookings': total_bookings,
                'cancelled_count': cancelled_count,
                'cancellation_rate': (cancelled_count / total_bookings) * 100,
                'average_price': total_revenue / total_bookings
            }
        except Exception as e:
            raise AnalyticsError(f"Ошибка при генерации месячного отчета: {str(e)}")
    
    def get_full_analytics_report(self, bookings: List[Dict]) -> Dict[str, Any]:
        """Полный аналитический отчет."""
        try:
            return {
                'total_revenue': self.get_total_revenue(bookings),
                'average_booking_value': self.get_average_booking_value(bookings),
                'cancellation_rate': self.get_cancellation_rate(bookings),
                'monthly_trends': self.get_booking_trends(bookings),
                'revenue_by_room_type': self.get_revenue_by_room_type(bookings),
                'peak_season': self.get_peak_season_analysis(bookings),
                'guest_retention_rate': self.get_guest_retention_rate(bookings),
                'duration_stats': self.get_booking_duration_stats(bookings),
                'anomalies': self.detect_anomalies(bookings),
                'total_bookings': len(bookings)
            }
        except Exception as e:
            raise AnalyticsError(f"Ошибка при генерации полного отчета: {str(e)}")