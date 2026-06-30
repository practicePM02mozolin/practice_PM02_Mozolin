# services/library_service.py
import logging
from typing import Optional, List, Dict, Any
from datetime import date, timedelta
from interfaces.repositories import BookRepository, ReaderRepository, LoanRepository


# Собственные исключения
class LibraryError(Exception):
    """Базовое исключение для библиотеки"""
    pass


class ValidationError(LibraryError):
    """Ошибка валидации данных"""
    pass


class BookNotFoundError(LibraryError):
    """Книга не найдена"""
    pass


class ReaderNotFoundError(LibraryError):
    """Читатель не найден"""
    pass


class NoAvailableCopiesError(LibraryError):
    """Нет доступных экземпляров"""
    pass


class ReaderBlockedError(LibraryError):
    """Читатель заблокирован"""
    pass


class TooManyLoansError(LibraryError):
    """Превышено максимальное количество выдач"""
    pass


class DuplicateIsbnError(LibraryError):
    """Книга с таким ISBN уже существует"""
    pass


class LoanNotFoundError(LibraryError):
    """Выдача не найдена"""
    pass


class LibraryService:
    """Сервисный слой для управления библиотекой"""
    
    def __init__(
        self,
        book_repo: BookRepository,
        reader_repo: ReaderRepository,
        loan_repo: LoanRepository
    ):
        self._book_repo = book_repo
        self._reader_repo = reader_repo
        self._loan_repo = loan_repo
        
        # Настройка логирования
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)
        
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
    
    # === Валидация ===
    def _validate_book_data(self, title: str, author: str, isbn: str, 
                           year: int, genre: str, copies: int, 
                           electronic_link: Optional[str] = None) -> None:
        """Валидация данных книги"""
        if not title or not title.strip():
            raise ValidationError("Название книги не может быть пустым")
        if not author or not author.strip():
            raise ValidationError("Автор не может быть пустым")
        if not isbn or not isbn.strip():
            raise ValidationError("ISBN не может быть пустым")
        if len(isbn) < 10:
            raise ValidationError("Некорректный ISBN")
        if year < 0 or year > date.today().year:
            raise ValidationError(f"Некорректный год: {year}")
        if copies < 0:
            raise ValidationError("Количество экземпляров не может быть отрицательным")
        if not genre or not genre.strip():
            raise ValidationError("Жанр не может быть пустым")
        if electronic_link and not electronic_link.startswith(('http://', 'https://')):
            raise ValidationError("Некорректная ссылка на электронную книгу")
    
    def _validate_reader_data(self, name: str, email: str, phone: str) -> None:
        """Валидация данных читателя"""
        if not name or not name.strip():
            raise ValidationError("Имя не может быть пустым")
        if not email or not email.strip():
            raise ValidationError("Email не может быть пустым")
        if '@' not in email or '.' not in email:
            raise ValidationError("Некорректный email")
        if not phone or not phone.strip():
            raise ValidationError("Телефон не может быть пустым")
    
    # === Бизнес-методы ===
    def add_book(
        self,
        title: str,
        author: str,
        isbn: str,
        year: int,
        genre: str,
        copies: int,
        electronic_link: Optional[str] = None
    ) -> Dict[str, Any]:
        """Добавление новой книги"""
        self._validate_book_data(title, author, isbn, year, genre, copies, electronic_link)
        
        existing = self._book_repo.find_by_isbn(isbn)
        if existing:
            raise DuplicateIsbnError(f"Книга с ISBN {isbn} уже существует")
        
        book_data = {
            'title': title.strip(),
            'author': author.strip(),
            'isbn': isbn,
            'year': year,
            'genre': genre.strip(),
            'copies': copies,
            'electronic_link': electronic_link,
            'rating': 0.0,
            'rating_count': 0
        }
        
        result = self._book_repo.save(book_data)
        self._logger.info(f"Книга добавлена: {title} (ISBN: {isbn})")
        return result
    
    def register_reader(self, name: str, email: str, phone: str) -> Dict[str, Any]:
        """Регистрация нового читателя"""
        self._validate_reader_data(name, email, phone)
        
        existing = self._reader_repo.find_by_email(email)
        if existing:
            raise ValidationError(f"Читатель с email {email} уже зарегистрирован")
        
        reader_data = {
            'name': name.strip(),
            'email': email,
            'phone': phone
        }
        
        result = self._reader_repo.save(reader_data)
        self._logger.info(f"Читатель зарегистрирован: {name} (email: {email})")
        return result
    
    def lend_book(self, book_id: int, reader_id: int) -> Dict[str, Any]:
        """Выдача книги читателю"""
        # Проверка существования книги
        book = self._book_repo.find_by_id(book_id)
        if not book:
            raise BookNotFoundError(f"Книга с ID {book_id} не найдена")
        
        # Проверка существования читателя
        reader = self._reader_repo.find_by_id(reader_id)
        if not reader:
            raise ReaderNotFoundError(f"Читатель с ID {reader_id} не найден")
        
        # Проверка блокировки
        if self._reader_repo.is_blocked(reader_id):
            raise ReaderBlockedError("Читатель заблокирован")
        
        # Проверка количества активных выдач
        active_loans = self._loan_repo.find_active_by_reader(reader_id)
        if len(active_loans) >= 5:
            raise TooManyLoansError("Читатель уже взял максимальное количество книг (5)")
        
        # Проверка наличия экземпляров
        if book.get('copies', 0) <= 0:
            raise NoAvailableCopiesError(f"Нет доступных экземпляров книги '{book['title']}'")
        
        # Проверка активной выдачи этой книги читателю
        active_loan = self._loan_repo.find_active_loan(book_id, reader_id)
        if active_loan:
            raise ValidationError("Эта книга уже выдана данному читателю")
        
        # Уменьшаем количество экземпляров
        if not self._book_repo.decrement_copies(book_id):
            raise NoAvailableCopiesError("Не удалось уменьшить количество экземпляров")
        
        # Создаем запись о выдаче
        loan_data = {
            'book_id': book_id,
            'reader_id': reader_id,
            'loan_date': date.today().isoformat(),
            'due_date': (date.today() + timedelta(days=14)).isoformat()
        }
        
        try:
            result = self._loan_repo.save(loan_data)
            self._logger.info(f"Книга выдана: {book['title']} читателю {reader['name']}")
            return result
        except Exception as e:
            # Откат: возвращаем экземпляр
            self._book_repo.increment_copies(book_id)
            self._logger.error(f"Ошибка при выдаче книги: {str(e)}")
            raise
    
    def return_book(self, book_id: int, reader_id: int) -> Dict[str, Any]:
        """Возврат книги"""
        book = self._book_repo.find_by_id(book_id)
        if not book:
            raise BookNotFoundError(f"Книга с ID {book_id} не найдена")
        
        reader = self._reader_repo.find_by_id(reader_id)
        if not reader:
            raise ReaderNotFoundError(f"Читатель с ID {reader_id} не найден")
        
        loan = self._loan_repo.find_active_loan(book_id, reader_id)
        if not loan:
            raise LoanNotFoundError("Активная выдача не найдена")
        
        # Расчет штрафа
        today = date.today()
        due_date = date.fromisoformat(loan['due_date']) if isinstance(loan['due_date'], str) else loan['due_date']
        days_overdue = (today - due_date).days
        
        fine = 0.0
        if days_overdue > 14:
            fine = days_overdue * 10  # 10 руб/день
        
        # Обновление записи о выдаче
        loan_data = {
            'return_date': today.isoformat(),
            'status': 'returned',
            'fine': fine
        }
        
        # Увеличиваем количество экземпляров
        self._book_repo.increment_copies(book_id)
        
        # Обновляем запись
        updated_loan = self._loan_repo.update(loan['id'], loan_data)
        
        # Если просрочка > 30 дней, блокируем читателя
        if days_overdue > 30:
            self._reader_repo.set_blocked(reader_id, True)
            self._logger.warning(f"Читатель {reader['name']} заблокирован за просрочку {days_overdue} дней")
        
        # Обновляем рейтинг (если возврат без просрочки)
        if days_overdue <= 0:
            self._book_repo.update_rating(book_id, 5.0)
        
        self._logger.info(f"Книга возвращена: {book['title']}, штраф: {fine} руб.")
        return updated_loan
    
    def search_books(self, query: str, **filters) -> List[Dict[str, Any]]:
        """Поиск книг"""
        if not query or len(query) < 2:
            raise ValidationError("Поисковый запрос должен содержать минимум 2 символа")
        
        result = self._book_repo.search(query, **filters)
        self._logger.debug(f"Найдено {len(result)} книг по запросу '{query}'")
        return result
    
    def get_reader_history(self, reader_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Получить историю выдач читателя"""
        reader = self._reader_repo.find_by_id(reader_id)
        if not reader:
            raise ReaderNotFoundError(f"Читатель с ID {reader_id} не найден")
        
        return self._loan_repo.get_history_by_reader(reader_id, limit)
    
    def get_recommendations(self, reader_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Получить рекомендации для читателя на основе истории"""
        reader = self._reader_repo.find_by_id(reader_id)
        if not reader:
            raise ReaderNotFoundError(f"Читатель с ID {reader_id} не найден")
        
        history = self._loan_repo.get_history_by_reader(reader_id, limit=20)
        
        if not history:
            all_books = self._book_repo.find_all(limit=20)
            sorted_books = sorted(
                all_books, 
                key=lambda b: b.get('rating', 0.0), 
                reverse=True
            )
            return sorted_books[:limit]
        
        # Собираем жанры и авторов из истории
        genres = {}
        authors = {}
        for loan in history:
            book = self._book_repo.find_by_id(loan['book_id'])
            if book:
                genre = book.get('genre', '')
                author = book.get('author', '')
                genres[genre] = genres.get(genre, 0) + 1
                authors[author] = authors.get(author, 0) + 1
        
        top_genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)[:3]
        
        read_book_ids = {loan['book_id'] for loan in history}
        recommendations = []
        
        for genre, _ in top_genres:
            for book in self._book_repo.search(genre):
                if book['id'] not in read_book_ids and len(recommendations) < limit:
                    recommendations.append(book)
        
        if len(recommendations) < limit:
            all_books = self._book_repo.find_all(limit=50)
            sorted_books = sorted(
                [b for b in all_books if b['id'] not in read_book_ids],
                key=lambda b: b.get('rating', 0.0),
                reverse=True
            )
            for book in sorted_books:
                if len(recommendations) >= limit:
                    break
                if not any(r['id'] == book['id'] for r in recommendations):
                    recommendations.append(book)
        
        self._logger.info(f"Сформировано {len(recommendations)} рекомендаций")
        return recommendations[:limit]
    
    def get_overdue_loans(self) -> List[Dict[str, Any]]:
        """Получить все просроченные выдачи"""
        today = date.today()
        overdue = self._loan_repo.find_overdue(today)
        
        result = []
        for loan in overdue:
            book = self._book_repo.find_by_id(loan['book_id'])
            reader = self._reader_repo.find_by_id(loan['reader_id'])
            due_date = date.fromisoformat(loan['due_date']) if isinstance(loan['due_date'], str) else loan['due_date']
            days_overdue = (today - due_date).days
            loan['book_title'] = book['title'] if book else 'Unknown'
            loan['reader_name'] = reader['name'] if reader else 'Unknown'
            loan['days_overdue'] = days_overdue
            result.append(loan)
        
        return result