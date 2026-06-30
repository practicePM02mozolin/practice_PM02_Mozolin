"""Кастомные исключения для системы"""


class BookingError(Exception):
    """Базовое исключение для ошибок бронирования"""
    pass


class BookingNotFoundError(BookingError):
    """Бронирование не найдено"""
    def __init__(self, booking_id: int):
        self.booking_id = booking_id
        super().__init__(f"Бронирование с ID {booking_id} не найдено")


class RoomUnavailableError(BookingError):
    """Номер недоступен"""
    def __init__(self, room_id: int, check_in: str, check_out: str):
        self.room_id = room_id
        self.check_in = check_in
        self.check_out = check_out
        super().__init__(
            f"Номер {room_id} недоступен с {check_in} по {check_out}"
        )


class InvalidBookingDataError(BookingError):
    """Неверные данные бронирования"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Неверные данные бронирования: {message}")


class AnalyticsError(Exception):
    """Ошибка при выполнении аналитики"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Ошибка аналитики: {message}")


class GuestNotFoundError(Exception):
    """Гость не найден"""
    def __init__(self, guest_id: int):
        self.guest_id = guest_id
        super().__init__(f"Гость с ID {guest_id} не найден")


class RoomNotFoundError(Exception):
    """Номер не найден"""
    def __init__(self, room_id: int):
        self.room_id = room_id
        super().__init__(f"Номер с ID {room_id} не найден")