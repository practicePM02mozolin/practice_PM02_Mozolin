"""CLI интерфейс"""

import sys
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any


def cli():
    """Командная строка для аналитики"""
    parser = argparse.ArgumentParser(description='Аналитика бронирований')
    subparsers = parser.add_subparsers(dest='command', help='Команды')
    
    # Команда для расчета общей выручки
    revenue_parser = subparsers.add_parser('revenue', help='Расчет общей выручки')
    revenue_parser.add_argument('--bookings', type=str, help='Путь к файлу с бронированиями')
    
    # Команда для расчета процента отмен
    cancel_parser = subparsers.add_parser('cancellation', help='Расчет процента отмен')
    cancel_parser.add_argument('--bookings', type=str, help='Путь к файлу с бронированиями')
    
    # Команда для расчета загрузки
    occupancy_parser = subparsers.add_parser('occupancy', help='Расчет загрузки')
    occupancy_parser.add_argument('--total-rooms', type=int, required=True, help='Общее количество номеров')
    occupancy_parser.add_argument('--booked-rooms', type=int, required=True, help='Количество забронированных номеров')
    
    # Команда для полного отчета
    report_parser = subparsers.add_parser('report', help='Полный отчет')
    report_parser.add_argument('--bookings', type=str, help='Путь к файлу с бронированиями')
    report_parser.add_argument('--output', type=str, help='Путь для сохранения отчета')
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    
    # Загрузка данных
    bookings = []
    if hasattr(args, 'bookings') and args.bookings:
        try:
            with open(args.bookings, 'r', encoding='utf-8') as f:
                bookings = json.load(f)
        except FileNotFoundError:
            print(f"Ошибка: файл {args.bookings} не найден", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Ошибка: неверный формат JSON в файле {args.bookings}", file=sys.stderr)
            sys.exit(1)
    
    # Создаем сервис аналитики
    from src.infrastructure.repositories import InMemoryBookingRepository
    from src.application.services import AnalyticsService
    
    repository = InMemoryBookingRepository()
    service = AnalyticsService(repository)
    
    # Выполнение команд
    if args.command == 'revenue':
        result = service.get_total_revenue(bookings)
        print(f"Общая выручка: {result}")
    
    elif args.command == 'cancellation':
        result = service.get_cancellation_rate(bookings)
        print(f"Процент отмен: {result}%")
    
    elif args.command == 'occupancy':
        result = service.get_occupancy_rate(args.total_rooms, args.booked_rooms)
        print(f"Загрузка: {result}%")
    
    elif args.command == 'report':
        result = service.get_full_analytics_report(bookings)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Отчет сохранен в {args.output}")
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    cli()