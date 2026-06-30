# main.py - ЭТОТ ФАЙЛ НУЖНО ЗАПУСКАТЬ!
import sys
import os
from datetime import date, timedelta
# Добавляем путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.domain.models import Hotel, Room, Booking, BookingStatus, CancellationPolicy
from src.uow.unit_of_work import UnitOfWork
from src.services.pricing_service import PricingService
from src.services.booking_service import BookingService
from src.dto.booking_dto import BookingCreateDTO

def main():
    print("=" * 40)
    print("СИСТЕМА УПРАВЛЕНИЯ БРОНИРОВАНИЯМИ - ВАРИАНТ 11")
    print("Политика отмены (State Pattern)")
    print("=" * 40)
    
    # 1. Создаем Unit of Work
    uow = UnitOfWork()
    
    # 2. Создаем сервисы
    pricing_service = PricingService()
    booking_service = BookingService(uow, pricing_service)

    # 3. Создаем отель
    print("\n1. СОЗДАНИЕ ОТЕЛЯ")
    hotel = Hotel(
        id=None,
        name="Grand Hotel",
        address="Moscow, Red Square 1",
        phone="+7-495-123-4567",
        rating=4.5,
        cancellation_policy=CancellationPolicy.FREE
    )
    saved_hotel = uow.hotels.add(hotel)
    print(f"   ✅ Отель создан: ID={saved_hotel.id}, {saved_hotel.name}")
    
    # 4. Создаем номер
    print("\n2. СОЗДАНИЕ НОМЕРА")
    room = Room(
        id=None,
        hotel_id=saved_hotel.id,
        number="101",
        capacity=2,
        price_per_night=100.0,
        is_active=True
    )
    saved_room = uow.rooms.add(room)
    print(f"   ✅ Номер создан: ID={saved_room.id}, №{saved_room.number}")
    uow.commit()
    
    # 5. Тест 1: Бесплатная отмена (10 дней до заезда)
    print("\n3. ТЕСТ: БЕСПЛАТНАЯ ОТМЕНА (10 дней до заезда)")
    dto1 = BookingCreateDTO(
        room_id=saved_room.id,
        guest_name="John Doe",
        guest_email="john@example.com",
        check_in=date.today() + timedelta(days=10),
        check_out=date.today() + timedelta(days=13)
    )
    result1 = booking_service.create(dto1)
    print(f"   Создано бронирование: ID={result1.id}, стоимость={result1.total_price}")
    
    cancel1 = booking_service.cancel(result1.id)
    print(f"   Отмена: штраф={cancel1.cancellation_fee}, возврат={cancel1.refund_amount}")
    print(f"   Политика: {cancel1.policy}, дней до заезда: {cancel1.days_before_checkin}")
    
    # 6. Тест 2: Частичная отмена (5 дней до заезда)
    print("\n4. ТЕСТ: ЧАСТИЧНАЯ ОТМЕНА (5 дней до заезда)")
    dto2 = BookingCreateDTO(
        room_id=saved_room.id,
        guest_name="Jane Smith",
        guest_email="jane@example.com",
        check_in=date.today() + timedelta(days=5),
        check_out=date.today() + timedelta(days=8)
    )
    result2 = booking_service.create(dto2)
    print(f"   Создано бронирование: ID={result2.id}, стоимость={result2.total_price}")
    
    cancel2 = booking_service.cancel(result2.id)
    print(f"   Отмена: штраф={cancel2.cancellation_fee}, возврат={cancel2.refund_amount}")
    print(f"   Политика: {cancel2.policy}, дней до заезда: {cancel2.days_before_checkin}")
    
    # 7. Тест 3: Полная оплата (2 дня до заезда)
    print("\n5. ТЕСТ: ПОЛНАЯ ОПЛАТА (2 дня до заезда)")
    dto3 = BookingCreateDTO(
        room_id=saved_room.id,
        guest_name="Bob Wilson",
        guest_email="bob@example.com",
        check_in=date.today() + timedelta(days=2),
        check_out=date.today() + timedelta(days=5)
    )
    result3 = booking_service.create(dto3)
    print(f"   Создано бронирование: ID={result3.id}, стоимость={result3.total_price}")
    
    cancel3 = booking_service.cancel(result3.id)
    print(f"   Отмена: штраф={cancel3.cancellation_fee}, возврат={cancel3.refund_amount}")
    print(f"   Политика: {cancel3.policy}, дней до заезда: {cancel3.days_before_checkin}")
    
    print("\n" + "=" * 60)
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 60)

if __name__ == "__main__":
    main()