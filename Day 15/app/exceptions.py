"""
Модуль с пользовательскими исключениями приложения
"""

class EntityNotFoundException(Exception):
    """
    Исключение, выбрасываемое при отсутствии запрашиваемой сущности
    """
    def __init__(self, message: str = "Entity not found"):
        self.message = message
        super().__init__(self.message)