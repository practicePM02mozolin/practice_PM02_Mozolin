"""Unit of Work"""

from typing import Dict, Type
from src.application.interfaces import IUnitOfWork, IBookingRepository
from src.infrastructure.repositories import InMemoryBookingRepository


class UnitOfWork(IUnitOfWork):
    """Реализация Unit of Work"""
    
    def __init__(self):
        self._repositories: Dict[str, IBookingRepository] = {}
        self._is_active = False
    
    def begin(self) -> None:
        """Начать транзакцию"""
        self._is_active = True
    
    def commit(self) -> None:
        """Подтвердить транзакцию"""
        if not self._is_active:
            raise ValueError("Транзакция не активна")
        self._is_active = False
    
    def rollback(self) -> None:
        """Откатить транзакцию"""
        self._is_active = False
    
    def get_repository(self, repo_type: str) -> IBookingRepository:
        """Получить репозиторий"""
        if repo_type not in self._repositories:
            if repo_type == 'booking':
                self._repositories[repo_type] = InMemoryBookingRepository()
            else:
                raise ValueError(f"Неизвестный тип репозитория: {repo_type}")
        
        return self._repositories[repo_type]