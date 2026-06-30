# interfaces/repositories.py
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import date


class BookRepository(ABC):
    """Интерфейс репозитория книг"""
    
    @abstractmethod
    def save(self, book: Dict[str, Any]) -> Dict[str, Any]:
        """Сохранить книгу"""
        pass
    
    @abstractmethod
    def find_by_id(self, book_id: int) -> Optional[Dict[str, Any]]:
        """Найти книгу по ID"""
        pass
    
    @abstractmethod
    def find_by_isbn(self, isbn: str) -> Optional[Dict[str, Any]]:
        """Найти книгу по ISBN"""
        pass
    
    @abstractmethod
    def find_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Получить все книги с пагинацией"""
        pass
    
    @abstractmethod
    def search(self, query: str, **filters) -> List[Dict[str, Any]]:
        """Поиск книг по названию, автору, жанру"""
        pass
    
    @abstractmethod
    def update(self, book_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Обновить данные книги"""
        pass
    
    @abstractmethod
    def delete(self, book_id: int) -> bool:
        """Удалить книгу (мягкое удаление)"""
        pass
    
    @abstractmethod
    def update_rating(self, book_id: int, new_rating: float) -> None:
        """Обновить рейтинг книги"""
        pass
    
    @abstractmethod
    def decrement_copies(self, book_id: int) -> bool:
        """Атомарно уменьшить количество экземпляров"""
        pass
    
    @abstractmethod
    def increment_copies(self, book_id: int) -> bool:
        """Атомарно увеличить количество экземпляров"""
        pass


class ReaderRepository(ABC):
    """Интерфейс репозитория читателей"""
    
    @abstractmethod
    def save(self, reader: Dict[str, Any]) -> Dict[str, Any]:
        """Сохранить читателя"""
        pass
    
    @abstractmethod
    def find_by_id(self, reader_id: int) -> Optional[Dict[str, Any]]:
        """Найти читателя по ID"""
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Найти читателя по email"""
        pass
    
    @abstractmethod
    def find_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Получить всех читателей с пагинацией"""
        pass
    
    @abstractmethod
    def update(self, reader_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Обновить данные читателя"""
        pass
    
    @abstractmethod
    def is_blocked(self, reader_id: int) -> bool:
        """Проверить, заблокирован ли читатель"""
        pass
    
    @abstractmethod
    def set_blocked(self, reader_id: int, blocked: bool) -> None:
        """Установить статус блокировки"""
        pass


class LoanRepository(ABC):
    """Интерфейс репозитория выдач"""
    
    @abstractmethod
    def save(self, loan: Dict[str, Any]) -> Dict[str, Any]:
        """Сохранить запись о выдаче"""
        pass
    
    @abstractmethod
    def find_by_id(self, loan_id: int) -> Optional[Dict[str, Any]]:
        """Найти запись о выдаче по ID"""
        pass
    
    @abstractmethod
    def find_active_by_reader(self, reader_id: int) -> List[Dict[str, Any]]:
        """Найти активные выдачи читателя"""
        pass
    
    @abstractmethod
    def find_active_by_book(self, book_id: int) -> List[Dict[str, Any]]:
        """Найти активные выдачи книги"""
        pass
    
    @abstractmethod
    def find_active_loan(self, book_id: int, reader_id: int) -> Optional[Dict[str, Any]]:
        """Найти активную выдачу для пары книга-читатель"""
        pass
    
    @abstractmethod
    def find_overdue(self, as_of: date) -> List[Dict[str, Any]]:
        """Найти все просроченные выдачи"""
        pass
    
    @abstractmethod
    def update(self, loan_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Обновить запись о выдаче"""
        pass
    
    @abstractmethod
    def get_history_by_reader(self, reader_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Получить историю выдач читателя"""
        pass