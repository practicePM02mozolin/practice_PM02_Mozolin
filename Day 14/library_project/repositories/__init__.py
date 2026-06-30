# repositories/__init__.py
from .in_memory import (
    InMemoryBookRepository,
    InMemoryReaderRepository,
    InMemoryLoanRepository
)

__all__ = [
    'InMemoryBookRepository',
    'InMemoryReaderRepository',
    'InMemoryLoanRepository'
]