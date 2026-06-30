# src/services/booking_service.py
from datetime import date, datetime
from typing import List, Optional
from src.domain.models import Booking, BookingStatus
from src.domain.exceptions import (
    RoomNotFoundError, RoomNotAvailableError,
    BookingConflictError, BookingNotFoundError, InvalidDatesError,
    HotelNotFoundError, CancellationNotAllowedError, DomainError
)
from src.dto.booking_dto import (
    BookingCreateDTO, BookingResponseDTO,
    BookingUpdateDTO, CancellationResultDTO
)
from src.uow.unit_of_work import UnitOfWork
from src.services.pricing_service import PricingService
from src.services.cancellation_service import CancellationContext

class BookingService:
    """Сервис для управления бронированиями"""

    def __init__(self, uow: UnitOfWork, pricing_service: PricingService):
        self.uow = uow
        self.pricing_service = pricing_service
        self.booking_repo = uow.bookings
        self.room_repo = uow.rooms
        self.hotel_repo = uow.hotels
    def create(self, dto: BookingCreateDTO) -> BookingResponseDTO:
        """Создать новое бронирование"""
        # 1. Проверяем существование номера
        room = self.room_repo.get_by_id(dto.room_id)
        if not room:
            raise RoomNotFoundError(f"Номер {dto.room_id} не найден")
        if not room.is_active:
            raise RoomNotFoundError(f"Номер {dto.room_id} не активен")

        # 2. Проверяем пересечения бронирований
        existing = self.booking_repo.get_by_room_and_dates(
            dto.room_id, dto.check_in, dto.check_out
        )
        if existing:
            raise BookingConflictError(
                f"Номер {dto.room_id} уже забронирован на эти даты",
                details={"conflicting_bookings": [b.id for b in existing]}
            )

        # 3. Рассчитываем стоимость
        total_price = self.pricing_service.calculate_price(
            room, dto.check_in, dto.check_out
        )

        # 4. Создаем бронирование
        booking = Booking(
            id=None,
            room_id=dto.room_id,
            guest_name=dto.guest_name,
            guest_email=dto.guest_email,
            check_in=dto.check_in,
            check_out=dto.check_out,
            total_price=total_price,
            status=BookingStatus.PENDING,
            cancellation_fee=0.0
        )

        #5 Сохраняем
        saved = self.booking_repo.add(booking)
        self.uow.commit()

        return BookingResponseDTO(
            id=saved.id,
            room_id=saved.room_id,
            guest_name=saved.guest_name,
            check_in=saved.check_in,
            check_out=saved.check_out,
            total_price=saved.total_price,
            status=saved.status.value,
            created_at=saved.created_at,
            cancellation_fee=saved.cancellation_fee
        )
    def cancel(self, booking_id: int) -> CancellationResultDTO:
        """Отменить бронирование с расчетом штрафа"""
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError(f"Бронирование {booking_id} не найдено")

        if booking.status in (BookingStatus.CHECKED_IN, BookingStatus.CHECKED_OUT):
            raise CancellationNotAllowedError(
                f"Нельзя отменить бронирование в статусе {booking.status.value}"
            )

        if booking.status == BookingStatus.CANCELLED:
            raise CancellationNotAllowedError("Бронирование уже отменено")

        # Получаем отель для определения политики отмены
        room = self.room_repo.get_by_id(booking.room_id)
        if not room:
            raise RoomNotFoundError(f"Номер {booking.room_id} не найден")

        hotel = self.hotel_repo.get_by_id(room.hotel_id)
        if not hotel:
            raise HotelNotFoundError(f"Отель {room.hotel_id} не найден")

        # Применяем политику отмены
        context = CancellationContext(booking, hotel.cancellation_policy)
        policy_state = context.get_policy()
        
        try:
            cancellation_fee = policy_state.calculate_fee(context)
        except CancellationNotAllowedError:
            raise

        #Обновляем бронирование
        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = datetime.now()
        booking.cancellation_fee = cancellation_fee

        self.booking_repo.update(booking)
        self.uow.commit()

        return CancellationResultDTO(
            booking_id=booking.id,
            cancellation_fee=cancellation_fee,
            refund_amount=booking.total_price - cancellation_fee,
            policy=policy_state.get_policy_name(),
            days_before_checkin=context.days_before_checkin
        )

    def get_available_rooms(
        self,
        hotel_id: int,
        check_in: date,
        check_out: date,
        capacity: Optional[int] = None
    ) -> List[dict]:
        """Получить доступные номера в отеле на указанные даты"""
        rooms = self.room_repo.get_by_hotel(hotel_id, active_only=True)

        if capacity:
            rooms = [r for r in rooms if r.capacity >= capacity]

        available = []
        for room in rooms:
            existing = self.booking_repo.get_by_room_and_dates(
                room.id, check_in, check_out
            )
            if not existing:
                available.append({
                    'room_id': room.id,
                    'number': room.number,
                    'capacity': room.capacity,
                    'price_per_night': room.price_per_night
                })
        return available

    def confirm(self, booking_id: int) -> None:
        """Подтвердить бронирование (администратор)"""
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError(f"Бронирование {booking_id} не найдено")

        if booking.status != BookingStatus.PENDING:
            raise DomainError(
                f"Бронирование в статусе {booking.status.value} нельзя подтвердить"
            )

        booking.status = BookingStatus.CONFIRMED
        self.booking_repo.update(booking)
        self.uow.commit()

    def get_by_id(self, booking_id: int) -> Optional[BookingResponseDTO]:
        """Получить бронирование по ID"""
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            return None
        return BookingResponseDTO(
            id=booking.id,
            room_id=booking.room_id,
            guest_name=booking.guest_name,
            check_in=booking.check_in,
            check_out=booking.check_out,
            total_price=booking.total_price,
            status=booking.status.value,
            created_at=booking.created_at,
            cancellation_fee=booking.cancellation_fee
        )

    def get_all(self, **filters) -> List[BookingResponseDTO]:
        """Получить все бронирования с фильтрами"""
        bookings = self.booking_repo.get_all(**filters)
        return [
            BookingResponseDTO(
                id=b.id,
                room_id=b.room_id,
                guest_name=b.guest_name,
                check_in=b.check_in,
                check_out=b.check_out,
                total_price=b.total_price,
                status=b.status.value,
                created_at=b.created_at,
                cancellation_fee=b.cancellation_fee
            )
            for b in bookings
        ]