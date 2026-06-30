"""
Пользовательские исключения приложения
"""


class EntityNotFoundException(Exception):
    """
    Исключение, выбрасываемое при отсутствии запрашиваемой сущности в БД
    """
    def __init__(self, message: str = "Entity not found"):
        self.message = message
        super().__init__(self.message)


class DeliveryCalculationException(Exception):
    """
    Исключение, выбрасываемое при ошибке расчёта доставки
    """
    def __init__(self, message: str = "Delivery calculation failed"):
        self.message = message
        super().__init__(self.message)