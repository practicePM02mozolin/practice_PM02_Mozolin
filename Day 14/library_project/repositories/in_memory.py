# repositories/in_memory.py
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from collections import defaultdict
from interfaces.repositories import BookRepository, ReaderRepository, LoanRepository


class InMemoryBookRepository(BookRepository):
    """In-Memory реализация репозитория книг"""
    
    def __init__(self):
        self._books: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1
    
    def save(self, book: Dict[str, Any]) -> Dict[str, Any]:
        book_id = self._next_id
        self._next_id += 1
        book['id'] = book_id
        book['is_deleted'] = False
        book['rating'] = book.get('rating', 0.0)
        book['rating_count'] = book.get('rating_count', 0)
        self._books[book_id] = book.copy()
        return self._books[book_id]
    
    def find_by_id(self, book_id: int) -> Optional[Dict[str, Any]]:
        book = self._books.get(book_id)
        if book and not book.get('is_deleted', False):
            return book.copy()
        return None
    
    def find_by_isbn(self, isbn: str) -> Optional[Dict[str, Any]]:
        for book in self._books.values():
            if book.get('isbn') == isbn and not book.get('is_deleted', False):
                return book.copy()
        return None
    
    def find_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        result = [b.copy() for b in self._books.values() 
                  if not b.get('is_deleted', False)]
        return result[skip:skip + limit]
    
    def search(self, query: str, **filters) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        result = []
        for book in self._books.values():
            if book.get('is_deleted', False):
                continue
            if (query_lower in book.get('title', '').lower() or
                query_lower in book.get('author', '').lower() or
                query_lower in book.get('genre', '').lower()):
                result.append(book.copy())
        
        if 'genre' in filters:
            result = [b for b in result if b.get('genre') == filters['genre']]
        if 'year' in filters:
            result = [b for b in result if b.get('year') == filters['year']]
        
        return result
    
    def update(self, book_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        book = self._books.get(book_id)
        if not book or book.get('is_deleted', False):
            return None
        for key, value in data.items():
            if key != 'id' and key != 'is_deleted':
                book[key] = value
        return book.copy()
    
    def delete(self, book_id: int) -> bool:
        book = self._books.get(book_id)
        if not book:
            return False
        book['is_deleted'] = True
        return True
    
    def update_rating(self, book_id: int, new_rating: float) -> None:
        book = self._books.get(book_id)
        if book and not book.get('is_deleted', False):
            current_total = book.get('rating', 0.0) * book.get('rating_count', 0)
            book['rating_count'] = book.get('rating_count', 0) + 1
            book['rating'] = (current_total + new_rating) / book['rating_count']
    
    def decrement_copies(self, book_id: int) -> bool:
        book = self._books.get(book_id)
        if not book or book.get('is_deleted', False):
            return False
        if book.get('copies', 0) <= 0:
            return False
        book['copies'] -= 1
        return True
    
    def increment_copies(self, book_id: int) -> bool:
        book = self._books.get(book_id)
        if not book or book.get('is_deleted', False):
            return False
        book['copies'] += 1
        return True


class InMemoryReaderRepository(ReaderRepository):
    """In-Memory реализация репозитория читателей"""
    
    def __init__(self):
        self._readers: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1
    
    def save(self, reader: Dict[str, Any]) -> Dict[str, Any]:
        reader_id = self._next_id
        self._next_id += 1
        reader['id'] = reader_id
        reader['blocked'] = False
        reader['registration_date'] = date.today().isoformat()
        self._readers[reader_id] = reader.copy()
        return self._readers[reader_id]
    
    def find_by_id(self, reader_id: int) -> Optional[Dict[str, Any]]:
        return self._readers.get(reader_id, {}).copy() if reader_id in self._readers else None
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        for reader in self._readers.values():
            if reader.get('email') == email:
                return reader.copy()
        return None
    
    def find_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        result = [r.copy() for r in self._readers.values()]
        return result[skip:skip + limit]
    
    def update(self, reader_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        reader = self._readers.get(reader_id)
        if not reader:
            return None
        for key, value in data.items():
            if key != 'id':
                reader[key] = value
        return reader.copy()
    
    def is_blocked(self, reader_id: int) -> bool:
        reader = self._readers.get(reader_id)
        return reader.get('blocked', False) if reader else True
    
    def set_blocked(self, reader_id: int, blocked: bool) -> None:
        reader = self._readers.get(reader_id)
        if reader:
            reader['blocked'] = blocked


class InMemoryLoanRepository(LoanRepository):
    """In-Memory реализация репозитория выдач"""
    
    def __init__(self):
        self._loans: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1
        self._reader_loans: Dict[int, List[int]] = defaultdict(list)
    
    def save(self, loan: Dict[str, Any]) -> Dict[str, Any]:
        loan_id = self._next_id
        self._next_id += 1
        loan['id'] = loan_id
        loan['return_date'] = None
        loan['status'] = 'active'
        loan['fine'] = 0.0
        self._loans[loan_id] = loan.copy()
        self._reader_loans[loan['reader_id']].append(loan_id)
        return self._loans[loan_id]
    
    def find_by_id(self, loan_id: int) -> Optional[Dict[str, Any]]:
        return self._loans.get(loan_id, {}).copy() if loan_id in self._loans else None
    
    def find_active_by_reader(self, reader_id: int) -> List[Dict[str, Any]]:
        result = []
        for loan_id in self._reader_loans.get(reader_id, []):
            loan = self._loans.get(loan_id)
            if loan and loan.get('status') == 'active':
                result.append(loan.copy())
        return result
    
    def find_active_by_book(self, book_id: int) -> List[Dict[str, Any]]:
        result = []
        for loan in self._loans.values():
            if loan.get('book_id') == book_id and loan.get('status') == 'active':
                result.append(loan.copy())
        return result
    
    def find_active_loan(self, book_id: int, reader_id: int) -> Optional[Dict[str, Any]]:
        for loan in self._loans.values():
            if (loan.get('book_id') == book_id and 
                loan.get('reader_id') == reader_id and 
                loan.get('status') == 'active'):
                return loan.copy()
        return None
    
    def find_overdue(self, as_of: date) -> List[Dict[str, Any]]:
        result = []
        for loan in self._loans.values():
            if loan.get('status') == 'active':
                loan_date = loan.get('loan_date')
                if isinstance(loan_date, str):
                    loan_date = date.fromisoformat(loan_date)
                days = (as_of - loan_date).days
                if days > 14:
                    result.append(loan.copy())
        return result
    
    def update(self, loan_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        loan = self._loans.get(loan_id)
        if not loan:
            return None
        for key, value in data.items():
            if key != 'id':
                loan[key] = value
        return loan.copy()
    
    def get_history_by_reader(self, reader_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        result = []
        for loan_id in self._reader_loans.get(reader_id, []):
            loan = self._loans.get(loan_id)
            if loan:
                result.append(loan.copy())
        return result[:limit]